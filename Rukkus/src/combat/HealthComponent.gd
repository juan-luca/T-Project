extends Node
class_name HealthComponent
## Reusable HP + shield + i-frames. Attached to Player, Enemy, Destructible — anything
## that can be hurt. Owns no visuals; emits signals the host/HUD react to.

signal health_changed(hp: float, max_hp: float)
signal shield_changed(shield: float, max_shield: float)
signal damaged(info: DamageInfo)
signal died(info: DamageInfo)

@export var max_hp: float = 100.0
@export var max_shield: float = 0.0
@export var invuln_time: float = 0.0        ## i-frames granted after each hit
## Per-type damage multipliers (weaknesses/resistances). Index by DamageInfo.Type.
@export var resistances: PackedFloat32Array = PackedFloat32Array([1, 1, 1, 1, 1, 1])

var hp: float
var shield: float
var _invuln := 0.0
var is_dead := false

func _ready() -> void:
	hp = max_hp
	shield = max_shield

func _process(delta: float) -> void:
	if _invuln > 0.0:
		_invuln -= delta

func is_invulnerable() -> bool:
	return _invuln > 0.0

## Central damage entry point. Returns the HP actually removed.
func apply(info: DamageInfo) -> float:
	if is_dead or is_invulnerable():
		return 0.0
	var mult := 1.0
	if info.type < resistances.size():
		mult = resistances[info.type]
	var dmg := maxf(0.0, info.amount * mult)
	# Shield soaks first.
	if shield > 0.0:
		var soaked := minf(shield, dmg)
		shield -= soaked
		dmg -= soaked
		shield_changed.emit(shield, max_shield)
	hp = maxf(0.0, hp - dmg)
	health_changed.emit(hp, max_hp)
	damaged.emit(info)
	if invuln_time > 0.0:
		_invuln = invuln_time
	if hp <= 0.0:
		is_dead = true
		died.emit(info)
	return dmg

func heal(amount: float) -> void:
	if is_dead:
		return
	hp = minf(max_hp, hp + amount)
	health_changed.emit(hp, max_hp)

func add_shield(amount: float, new_max: float = -1.0) -> void:
	if new_max >= 0.0:
		max_shield = new_max
	shield = minf(max_shield, shield + amount)
	shield_changed.emit(shield, max_shield)

func grant_invuln(seconds: float) -> void:
	_invuln = maxf(_invuln, seconds)

func reset() -> void:
	hp = max_hp
	shield = max_shield
	is_dead = false
	_invuln = 0.0
	health_changed.emit(hp, max_hp)
