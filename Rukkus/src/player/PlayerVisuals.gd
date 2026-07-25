extends Node2D
## Pure presentation for the Player: placeholder body art, facing flip, squash & stretch,
## muzzle flash and i-frame flicker. Contains ZERO gameplay logic — it only reads state.
## Swap `_draw` for an AnimatedSprite2D once real pixel-art frames exist.

@export var body_color: Color = Color(0.95, 0.45, 0.2)
@export var body_size: Vector2 = Vector2(26, 44)

var _player: Player
var _squash: Vector2 = Vector2.ONE
var _muzzle_flash: float = 0.0

func _ready() -> void:
	_player = get_parent() as Player
	EventBus.weapon_fired.connect(_on_weapon_fired)
	if _player and _player.character:
		body_color = _player.character.color

func _process(delta: float) -> void:
	if _player == null:
		return
	# Squash & stretch from vertical velocity for juicy jumps/landings.
	var vy := _player.velocity.y
	var stretch := clampf(-vy / 1200.0, -0.25, 0.35)
	_squash = _squash.lerp(Vector2(1.0 - stretch * 0.6, 1.0 + stretch), 12.0 * delta)
	scale = Vector2(_squash.x * _player.facing, _squash.y)
	_muzzle_flash = maxf(0.0, _muzzle_flash - delta * 6.0)
	# I-frame flicker.
	modulate.a = 0.4 if (_player.health.is_invulnerable() and int(Time.get_ticks_msec() / 60) % 2 == 0) else 1.0
	queue_redraw()

func _draw() -> void:
	var half := body_size * 0.5
	# Body (rounded rect approximation).
	draw_rect(Rect2(-half, body_size), body_color)
	draw_rect(Rect2(-half, body_size), body_color.darkened(0.3), false, 2.0)
	# Eye/visor to convey facing.
	draw_rect(Rect2(Vector2(2, -half.y + 8), Vector2(8, 6)), Color(0.1, 0.9, 1.0))
	# Muzzle flash.
	if _muzzle_flash > 0.0 and _player:
		var mp := _player.aim_pivot.position + Vector2(28, 0).rotated(_player.aim_pivot.rotation)
		draw_circle(mp / scale, 10.0 * _muzzle_flash, Color(1, 0.9, 0.5, _muzzle_flash))

func _on_weapon_fired(slot: int, _id: StringName) -> void:
	if _player and slot == _player.slot:
		_muzzle_flash = 1.0
