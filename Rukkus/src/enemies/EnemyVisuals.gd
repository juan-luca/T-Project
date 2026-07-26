extends Node2D
## Placeholder enemy presentation. Draws a tinted body, flips to face, flashes on damage,
## and shows an alert glyph when the AI has a target. Swap for AnimatedSprite2D later.

@export var body_size: Vector2 = Vector2(30, 46)
var _color: Color = Color(0.75, 0.2, 0.2)
var _enemy: Enemy
var _flash: float = 0.0

func _ready() -> void:
	_enemy = get_parent() as Enemy
	if _enemy:
		_enemy.health.damaged.connect(func(_i): _flash = 1.0)

func set_color(c: Color) -> void:
	_color = c
	queue_redraw()

func _process(delta: float) -> void:
	_flash = maxf(0.0, _flash - delta * 5.0)
	if _enemy:
		scale.x = _enemy.facing
	queue_redraw()

func _draw() -> void:
	var half := body_size * 0.5
	var col := _color.lerp(Color.WHITE, _flash)
	draw_rect(Rect2(-half, body_size), col)
	draw_rect(Rect2(-half, body_size), col.darkened(0.35), false, 2.0)
	draw_rect(Rect2(Vector2(4, -half.y + 8), Vector2(7, 6)), Color(1, 0.9, 0.2))
	if _enemy and _enemy.perception and _enemy.perception.has_target:
		draw_string(ThemeDB.fallback_font, Vector2(-4, -half.y - 8), "!", HORIZONTAL_ALIGNMENT_CENTER, -1, 20, Color(1, 0.3, 0.2))
