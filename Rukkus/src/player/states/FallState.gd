extends PlayerState
## Airborne and descending. Honours coyote time and jump buffer for forgiving platforming.

func physics_update(delta: float) -> void:
	player.move_horizontal(delta, true)
	player.apply_gravity(delta)
	# Coyote-time jump: still allowed briefly after walking off a ledge.
	if player.try_consume_jump_buffer() and player.coyote > 0.0:
		transition_to(&"jump")
	elif player.intent.jump_pressed and player.air_jumps_used < player.tuning.max_air_jumps:
		transition_to(&"doublejump")
	elif player.intent.dash_pressed and player.dash_cd <= 0.0:
		transition_to(&"dash")
	elif player.wall_dir() != 0 and signf(player.intent.move.x) == player.wall_dir():
		transition_to(&"wallslide")
	elif player.is_on_floor():
		# Land: buffered jump fires immediately, otherwise idle/run.
		if player.try_consume_jump_buffer():
			transition_to(&"jump")
		elif absf(player.intent.move.x) > 0.1:
			transition_to(&"run")
		else:
			transition_to(&"idle")
