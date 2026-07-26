extends Area2D
class_name Checkpoint
## Activates on first player touch; CheckpointManager stores it as the respawn point and
## triggers an autosave.

var _active: bool = false

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2            # player body
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node) -> void:
	if _active or not (body is Player):
		return
	_active = true
	EventBus.checkpoint_activated.emit(self)
	queue_redraw()

func _draw() -> void:
	var col := Color(0.3, 1, 0.4) if _active else Color(0.6, 0.6, 0.6)
	draw_rect(Rect2(Vector2(-3, -48), Vector2(6, 48)), Color(0.4, 0.3, 0.2))
	draw_colored_polygon(PackedVector2Array([Vector2(3, -48), Vector2(34, -40), Vector2(3, -30)]), col)
