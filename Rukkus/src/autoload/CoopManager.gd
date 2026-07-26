extends Node
## Local co-op (up to 4) with drop-in join. Owns which slots are active, which control
## scheme each uses, and spawning/respawning. Built on the slot-based InputManager, so the
## same seam extends to online co-op later (bind remote intents instead of local devices).
##
## Join: press ENTER or a P2 key to add a keyboard player; press START/A on any extra
## controller (device >= 1; device 0 is reserved for P1) to add a gamepad player.

const PLAYER_SCENE := preload("res://scenes/Player.tscn")
const CHARACTERS := [
	preload("res://src/characters/resources/rukk.tres"),
	preload("res://src/characters/resources/blaze.tres"),
	preload("res://src/characters/resources/volt.tres"),
	preload("res://src/characters/resources/boomer.tres"),
]

var joined: Array[int] = []
var _pad_join_prev: Dictionary = {}     ## device -> bool (START/A edge for join)

func _ready() -> void:
	EventBus.level_loaded.connect(_on_level_loaded)
	# Player 1 is always present, on keyboard-A (+ gamepad device 0 via the action map).
	_join(0, InputManager.Scheme.KEYBOARD_A, -1, false)

func _process(_delta: float) -> void:
	if GameManager.state != GameManager.GameState.PLAYING:
		return
	if joined.size() >= GameManager.max_players:
		return
	_detect_keyboard_join()
	_detect_gamepad_join()

# --- Join detection --------------------------------------------------------
func _detect_keyboard_join() -> void:
	if InputManager.is_scheme_bound(InputManager.Scheme.KEYBOARD_B):
		return
	if Input.is_action_just_pressed("coop_join") or _any_p2_key_pressed():
		_join(_next_slot(), InputManager.Scheme.KEYBOARD_B, -1, true)

func _any_p2_key_pressed() -> bool:
	for a in ["p2_jump", "p2_fire", "p2_left", "p2_right"]:
		if Input.is_action_just_pressed(a):
			return true
	return false

func _detect_gamepad_join() -> void:
	for device in Input.get_connected_joypads():
		if device == 0:
			continue   # reserved for Player 1
		var pressed := Input.is_joy_button_pressed(device, JOY_BUTTON_START) \
			or Input.is_joy_button_pressed(device, JOY_BUTTON_A)
		var prev: bool = _pad_join_prev.get(device, false)
		_pad_join_prev[device] = pressed
		if pressed and not prev and not InputManager.is_scheme_bound(InputManager.Scheme.GAMEPAD, device):
			if joined.size() < GameManager.max_players:
				_join(_next_slot(), InputManager.Scheme.GAMEPAD, device, true)

func _next_slot() -> int:
	for s in range(GameManager.max_players):
		if s not in joined:
			return s
	return joined.size()

# --- Join / spawn ----------------------------------------------------------
func _join(slot: int, scheme: int, device: int, announce: bool) -> void:
	if slot in joined:
		return
	joined.append(slot)
	joined.sort()
	InputManager.bind(slot, scheme, device)
	GameManager.register_player(slot)
	if announce:
		EventBus.notify.emit("PLAYER %d JOINED!" % (slot + 1))
	# Spawn immediately if a level is already running.
	if LevelManager.current_level and is_instance_valid(LevelManager.current_level):
		spawn_player(slot, _live_spawn_position())

func _on_level_loaded(_level_id: StringName) -> void:
	# (Re)spawn every joined player when a level finishes loading.
	var base := CheckpointManager.get_spawn()
	for i in joined.size():
		spawn_player(joined[i], base + Vector2(i * 44, 0))

func spawn_player(slot: int, pos: Vector2) -> void:
	var level := LevelManager.current_level
	if level == null:
		return
	# Avoid duplicates if already spawned.
	for p in get_tree().get_nodes_in_group("player"):
		if p is Player and p.slot == slot:
			return
	var player := PLAYER_SCENE.instantiate()
	player.slot = slot
	player.character = CHARACTERS[slot % CHARACTERS.size()]
	level.add_child(player)
	if player is Node2D:
		player.global_position = pos

## Where a newly joined / respawning player appears: near a living teammate, else checkpoint.
func _live_spawn_position() -> Vector2:
	for p in get_tree().get_nodes_in_group("player"):
		if p is Player and not p.state_machine.is_state(&"dead"):
			return (p as Node2D).global_position + Vector2(30, -20)
	return CheckpointManager.get_spawn()

func get_respawn_position(_slot: int) -> Vector2:
	return _live_spawn_position()

func active_count() -> int:
	return joined.size()
