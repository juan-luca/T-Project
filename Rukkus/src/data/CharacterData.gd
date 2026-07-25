extends Resource
class_name CharacterData
## An original playable hero. Stats + exclusive weapon + unique ability + ultimate.
## Add a new character = one .tres, no code.

@export var id: StringName = &"rukk"
@export var display_name: String = "Sarge Rukk"
@export_multiline var backstory: String = ""
@export_multiline var personality: String = ""

@export_group("Stats")
@export var max_hp: float = 100.0
@export var max_shield: float = 0.0
@export var move_tuning: MovementTuning
@export var starting_weapon: WeaponData

@export_group("Kit")
@export var ability_id: StringName = &"combat_roll"     ## unique active ability
@export var ability_cooldown: float = 4.0
@export var ultimate_id: StringName = &"rocket_barrage"  ## charges via special meter
@export var ultimate_cost: float = 100.0

@export_group("Flavor")
@export var color: Color = Color(0.9, 0.4, 0.2)          ## placeholder tint / UI accent
@export var barks: PackedStringArray = PackedStringArray()  ## random quips
@export var unlock_cost: int = 0
