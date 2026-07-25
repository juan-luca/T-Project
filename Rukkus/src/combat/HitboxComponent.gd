extends Area2D
class_name HitboxComponent
## Deals damage to overlapping HurtboxComponents. Used by melee swings, contact-damage
## enemies (kamikaze), boss attacks. Enable/disable to gate active frames.

@export var damage: float = 10.0
@export var damage_type: DamageInfo.Type = DamageInfo.Type.MELEE
@export var knockback: float = 200.0
@export var one_shot: bool = false        ## deal once then disable (grenades/kamikaze)
@export var owner_node: Node

var _already_hit: Array[Node] = []

func _ready() -> void:
	monitoring = false
	area_entered.connect(_on_area_entered)

func activate() -> void:
	_already_hit.clear()
	monitoring = true

func deactivate() -> void:
	monitoring = false

func _on_area_entered(area: Area2D) -> void:
	if area is HurtboxComponent and area not in _already_hit:
		_already_hit.append(area)
		var dir := (area.global_position - global_position).normalized()
		var info := DamageInfo.make(damage, damage_type, dir * knockback, owner_node)
		area.receive(info)
		if one_shot:
			deactivate()
