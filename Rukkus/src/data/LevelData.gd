extends Resource
class_name LevelData
## Level/biome metadata. Lets designers register biomes, music, palette and hazards
## without touching level scenes' scripts.

enum Biome { JUNGLE, DESERT, MILITARY_BASE, CITY, LAB, VOLCANO, MOUNTAIN, SNOW, FACTORY, RUINS }

@export var id: StringName = &"jungle_01"
@export var display_name: String = "Jungle — Insertion Point"
@export var biome: Biome = Biome.JUNGLE
@export var scene_path: String = "res://scenes/levels/jungle_01.tscn"
@export var music: AudioStream
@export var palette: PackedColorArray = PackedColorArray()
@export var par_time: float = 120.0
@export var secrets_count: int = 3
@export var next_level: StringName = &""
