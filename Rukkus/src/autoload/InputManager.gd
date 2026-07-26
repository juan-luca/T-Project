extends Node
## Device-aware input. Each player SLOT (0-3) is bound to a control scheme:
##   KEYBOARD_A (WASD+JKL), KEYBOARD_B (arrows + M/N/B/,./), or a specific GAMEPAD device.
## Gameplay asks `InputManager.get_intent(slot)` and never touches the global Input singleton,
## so local co-op is just "bind more slots" and online co-op is "feed remote intents".
##
## Gamepads are polled per-device (Input.get_joy_axis/is_joy_button_pressed) with manual edge
## detection, because Godot's action map can't distinguish which controller pressed a button.

enum Scheme { KEYBOARD_A, KEYBOARD_B, GAMEPAD }

const DEADZONE := 0.35
# Standard Godot joypad button ids.
const BTN := {
	"jump": JOY_BUTTON_A, "melee": JOY_BUTTON_B, "fire": JOY_BUTTON_X,
	"grenade": JOY_BUTTON_Y, "special": JOY_BUTTON_LEFT_SHOULDER,
	"dash": JOY_BUTTON_RIGHT_SHOULDER, "start": JOY_BUTTON_START,
}

var _bindings: Dictionary = {}     ## slot -> {scheme:int, device:int}
var _intents: Dictionary = {}      ## slot -> PlayerIntent (rebuilt each physics frame)
var _pad_prev: Dictionary = {}     ## "device:button" -> bool (edge detection)
var _last_aim: Dictionary = {}     ## slot -> Vector2 (keep last aim when stick centered)

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE
	process_priority = -100           # poll before any player reads intents this frame

func _physics_process(_delta: float) -> void:
	for slot in _bindings:
		_intents[slot] = _build_intent(slot)

# --- Binding API (used by CoopManager) -------------------------------------
func bind(slot: int, scheme: Scheme, device: int = -1) -> void:
	_bindings[slot] = {"scheme": scheme, "device": device}
	_last_aim[slot] = Vector2.RIGHT

func unbind(slot: int) -> void:
	_bindings.erase(slot)
	_intents.erase(slot)

func is_scheme_bound(scheme: Scheme, device: int = -1) -> bool:
	for b in _bindings.values():
		if b.scheme == scheme and b.device == device:
			return true
	return false

func get_binding(slot: int) -> Dictionary:
	return _bindings.get(slot, {})

# --- Intent access ---------------------------------------------------------
func get_intent(slot: int) -> PlayerIntent:
	if not _intents.has(slot):
		# Fall back to a fresh keyboard-A read if asked before first physics tick.
		return _build_intent(slot)
	return _intents[slot]

func _build_intent(slot: int) -> PlayerIntent:
	var b: Dictionary = _bindings.get(slot, {"scheme": Scheme.KEYBOARD_A, "device": -1})
	match b.scheme:
		Scheme.KEYBOARD_A:
			return _keyboard_intent(slot, "p1")
		Scheme.KEYBOARD_B:
			return _keyboard_intent(slot, "p2")
		Scheme.GAMEPAD:
			return _gamepad_intent(slot, b.device)
	return PlayerIntent.new()

# --- Keyboard (via action map) ---------------------------------------------
func _keyboard_intent(slot: int, p: String) -> PlayerIntent:
	var it := PlayerIntent.new()
	var x := Input.get_axis(p + "_left", p + "_right")
	var y := Input.get_axis(p + "_up", p + "_down")
	it.move = Vector2(x, y)
	it.aim = _resolve_aim(slot, Vector2(x, y), x)
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

# --- Gamepad (per-device polling + manual edges) ---------------------------
func _gamepad_intent(slot: int, device: int) -> PlayerIntent:
	var it := PlayerIntent.new()
	var x := _dz(Input.get_joy_axis(device, JOY_AXIS_LEFT_X))
	var y := _dz(Input.get_joy_axis(device, JOY_AXIS_LEFT_Y))
	it.move = Vector2(x, y)
	it.aim = _resolve_aim(slot, Vector2(x, y), x)
	it.jump_held = Input.is_joy_button_pressed(device, BTN.jump)
	it.jump_pressed = _edge(device, BTN.jump, true)
	it.jump_released = _edge(device, BTN.jump, false)
	var fire := Input.is_joy_button_pressed(device, BTN.fire) or Input.get_joy_axis(device, JOY_AXIS_TRIGGER_RIGHT) > 0.5
	it.fire_held = fire
	it.fire_pressed = _edge(device, BTN.fire, true)
	it.dash_pressed = _edge(device, BTN.dash, true)
	it.grenade_pressed = _edge(device, BTN.grenade, true)
	it.melee_pressed = _edge(device, BTN.melee, true)
	it.special_pressed = _edge(device, BTN.special, true)
	return it

## Returns a rising (want_press) or falling edge for a device button, updating stored state.
func _edge(device: int, button: int, want_press: bool) -> bool:
	var key := "%d:%d" % [device, button]
	var now := Input.is_joy_button_pressed(device, button)
	var prev: bool = _pad_prev.get(key, false)
	_pad_prev[key] = now
	return (now and not prev) if want_press else (prev and not now)

func _dz(v: float) -> float:
	return 0.0 if absf(v) < DEADZONE else v

func _resolve_aim(slot: int, move: Vector2, x: float) -> Vector2:
	if move.length() >= 0.3:
		var ang := snappedf(move.angle(), PI / 4.0)
		var a := Vector2.RIGHT.rotated(ang)
		_last_aim[slot] = a
		return a
	# Stick/keys centered: keep facing horizontally from last aim.
	var last: Vector2 = _last_aim.get(slot, Vector2.RIGHT)
	return Vector2(1 if last.x >= 0 else -1, 0)
