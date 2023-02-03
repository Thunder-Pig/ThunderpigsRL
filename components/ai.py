from __future__ import annotations

import random

from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction
from components.base_component import BaseComponent

import settings

if TYPE_CHECKING:
	from entity import Actor

class BaseAI(Action):
	""" Basic AI """
	entity: Actor

	def perform(self) -> None:
		raise NotImplementedError()
		
	def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
		""" Compute and return a path the the target position.
		
		If there is no valid path then returns an empty list.
		"""
		
		""" Copy the walkable array """
		cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)
		
		for entity in self.entity.gamemap.entities:
			# Check that an entity blocks movement and the cost isn't zero (blocking.)
			if entity.blocks_movement and cost[entity.x, entity.y]:
				# Add to the cost of a blocked position.
				# A lower number means more enemies will crowd behind each other in
				# hallways. A higher number means enemies will take longer paths in
				# order to surround the player.
				cost[entity.x, entity.y] += 10
				
		""" create a graph from the cost array and pass that graph to a new pathfinder """
		graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
		pathfinder = tcod.path.Pathfinder(graph)
		
		""" Set start position """
		pathfinder.add_root((self.entity.x, self.entity.y))
		
		""" Compute the path to the destination and remove the starting point """
		path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()
		
		""" Convert from List[List[int]] to List[Tuple[int, int]] """
		return [(index[0], index[1]) for index in path]


class ConfusedEnemy(BaseAI):
	"""
	A confused enemy will stumble around aimlessly for a given number of turns, then revert
	back to its previous AI. If an actor occupies a tile it is randomly moving into, it will attack.

	"""
	def __init__(
		self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
	):
		super().__init__(entity)
		
		self.previous_ai = previous_ai
		self.turns_remaining = turns_remaining
		
	def perform(self) -> None:
		""" Revert the AI back to original if the effect has run its course """
		if self.turns_remaining <= 0:
			self.engine.message_log.add_message(settings.str_no_longer_confused.format(self.entity.name))
			self.entity.ai = self.previous_ai
		else:
			""" If confused pick random direction """
			direction_x, direction_y = random.choice(
				[
					(-1, -1),	# Northwest
					(0, -1),	# North
					(1, -1),	# Northeast
					(-1, 0),	# West
					(1, 0),		# East
					(-1, 1),	# Southeast
					(0, 1),		# South
					(1, 1),		# Southeast
				]
			)
			
			self.turns_remaining -= 1
			
			""" The actor will either try to move or attack in the chosen random
			direction. Its possible the actor will just bump into the wall, wasting
			a turn. """
			return BumpAction(self.entity, direction_x, direction_y,).perform()

class FriendlyAI(BaseAI):
	"""
	A friendly AI will just wander around.
	"""

	def __init__( self, entity: Actor):
		super().__init__(entity)
		
	def perform(self) -> None:
		""" Wander around """
		
		direction_x, direction_y = random.choice(
			[
				(-1, -1),	# Northwest
				(0, -1),	# North
				(1, -1),	# Northeast
				(-1, 0),	# West
				(1, 0),		# East
				(-1, 1),	# Southeast
				(0, 1),		# South
				(1, 1),		# Southeast
			]
		)
		
		return MovementAction(self.entity, direction_x, direction_y,).perform()

class HostileEnemy(BaseAI):
	""" A attacking enemy """
	def __init__(self, entity: Actor):
		super().__init__(entity)
		self.path: List[Tuple[int, int]] = []
		
	def perform(self) -> None:
		""" Get player as target and calculate distance """
		target = self.engine.player
		dx = target.x - self.entity.x
		dy = target.y - self.entity.y
		distance = max(abs(dx), abs(dy)) # Chebyshev distance
		
		""" Only become active when self is in visible part of the map """
		if self.engine.game_map.visible[self.entity.x, self.entity.y]:
			if distance <= 1:
				return MeleeAction(self.entity, dx, dy).perform()
				
			self.path = self.get_path_to(target.x, target.y)
			
		if self.path:
			""" Move closer to player """
			dest_x, dest_y = self.path.pop(0)
			
			return MovementAction(self.entity, dest_x - self.entity.x, dest_y - self.entity.y,).perform()
			
		return WaitAction(self.entity).perform()

class ShopAI(BaseAI):
	""" Shop AI is in principle a non attacking NPC which follows the player """
	def __init__(self, entity: Actor):
		super().__init__(entity)
		self.path: List[Tuple[int, int]] = []
		
	def perform(self) -> None:
		""" Get player as target and calculate distance """
		target = self.engine.player
		dx = target.x - self.entity.x
		dy = target.y - self.entity.y
		distance = max(abs(dx), abs(dy)) # Chebyshev distance
		
		""" Only become active when self is in visible part of the map """
		if self.engine.game_map.visible[self.entity.x, self.entity.y]:
			if distance <= 1:
				return WaitAction(self.entity).perform()
				
			self.path = self.get_path_to(target.x, target.y)
			
		if self.path:
			""" Move closer to the player """
			dest_x, dest_y = self.path.pop(0)

			""" Update the path after it is generated the first time to ensure that changes in the path will be processed """
			self.path = self.get_path_to(target.x, target.y)

			return MovementAction(self.entity, dest_x - self.entity.x, dest_y - self.entity.y,).perform()			
			
		return WaitAction(self.entity).perform()
