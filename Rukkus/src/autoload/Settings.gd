extends Node
## User settings: audio volumes, difficulty, accessibility. Persisted via SaveSystem.
## Difficulty is read by EnemyData consumers to scale AI aggression/damage globally.

enum Difficulty { EASY, NORMAL, HARD, INSANE }

var master_volume: float = 1.0
var music_volume: float = 0.8
var sfx_volume: float = 0.9
var difficulty: Difficulty = Difficulty.NORMAL
var screen_shake: float = 1.0        ## global multiplier (accessibility)
var show_damage_numbers: bool = true
var show_fps: bool = false

func _ready() -> void:
	var data := SaveSystem.load_settings()
	if not data.is_empty():
		_apply(data)
	_push_to_audio()

func _apply(d: Dictionary) -> void:
	master_volume = d.get("master_volume", master_volume)
	music_volume = d.get("music_volume", music_volume)
	sfx_volume = d.get("sfx_volume", sfx_volume)
	difficulty = d.get("difficulty", difficulty)
	screen_shake = d.get("screen_shake", screen_shake)
	show_damage_numbers = d.get("show_damage_numbers", show_damage_numbers)
	show_fps = d.get("show_fps", show_fps)

func save() -> void:
	SaveSystem.save_settings({
		"master_volume": master_volume, "music_volume": music_volume,
		"sfx_volume": sfx_volume, "difficulty": difficulty,
		"screen_shake": screen_shake, "show_damage_numbers": show_damage_numbers,
		"show_fps": show_fps,
	})
	_push_to_audio()

func _push_to_audio() -> void:
	AudioManager.set_bus_volume("Master", master_volume)
	AudioManager.set_bus_volume("Music", music_volume)
	AudioManager.set_bus_volume("SFX", sfx_volume)

## Global difficulty scalar consumed by enemy stats (0.8 easy .. 1.4 insane).
func difficulty_scale() -> float:
	match difficulty:
		Difficulty.EASY: return 0.8
		Difficulty.NORMAL: return 1.0
		Difficulty.HARD: return 1.2
		Difficulty.INSANE: return 1.4
	return 1.0
