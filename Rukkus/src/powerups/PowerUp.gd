extends Area2D
class_name PowerUp
## A pickup that applies a PowerUpData effect to the collecting player. Timed effects
## auto-revert. Adding a new power-up = a new .tres, no code.

@export var data: PowerUpData

var _t: float = 0.0

func _ready() -> void:
	add_to_group("pickup")
	collision_layer = 32          # pickup layer
	collision_mask = 2            # detect player body (layer 2)
	monitoring = true
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	_t += delta
	position.y += sin(_t * 3.0) * 0.3   # gentle bob
	queue_redraw()

func _draw() -> void:
	var c := data.color if data else Color.WHITE
	draw_circle(Vector2.ZERO, 14, Color(c, 0.25))
	draw_circle(Vector2.ZERO, 9, c)
	draw_arc(Vector2.ZERO, 14, 0, TAU, 24, c, 2.0)

func _on_body_entered(body: Node) -> void:
	if not (body is Player) or data == null:
		return
	_apply(body as Player)
	EventBus.powerup_collected.emit(body.slot, data.id)
	AudioManager.play_sfx_at(data.pickup_sfx, global_position)
	EventBus.notify.emit(data.display_name)
	queue_free()

func _apply(p: Player) -> void:
	match data.effect:
		PowerUpData.Effect.HEAL:
			p.health.heal(data.magnitude)
		PowerUpData.Effect.SHIELD:
			p.health.add_shield(data.magnitude, maxf(p.health.max_shield, data.magnitude))
		PowerUpData.Effect.INVINCIBILITY:
			p.health.grant_invuln(data.duration)
		PowerUpData.Effect.DAMAGE_MULT:
			p.weapons.set_damage_mult(data.magnitude)
			_revert_after(p, func(): p.weapons.set_damage_mult(1.0))
		PowerUpData.Effect.SPEED:
			var base := p.tuning.max_speed
			p.tuning.max_speed = base * data.magnitude
			_revert_after(p, func(): p.tuning.max_speed = base)
		PowerUpData.Effect.EXTRA_JUMP:
			p.tuning.max_air_jumps += int(data.magnitude)
			_revert_after(p, func(): p.tuning.max_air_jumps -= int(data.magnitude))
		PowerUpData.Effect.INFINITE_AMMO:
			if p.weapons.current:
				var w := p.weapons.current
				var was := w.infinite_ammo
				w.infinite_ammo = true
				_revert_after(p, func(): w.infinite_ammo = was)
		PowerUpData.Effect.SLOW_MOTION:
			EventBus.request_slow_motion.emit(0.4, data.duration)
		PowerUpData.Effect.WEAPON_SWAP:
			if data.weapon_grant:
				p.weapons.equip(data.weapon_grant)
		_:
			pass

func _revert_after(p: Player, cb: Callable) -> void:
	if data.duration <= 0.0:
		return
	var timer := p.get_tree().create_timer(data.duration)
	timer.timeout.connect(cb)
