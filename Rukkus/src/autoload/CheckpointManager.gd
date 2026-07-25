extends Node
## Tracks the active respawn point and drives the respawn flow. Autosaves on activation.

var _spawn_position: Vector2 = Vector2.ZERO
var _has_checkpoint: bool = false

func _ready() -> void:
	EventBus.checkpoint_activated.connect(_on_checkpoint_activated)
	EventBus.player_died.connect(_on_player_died)

func set_spawn(pos: Vector2) -> void:
	_spawn_position = pos

func get_spawn() -> Vector2:
	return _spawn_position

func _on_checkpoint_activated(checkpoint: Node) -> void:
	if checkpoint is Node2D:
		_spawn_position = checkpoint.global_position
		_has_checkpoint = true
		SaveSystem.autosave()
		EventBus.notify.emit("Checkpoint reached")

func _on_player_died(slot: int) -> void:
	# Respawn after a short delay; in shared-lives co-op this could gate on all players.
	var t := get_tree().create_timer(1.5)
	await t.timeout
	EventBus.player_respawned.emit(slot)
