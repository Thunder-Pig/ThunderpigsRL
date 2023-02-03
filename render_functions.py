from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color
import settings

if TYPE_CHECKING:
	from tcod import Console
	from engine import Engine
	from game_map import GameMap
	
def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
	""" Returns the name of objects at a given location """
	if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
		return ""
		
	names = ", ".join(
		entity.name for entity in game_map.entities if entity.x == x and entity.y == y
	)
	# old return names.capitalize()
	return names

def render_bar(console: Console, current_value: int, maximum_value: int, total_width: int) -> None:
	""" Draws an Hitpoint Bar Graph for the player, overlayed by the HP numbers """
	bar_width = int(float(current_value) / maximum_value * total_width)
	
	console.draw_rect(x=0, y=45, width=20, height=1, ch=1, bg=color.bar_empty)
	
	if bar_width > 0:
		console.draw_rect(
			x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled
		)
		
	console.print(
		x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
	)

def render_dungeon_level(console: Console, dungeon_level: int, location: Tuple[int, int]) -> None:
	""" Render the level the player is currently on, at the given location. """
	x, y = location
	
	console.print(x=x, y=y, string=settings.str_dungeon_level.ljust(10) + f": {dungeon_level}")

def render_xp_points(console: Console, xp_points: int, location: Tuple[int, int]) -> None:
	""" Render the players actual XP points. """
	x, y = location
	
	console.print(x=x, y=y, string=settings.str_experience.ljust(10) + f": {xp_points}")

def render_names_at_mouse_location(console: Console, x: int, y: int, engine: Engine) -> None:
	""" Renders the names of objects at the mouse location, unsing get_names_at_location """
	mouse_x, mouse_y = engine.mouse_location
	
	names_at_mouse_location = get_names_at_location(
		x = mouse_x, y = mouse_y, game_map = engine.game_map
	)
	
	console.print(x=x, y=y, string=names_at_mouse_location)
	
def render_weapon(console: Console, location: Tuple[int, int], weapon: str, engine: Engine) -> None:
	""" Render the currently equipped weapon """
	x, y = location

	console.print(x=x, y=y, string=settings.str_weapon.ljust(10) + f": {weapon}")

	
def render_quiver(console: Console, location: Tuple[int, int], quiver: str, engine: Engine) -> None:
	""" Render the Number of Arrows inside the quiver """
	x, y = location

	console.print(x=x, y=y, string=settings.str_quiver.ljust(10) + f": {quiver}")

