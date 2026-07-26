extends Node2D
class_name Level
## Builds a playable placeholder biome procedurally: parallax backdrop, solid terrain,
## a player spawn, enemies, destructibles, power-ups, a moving platform, a checkpoint and a
## rescue NPC. Real levels will use TileMaps + hand-placed instances; this proves the loop
## and every system end-to-end.

@export var level_data: LevelData

const ENEMY := preload("res://scenes/Enemy.tscn")
const DEST := preload("res://scenes/Destructible.tscn")
const POWERUP := preload("res://scenes/PowerUp.tscn")
const GRUNT := preload("res://src/enemies/resources/grunt.tres")
const BRUISER := preload("res://src/enemies/resources/bruiser.tres")
const DRONE := preload("res://src/enemies/resources/drone.tres")
const HEAL := preload("res://src/powerups/resources/heal.tres")
const DMG := preload("res://src/powerups/resources/damage_x2.tres")
const INVI := preload("res://src/powerups/resources/invincibility.tres")

const GROUND_Y := 520.0

func _ready() -> void:
	add_to_group("level")
	_build_background()
	_build_terrain()
	_build_spawn()
	_populate()
	if level_data and level_data.music:
		AudioManager.play_music(level_data.music)
	EventBus.objective_updated.emit("Clear the outpost — rescue the civilian — reach extraction")

# --- Parallax backdrop ------------------------------------------------------
func _build_background() -> void:
	var bg := ParallaxBackground.new()
	add_child(bg)
	_add_parallax_layer(bg, 0.2, Color(0.10, 0.16, 0.14), 220.0, 1400)
	_add_parallax_layer(bg, 0.5, Color(0.14, 0.24, 0.18), 120.0, 900)

func _add_parallax_layer(bg: ParallaxBackground, scale: float, color: Color, hill_h: float, mirror: int) -> void:
	var layer := ParallaxLayer.new()
	layer.motion_scale = Vector2(scale, scale)
	layer.motion_mirroring = Vector2(mirror, 0)
	bg.add_child(layer)
	var poly := Polygon2D.new()
	poly.color = color
	var pts := PackedVector2Array()
	pts.append(Vector2(0, 700))
	var x := 0.0
	while x <= mirror:
		pts.append(Vector2(x, GROUND_Y - hill_h * (0.5 + 0.5 * sin(x * 0.01))))
		x += 80.0
	pts.append(Vector2(mirror, 700))
	poly.polygon = pts
	layer.add_child(poly)

# --- Terrain (solid, on world layer 1) --------------------------------------
func _build_terrain() -> void:
	_platform(Vector2(1500, GROUND_Y + 60), Vector2(3400, 120), Color(0.20, 0.30, 0.16))  # main floor
	_platform(Vector2(700, 400), Vector2(240, 24), Color(0.24, 0.34, 0.2))
	_platform(Vector2(1150, 320), Vector2(200, 24), Color(0.24, 0.34, 0.2))
	_platform(Vector2(1650, 380), Vector2(220, 24), Color(0.24, 0.34, 0.2))
	_platform(Vector2(2300, 300), Vector2(260, 24), Color(0.24, 0.34, 0.2))
	# A tall wall to demo wall-slide / wall-jump.
	_platform(Vector2(1950, 360), Vector2(30, 340), Color(0.18, 0.26, 0.15))
	var mp := MovingPlatform.new()
	mp.position = Vector2(1300, 440)
	mp.travel = Vector2(0, -160)
	mp.period = 3.5
	add_child(mp)

func _platform(center: Vector2, size: Vector2, color: Color) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = center
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	cs.shape = shape
	body.add_child(cs)
	var poly := Polygon2D.new()
	poly.color = color
	poly.polygon = PackedVector2Array([-size * 0.5, Vector2(size.x * 0.5, -size.y * 0.5),
		size * 0.5, Vector2(-size.x * 0.5, size.y * 0.5)])
	body.add_child(poly)
	add_child(body)

# --- Spawn ------------------------------------------------------------------
func _build_spawn() -> void:
	var spawn := Marker2D.new()
	spawn.position = Vector2(140, GROUND_Y - 40)
	spawn.add_to_group("player_spawn")
	add_child(spawn)

# --- Entities ---------------------------------------------------------------
func _populate() -> void:
	_spawn_enemy(GRUNT, Vector2(650, GROUND_Y - 40))
	_spawn_enemy(GRUNT, Vector2(900, GROUND_Y - 40))
	_spawn_enemy(DRONE, Vector2(1150, 240))
	_spawn_enemy(BRUISER, Vector2(1750, GROUND_Y - 40))
	_spawn_enemy(GRUNT, Vector2(2100, GROUND_Y - 40))
	_spawn_enemy(DRONE, Vector2(2400, 200))

	_spawn_destructible(Vector2(500, GROUND_Y - 20), Destructible.Material.EXPLOSIVE, true, Color(1, 0.5, 0.2))
	_spawn_destructible(Vector2(560, GROUND_Y - 20), Destructible.Material.WOOD, false, Color(0.55, 0.38, 0.2))
	_spawn_destructible(Vector2(1600, 340), Destructible.Material.GLASS, false, Color(0.5, 0.8, 0.9))
	_spawn_destructible(Vector2(2050, GROUND_Y - 20), Destructible.Material.EXPLOSIVE, true, Color(1, 0.5, 0.2))

	_spawn_powerup(HEAL, Vector2(1150, 280))
	_spawn_powerup(DMG, Vector2(1650, 340))
	_spawn_powerup(INVI, Vector2(2300, 260))

	var cp := Checkpoint.new()
	cp.position = Vector2(1400, GROUND_Y - 24)
	add_child(cp)

	var npc := RescueNPC.new()
	npc.position = Vector2(2200, GROUND_Y - 30)
	add_child(npc)

func _spawn_enemy(data: EnemyData, pos: Vector2) -> void:
	var e := ENEMY.instantiate()
	e.data = data
	e.position = pos
	add_child(e)

func _spawn_destructible(pos: Vector2, mat: int, explosive: bool, color: Color) -> void:
	var d := DEST.instantiate()
	d.material_type = mat
	d.explosive = explosive
	d.color = color
	d.position = pos
	add_child(d)

func _spawn_powerup(data: PowerUpData, pos: Vector2) -> void:
	var pu := POWERUP.instantiate()
	pu.data = data
	pu.position = pos
	add_child(pu)
