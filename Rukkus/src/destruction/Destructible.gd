extends Node2D
class_name Destructible
## A breakable prop (crate, barrel, glass, vegetation, light). Damaged by bullets, melee
## and explosions via its HurtboxComponent. On break it spawns debris + FX and, if
## explosive, triggers a chain-reaction blast. Level-critical geometry never uses this —
## it is intentionally non-solid so the floor can't be deleted.

enum Material { WOOD, METAL, GLASS, FOLIAGE, EXPLOSIVE, STONE }

@export var material_type: Material = Material.WOOD
@export var max_hp: float = 30.0
@export var size: Vector2 = Vector2(40, 40)
@export var color: Color = Color(0.55, 0.38, 0.2)
@export var explosive: bool = false
@export var explosion_radius: float = 120.0
@export var explosion_damage: float = 80.0
@export var debris_count: int = 8

@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent

func _ready() -> void:
	add_to_group("destructible")
	health.max_hp = max_hp
	health.reset()
	hurtbox.team = 2                     # neutral: any team's damage breaks it
	hurtbox.health = health
	hurtbox.floating_numbers = false
	health.died.connect(_on_died)
	_size_shape()
	queue_redraw()

func _size_shape() -> void:
	var cs := hurtbox.get_node_or_null("CollisionShape2D")
	if cs and cs.shape is RectangleShape2D:
		(cs.shape as RectangleShape2D).size = size

func _draw() -> void:
	draw_rect(Rect2(-size * 0.5, size), color)
	draw_rect(Rect2(-size * 0.5, size), color.darkened(0.4), false, 2.0)
	if explosive:
		draw_circle(Vector2.ZERO, size.x * 0.2, Color(1, 0.5, 0.1))

func _on_died(_info: DamageInfo) -> void:
	EventBus.destructible_destroyed.emit(global_position, material_type)
	_spawn_debris()
	if explosive:
		EventBus.explosion.emit(global_position, explosion_radius, explosion_damage)
	queue_free()

func _spawn_debris() -> void:
	var world := get_parent()
	for i in debris_count:
		var chunk := RigidBody2D.new()
		chunk.gravity_scale = 1.0
		chunk.collision_layer = 0
		chunk.collision_mask = 1
		var poly := Polygon2D.new()
		var s := randf_range(4, 9)
		poly.polygon = PackedVector2Array([Vector2(-s, -s), Vector2(s, -s), Vector2(s, s), Vector2(-s, s)])
		poly.color = color.lerp(Color(0.1, 0.1, 0.1), randf() * 0.4)
		chunk.add_child(poly)
		world.add_child(chunk)
		chunk.global_position = global_position + Vector2(randf_range(-size.x, size.x), randf_range(-size.y, size.y)) * 0.4
		chunk.linear_velocity = Vector2(randf_range(-200, 200), randf_range(-360, -80))
		chunk.angular_velocity = randf_range(-12, 12)
		# Auto-clean debris so it never accumulates.
		get_tree().create_timer(randf_range(1.5, 3.0)).timeout.connect(chunk.queue_free)
