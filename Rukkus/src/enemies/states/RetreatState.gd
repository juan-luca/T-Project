extends EnemyState
## Fall back away from the target while hurt; re-engage once patched up / distance gained.

var _timer: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_timer = 2.0

func physics_update(delta: float) -> void:
	_timer -= delta
	var t := enemy.perception.target
	if t:
		# Move away from the target, still facing it to lay down suppressing fire.
		var away := enemy.global_position.x + (enemy.global_position.x - t.global_position.x)
		enemy.move_toward_x(away, delta, 1.1)
		enemy.face_point(t.global_position.x)
		if enemy.can_fire() and randf() < 0.3:
			enemy.fire_at(t)
	else:
		enemy.stop(delta)
	if _timer <= 0.0 or enemy.hp_ratio() > enemy.data.retreat_hp_ratio + 0.2:
		transition_to(&"chase" if enemy.perception.has_target else &"investigate")
