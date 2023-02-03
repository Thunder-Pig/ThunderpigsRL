from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from random import randint

import os
import lzma
import pickle

import numpy as np	# type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
	from engine import Engine
	from entity import Entity

class GameMap:
	""" GameMap is where all the great stuff will happen """

	def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()):

		self.engine = engine
		self.width, self.height = width, height
		self.entities = set(entities)

		""" the map filled with tiles """
		self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
		
		""" visible are the tiles actually seen """
		self.visible = np.full((width, height), fill_value=False, order="F")
		""" explored are all tiles seen up to now """
		self.explored = np.full((width, height), fill_value=False, order="F")
		
		self.downstairs_location = (0,0)
		
	@property
	def gamemap(self) -> GameMap:
		return self
	
	@property
	def actors(self) -> Iterator[Actor]:
		""" Iterate over this maps living actors."""
		yield from (
			entity
			for entity in self.entities
			if isinstance(entity, Actor) and entity.is_alive
		)
	
	@property
	def items(self) -> Iterator[Item]:
		yield from (entity for entity in self.entities if isinstance(entity, Item))
		
	
	def get_blocking_entity_at_location(
		self, location_x: int, location_y: int,
	) -> Optional[Entity]:
		for entity in self.entities:
			if (
				entity.blocks_movement
				and entity.x == location_x
				and entity.y == location_y
			):	
				return entity
		
		return None
	
	def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
		for actor in self.actors:
			if actor.x == x and actor.y == y:
				return actor
			
		return None

	def get_entity_at_location(self, x: int, y: int) -> Optional[Entity]:
		for item in self.entities:
			if item.x == x and item.y == y:
				return item
			
		return None	
	
		
	def in_bounds(self, x:int, y:int) -> bool:
		"""Return True if x and y are inside of the bounds of this map."""
		return 0 <= x < self.width and 0 <= y < self.height

	def render(self, console: Console) -> None:
		""" Renders the map.
		
		If a tile is in the visible array, then draw it with the light colors. If it
		is explored, draw it dark, otherwise the default is shroud
		
		"""
		console.tiles_rgb[0 : self.width, 0 : self.height] = np.select(
			condlist = [self.visible, self.explored],
			choicelist = [self.tiles["light"], self.tiles["dark"]],
			default = tile_types.SHROUD,
		)
		
		""" Decide what will be rendered on top of what """
		entities_sorted_for_rendering = sorted(
			self.entities, key=lambda x: x.render_order.value
		)
		
		""" Render entities """
		for entity in entities_sorted_for_rendering:
			""" only render entities inside the players FOV """
			if self.visible[entity.x, entity.y]:
				console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)


