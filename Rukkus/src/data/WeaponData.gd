extends Resource
class_name WeaponData
## The heart of the data-driven weapon system. A new weapon (pistol, shotgun, rifle,
## minigun, flamethrower, bazooka, laser, railgun, boomerang, electric arc) = one .tres.

enum FireMode { SEMI, AUTO, BURST, BEAM }

@export var id: StringName = &"pistol"
@export var display_name: String = "Pistol"
@export_multiline var description: String = ""

@export_group("Ballistics")
@export var damage: float = 12.0
@export var damage_type: DamageInfo.Type = DamageInfo.Type.BALLISTIC
@export var fire_mode: FireMode = FireMode.SEMI
@export var fire_rate: float = 6.0             ## shots per second
@export var pellets: int = 1                   ## >1 = shotgun spread
@export var spread_degrees: float = 2.0        ## random cone
@export var burst_count: int = 3
@export var projectile: ProjectileData

@export_group("Feel")
@export var recoil: float = 60.0               ## pushback on the shooter
@export var knockback: float = 120.0           ## pushback dealt to target
@export var screen_shake: float = 0.15
@export var muzzle_flash_scale: float = 1.0

@export_group("Ammo")
@export var infinite_ammo: bool = false
@export var mag_size: int = 12
@export var reserve_ammo: int = 120
@export var reload_time: float = 1.1

@export_group("Presentation")
@export var fire_sfx: StringName = &"shoot_pistol"
@export var muzzle_color: Color = Color(1, 0.85, 0.4)

func seconds_between_shots() -> float:
	return 1.0 / maxf(0.01, fire_rate)
