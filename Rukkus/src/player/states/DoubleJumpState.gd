extends PlayerState
## Air jump(s). Supports N air jumps via tuning.max_air_jumps.

func enter(_msg: Dictionary = {}) -> void:
	player.air_jumps_used += 1
	player.velocity.y = -player.tuning.double_jump_velocity
	EventBus.request_camera_shake.emit(0.05)

func physics_update(delta: float) -> void:
	player.move_horizontal(delta, true)
	player.apply_gravity(delta)
	if player.intent.jump_released and player.velocity.y < 0:
		player.velocity.y *= player.tuning.jump_cut_mult
	if player.intent.dash_pressed and player.dash_cd <= 0.0:
		transition_to(&"dash")
	elif player.intent.jump_pressed and player.air_jumps_used < player.tuning.max_air_jumps:
		transition_to(&"doublejump")
	elif player.velocity.y >= 0:
		transition_to(&"fall")
