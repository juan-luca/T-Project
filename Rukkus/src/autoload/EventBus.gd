extends Node
## Global, typed signal hub — the ONLY place cross-system signals are declared.
##
## Systems emit here and listen here so no system needs a hard reference to another.
## Keeping every global signal in one file makes the whole game's event surface auditable.
##
## Convention: past-tense names for "something happened" facts (player_died),
## imperative names for requests (request_slow_motion).

# --- Game flow -------------------------------------------------------------
signal game_state_changed(new_state: int)          ## GameManager.GameState
signal level_load_requested(level_id: StringName)
signal level_loaded(level_id: StringName)
signal level_completed(level_id: StringName)
signal game_paused(is_paused: bool)

# --- Player ----------------------------------------------------------------
signal player_spawned(player: Node, slot: int)
signal player_health_changed(slot: int, hp: float, max_hp: float)
signal player_shield_changed(slot: int, shield: float, max_shield: float)
signal player_special_changed(slot: int, value: float, max_value: float)
signal player_died(slot: int)
signal player_respawned(slot: int)
signal player_state_changed(slot: int, state_name: StringName)

# --- Weapons / combat ------------------------------------------------------
signal weapon_equipped(slot: int, weapon_id: StringName)
signal weapon_fired(slot: int, weapon_id: StringName)
signal ammo_changed(slot: int, in_mag: int, reserve: int)
signal reload_started(slot: int)
signal grenades_changed(slot: int, count: int)
signal damage_dealt(target: Node, info: Resource)      ## info: DamageInfo
signal noise_emitted(position: Vector2, radius: float)  ## for enemy hearing

# --- Enemies / bosses ------------------------------------------------------
signal enemy_spawned(enemy: Node)
signal enemy_died(enemy: Node, position: Vector2)
signal boss_intro(boss: Node)
signal boss_phase_changed(boss: Node, phase: int)
signal boss_defeated(boss: Node)

# --- World / destruction / pickups ----------------------------------------
signal destructible_destroyed(position: Vector2, material_type: int)
signal explosion(position: Vector2, radius: float, damage: float)
signal powerup_collected(slot: int, powerup_id: StringName)
signal npc_rescued(npc: Node)
signal checkpoint_activated(checkpoint: Node)

# --- Camera / juice --------------------------------------------------------
signal request_camera_shake(trauma: float)
signal request_slow_motion(scale: float, duration: float)
signal request_hitstop(duration: float)
signal request_zoom(zoom: float, duration: float)

# --- UI / feedback ---------------------------------------------------------
signal floating_number_requested(position: Vector2, amount: float, kind: int)
signal objective_updated(text: String)
signal notify(text: String)

func _ready() -> void:
	# EventBus must keep running while the tree is paused so pause/unpause events flow.
	process_mode = Node.PROCESS_MODE_ALWAYS
