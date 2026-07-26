extends EnemyState
## Look around at the last-known position for a while, then give up and resume patrol.

var _timer: float = 0.0
var _look_cd: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_timer = 2.5
	_look_cd = 0.0

func physics_update(delta: float) -> void:
	enemy.stop(delta)
	_timer -= delta
	_look_cd -= delta
	if _look_cd <= 0.0:
		enemy.facing = -enemy.facing        # scan side to side
		_look_cd = 0.6
	if enemy.perception.has_target:
		transition_to(&"chase")
	elif _timer <= 0.0:
		enemy.last_known = Vector2.ZERO
		transition_to(&"patrol")
