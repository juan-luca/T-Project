extends PlayerState
## Clinging to and sliding down a wall. Feeds Wall Jump and Ledge Grab.

var _stick: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_stick = player.tuning.wall_stick_time
	player.air_jumps_used = 0                 # refresh air jump on wall touch

func physics_update(delta: float) -> void:
	var wd := player.wall_dir()
	player.velocity.y = minf(player.velocity.y + player.tuning.gravity * delta, player.tuning.wall_slide_speed)
	# Ledge grab when the top of the wall is reached.
	if player.at_ledge():
		transition_to(&"ledgegrab")
		return
	if player.try_consume_jump_buffer() or player.intent.jump_pressed:
		transition_to(&"walljump", {"dir": -wd})
		return
	# Push away from wall or land to leave the slide.
	if wd == 0 or signf(player.intent.move.x) == -wd:
		_stick -= delta
		if _stick <= 0.0:
			transition_to(&"fall")
	else:
		_stick = player.tuning.wall_stick_time
	if player.is_on_floor():
		transition_to(&"idle")
