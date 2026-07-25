extends PlayerState
## Hanging on a ledge; can climb up or drop. Freezes gravity while hanging.

var _dir: int = 1

func enter(_msg: Dictionary = {}) -> void:
	_dir = player.wall_dir()
	player.velocity = Vector2.ZERO
	player.air_jumps_used = 0

func physics_update(delta: float) -> void:
	player.velocity = Vector2.ZERO            # hang in place
	if player.intent.jump_pressed:
		transition_to(&"jump")
	elif player.intent.move.y < -0.4 or (signf(player.intent.move.x) == _dir):
		# Climb up over the ledge.
		player.velocity = Vector2(_dir * player.tuning.climb_speed, -player.tuning.climb_speed)
		transition_to(&"fall")
	elif player.intent.move.y > 0.4 or signf(player.intent.move.x) == -_dir:
		transition_to(&"fall")
