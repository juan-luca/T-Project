extends EnemyState
## Death pop + ragdoll-lite launch, then despawn (returns debris/fx via EventBus).

func enter(_msg: Dictionary = {}) -> void:
	enemy.hurtbox.set_deferred("monitorable", false)
	enemy.contact_hitbox.deactivate()
	enemy.velocity = Vector2(-enemy.facing * 160.0, -280.0)
	enemy.collision_layer = 0
	EventBus.destructible_destroyed.emit(enemy.global_position, 0)
	# Small delay so the corpse pop reads before cleanup.
	enemy.get_tree().create_timer(1.2).timeout.connect(enemy.queue_free)

func physics_update(delta: float) -> void:
	enemy.velocity.y = minf(enemy.velocity.y + enemy.gravity * delta, 1200.0)
	enemy.velocity.x = move_toward(enemy.velocity.x, 0, 400.0 * delta)
