from typing import Tuple

import numpy as np	# type: ignore


# Tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
	[
		("ch", np.int32),	# Unicode Codepoint
		("fg", "3B"),		# 3 unsigned bytes for RGB Colors, foreground
		("bg", "3B"),		# 3 unsigned bytes for RGB colors, background
	]
)

# Tile struct used for statically defined tile data
tile_dt = np.dtype(
	[
		("walkable", np.bool),		# True if can be walked over
		("transparent", np.bool),	# True if dosent block FOV
		("dark", graphic_dt),		# Graphics when tile is not in FOV
		("light", graphic_dt),		# Graphic when tile is in FOV
		("kind", "S20"),			# kind of tile (wall, floor, door, ...)
	]
)

def new_tile(
	*, 	# Enforce the use of keywords, so that parameter doesnt matter
	walkable: int,
	transparent: int,
	dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
	light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
	kind: str,
) -> np.ndarray:
	"""Helper Function for defining individual tile types """
	return np.array((walkable, transparent, dark, light, kind), dtype=tile_dt)
	
# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255,255,255), (0,0,0)), dtype = graphic_dt)

		
floor = new_tile(
	walkable=True,
	transparent=True,
	dark=(ord(" "), (255, 255, 255), (50, 50, 150)),
	light=(ord(" "), (255, 255, 255), (200,180,50)),
	kind=("Floor"),
)

wall = new_tile(
	kind=("Wall"),
	walkable=False,
	transparent=False,
	dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
	light=(ord(" "), (255, 255, 255), (130, 110, 50)),
)

door = new_tile(
	kind=("Door"),
	walkable=True,
	transparent=False,
	dark=(ord("X"), (0, 0, 100), (50, 50, 150)),
	light=(ord("X"), (255, 255, 255), (200,180,50)),
)

door_open = new_tile(
	kind=("Door"),
	walkable=True,
	transparent=True,
	dark=(ord("."), (0, 0, 100), (50, 50, 150)),
	light=(ord("."), (255, 255, 255), (200,180,50)),
)

ironbar = new_tile(
	kind=("Ironbar"),
	walkable=False,
	transparent=True,
	dark=(ord("#"), (10, 90, 100), (50, 50, 150)),
	light=(ord("#"), (10, 140, 160), (200,180,50)),
)

down_stairs = new_tile(
	kind=("Stairs"),
	walkable = True,
	transparent = True,
	dark=(ord(">"), (0,0,100), (50, 50, 150)),
	light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)

up_stairs = new_tile(
	kind=("Stairs"),
	walkable = True,
	transparent = True,
	dark=(ord("<"), (0,0,100), (50, 50, 150)),
	light=(ord("<"), (255, 255, 255), (200, 180, 50)),
)

""" Shop not used at the moment, and unsure if it will ever be used """
shop = new_tile(
	kind=("Shop"),
	walkable = False,
	transparent = True,
	dark=(ord("S"), (0,0,100), (50, 50, 150)),
	light=(ord("S"), (255, 255, 255), (200, 140, 50)),
)

""" Used as a base for furniture which blocks the FOV; when not in FOV rendered as a wall """
fake_wall = new_tile(
	kind=(""),
	walkable=True,
	transparent=False,
	dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
	light=(ord(" "), (255, 255, 255), (200, 180, 50)),
)

""" Used as a base for furniture which blocks the FOV, when not in FOV rendered as a floor """
fake_cloud = new_tile(
	kind=(""),
	walkable=True,
	transparent=False,
	dark=(ord(" "), (255, 255, 255), (50, 50, 150)),
	light=(ord(" "), (255, 255, 255), (200,180,50)),
)

""" Used as a base for ironbars,... which do not block the FOV; when not in FOV rendered as a window (of course) """
window_base = new_tile(
	kind=("Ironbar"),
	walkable=True,
	transparent=True,
	dark=(ord("#"), (10, 90, 100), (50, 50, 150)),
	light=(ord("#"), (10, 140, 160), (200,180,50)),
)

open_door_base = new_tile(
	kind = ("Door"),
	walkable=True,
	transparent=True,
	dark=(ord("."), (10, 90, 100), (50, 50, 150)),
	light=(ord("."), (255, 255, 255), (200,180,50)),
)

closed_door_base = new_tile(
	kind=("Door"),
	walkable=False,
	transparent=False,
	dark=(ord("+"), (50, 50, 150), (0, 0, 100)),
	light=(ord("+"), (255, 255, 255), (130, 110, 50)),
)

hidden_door_base = new_tile(
	kind=("Door"),
	walkable=False,
	transparent=False,
	dark=(ord(" "), (50, 50, 150), (0, 0, 100)),
	light=(ord(" "), (255, 255, 255), (130, 110, 50)),
)
