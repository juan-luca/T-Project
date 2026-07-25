extends Node
## Centralised audio: pooled 2D SFX players, a music player with adaptive-layer hooks,
## and bus volume control. SFX are addressed by id so gameplay code stays asset-agnostic.

const SFX_POOL_SIZE := 24

var _sfx_players: Array[AudioStreamPlayer2D] = []
var _music: AudioStreamPlayer
var _sfx_library: Dictionary = {}   ## StringName -> AudioStream (populated from res or code)
var _music_intensity: float = 0.0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_buses()
	for i in SFX_POOL_SIZE:
		var p := AudioStreamPlayer2D.new()
		p.bus = "SFX"
		add_child(p)
		_sfx_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.bus = "Music"
	add_child(_music)
	EventBus.weapon_fired.connect(func(_s, id): play_sfx(id))
	EventBus.explosion.connect(func(pos, _r, _d): play_sfx_at(&"explosion", pos))

func _ensure_buses() -> void:
	# Guarantee Master/Music/SFX exist even without a saved bus layout.
	for bus_name in ["Music", "SFX"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			var idx := AudioServer.bus_count
			AudioServer.add_bus(idx)
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "Master")

func register_sfx(id: StringName, stream: AudioStream) -> void:
	_sfx_library[id] = stream

func play_sfx(id: StringName) -> void:
	play_sfx_at(id, Vector2.ZERO)

func play_sfx_at(id: StringName, pos: Vector2) -> void:
	var stream: AudioStream = _sfx_library.get(id, null)
	if stream == null:
		return   # No asset yet — silent placeholder, never an error.
	var p := _get_free_player()
	if p == null:
		return
	p.stream = stream
	p.global_position = pos
	p.play()

func play_music(stream: AudioStream, fade: float = 1.0) -> void:
	if stream == null:
		return
	_music.stream = stream
	_music.play()

## Adaptive-music hook: combat systems push intensity 0..1; layers crossfade to it.
func set_music_intensity(value: float) -> void:
	_music_intensity = clampf(value, 0.0, 1.0)

func set_bus_volume(bus_name: String, linear: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx >= 0:
		AudioServer.set_bus_volume_db(idx, linear_to_db(clampf(linear, 0.0, 1.0)))

func _get_free_player() -> AudioStreamPlayer2D:
	for p in _sfx_players:
		if not p.playing:
			return p
	return _sfx_players[0]  # steal oldest if saturated
