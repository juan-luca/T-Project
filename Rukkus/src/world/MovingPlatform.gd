extends AnimatableBody2D
class_name MovingPlatform
## A platform that ferries the player between two points. AnimatableBody2D carries riders
## correctly via move_and_collide semantics. Demonstrates the moving-platform/elevator pillar.

@export var travel: Vector2 = Vector2(200, 0)
@export var period: float = 3.0
@export var size: Vector2 = Vector2(96, 20)
@export var color: Color = Color(0.4, 0.4, 0.5)

var _origin: Vector2
var _t: float = 0.0

func _ready() -> void:
	sync_to_physics = true
	_origin = position
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	cs.shape = shape
	add_child(cs)

func _physics_process(delta: float) -> void:
	_t += delta
	var phase := (sin(_t / period * TAU) * 0.5 + 0.5)
	position = _origin + travel * phase
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(-size * 0.5, size), color)
	draw_rect(Rect2(-size * 0.5, size), color.lightened(0.2), false, 2.0)
