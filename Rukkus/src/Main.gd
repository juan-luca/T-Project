extends Node2D
## Entry point. Assembles the persistent world container, camera, explosion resolver and HUD,
## then asks LevelManager to stream in the first level. Kept tiny — it only wires singletons
## to scene nodes; it contains no gameplay logic.

const HUD_SCENE := preload("res://scenes/HUD.tscn")
const EXPLOSION_RESOLVER := preload("res://src/fx/ExplosionResolver.gd")

@export var start_level: StringName = &"jungle_01"

func _ready() -> void:
	var world := Node2D.new()
	world.name = "World"
	add_child(world)
	LevelManager.set_world_root(world)

	# Explosion AOE resolver lives at world scope (persists across level swaps).
	var resolver := EXPLOSION_RESOLVER.new()
	resolver.name = "ExplosionResolver"
	add_child(resolver)

	# Camera + HUD.
	var cam := GameCamera.new()
	cam.name = "GameCamera"
	add_child(cam)
	add_child(HUD_SCENE.instantiate())

	# Start the run and stream in the first level.
	GameManager.start_new_run()
	EventBus.notify.emit("RUKKUS")
	LevelManager.load_level(start_level)
