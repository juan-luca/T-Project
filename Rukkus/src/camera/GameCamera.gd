extends Camera2D
class_name GameCamera
## Follows the player(s) with look-ahead, trauma-based screen shake, and dynamic zoom.
## Driven by EventBus so any system can add juice without referencing the camera.

@export var follow_smoothing: float = 6.0
@export var look_ahead: float = 90.0
@export var base_zoom: float = 1.0
@export var max_offset: float = 42.0
@export var max_roll: float = 0.1

var _trauma: float = 0.0
var _zoom_target: float = 1.0
var _zoom_timer: float = 0.0
var _time: float = 0.0

func _ready() -> void:
	make_current()
	_zoom_target = base_zoom
	zoom = Vector2.ONE * base_zoom
	EventBus.request_camera_shake.connect(add_trauma)
	EventBus.request_zoom.connect(_on_request_zoom)
	EventBus.explosion.connect(func(_p, _r, _d): add_trauma(0.4))
	EventBus.boss_intro.connect(func(_b): _on_request_zoom(1.2, 2.0))

func add_trauma(amount: float) -> void:
	_trauma = clampf(_trauma + amount * Settings.screen_shake, 0.0, 1.0)

func _on_request_zoom(z: float, duration: float) -> void:
	_zoom_target = z
	_zoom_timer = duration

func _process(delta: float) -> void:
	_time += delta
	_follow(delta)
	_shake(delta)
	_zoom(delta)

func _follow(delta: float) -> void:
	var players := get_tree().get_nodes_in_group("player")
	if players.is_empty():
		return
	# Average position of all active players (supports co-op framing).
	var center := Vector2.ZERO
	for p in players:
		center += (p as Node2D).global_position
	center /= players.size()
	# Look ahead in the lead player's facing/velocity direction.
	var lead := players[0] as Node2D
	if lead is CharacterBody2D:
		center.x += clampf(lead.velocity.x / 320.0, -1.0, 1.0) * look_ahead
	global_position = global_position.lerp(center, clampf(follow_smoothing * delta, 0.0, 1.0))
	# Co-op framing: zoom out as players spread apart (only when no scripted zoom is active).
	if players.size() > 1 and _zoom_timer <= 0.0:
		var spread := 0.0
		for p in players:
			spread = maxf(spread, center.distance_to((p as Node2D).global_position))
		_zoom_target = clampf(base_zoom - spread / 1600.0, 0.55, base_zoom)

func _shake(_delta: float) -> void:
	var shake := _trauma * _trauma          # quadratic feels better than linear
	_trauma = maxf(0.0, _trauma - 0.8 * get_process_delta_time())
	if shake <= 0.0:
		offset = Vector2.ZERO
		rotation = 0.0
		return
	offset = Vector2(
		max_offset * shake * _noise(0),
		max_offset * shake * _noise(1))
	rotation = max_roll * shake * _noise(2)

func _zoom(delta: float) -> void:
	if _zoom_timer > 0.0:
		_zoom_timer -= delta
		if _zoom_timer <= 0.0:
			_zoom_target = base_zoom
	zoom = zoom.lerp(Vector2.ONE * _zoom_target, clampf(4.0 * delta, 0.0, 1.0))

func _noise(seed_offset: int) -> float:
	# Cheap pseudo-noise in [-1,1] from time; deterministic enough for shake.
	return sin(_time * (37.0 + seed_offset * 13.0) + seed_offset * 2.4) * cos(_time * (19.0 + seed_offset * 7.0))
