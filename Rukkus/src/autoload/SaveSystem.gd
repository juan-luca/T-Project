extends Node
## JSON save/load to user:// with multiple profile slots and autosave-on-checkpoint.
## Progression, unlocks and settings all round-trip through here.

const SAVE_DIR := "user://saves"
const SETTINGS_PATH := "user://settings.json"

var active_slot: int = 0
var profile: Dictionary = _default_profile()

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)

func _default_profile() -> Dictionary:
	return {
		"version": 1,
		"xp": 0, "level": 1,
		"unlocked_characters": ["rukk"],
		"unlocked_weapons": ["pistol"],
		"collectibles": [],
		"achievements": [],
		"level_progress": {},
	}

func _slot_path(slot: int) -> String:
	return "%s/slot_%d.json" % [SAVE_DIR, slot]

func save_game(slot: int = -1) -> void:
	if slot >= 0:
		active_slot = slot
	var f := FileAccess.open(_slot_path(active_slot), FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(profile, "\t"))
		f.close()

func load_game(slot: int) -> bool:
	active_slot = slot
	var path := _slot_path(slot)
	if not FileAccess.file_exists(path):
		profile = _default_profile()
		return false
	var f := FileAccess.open(path, FileAccess.READ)
	var data: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if data is Dictionary:
		profile = data
		return true
	profile = _default_profile()
	return false

func autosave() -> void:
	save_game()

# --- Progression helpers ---------------------------------------------------
func add_xp(amount: int) -> void:
	profile.xp += amount
	while profile.xp >= _xp_for_level(profile.level + 1):
		profile.level += 1
		EventBus.notify.emit("Level up! Lv %d" % profile.level)

func unlock(category: String, id: String) -> void:
	var key := "unlocked_%s" % category
	if profile.has(key) and id not in profile[key]:
		profile[key].append(id)
		autosave()

func _xp_for_level(lvl: int) -> int:
	return 100 * (lvl - 1) * lvl / 2   # gentle triangular curve

# --- Settings persistence (used by Settings autoload) ----------------------
func save_settings(data: Dictionary) -> void:
	var f := FileAccess.open(SETTINGS_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data, "\t"))
		f.close()

func load_settings() -> Dictionary:
	if not FileAccess.file_exists(SETTINGS_PATH):
		return {}
	var f := FileAccess.open(SETTINGS_PATH, FileAccess.READ)
	var data: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return data if data is Dictionary else {}
