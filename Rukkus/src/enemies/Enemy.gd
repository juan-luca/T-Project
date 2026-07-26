extends CharacterBody2D
class_name Enemy
## Data-driven enemy actor. Behaviour comes from an EnemyData resource + a shared AI state
## machine (Patrol → Investigate → Chase → Attack → Retreat → Search → Dead). Perception
## feeds the states. Difficulty scales stats globally at spawn.

@export var data: EnemyData

@onready var state_machine: StateMachine = $StateMachine
@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var perception: PerceptionComponent = $PerceptionComponent
@onready var weapons: WeaponHolder = $WeaponHolder
@onready var contact_hitbox: HitboxComponent = $ContactHitbox
@onready var visuals: Node2D = $Visuals

var facing: int = 1
var speed: float = 120.0
var gravity: float = 1500.0
var last_known: Vector2 = Vector2.ZERO
var _fire_cd: float = 0.0
var _contact_rearm: float = 0.0

const STATE_SCRIPTS := {
	"patrol": preload("res://src/enemies/states/PatrolState.gd"),
	"investigate": preload("res://src/enemies/states/InvestigateState.gd"),
	"chase": preload("res://src/enemies/states/ChaseState.gd"),
	"attack": preload("res://src/enemies/states/AttackState.gd"),
	"retreat": preload("res://src/enemies/states/RetreatState.gd"),
	"search": preload("res://src/enemies/states/SearchState.gd"),
	"dead": preload("res://src/enemies/states/EnemyDeadState.gd"),
}

func _ready() -> void:
	add_to_group("enemy")
	_apply_data()
	_build_states()
	health.died.connect(_on_died)
	perception.noise_heard.connect(func(pos): last_known = pos)
	contact_hitbox.owner_node = self
	contact_hitbox.damage_type = DamageInfo.Type.MELEE
	contact_hitbox.activate()
	EventBus.enemy_spawned.emit(self)

func _apply_data() -> void:
	if data == null:
		data = EnemyData.new()
	var scale := Settings.difficulty_scale()
	health.max_hp = data.max_hp * scale
	health.resistances = data.resistances
	health.reset()
	speed = data.move_speed
	hurtbox.team = 1
	hurtbox.health = health
	perception.vision_range = data.vision_range
	perception.vision_angle_deg = data.vision_angle_deg
	perception.hearing_range = data.hearing_range
	perception.set_facing_provider(func(): return facing)
	contact_hitbox.damage = data.contact_damage * scale
	if data.weapon:
		weapons.team = 1
		weapons.slot = -1
		weapons.equip(data.weapon)
	if visuals.has_method("set_color"):
		visuals.call("set_color", data.color)

func _build_states() -> void:
	for key in STATE_SCRIPTS:
		var s: State = STATE_SCRIPTS[key].new()
		s.name = key
		state_machine.add_child(s)
	state_machine.boot(self)

func _physics_process(delta: float) -> void:
	# Flyers hover (no gravity); everyone else falls.
	if data.archetype == EnemyData.Archetype.FLYER:
		velocity.y = move_toward(velocity.y, 0.0, 400.0 * delta)
	elif not is_on_floor():
		velocity.y = minf(velocity.y + gravity * delta, 1200.0)
	_fire_cd = maxf(0.0, _fire_cd - delta)
	# Re-arm contact damage periodically so touching the player keeps hurting.
	_contact_rearm -= delta
	if _contact_rearm <= 0.0 and not state_machine.is_state(&"dead"):
		contact_hitbox.activate()
		_contact_rearm = 0.6
	state_machine.physics_update(delta)
	move_and_slide()
	if velocity.x != 0:
		facing = signi(int(sign(velocity.x)))

# --- Shared AI helpers used by states --------------------------------------
func move_toward_x(target_x: float, delta: float, mult: float = 1.0) -> void:
	var dir := signf(target_x - global_position.x)
	velocity.x = move_toward(velocity.x, dir * speed * mult * data.aggression, 1200.0 * delta)

func stop(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 2000.0 * delta)

func face_point(x: float) -> void:
	facing = 1 if x >= global_position.x else -1

func can_fire() -> bool:
	return data.weapon != null and _fire_cd <= 0.0

func fire_at(target: Node2D) -> void:
	if not can_fire():
		return
	var dir := (target.global_position - global_position).normalized()
	face_point(target.global_position.x)
	weapons.try_fire(dir, true, true)
	_fire_cd = 1.0 / maxf(0.5, data.aggression * 1.5)

func hp_ratio() -> float:
	return health.hp / maxf(1.0, health.max_hp)

# --- Death -----------------------------------------------------------------
func _on_died(_info: DamageInfo) -> void:
	AudioManager.play_sfx_at(data.death_sfx, global_position)
	EventBus.enemy_died.emit(self, global_position)
	EventBus.request_hitstop.emit(0.04)
	# Award special charge to nearby players (juice + feedback loop).
	for p in get_tree().get_nodes_in_group("player"):
		if p is Player and p.global_position.distance_to(global_position) < 500:
			p.add_special(10.0)
	state_machine.transition_to(&"dead")
