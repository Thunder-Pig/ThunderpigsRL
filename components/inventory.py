from __future__ import annotations
from typing import List, TYPE_CHECKING

import settings

from components.base_component import BaseComponent

if TYPE_CHECKING:
	from entity import Actor, Item
	

class Inventory(BaseComponent):
	""" The inventory """
	parent: Actor
	
	def __init__(self, capacity: int):
		self.capacity = capacity
		self.items: List[Item] = []
		
	def drop(self, item: Item) -> None:
		""" Remove item from inventory and place on gamemap """
		
		self.items.remove(item)
		item.place(self.parent.x, self.parent.y, self.gamemap)
		self.engine.message_log.add_message(settings.str_drop_item.format(item.name))
		
