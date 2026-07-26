extends RefCounted
class_name PlayerIntent
## An immutable-ish snapshot of one player's inputs for a single frame. Produced by
## InputManager.get_intent(slot). Gameplay reads this instead of the global Input singleton,
## which is what makes local/online co-op a matter of feeding more slots.

var move := Vector2.ZERO       ## analog move (x) / vertical aim (y)
var aim := Vector2.RIGHT       ## 8-direction aim vector
var jump_pressed := false
var jump_held := false
var jump_released := false
var fire_held := false
var fire_pressed := false
var dash_pressed := false
var grenade_pressed := false
var melee_pressed := false
var special_pressed := false
