extends Node
class_name StateMachine
## Generic hierarchical-ready finite state machine. States are child `State` nodes.
## The host actor calls `boot(host)` once, then feeds physics/update/input.

signal state_changed(state_name: StringName)

@export var initial_state: NodePath

var current: State
var current_name: StringName = &""
var _states: Dictionary = {}   ## StringName -> State
var _host: Node

func boot(host: Node) -> void:
	_host = host
	for child in get_children():
		if child is State:
			var key := StringName(child.name.to_lower())
			_states[key] = child
			child.setup(self, host)
			child.transition_requested.connect(_on_transition_requested)
	var start := initial_state
	if not start.is_empty() and get_node_or_null(start):
		current = get_node(start)
	elif not _states.is_empty():
		current = _states.values()[0]
	if current:
		current_name = StringName(current.name.to_lower())
		current.enter()
		state_changed.emit(current_name)

func transition_to(target: StringName, msg: Dictionary = {}) -> void:
	target = StringName(String(target).to_lower())
	if not _states.has(target):
		push_warning("StateMachine: unknown state '%s'" % target)
		return
	if current:
		current.exit()
	current = _states[target]
	current_name = target
	current.enter(msg)
	state_changed.emit(target)

func physics_update(delta: float) -> void:
	if current:
		current.physics_update(delta)

func update(delta: float) -> void:
	if current:
		current.update(delta)

func handle_input(event: InputEvent) -> void:
	if current:
		current.handle_input(event)

func is_state(name: StringName) -> bool:
	return current_name == StringName(String(name).to_lower())

func _on_transition_requested(target: StringName) -> void:
	transition_to(target)
