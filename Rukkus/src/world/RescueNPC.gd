extends Area2D
class_name RescueNPC
## A trapped civilian to rescue (a Broforce-style staple, original character). Touch to free;
## rewards score + XP and cheers.

@export var reward_score: int = 250
@export var reward_xp: int = 50
@export var color: Color = Color(0.9, 0.8, 0.5)

var _rescued: bool = false
var _t: float = 0.0

func _ready() -> void:
	add_to_group("npc")
	collision_layer = 0
	collision_mask = 2
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	_t += delta
	queue_redraw()

func _on_body_entered(body: Node) -> void:
	if _rescued or not (body is Player):
		return
	_rescued = true
	GameManager.add_score(reward_score)
	SaveSystem.add_xp(reward_xp)
	EventBus.npc_rescued.emit(self)
	EventBus.notify.emit("Civilian rescued! +%d" % reward_score)
	# Run off cheering, then vanish.
	var tw := create_tween()
	tw.tween_property(self, "position:y", position.y - 400, 1.0)
	tw.parallel().tween_property(self, "modulate:a", 0.0, 1.0)
	tw.tween_callback(queue_free)

func _draw() -> void:
	var bob := sin(_t * 4.0) * 2.0
	var c := color if not _rescued else Color(0.4, 1, 0.5)
	draw_rect(Rect2(Vector2(-9, -30 + bob), Vector2(18, 30)), c)
	draw_circle(Vector2(0, -34 + bob), 8, c.lightened(0.2))
	if not _rescued:
		draw_string(ThemeDB.fallback_font, Vector2(-6, -48), "?", HORIZONTAL_ALIGNMENT_CENTER, -1, 18, Color(1, 1, 0.4))
