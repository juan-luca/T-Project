extends Node
class_name State
## Base class for a single state in a StateMachine. Subclass and override the hooks.
##
## Open/Closed principle: adding a new behaviour = a new State node, with zero edits to
## sibling states or the machine itself.

## Emit with a state name (StringName) to request a transition. The machine listens.
signal transition_requested(target: StringName)

var machine: StateMachine        ## injected by the machine on setup
var host: Node                   ## the actor this state controls (Player/Enemy/Boss)

func setup(_machine: StateMachine, _host: Node) -> void:
	machine = _machine
	host = _host

## Called once when this state becomes active. `msg` carries optional transition data.
func enter(_msg: Dictionary = {}) -> void:
	pass

## Called when leaving this state.
func exit() -> void:
	pass

## Per-frame logic (visuals, timers).
func update(_delta: float) -> void:
	pass

## Per-physics-tick logic (movement, collisions).
func physics_update(_delta: float) -> void:
	pass

## Optional input handling.
func handle_input(_event: InputEvent) -> void:
	pass

## Helper to ask the machine to switch state.
func transition_to(target: StringName, msg: Dictionary = {}) -> void:
	machine.transition_to(target, msg)
