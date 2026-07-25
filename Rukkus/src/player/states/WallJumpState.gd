extends PlayerState
## Explosive jump away from a wall. Temporarily reduces air control so the arc reads.

var _lockout: float = 0.0

func enter(msg: Dictionary = {}) -> void:
	var dir: int = msg.get("dir", -player.facing)
	var v := player.tuning.wall_jump_velocity
	player.velocity = Vector2(dir * v.x, -v.y)
	player.facing = dir
	player.jump_buffer = 0.0
	_lockout = 0.14
	EventBus.request_camera_shake.emit(0.1)

func physics_update(delta: float) -> void:
	_lockout -= delta
	if _lockout > 0.0:
		player.apply_gravity(delta)          # keep momentum, ignore horizontal input briefly
	else:
		player.move_horizontal(delta, true)
		player.apply_gravity(delta)
	if player.intent.jump_released and player.velocity.y < 0:
		player.velocity.y *= player.tuning.jump_cut_mult
	if player.velocity.y >= 0:
		transition_to(&"fall")
	elif player.is_on_floor():
		transition_to(&"idle")
