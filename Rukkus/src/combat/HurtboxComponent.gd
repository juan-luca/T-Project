extends Area2D
class_name HurtboxComponent
## Receives damage on behalf of a HealthComponent. Projectiles/hitboxes call
## `receive(DamageInfo)`. Decouples "what can be hit" (an Area2D shape) from "what has HP".

@export var health: HealthComponent
@export var team: int = 0                ## 0 = player team, 1 = enemy team
@export var floating_numbers: bool = true

func receive(info: DamageInfo) -> void:
	if health == null or health.is_dead:
		return
	# Friendly-fire gate: same-team damage only if enabled globally.
	if info.source and _same_team(info.source) and not GameManager.friendly_fire:
		return
	var dealt := health.apply(info)
	if dealt > 0.0:
		EventBus.damage_dealt.emit(get_parent(), info)
		if floating_numbers and Settings.show_damage_numbers:
			var kind := 1 if info.is_crit else 0
			EventBus.floating_number_requested.emit(global_position, dealt, kind)
		# Impacts create noise that enemies can hear.
		EventBus.noise_emitted.emit(global_position, 120.0)

func _same_team(source: Node) -> bool:
	var hb := source.get_node_or_null("HurtboxComponent")
	return hb is HurtboxComponent and hb.team == team
