extends Area2D
class_name Projectile
## Pooled projectile driven by a ProjectileData resource. Handles straight/gravity/homing/
## boomerang motion, piercing, bouncing and explode-on-hit. Returns itself to the pool.

var data: ProjectileData
var _velocity: Vector2
var _life: float
var _pierced: int = 0
var _bounced: int = 0
var _team: int = 0
var _damage: float = 10.0
var _damage_type: int = DamageInfo.Type.BALLISTIC
var _knockback: float = 0.0
var _source: Node
var _origin: Vector2
var _returning: bool = false

@onready var _shape: CollisionShape2D = $CollisionShape2D

func pool_reset() -> void:
	_life = 0.0
	_pierced = 0
	_bounced = 0
	_returning = false
	monitoring = true
	monitorable = true

## Fired by WeaponHolder. `team` 0=player projectile, 1=enemy projectile.
func launch(p_data: ProjectileData, pos: Vector2, dir: Vector2, team: int, damage: float, dtype: int, knockback: float, source: Node) -> void:
	data = p_data
	global_position = pos
	_origin = pos
	_velocity = dir.normalized() * p_data.speed
	rotation = dir.angle()
	_team = team
	_damage = damage
	_damage_type = dtype
	_knockback = knockback
	_source = source
	_life = p_data.lifetime
	# Detect all hurtboxes (layer 8) and filter by team in code; also collide with world +
	# destructible geometry. Actor BODIES are on layers 2/3 which we intentionally do NOT
	# mask, so bullets fly past the shooter and other actors and only hit hurtboxes.
	collision_layer = 0
	set_collision_mask_value(8, true)       # hurtboxes (team-filtered in _on_area_entered)
	set_collision_mask_value(7, true)       # destructible
	set_collision_mask_value(1, true)       # world
	queue_redraw()

func _physics_process(delta: float) -> void:
	_life -= delta
	if _life <= 0.0:
		_expire()
		return
	match data.motion:
		ProjectileData.Motion.GRAVITY:
			_velocity.y += data.gravity_scale * 1500.0 * delta
		ProjectileData.Motion.HOMING:
			var target := _nearest_target()
			if target:
				var desired := (target.global_position - global_position).normalized() * data.speed
				_velocity = _velocity.lerp(desired, data.homing_strength * delta)
		ProjectileData.Motion.BOOMERANG:
			if not _returning and global_position.distance_to(_origin) > data.speed * 0.4:
				_returning = true
			if _returning and _source is Node2D and is_instance_valid(_source):
				var back: Vector2 = ((_source as Node2D).global_position - global_position).normalized() * data.speed
				_velocity = _velocity.lerp(back, 6.0 * delta)
		_:
			pass
	global_position += _velocity * delta
	rotation = _velocity.angle()

func _draw() -> void:
	if data == null:
		return
	var s := data.size
	draw_rect(Rect2(-s * 0.5, s), data.color)
	if data.trail:
		draw_line(Vector2(-s.x * 2.0, 0), Vector2.ZERO, Color(data.color, 0.35), s.y)

func _ready() -> void:
	area_entered.connect(_on_area_entered)
	body_entered.connect(_on_body_entered)

func _on_area_entered(area: Area2D) -> void:
	if area is HurtboxComponent:
		if area.team == _team:
			return
		var dir := _velocity.normalized()
		area.receive(DamageInfo.make(_damage, _damage_type, dir * _knockback, _source))
		_on_hit(global_position)

func _on_body_entered(_body: Node) -> void:
	# Hit world geometry / destructible tilemap.
	if data.bounces > _bounced:
		_bounced += 1
		_velocity = _velocity.bounce(Vector2.UP)  # simple approximation; refined via ray normal later
		return
	_on_hit(global_position)

func _on_hit(pos: Vector2) -> void:
	AudioManager.play_sfx_at(data.impact_sfx, pos)
	if data.explode_on_hit and data.explosion_radius > 0.0:
		EventBus.explosion.emit(pos, data.explosion_radius, data.explosion_damage)
	if _pierced < data.pierce:
		_pierced += 1
		return
	_expire()

func _expire() -> void:
	monitoring = false
	ObjectPool.release(self)

func _nearest_target() -> Node2D:
	var group := "enemy" if _team == 0 else "player"
	var best: Node2D = null
	var best_d := INF
	for n in get_tree().get_nodes_in_group(group):
		if n is Node2D:
			var d := global_position.distance_squared_to(n.global_position)
			if d < best_d:
				best_d = d
				best = n
	return best
