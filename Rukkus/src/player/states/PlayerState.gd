extends State
class_name PlayerState
## Base for player locomotion states. Gives typed access to the Player host.

var player: Player

func setup(m: StateMachine, h: Node) -> void:
	super.setup(m, h)
	player = h as Player
