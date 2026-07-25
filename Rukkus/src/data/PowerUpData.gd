extends Resource
class_name PowerUpData
## Data-driven power-up. A timed or instant modifier applied to a player.
## Add "Damage x2 / Invincibility / Speed / Triple Jump / Explosive Rounds / Laser /
## Shield / Infinite Ammo / Heal / Slow-Mo / Coin Magnet" as .tres files.

enum Effect {
	HEAL, SHIELD, DAMAGE_MULT, INVINCIBILITY, SPEED, EXTRA_JUMP,
	EXPLOSIVE_ROUNDS, INFINITE_AMMO, SLOW_MOTION, COIN_MAGNET, WEAPON_SWAP,
}

@export var id: StringName = &"heal"
@export var display_name: String = "Med Kit"
@export var effect: Effect = Effect.HEAL
@export var magnitude: float = 50.0            ## meaning depends on effect (hp / mult / speed%)
@export var duration: float = 0.0              ## 0 = instant/permanent-for-run
@export var weapon_grant: WeaponData           ## for WEAPON_SWAP
@export_group("Presentation")
@export var color: Color = Color(0.3, 1.0, 0.4)
@export var pickup_sfx: StringName = &"pickup"
