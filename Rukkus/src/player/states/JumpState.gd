extends PlayerState
## Rising after a ground jump. Implements variable jump height (jump cut on release).

func enter(_msg: Dictionary = {}) -> void:
	player.start_jump(player.tuning.jump_velocity)
	EventBus.noise_emitted.emit(player.global_position, 60.0)

func physics_update(delta: float) -> void:
	player.move_horizontal(delta, true)     # full air control
	player.apply_gravity(delta)
	# Variable jump height: releasing early cuts upward velocity.
	if player.intent.jump_released and player.velocity.y < 0:
		player.velocity.y *= player.tuning.jump_cut_mult
	if player.intent.dash_pressed and player.dash_cd <= 0.0:
		transition_to(&"dash")
	elif player.intent.jump_pressed and player.air_jumps_used < player.tuning.max_air_jumps:
		transition_to(&"doublejump")
	elif player.wall_dir() != 0 and signf(player.intent.move.x) == player.wall_dir() and player.velocity.y > 0:
		transition_to(&"wallslide")
	elif player.velocity.y >= 0:
		transition_to(&"fall")
