extends CharacterBody2D
class_name Player
## The player actor. Composition of components + a locomotion state machine.
## Presentation lives in PlayerVisuals; combat (shoot/grenade/melee) is handled here
## centrally so locomotion states stay focused on movement feel.
##
## Multiplayer-ready: all input comes from InputManager.get_intent(slot); nothing here
## reads the global Input singleton, so slots 1-3 are added by spawning more Players.

@export var slot: int = 0
@export var character: CharacterData
@export var default_tuning: MovementTuning
@export var default_weapon: WeaponData

# --- Components (wired in the scene) ---------------------------------------
@onready var state_machine: StateMachine = $StateMachine
@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var weapons: WeaponHolder = $WeaponHolder
@onready var aim_pivot: Node2D = $AimPivot
@onready var melee_hitbox: HitboxComponent = $MeleeHitbox
@onready var visuals: Node = $Visuals
@onready var wall_ray_l: RayCast2D = $WallRayLeft
@onready var wall_ray_r: RayCast2D = $WallRayRight
@onready var ledge_ray: RayCast2D = $LedgeRay
@onready var floor_ray: RayCast2D = $FloorRay

var tuning: MovementTuning
var intent: PlayerIntent
var facing: int = 1                       ## 1 = right, -1 = left
var aim_dir: Vector2 = Vector2.RIGHT

# Game-feel timers
var coyote: float = 0.0
var jump_buffer: float = 0.0
var air_jumps_used: int = 0
var dash_cd: float = 0.0

# Resources / run state
var grenades: int = 3
var special_charge: float = 0.0
var ability_cd: float = 0.0
var _melee_cd: float = 0.0

const STATE_SCRIPTS := {
	"idle": preload("res://src/player/states/IdleState.gd"),
	"run": preload("res://src/player/states/RunState.gd"),
	"jump": preload("res://src/player/states/JumpState.gd"),
	"doublejump": preload("res://src/player/states/DoubleJumpState.gd"),
	"fall": preload("res://src/player/states/FallState.gd"),
	"dash": preload("res://src/player/states/DashState.gd"),
	"wallslide": preload("res://src/player/states/WallSlideState.gd"),
	"walljump": preload("res://src/player/states/WallJumpState.gd"),
	"ledgegrab": preload("res://src/player/states/LedgeGrabState.gd"),
	"hurt": preload("res://src/player/states/HurtState.gd"),
	"dead": preload("res://src/player/states/DeadState.gd"),
}

func _ready() -> void:
	add_to_group("player")
	_apply_character()
	_build_states()
	health.died.connect(_on_died)
	health.damaged.connect(_on_damaged)
	weapons.recoil_applied.connect(func(imp): velocity += imp)
	hurtbox.team = 0
	melee_hitbox.owner_node = self
	EventBus.player_respawned.connect(_on_respawned)
	GameManager.register_player(slot)
	EventBus.player_spawned.emit(self, slot)

func _apply_character() -> void:
	tuning = default_tuning
	var weapon := default_weapon
	if character:
		if character.move_tuning:
			tuning = character.move_tuning
		if character.starting_weapon:
			weapon = character.starting_weapon
		health.max_hp = character.max_hp
		health.max_shield = character.max_shield
	if tuning == null:
		tuning = MovementTuning.new()          # safe defaults so the player always moves
	health.reset()
	weapons.slot = slot
	weapons.team = 0
	weapons.equip(weapon if weapon else _fallback_weapon())

func _fallback_weapon() -> WeaponData:
	# Guarantees the player can always shoot even before any .tres is authored.
	var pd := ProjectileData.new()
	var wd := WeaponData.new()
	wd.projectile = pd
	return wd

func _build_states() -> void:
	for key in STATE_SCRIPTS:
		var s: State = STATE_SCRIPTS[key].new()
		s.name = key
		state_machine.add_child(s)
	state_machine.boot(self)
	state_machine.state_changed.connect(func(n): EventBus.player_state_changed.emit(slot, n))

func _physics_process(delta: float) -> void:
	if GameManager.state == GameManager.GameState.PAUSED:
		return
	intent = InputManager.get_intent(slot)
	_tick_timers(delta)
	_update_aim()
	if not state_machine.is_state(&"dead") and not state_machine.is_state(&"hurt"):
		_handle_combat()
	state_machine.physics_update(delta)
	move_and_slide()
	_post_move(delta)

# --- Timers & aim ----------------------------------------------------------
func _tick_timers(delta: float) -> void:
	if intent.jump_pressed:
		jump_buffer = tuning.jump_buffer
	jump_buffer = maxf(0.0, jump_buffer - delta)
	dash_cd = maxf(0.0, dash_cd - delta)
	ability_cd = maxf(0.0, ability_cd - delta)
	_melee_cd = maxf(0.0, _melee_cd - delta)

