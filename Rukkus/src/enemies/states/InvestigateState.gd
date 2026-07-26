extends EnemyState
## Move to the last-known noise/sighting position, then search the area.

func physics_update(delta: float) -> void:
	if enemy.perception.has_target:
		transition_to(&"chase")
		return
	var target := enemy.last_known
	if enemy.global_position.distance_to(target) <= 24.0:
		transition_to(&"search")
		return
	enemy.move_toward_x(target.x, delta, 0.8)
	enemy.face_point(target.x)
