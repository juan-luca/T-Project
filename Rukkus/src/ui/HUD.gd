extends CanvasLayer
## Heads-up display. Pure view: it only listens to EventBus and renders. It never reads or
## mutates gameplay state, so it can be redesigned freely without touching systems.
## Shows health, shield, ammo, grenades, special meter, score, objective, notifications,
## floating damage numbers and (debug) FPS.

var _hp_bar: ColorRect
var _hp_bg: ColorRect
var _shield_bar: ColorRect
var _special_bar: ColorRect
var _ammo_label: Label
var _nade_label: Label
var _score_label: Label
var _objective_label: Label
var _notify_label: Label
var _fps_label: Label
var _notify_t: float = 0.0

func _ready() -> void:
	layer = 10
	_build()
	EventBus.player_health_changed.connect(_on_health)
	EventBus.player_shield_changed.connect(_on_shield)
	EventBus.player_special_changed.connect(_on_special)
	EventBus.ammo_changed.connect(_on_ammo)
	EventBus.grenades_changed.connect(_on_grenades)
	EventBus.objective_updated.connect(func(t): _objective_label.text = t)
	EventBus.notify.connect(_on_notify)
	EventBus.floating_number_requested.connect(_on_floating_number)

func _build() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	_hp_bg = _panel(root, Vector2(24, 24), Vector2(300, 26), Color(0, 0, 0, 0.5))
	_hp_bar = _panel(root, Vector2(26, 26), Vector2(296, 22), Color(0.9, 0.25, 0.25))
	_shield_bar = _panel(root, Vector2(26, 52), Vector2(220, 10), Color(0.35, 0.7, 1.0))
	_special_bar = _panel(root, Vector2(26, 66), Vector2(220, 8), Color(1.0, 0.85, 0.3))

	_ammo_label = _label(root, Vector2(24, 84), 22, Color.WHITE)
	_ammo_label.text = "AMMO --/--"
	_nade_label = _label(root, Vector2(24, 112), 20, Color(0.6, 1.0, 0.6))
	_nade_label.text = "GRENADES 3"

	_score_label = _label(root, Vector2(0, 24), 24, Color.WHITE)
	_score_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_score_label.position = Vector2(-220, 24)
	_score_label.size.x = 200
	_score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	_objective_label = _label(root, Vector2(0, 24), 18, Color(0.9, 0.9, 0.7))
	_objective_label.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_objective_label.position = Vector2(-200, 20)
	_objective_label.size.x = 400
	_objective_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	_notify_label = _label(root, Vector2(0, 120), 34, Color(1, 0.95, 0.6))
	_notify_label.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_notify_label.position = Vector2(-300, 120)
	_notify_label.size.x = 600
	_notify_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_notify_label.modulate.a = 0.0

	_fps_label = _label(root, Vector2(-90, 60), 16, Color(0.6, 1, 0.6))
	_fps_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_fps_label.position = Vector2(-90, 60)

func _process(delta: float) -> void:
	_score_label.text = "SCORE %06d" % GameManager.score
	if Settings.show_fps:
		_fps_label.visible = true
		_fps_label.text = "%d FPS" % Engine.get_frames_per_second()
	else:
		_fps_label.visible = false
	if _notify_t > 0.0:
		_notify_t -= delta
		_notify_label.modulate.a = clampf(_notify_t, 0.0, 1.0)

# --- EventBus reactions -----------------------------------------------------
func _on_health(_slot: int, hp: float, max_hp: float) -> void:
	var frac := clampf(hp / maxf(1.0, max_hp), 0.0, 1.0)
	_hp_bar.size.x = 296 * frac
	_hp_bar.color = Color(0.9, 0.25, 0.25).lerp(Color(0.3, 0.9, 0.35), frac)

func _on_shield(_slot: int, shield: float, max_shield: float) -> void:
	_shield_bar.visible = max_shield > 0.0
	if max_shield > 0.0:
		_shield_bar.size.x = 220 * clampf(shield / max_shield, 0.0, 1.0)

func _on_special(_slot: int, value: float, max_value: float) -> void:
	_special_bar.size.x = 220 * clampf(value / maxf(1.0, max_value), 0.0, 1.0)

func _on_ammo(_slot: int, in_mag: int, reserve: int) -> void:
	_ammo_label.text = "AMMO %d / %d" % [in_mag, reserve]

func _on_grenades(_slot: int, count: int) -> void:
	_nade_label.text = "GRENADES %d" % count

func _on_notify(text: String) -> void:
	_notify_label.text = text
	_notify_t = 1.6

func _on_floating_number(pos: Vector2, amount: float, kind: int) -> void:
	var world := get_tree().current_scene
	if world == null:
		return
	var fn := FloatingNumber.new()
	fn.setup(amount, kind)
	world.add_child(fn)
	fn.global_position = pos + Vector2(randf_range(-8, 8), -20)

# --- Small UI helpers -------------------------------------------------------
func _panel(parent: Control, pos: Vector2, sz: Vector2, col: Color) -> ColorRect:
	var r := ColorRect.new()
	r.position = pos
	r.size = sz
	r.color = col
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(r)
	return r

func _label(parent: Control, pos: Vector2, font_size: int, col: Color) -> Label:
	var l := Label.new()
	l.position = pos
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	l.add_theme_constant_override("outline_size", 4)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(l)
	return l

## World-space damage number that floats up and fades.
class FloatingNumber extends Node2D:
	var _amount: float = 0.0
	var _kind: int = 0
	var _t: float = 0.0
	func setup(amount: float, kind: int) -> void:
		_amount = amount
		_kind = kind
	func _process(delta: float) -> void:
		_t += delta
		position.y -= 40.0 * delta
		queue_redraw()
		if _t >= 0.8:
			queue_free()
	func _draw() -> void:
		var col := Color(1, 0.9, 0.3) if _kind == 1 else Color(1, 1, 1)
		col.a = 1.0 - _t / 0.8
		var size := 26 if _kind == 1 else 20
		draw_string(ThemeDB.fallback_font, Vector2(-10, 0), str(roundi(_amount)),
			HORIZONTAL_ALIGNMENT_CENTER, -1, size, col)
