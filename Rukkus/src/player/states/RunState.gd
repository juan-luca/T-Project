extends PlayerState
## Running on the ground (with acceleration, deceleration and friction from tuning).

func physics_update(delta: float) -> void:
	player.move_horizontal(delta, false)
	player.apply_gravity(delta)
	if not player.is_on_floor():
		transition_to(&"fall")
	elif player.try_consume_jump_buffer():
		transition_to(&"jump")
	elif player.intent.dash_pressed and player.dash_cd <= 0.0:
		transition_to(&"dash")
	elif absf(player.intent.move.x) <= 0.1 and absf(player.velocity.x) < 5.0:
		transition_to(&"idle")
