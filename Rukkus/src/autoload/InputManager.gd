extends Node
## Maps physical devices to player SLOTS (0-3) and exposes a per-slot "intent".
##
## Gameplay code asks `InputManager.get_intent(slot)` and never touches `Input` directly,
## so adding players 2-4 (local co-op) is a device-binding change, not a rewrite.
## This is the single most important seam for the multiplayer-readiness requirement.

## An immutable snapshot of a player's inputs for one frame.
class Intent:
	var move := Vector2.ZERO       ## analog move (x) / aim vertical (y)
	var aim := Vector2.RIGHT       ## 8-direction aim vector
	var jump_pressed := false
	var jump_held := false
	var jump_released := false
	var fire_held := false
	var fire_pressed := false
	var dash_pressed := false
	var grenade_pressed := false
	var melee_pressed := false
	var special_pressed := false

const ACTIONS := {
	"left": "_left", "right": "_right", "up": "_up", "down": "_down",
	"jump": "_jump", "fire": "_fire", "dash": "_dash",
	"grenade": "_grenade", "melee": "_melee", "special": "_special",
}

## slot -> input prefix ("p1", "p2"...). Slot 0 is always keyboard+pad0 by default.
var _slot_prefix := {0: "p1", 1: "p2", 2: "p3", 3: "p4"}

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE

## Returns the aim vector snapped to 8 directions from the raw stick/keys.
func _snap_8(v: Vector2, fallback: Vector2) -> Vector2:
	if v.length() < 0.3:
		return fallback
	var ang := snappedf(v.angle(), PI / 4.0)
	return Vector2.RIGHT.rotated(ang)

func get_intent(slot: int) -> Intent:
	var p: String = _slot_prefix.get(slot, "p1")
	var it := Intent.new()
	var x := Input.get_axis(p + "_left", p + "_right")
	var y := Input.get_axis(p + "_up", p + "_down")
	it.move = Vector2(x, y)
	it.aim = _snap_8(Vector2(x, y), Vector2(1 if x >= 0 else -1, 0))
	it.jump_pressed = Input.is_action_just_pressed(p + "_jump")
	it.jump_held = Input.is_action_pressed(p + "_jump")
	it.jump_released = Input.is_action_just_released(p + "_jump")
	it.fire_held = Input.is_action_pressed(p + "_fire")
	it.fire_pressed = Input.is_action_just_pressed(p + "_fire")
	it.dash_pressed = Input.is_action_just_pressed(p + "_dash")
	it.grenade_pressed = Input.is_action_just_pressed(p + "_grenade")
	it.melee_pressed = Input.is_action_just_pressed(p + "_melee")
	it.special_pressed = Input.is_action_just_pressed(p + "_special")
	return it

## Called when local co-op is enabled to bind an extra device to a slot.
func assign_slot(slot: int, prefix: String) -> void:
	_slot_prefix[slot] = prefix
