extends Node
## Generic scene pool. Avoids per-frame instancing of projectiles, particles,
## debris and damage numbers — the main allocation hot path in a bullet-heavy game.
##
## Usage:
##   var p = ObjectPool.acquire(BULLET_SCENE)
##   ...configure and add to world...
##   ObjectPool.release(p)      # or the node calls ObjectPool.release(self)
##
## Pooled nodes should implement `pool_reset()` (optional) to clear per-use state.

const DEFAULT_PREWARM := 16
const MAX_PER_POOL := 512

var _pools: Dictionary = {}   ## PackedScene -> Array[Node] (free list)
var _counts: Dictionary = {}  ## PackedScene -> int (total created)

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE

func prewarm(scene: PackedScene, amount: int = DEFAULT_PREWARM) -> void:
	var free_list: Array = _pools.get(scene, [])
	for i in amount:
		var n := _instantiate(scene)
		_deactivate(n)
		free_list.append(n)
	_pools[scene] = free_list

func acquire(scene: PackedScene) -> Node:
	var free_list: Array = _pools.get(scene, [])
	var node: Node
	if free_list.is_empty():
		node = _instantiate(scene)
	else:
		node = free_list.pop_back()
	_pools[scene] = free_list
	if node.has_method("pool_reset"):
		node.call("pool_reset")
	_activate(node)
	return node

func release(node: Node) -> void:
	if not is_instance_valid(node):
		return
	var scene: PackedScene = node.get_meta("pool_scene", null)
	_deactivate(node)
	if node.get_parent() != self:
		if node.get_parent():
			node.get_parent().remove_child(node)
		add_child(node)
	if scene:
		var free_list: Array = _pools.get(scene, [])
		if free_list.size() < MAX_PER_POOL:
			free_list.append(node)
			_pools[scene] = free_list
		else:
			node.queue_free()

func _instantiate(scene: PackedScene) -> Node:
	var n := scene.instantiate()
	n.set_meta("pool_scene", scene)
	add_child(n)
	_counts[scene] = int(_counts.get(scene, 0)) + 1
	return n

func _activate(n: Node) -> void:
	if n is CanvasItem:
		n.visible = true
	n.set_process(true)
	n.set_physics_process(true)

func _deactivate(n: Node) -> void:
	if n is CanvasItem:
		n.visible = false
	n.set_process(false)
	n.set_physics_process(false)
	if n is Node2D:
		n.global_position = Vector2(-100000, -100000)
