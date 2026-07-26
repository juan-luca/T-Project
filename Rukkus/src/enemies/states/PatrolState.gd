extends EnemyState
## Walk back and forth, turning at walls/ledges. Reacts to sight and sound.

var _dir: int = 1
var _turn_cd: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_dir = enemy.facing

func physics_update(delta: float) -> void:
	_turn_cd = maxf(0.0, _turn_cd - delta)
	enemy.velocity.x = move_toward(enemy.velocity.x, _dir * enemy.speed * 0.5, 800.0 * delta)
	enemy.facing = _dir
	# Turn around at a wall or the edge of a platform.
	if _turn_cd <= 0.0 and (enemy.is_on_wall() or not _ground_ahead()):
		_dir = -_dir
		_turn_cd = 0.3
	# Perception-driven transitions.
	if enemy.perception.has_target:
		transition_to(&"chase")
	elif enemy.last_known != Vector2.ZERO and enemy.global_position.distance_to(enemy.last_known) > 32.0:
		transition_to(&"investigate")

func _ground_ahead() -> bool:
	# Probe just ahead and below to avoid walking off ledges.
	var space := enemy.get_world_2d().direct_space_state
	var from := enemy.global_position + Vector2(_dir * 24, 0)
	var q := PhysicsRayQueryParameters2D.create(from, from + Vector2(0, 40), 1)
	return not space.intersect_ray(q).is_empty()
