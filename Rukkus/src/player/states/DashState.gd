extends PlayerState
## Dash / air-dash with i-frames and dash-cancel. Also doubles as ground slide when crouching.

var _time: float = 0.0
var _dir: int = 1
var _sliding: bool = false

func enter(_msg: Dictionary = {}) -> void:
	_sliding = player.is_on_floor() and player.intent.move.y > 0.3
	_time = player.tuning.slide_time if _sliding else player.tuning.dash_time
	_dir = player.facing if absf(player.intent.move.x) < 0.1 else signi(int(sign(player.intent.move.x)))
	player.dash_cd = player.tuning.dash_cooldown
	player.health.grant_invuln(player.tuning.dash_invuln)
	var spd := player.tuning.slide_speed if _sliding else player.tuning.dash_speed
	player.velocity = Vector2(_dir * spd, 0 if not _sliding else player.velocity.y)
	EventBus.request_camera_shake.emit(0.12)

func physics_update(delta: float) -> void:
	_time -= delta
	if _sliding:
		player.apply_gravity(delta)
		player.velocity.x = move_toward(player.velocity.x, 0, player.tuning.friction * 0.5 * delta)
	# Dash-cancel: a jump interrupts the dash into a jump immediately.
	if player.intent.jump_pressed and (player.is_on_floor() or player.coyote > 0.0):
		transition_to(&"jump")
		return
	if _time <= 0.0:
		if not player.is_on_floor():
			transition_to(&"fall")
		elif absf(player.intent.move.x) > 0.1:
			transition_to(&"run")
		else:
			transition_to(&"idle")
