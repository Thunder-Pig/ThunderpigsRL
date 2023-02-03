""" Handle the loading and initialization of game sessions. """

from __future__ import annotations

import copy
import lzma
import pickle
import traceback

from typing import Optional

import tcod

import settings
import color
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers


""" Load the background image and remove the alpha channel """
background_file = settings.menu_background_file
background_image = tcod.image.load(background_file)[:, :, :3]


def new_game() -> Engine:
	""" Return a brand new game session as an engine instance. """
	map_width = settings.map_width
	map_height = settings.map_height
	room_max_size = settings.room_max_size
	room_min_size = settings.room_min_size
	max_rooms = settings.max_rooms
	
	""" Create the player """
	player = copy.deepcopy(entity_factories.player)
	
	""" Set up the game engine and floor """
	engine = Engine(player=player)
	engine.game_world = GameWorld(
		engine = engine,
		max_rooms = max_rooms,
		room_min_size = room_min_size,
		room_max_size = room_max_size,
		map_width = map_width,
		map_height = map_height,
	)
		
	engine.game_world.generate_floor()

	""" Calculate Fov and display welcome message """
	engine.update_fov()
	engine.message_log.add_message(settings.welcome_text, color.welcome_text)
	
	""" Place dagger and healing potion in inventory and equip it without displaying equip message """
	dagger = copy.deepcopy(entity_factories.dagger)
	dagger.parent = player.inventory
	player.inventory.items.append(dagger)
	player.equipment.toggle_equip(dagger, add_message=False)
	
	potion = copy.deepcopy(entity_factories.health_potion)
	potion.parent = player.inventory
	player.inventory.items.append(potion)

	""" Update the players values and skills accordingly to its race/class """
	player.race.adjust_fighter()	
	player.body.update_skills()
	
	return engine

def load_game(filename: str) -> Engine:
	""" Load an Engine instance from a file. """
	with open(filename, "rb") as f:
		engine = pickle.loads(lzma.decompress(f.read()))
	assert isinstance(engine, Engine)
	return engine
	
	
class MainMenu(input_handlers.BaseEventHandler):
	""" Handle the main menu rendering and input. """
	
	def on_render(self, console: tcod.Console) -> None:
		""" Render the main menu on a background image. """
		console.draw_semigraphics(background_image, 0, 0)
		
		console.print(
			console.width // 2,
			console.height // 2 - 4,
			settings.title,
			fg=color.menu_title,
			alignment=tcod.CENTER,
		)
		console.print(
			console.width // 2,
			console.height -2,
			settings.creator,
			fg=color.menu_title,
			alignment=tcod.CENTER,
		)
		
		menu_width = 30
		for i, text in enumerate(
			[settings.str_new_game, settings.str_setup_game, settings.str_load_game, settings.str_quit_game]
		):
			console.print(
				console.width // 2,
				console.height // 2 - 2 + i,
				text.ljust(menu_width),
				fg=color.menu_text,
				bg=color.black,
				alignment=tcod.CENTER,
				bg_blend=tcod.BKGND_ALPHA(64),
			)
			
	def ev_keydown(
		self, event: tcod.event.KeyDown
	) -> Optional[input_handlers.BaseEventHandler]:
		if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
			raise SystemExit()
		elif event.sym == tcod.event.K_c:
			try:
				return input_handlers.MainGameEventHandler(load_game(settings.save_file))
			except FileNotFoundError:
				return input_handlers.PopupMessage(self, settings.str_file_not_found)
			except Exception as exc:
				traceback.print_exc()	# Print to stderr
				return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
		elif event.sym == tcod.event.K_n:
			return input_handlers.MainGameEventHandler(new_game())
		elif event.sym == tcod.event.K_s:
			return input_handlers.SetupRaceEventHandler(new_game())
		
		return None
