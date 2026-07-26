# Placeholder assets

This folder is intentionally (almost) empty. RUKKUS ships **no binary art/audio yet** — all
visuals are drawn procedurally (`_draw`, `Polygon2D`, particles, shockwave rings) and all SFX
are silent hooks routed through `AudioManager` by string id.

Drop real assets here as they are produced:
- `sprites/` — HD pixel-art sheets → swap `PlayerVisuals`/`EnemyVisuals` for `AnimatedSprite2D`.
- `audio/sfx/` — register with `AudioManager.register_sfx(&"shoot_pistol", stream)`.
- `audio/music/` — assign to `LevelData.music`; wire adaptive layers via
  `AudioManager.set_music_intensity`.

Nothing in code hard-codes an asset path, so adding art/audio never requires touching systems.
