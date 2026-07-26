extends EnemyState
## Fire at the target while it stays in sight/range. Falls back to Chase otherwise.

const ATTACK_RANGE := 300.0

func physics_update(delta: float) -> void:
	if enemy.data.can_retreat and enemy.hp_ratio() < enemy.data.retreat_hp_ratio:
		transition_to(&"retreat")
		return
	var t := enemy.perception.target
	if t == null or not enemy.perception.has_target:
		transition_to(&"chase")
		return
	enemy.stop(delta)
	enemy.face_point(t.global_position.x)
	if enemy.global_position.distance_to(t.global_position) > ATTACK_RANGE:
		transition_to(&"chase")
		return
	enemy.fire_at(t)
	# Occasionally strafe/throw a grenade for variety if the data allows it.
	if enemy.data.can_throw_grenades and randf() < 0.01:
		EventBus.explosion.emit(t.global_position, 90.0, 40.0)
