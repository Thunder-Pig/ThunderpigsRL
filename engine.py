from __future__ import annotations

import lzma
import pickle

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import exceptions

from message_log import MessageLog

import render_functions

if TYPE_CHECKING:
	from entity import Entity
	from entity import Actor
	from game_map import GameMap, GameWorld

class Engine:
	""" The Game engine holds the whole game, including the game_map """
	game_map: GameMap
	game_world: GameWorld
	
	def __init__(self, player: Actor):
		self.message_log = MessageLog()
		self.mouse_location = (0,0)
		self.player = player
		self.spawned_items = []				# List of all items spawned up to now
		self.tick = 0						# The game "counter"
	
	def save_as(self, filename: str) -> None:
		""" Save a instance of the engine as a compressed file. """
		save_data = lzma.compress(pickle.dumps(self))
		with open(filename, "wb") as f:
			f.write(save_data)
	
	def handle_enemy_turns(self) -> None:
		""" Handles the turns of the actors, excluding the player """
		for entity in set(self.game_map.actors) - {self.player}:
			
			""" Let the AI of the actor do whatever it should do, otherwise do nothing """
			if entity.ai:
				try:
					entity.ai.perform()
				except exceptions.Impossible:
					pass # Ignore impossible action exceptions from AI.
	

	def update_fov(self) -> None:
		""" Recompute the visible area based on players POV."""
		
		""" Count the Game Ticks """
		self.tick += 1
		
		""" Check if temporary Skills must be removed at the actual game tick """
		for item in self.player.skills._temp_skills:
			if item[1] == self.tick:
				self.player.skills.remove_skill(item, self.tick)
		
		""" Calculate the new FOV """
		self.game_map.visible[:] = compute_fov(
			self.game_map.tiles["transparent"],
			(self.player.x, self.player.y),
			radius=self.player.fov,
		)
		""" If a tile visible, add to explored tile list """
		self.game_map.explored |= self.game_map.visible
		
				
	def render(self, console: Console) -> None:
		""" Renders the game screen """

		""" Render map and message log """
		self.game_map.render(console)
		self.message_log.render(console=console, x=21, y=45, width=60, height=5)
		
		""" Render different infos """
		render_functions.render_bar(
			console=console,
			current_value = self.player.fighter.hp,
			maximum_value = self.player.fighter.max_hp,
			total_width = 20,
		)
		
		render_functions.render_dungeon_level(
			console=console,
			dungeon_level=self.game_world.current_floor,
			location=(0, 46),
		)
		
		render_functions.render_xp_points(
			console=console,
			xp_points=self.player.level.current_xp,
			location=(0,47),
		)
		
		""" The name of entities at a given mouse location """
		render_functions.render_names_at_mouse_location(
			console=console,
			x=21,
			y=44,
			engine=self,
		)
		
		""" Render used weapon """
		if self.player.equipment.weapon is not None:
			weapon = self.player.equipment.weapon.name
		else:
			weapon = "Hands"
		
		render_functions.render_weapon(
			console=console,
			location=(0,48),
			weapon =weapon,
			engine=self,
		)
		
		""" Render quivered missiles """
		if self.player.equipment.quiver is not None:
			quiver=str(self.player.equipment.quiver.value) +"x " + self.player.equipment.quiver.name
		else:
			quiver = "Empty"
		
		render_functions.render_quiver(
			console=console,
			location=(0,49),
			quiver=quiver,
			engine=self,
		)


