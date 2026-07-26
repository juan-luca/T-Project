extends Node2D
## Lives in the world and turns EventBus.explosion events into actual gameplay: radial
## damage to every hurtbox in range (distance falloff), knockback impulses to rigid debris,
## a shockwave visual, camera trauma and noise for AI hearing. One place = chain reactions
## (an exploding barrel emits another explosion, which this resolves again).

func _ready() -> void:
	EventBus.explosion.connect(_on_explosion)

func _on_explosion(pos: Vector2, radius: float, damage: float) -> void:
	_spawn_shockwave(pos, radius)
	AudioManager.play_sfx_at(&"explosion", pos)
	EventBus.noise_emitted.emit(pos, radius * 2.0)
	var space := get_world_2d().direct_space_state
	# 1) Damage hurtboxes (layer 8) with linear falloff.
	var shape := CircleShape2D.new()
	shape.radius = radius
	var q := PhysicsShapeQueryParameters2D.new()
	q.shape = shape
	q.transform = Transform2D(0.0, pos)
	q.collision_mask = 128            # hurtbox layer
	q.collide_with_areas = true
	q.collide_with_bodies = false
	for hit in space.intersect_shape(q, 64):
		var area := hit.get("collider") as HurtboxComponent
		if area:
			var d: float = area.global_position.distance_to(pos)
			var falloff := clampf(1.0 - d / radius, 0.1, 1.0)
			var dir: Vector2 = (area.global_position - pos).normalized()
			area.receive(DamageInfo.make(damage * falloff, DamageInfo.Type.EXPLOSIVE, dir * 520.0 * falloff, self))
	# 2) Launch loose rigid debris for spectacle.
	q.collision_mask = 0xFFFFFFFF
	q.collide_with_areas = false
	q.collide_with_bodies = true
	for hit in space.intersect_shape(q, 64):
		var body := hit.get("collider") as RigidBody2D
		if body:
			var dir: Vector2 = (body.global_position - pos).normalized()
			var falloff := clampf(1.0 - body.global_position.distance_to(pos) / radius, 0.1, 1.0)
			body.apply_central_impulse(dir * 600.0 * falloff)

func _spawn_shockwave(pos: Vector2, radius: float) -> void:
	var ring := ExplosionRing.new()
	ring.max_radius = radius
	add_child(ring)
	ring.global_position = pos

## Self-contained expanding-ring + flash visual that frees itself.
class ExplosionRing extends Node2D:
	var max_radius: float = 100.0
	var t: float = 0.0
	func _process(delta: float) -> void:
		t += delta * 3.0
		queue_redraw()
		if t >= 1.0:
			queue_free()
	func _draw() -> void:
		var r := max_radius * ease(minf(t, 1.0), 0.35)
		var a := 1.0 - t
		draw_circle(Vector2.ZERO, r, Color(1.0, 0.7, 0.25, a * 0.5))
		draw_arc(Vector2.ZERO, r, 0, TAU, 48, Color(1.0, 0.95, 0.7, a), 4.0)
		draw_circle(Vector2.ZERO, r * 0.4, Color(1, 1, 0.8, a * 0.7))
