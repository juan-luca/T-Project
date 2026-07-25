extends Resource
class_name EnemyData
## Data-driven enemy definition: stats, senses, AI behaviour flags and weapon.
## Difficulty scaling is applied on top of these at spawn time.

enum Archetype { GRUNT, HEAVY, FLYER, SNIPER, KAMIKAZE, SHIELD, BOSS }

@export var id: StringName = &"grunt"
@export var display_name: String = "Grunt"
@export var archetype: Archetype = Archetype.GRUNT

@export_group("Stats")
@export var max_hp: float = 40.0
@export var move_speed: float = 120.0
@export var contact_damage: float = 12.0
@export var score_value: int = 100
## Per-type resistances (index by DamageInfo.Type). e.g. robots resist ballistic, weak electric.
@export var resistances: PackedFloat32Array = PackedFloat32Array([1, 1, 1, 1, 1, 1])

@export_group("Senses")
@export var vision_range: float = 380.0
@export var vision_angle_deg: float = 90.0
@export var hearing_range: float = 260.0
@export var reaction_time: float = 0.35

@export_group("Behaviour")
@export var aggression: float = 1.0            ## scales chase speed / fire cadence
@export var can_take_cover: bool = true
@export var can_flank: bool = false
@export var can_retreat: bool = true
@export var retreat_hp_ratio: float = 0.25
@export var can_throw_grenades: bool = false
@export var weapon: WeaponData

@export_group("Flavor")
@export var color: Color = Color(0.7, 0.2, 0.2)
@export var death_sfx: StringName = &"enemy_die"
