extends PlayerState
## Brief stagger with knockback after taking damage. Grants short i-frames.

var _time: float = 0.0

func enter(_msg: Dictionary = {}) -> void:
	_time = 0.25
	player.health.grant_invuln(0.6)
	EventBus.request_hitstop.emit(0.05)

func physics_update(delta: float) -> void:
	_time -= delta
	player.velocity.x = move_toward(player.velocity.x, 0, 1200.0 * delta)
	player.apply_gravity(delta)
	if _time <= 0.0:
		transition_to(&"idle" if player.is_on_floor() else &"fall")
