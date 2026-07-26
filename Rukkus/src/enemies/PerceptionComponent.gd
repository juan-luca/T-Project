extends Node2D
class_name PerceptionComponent
## Gives an enemy sight (LOS raycast within a vision cone) and hearing (subscribes to
## EventBus noise events). Reports the player's last-known position for investigation.

signal target_seen(target: Node2D)
signal noise_heard(position: Vector2)

@export var vision_range: float = 380.0
@export var vision_angle_deg: float = 90.0
@export var hearing_range: float = 260.0

var target: Node2D = null
var last_known_position: Vector2 = Vector2.ZERO
var has_target: bool = false

var _ray: RayCast2D
var _facing_provider: Callable

func _ready() -> void:
	_ray = RayCast2D.new()
	_ray.collision_mask = 1               # world only; unobstructed LOS check
	_ray.enabled = true
	add_child(_ray)
	EventBus.noise_emitted.connect(_on_noise)

func set_facing_provider(cb: Callable) -> void:
	_facing_provider = cb

func _physics_process(_delta: float) -> void:
	var player := _nearest_player()
	if player == null:
		has_target = false
		target = null
		return
	if _can_see(player):
		target = player
		has_target = true
		last_known_position = player.global_position
		target_seen.emit(player)
	else:
		has_target = false

func _can_see(p: Node2D) -> bool:
	var to := p.global_position - global_position
	if to.length() > vision_range:
		return false
	var facing := 1
	if _facing_provider.is_valid():
		facing = _facing_provider.call()
	var forward := Vector2(facing, 0)
	if forward.angle_to(to) > deg_to_rad(vision_angle_deg * 0.5):
		return false
	# Line of sight: cast toward the player; blocked if we hit world first.
	_ray.target_position = to
	_ray.force_raycast_update()
	return not _ray.is_colliding()

func _on_noise(pos: Vector2, radius: float) -> void:
	if global_position.distance_to(pos) <= hearing_range + radius:
		last_known_position = pos
		noise_heard.emit(pos)

func _nearest_player() -> Node2D:
	var best: Node2D = null
	var best_d := INF
	for n in get_tree().get_nodes_in_group("player"):
		if n is Node2D:
			var d := global_position.distance_squared_to(n.global_position)
			if d < best_d:
				best_d = d
				best = n
	return best
