extends EnemyState
## Pursue the visible target; break to Attack when in range, Retreat when low, or
## Investigate the last-known spot when the target slips out of sight.

const ATTACK_RANGE := 260.0
var _lost_timer: float = 0.0

func physics_update(delta: float) -> void:
	# Retreat when badly hurt (if allowed).
	if enemy.data.can_retreat and enemy.hp_ratio() < enemy.data.retreat_hp_ratio:
		transition_to(&"retreat")
		return
	var t := enemy.perception.target
	if t == null or not enemy.perception.has_target:
		_lost_timer += delta
		if _lost_timer > 0.6:
			transition_to(&"investigate")
		enemy.stop(delta)
		return
	_lost_timer = 0.0
	enemy.last_known = t.global_position
	var dist := enemy.global_position.distance_to(t.global_position)
	# Kamikaze charges in; ranged types keep a firing distance.
	var desired := 0.0 if enemy.data.archetype == EnemyData.Archetype.KAMIKAZE else ATTACK_RANGE * 0.7
	if dist > desired + 20.0:
		enemy.move_toward_x(t.global_position.x, delta)
	elif enemy.data.can_take_cover and dist < ATTACK_RANGE * 0.4:
		enemy.move_toward_x(enemy.global_position.x - (t.global_position.x - enemy.global_position.x), delta, 0.6)
	else:
		enemy.stop(delta)
	enemy.face_point(t.global_position.x)
	if dist <= ATTACK_RANGE and enemy.data.weapon != null:
		transition_to(&"attack")
