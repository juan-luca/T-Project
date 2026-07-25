extends Node
## Loads/unloads level scenes asynchronously and spawns the player(s) at the level's
## spawn point. Keeps the main scene free of level-specific wiring.

const PLAYER_SCENE := preload("res://scenes/Player.tscn")

var current_level: Node = null
var current_level_id: StringName = &""
var _world_root: Node = null

func _ready() -> void:
	EventBus.level_load_requested.connect(load_level)

## Where levels get added. Main.tscn registers its world container here.
func set_world_root(node: Node) -> void:
	_world_root = node

func load_level(level_id: StringName) -> void:
	var path := "res://scenes/levels/%s.tscn" % level_id
	if not ResourceLoader.exists(path):
		push_warning("LevelManager: level not found: %s" % path)
		return
	# Async load so streaming a big level never hitches the frame.
	ResourceLoader.load_threaded_request(path)
	while ResourceLoader.load_threaded_get_status(path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		await get_tree().process_frame
	var packed: PackedScene = ResourceLoader.load_threaded_get(path)
	_swap_level(packed, level_id)

func _swap_level(packed: PackedScene, level_id: StringName) -> void:
	if current_level and is_instance_valid(current_level):
		current_level.queue_free()
		await current_level.tree_exited
	current_level = packed.instantiate()
	current_level_id = level_id
	var parent := _world_root if _world_root else get_tree().current_scene
	parent.add_child(current_level)
	_spawn_players()
	EventBus.level_loaded.emit(level_id)

func _spawn_players() -> void:
	var spawn := _find_spawn()
	for slot in GameManager.get_active_players():
		var player := PLAYER_SCENE.instantiate()
		player.set("slot", slot)
		current_level.add_child(player)
		if player is Node2D and spawn:
			player.global_position = spawn.global_position
		CheckpointManager.set_spawn(spawn.global_position if spawn else Vector2.ZERO)
		EventBus.player_spawned.emit(player, slot)

func _find_spawn() -> Node2D:
	var nodes := get_tree().get_nodes_in_group("player_spawn")
	return nodes[0] if not nodes.is_empty() else null