func _update_aim() -> void:
	aim_dir = intent.aim
	# Diagonal aim vectors have fractional x (e.g. 0.707) — compare, don't int()-truncate.
	if aim_dir.x > 0.01:
		facing = 1
	elif aim_dir.x < -0.01:
		facing = -1
	elif absf(intent.move.x) > 0.1:
		facing = 1 if intent.move.x > 0 else -1
	aim_pivot.rotation = aim_dir.angle()

func _post_move(delta: float) -> void:
	if is_on_floor():
		coyote = tuning.coyote_time
		air_jumps_used = 0
	else:
		coyote = maxf(0.0, coyote - delta)

# --- Movement helpers used by states ---------------------------------------
func apply_gravity(delta: float, scale: float = 1.0) -> void:
	var g := tuning.gravity * scale
	if velocity.y > 0:
		g *= tuning.fall_gravity_mult
	velocity.y = minf(velocity.y + g * delta, tuning.max_fall_speed)

func move_horizontal(delta: float, airborne: bool) -> void:
	var target := intent.move.x * tuning.max_speed
	var accel: float
	if absf(target) < 0.01:
		accel = tuning.air_friction if airborne else tuning.friction
	elif signf(target) != signf(velocity.x) and absf(velocity.x) > 1.0:
		accel = tuning.deceleration               # turning around: snappy
	else:
		accel = tuning.air_acceleration if airborne else tuning.acceleration
	velocity.x = move_toward(velocity.x, target, accel * delta)

func start_jump(vel: float) -> void:
	velocity.y = -vel
	jump_buffer = 0.0
	coyote = 0.0

func try_consume_jump_buffer() -> bool:
	return jump_buffer > 0.0

func wall_dir() -> int:
	# Returns the direction of an adjacent wall (-1 left, 1 right, 0 none).
	if wall_ray_r.is_colliding():
		return 1
	if wall_ray_l.is_colliding():
		return -1
	return 0

func at_ledge() -> bool:
	# Ledge on the right: a low wall ray hits but the high ledge ray is clear.
	return tuning.can_ledge_grab and not is_on_floor() \
		and wall_ray_r.is_colliding() and not ledge_ray.is_colliding()

# --- Combat (central) ------------------------------------------------------
func _handle_combat() -> void:
	weapons.try_fire(aim_dir, intent.fire_pressed, intent.fire_held)
	if intent.grenade_pressed:
		throw_grenade()
	if intent.melee_pressed and _melee_cd <= 0.0:
		do_melee()
	if intent.special_pressed:
		use_special()

func throw_grenade() -> void:
	if grenades <= 0:
		return
	grenades -= 1
	EventBus.grenades_changed.emit(slot, grenades)
	var pd := ProjectileData.new()
	pd.motion = ProjectileData.Motion.GRAVITY
	pd.speed = 620.0
	pd.lifetime = 1.6
	pd.explode_on_hit = true
	pd.explosion_radius = 110.0
	pd.explosion_damage = 70.0
	pd.color = Color(0.2, 0.8, 0.3)
	pd.size = Vector2(10, 10)
	var proj: Projectile = ObjectPool.acquire(preload("res://scenes/Projectile.tscn"))
	var dir := (aim_dir + Vector2.UP * 0.5).normalized()
	proj.launch(pd, aim_pivot.global_position, dir, 0, 0.0, DamageInfo.Type.EXPLOSIVE, 0.0, self)

func do_melee() -> void:
	_melee_cd = 0.35
	melee_hitbox.position = Vector2(22 * facing, 0)
	melee_hitbox.activate()
	EventBus.request_camera_shake.emit(0.1)
	get_tree().create_timer(0.12).timeout.connect(melee_hitbox.deactivate)

func use_special() -> void:
	# Ultimate: consumes the special meter when full (hook for per-character ultimates).
	var cost := character.ultimate_cost if character else 100.0
	if special_charge < cost:
		return
	special_charge -= cost
	EventBus.player_special_changed.emit(slot, special_charge, cost)
	EventBus.request_slow_motion.emit(0.4, 0.6)
	EventBus.notify.emit("ULTIMATE!")

func add_special(amount: float) -> void:
	var cost := character.ultimate_cost if character else 100.0
	special_charge = minf(cost, special_charge + amount)
	EventBus.player_special_changed.emit(slot, special_charge, cost)

# --- Reactions -------------------------------------------------------------
func _on_damaged(_info: DamageInfo) -> void:
	EventBus.player_health_changed.emit(slot, health.hp, health.max_hp)
	EventBus.request_camera_shake.emit(0.25)
	if not state_machine.is_state(&"dead"):
		state_machine.transition_to(&"hurt")

func _on_died(_info: DamageInfo) -> void:
	EventBus.player_died.emit(slot)
	state_machine.transition_to(&"dead")

func _on_respawned(s: int) -> void:
	if s != slot:
		return
	health.reset()
	global_position = CheckpointManager.get_spawn()
	velocity = Vector2.ZERO
	state_machine.transition_to(&"idle")
	EventBus.player_health_changed.emit(slot, health.hp, health.max_hp)
