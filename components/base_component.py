from __future__ import annotations			# Annotations: -> arron in functions to specify return value
from typing import TYPE_CHECKING			# specify kwargs (name: str,)

if TYPE_CHECKING:
	from engine import Engine
	from entity import Entity
	from game_map import GameMap
	
class BaseComponent:
	""" Base component for everything """
	parent: Entity					
	
	@property
	def gamemap(self) -> GameMap:
		return self.parent.gamemap
	
	@property
	def engine(self) -> Engine:
		return self.gamemap.engine
		
