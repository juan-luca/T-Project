extends Resource
class_name ProjectileData
## Data-driven projectile definition. Designers create .tres files; no code needed for a
## new bullet type. Exotic behaviours (boomerang return, homing) are opt-in flags.

enum Motion { STRAIGHT, GRAVITY, HOMING, BOOMERANG, BEAM }

@export var speed: float = 900.0
@export var lifetime: float = 1.2
@export var motion: Motion = Motion.STRAIGHT
@export var gravity_scale: float = 1.0          ## for GRAVITY motion (grenades/bazooka arc)
@export var pierce: int = 0                     ## enemies to pass through
@export var bounces: int = 0                    ## wall bounces before dying
@export var homing_strength: float = 0.0
@export var explode_on_hit: bool = false
@export var explosion_radius: float = 0.0
@export var explosion_damage: float = 0.0
@export_group("Presentation")
@export var color: Color = Color(1, 0.9, 0.3)
@export var size: Vector2 = Vector2(10, 3)
@export var trail: bool = true
@export var impact_sfx: StringName = &"impact"
