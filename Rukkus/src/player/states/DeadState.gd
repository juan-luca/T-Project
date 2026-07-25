extends PlayerState
## Death: ragdoll-lite pop, disable control, wait for respawn (driven by CheckpointManager).

func enter(_msg: Dictionary = {}) -> void:
	player.velocity = Vector2(-player.facing * 120.0, -320.0)   # death pop
	player.hurtbox.set_deferred("monitorable", false)
	EventBus.request_camera_shake.emit(0.5)
	EventBus.request_slow_motion.emit(0.3, 0.5)

func physics_update(delta: float) -> void:
	player.apply_gravity(delta)
	player.velocity.x = move_toward(player.velocity.x, 0, 600.0 * delta)

func exit() -> void:
	player.hurtbox.set_deferred("monitorable", true)
