extends Node
## Owns high-level game state, run statistics, co-op config and global time scale
## (slow-motion / hit-stop). Deliberately thin: it coordinates, it does not do gameplay.

enum State { BOOT, MENU, PLAYING, PAUSED, CUTSCENE, GAME_OVER, VICTORY }

## Co-op configuration — single-player works today, these flags make it multiplayer-ready.
@export var max_players: int = 4
@export var friendly_fire: bool = false
@export var shared_lives: bool = true

var state: State = State.BOOT
var score: int = 0
var run_stats := {"kills": 0, "deaths": 0, "secrets": 0, "time": 0.0}

var _active_players: Array[int] = [0]   ## player slots currently in the run
var _hitstop_frames: int = 0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(_on_player_died)
	EventBus.request_slow_motion.connect(_on_request_slow_motion)
	EventBus.request_hitstop.connect(_on_request_hitstop)

func _process(delta: float) -> void:
	if state == State.PLAYING:
		run_stats.time += delta
	# Hit-stop: freeze time for a few frames then restore, for punchy impacts.
	if _hitstop_frames > 0:
		_hitstop_frames -= 1
		if _hitstop_frames == 0 and not is_equal_approx(Engine.time_scale, 0.0):
			Engine.time_scale = 1.0

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		toggle_pause()

func change_state(new_state: State) -> void:
	if state == new_state:
		return
	state = new_state
	EventBus.game_state_changed.emit(new_state)

func start_new_run() -> void:
	score = 0
	run_stats = {"kills": 0, "deaths": 0, "secrets": 0, "time": 0.0}
	change_state(State.PLAYING)

func toggle_pause() -> void:
	if state == State.PLAYING:
		change_state(State.PAUSED)
		get_tree().paused = true
		EventBus.game_paused.emit(true)
	elif state == State.PAUSED:
		change_state(State.PLAYING)
		get_tree().paused = false
		EventBus.game_paused.emit(false)

func add_score(amount: int) -> void:
	score += amount

func get_active_players() -> Array[int]:
	return _active_players.duplicate()

func register_player(slot: int) -> void:
	if slot not in _active_players:
		_active_players.append(slot)

# --- Time-scale juice ------------------------------------------------------
func _on_request_slow_motion(scale: float, duration: float) -> void:
	Engine.time_scale = scale
	# Real-time timer so it is unaffected by the very time_scale it restores.
	var t := get_tree().create_timer(duration * scale, true, false, true)
	t.timeout.connect(func(): Engine.time_scale = 1.0)

func _on_request_hitstop(duration: float) -> void:
	_hitstop_frames = maxi(_hitstop_frames, int(duration * Engine.physics_ticks_per_second))
	Engine.time_scale = 0.0001

func _on_enemy_died(_enemy: Node, _pos: Vector2) -> void:
	run_stats.kills += 1
	add_score(100)

func _on_player_died(_slot: int) -> void:
	run_stats.deaths += 1
