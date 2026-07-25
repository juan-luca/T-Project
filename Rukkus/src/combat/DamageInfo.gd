extends Resource
class_name DamageInfo
## Value object describing a single instance of damage. Passed from a Hitbox/Projectile
## to a Hurtbox so that targets can react differently per damage TYPE (e.g. robots take
## extra ELECTRIC, mutants extra FIRE).

enum Type { BALLISTIC, EXPLOSIVE, FIRE, ELECTRIC, MELEE, TRUE }

@export var amount: float = 10.0
@export var type: Type = Type.BALLISTIC
@export var knockback: Vector2 = Vector2.ZERO
@export var is_crit: bool = false
var source: Node = null          ## who dealt it (for scoring / friendly-fire checks)

static func make(amount: float, type: int, knockback: Vector2 = Vector2.ZERO, source: Node = null) -> DamageInfo:
	var d := DamageInfo.new()
	d.amount = amount
	d.type = type
	d.knockback = knockback
	d.source = source
	return d
