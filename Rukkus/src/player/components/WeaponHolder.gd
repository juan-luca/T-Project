extends Node2D
class_name WeaponHolder
## Fires the currently equipped WeaponData. Shared by Player and armed Enemies.
## Owns ammo/reload/cooldown state; spawns pooled projectiles; applies recoil to the host.

const PROJECTILE_SCENE := preload("res://scenes/Projectile.tscn")

@export var team: int = 0                  ## 0 = player projectiles, 1 = enemy
@export var muzzle: Node2D                 ## where shots originate; falls back to self
@export var slot: int = 0                  ## player slot for HUD events (-1 for enemies)

var current: WeaponData
var in_mag: int = 0
var reserve: int = 0
var _cooldown: float = 0.0
var _reloading: bool = false
var _reload_left: float = 0.0
var _burst_left: int = 0
var _damage_mult: float = 1.0              ## power-ups can bump this

signal recoil_applied(impulse: Vector2)

func _ready() -> void:
	ObjectPool.prewarm(PROJECTILE_SCENE, 48)

func equip(weapon: WeaponData) -> void:
	current = weapon
	if weapon == null:
		return
	in_mag = weapon.mag_size
	reserve = weapon.reserve_ammo
	_reloading = false
	_cooldown = 0.0
	if slot >= 0:
		EventBus.weapon_equipped.emit(slot, weapon.id)
		EventBus.ammo_changed.emit(slot, in_mag, reserve)

func set_damage_mult(m: float) -> void:
	_damage_mult = m

func _process(delta: float) -> void:
	if _cooldown > 0.0:
		_cooldown -= delta
	if _reloading:
		_reload_left -= delta
		if _reload_left <= 0.0:
			_finish_reload()

## Call every frame with the aim direction. `held` supports AUTO/BEAM weapons.
func try_fire(aim: Vector2, pressed: bool, held: bool) -> void:
	if current == null or _reloading or _cooldown > 0.0:
		return
	var want := held if current.fire_mode == WeaponData.FireMode.AUTO or current.fire_mode == WeaponData.FireMode.BEAM else pressed
	if current.fire_mode == WeaponData.FireMode.BURST and _burst_left > 0:
		want = true
	if not want:
		return
	if not current.infinite_ammo and in_mag <= 0:
		reload()
		return
	_fire(aim)

func _fire(aim: Vector2) -> void:
	var origin := (muzzle if muzzle else self).global_position
	for i in current.pellets:
		var spread := deg_to_rad(randf_range(-current.spread_degrees, current.spread_degrees))
		var dir := aim.rotated(spread)
		var proj: Projectile = ObjectPool.acquire(PROJECTILE_SCENE)
		proj.launch(current.projectile, origin, dir, team,
			current.damage * _damage_mult, current.damage_type, current.knockback, get_parent())
	_cooldown = current.seconds_between_shots()
	if not current.infinite_ammo:
		in_mag -= 1
	if current.fire_mode == WeaponData.FireMode.BURST:
		if _burst_left <= 0:
			_burst_left = current.burst_count
		_burst_left -= 1
	# Feel: recoil, muzzle flash, shake, sfx, noise for AI hearing.
	recoil_applied.emit(-aim * current.recoil)
	EventBus.request_camera_shake.emit(current.screen_shake)
	EventBus.weapon_fired.emit(slot, current.id)
	EventBus.noise_emitted.emit(origin, 320.0)
	if slot >= 0:
		EventBus.ammo_changed.emit(slot, in_mag, reserve)

func reload() -> void:
	if _reloading or current == null or current.infinite_ammo:
		return
	if reserve <= 0 or in_mag >= current.mag_size:
		return
	_reloading = true
	_reload_left = current.reload_time
	if slot >= 0:
		EventBus.reload_started.emit(slot)

func _finish_reload() -> void:
	var needed := current.mag_size - in_mag
	var taken := mini(needed, reserve)
	in_mag += taken
	reserve -= taken
	_reloading = false
	if slot >= 0:
		EventBus.ammo_changed.emit(slot, in_mag, reserve)
