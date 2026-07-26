extends State
class_name EnemyState
## Base for enemy AI states with typed access to the Enemy host and its perception.

var enemy: Enemy

func setup(m: StateMachine, h: Node) -> void:
	super.setup(m, h)
	enemy = h as Enemy