class GameWorld:
	""" Holds the settings for the GameMap, and generates new maps when using stairs. """
	
	def __init__(
		self,
		*,
		engine: Engine,
		map_width: int,
		map_height: int,
		max_rooms: int,
		room_min_size: int,
		room_max_size: int,
		current_floor: int = 0,
	):
		self.engine = engine
	
		self.map_width = map_width
		self.map_height = map_height
		
		self.max_rooms = max_rooms
		
		self.room_min_size = room_min_size
		self.room_max_size = room_max_size
		
		self.current_floor = current_floor


	def generate_floor_drunkjard(self) -> None:
		""" Generates a dungeon floor based on drunkjards walk """
		from procgen import generate_drunkjard

		self.current_floor += 1

		self.engine.new_map = generate_drunkjard(
			map_width = self.map_width,
			map_height = self.map_height,
			steps_min = 2,								# straight steps after each turn
			steps_max = 4,
			walks_min = 15,								# no of turns on each walk
			walks_max = 25,
			drunks_min = 10,							# no of walks from different starting points
			drunks_max = 30,
			engine = self.engine,
			current_floor = self.current_floor
		)

		""" The actual floor is game_map, the next floor ist new_map. At the beginning only acutal floor is valid """
		if self.current_floor == 1:
			self.engine.game_map = self.engine.new_map
		else:
			pass

	def generate_floor_rectangular(self) -> None:
		""" Generates a dungeon by connecting rectangular rooms """
		from procgen import generate_dungeon
		
		self.current_floor += 1

		self.engine.new_map = generate_dungeon(
			max_rooms = self.max_rooms,
			room_min_size = self.room_min_size,
			room_max_size = self.room_max_size,
			map_width = self.map_width,
			map_height = self.map_height,
			engine = self.engine,
			current_floor = self.current_floor,
		)

		if self.current_floor == 1:
			self.engine.game_map = self.engine.new_map
		else:
			pass

	def generate_floor(self) -> None:
		""" Called whenever a new floor is necessary, chooses wether drunkjard or rectangular floor will be created """
		
		x = randint(1,4)	# 25% chance to generate drunkjard floor
		
		if x == 1:
			self.generate_floor_drunkjard()
			#self.generate_floor_rectangular()
		else:
			#self.generate_floor_drunkjard()
			self.generate_floor_rectangular()

	def load_previous_floor(self) -> None:
		""" loads the previous floor when going upstairs """
		
		self.current_floor -= 1
		filename = str(self.current_floor) + ".lev"
		
		""" Open floor and place player """
		with open(filename, "rb") as f:
			self.engine.new_map = pickle.loads(lzma.decompress(f.read()))
		
		self.engine.player.place(self.engine.new_map.downstairs_location[0], self.engine.new_map.downstairs_location[1], self.engine.new_map)

		""" Save the actual dungeon level """
		filename = str(self.engine.game_world.current_floor + 1) + ".lev"
		save_level = lzma.compress(pickle.dumps(self.engine.game_map))
		with open(filename, "wb") as f:
			f.write(save_level)

		""" Switch the game_map & game engine to the new floor """
		self.engine.game_map = self.engine.new_map
		self.engine.game_map.engine = self.engine
		assert self.engine.game_map.engine is self.engine
		self.engine.update_fov()
		

	def load_next_floor(self) -> None:
		""" loads the next floor when going downstarts. UPDATE: Make one function for both """
		self.current_floor += 1
		filename = str(self.current_floor) + ".lev"
		with open(filename, "rb") as f:
			self.engine.new_map = pickle.loads(lzma.decompress(f.read()))
		
		self.engine.player.place(self.engine.new_map.upstairs_location[0], self.engine.new_map.upstairs_location[1], self.engine.new_map)

		""" Save the previous dungeon level """
		filename = str(self.engine.game_world.current_floor - 1) + ".lev"
		save_level = lzma.compress(pickle.dumps(self.engine.game_map))
		with open(filename, "wb") as f:
			f.write(save_level)


		self.engine.game_map = self.engine.new_map
		self.engine.game_map.engine = self.engine
		assert self.engine.game_map.engine is self.engine
		self.engine.update_fov()
		
		
		
	def load_floor(self, floor_number: int, direction: str) -> None:
		# Loads floor by floor number as new_map  
		
		self.current_floor = floor_number
		
		""" Load floor if exists, otherwise create new floor """
		if os.path.isfile(str(floor_number) + ".lev"):
			filename = str(floor_number) + ".lev"
			with open(filename, "rb") as f:
				self.engine.new_map = pickle.loads(lzma.decompress(f.read()))
		else:
			self.engine.new_map = self.engine.game_world.generate_new_floor()
		
		""" Place player accordingly to travel direction """
		if direction == "up":
			place_x = self.engine.new_map.downstairs_location[0]
			place_y = self.engine.new_map.downstairs_location[1]
		elif direction == "down":
			place_x = self.engine.new_map.upstairs_location[0]
			place_y = self.engine.new_map.upstairs_location[1]
			
		self.engine.player.place(place_x, place_y, self.engine.new_map)
		assert self.engine.player not in self.engine.game_map.entities	# Checks wether player is deleted from old map

		""" Save the actual dungeon floor """
		filename = str(self.engine.game_world.current_floor - 1) + ".lev"
		save_level = lzma.compress(pickle.dumps(self.engine.game_map))
		with open(filename, "wb") as f:
			f.write(save_level)
		
		""" Set up new floor as actual floor """
		self.engine.game_map = self.engine.new_map
		self.engine.game_map.engine = self.engine
		assert self.engine.game_map.engine is self.engine
		self.engine.update_fov()

