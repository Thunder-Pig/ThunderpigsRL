from __future__ import annotations
from typing import List, TYPE_CHECKING
from components.base_component import BaseComponent

import exceptions
import settings

if TYPE_CHECKING:
	from entity import Actor, Item
	
	
class Banking(BaseComponent):
	""" stores the money of the entity """
	parent: Actor
	
	def __init__(self,capital: int = 0):
		
		self.capital = capital
		
	def remove(self, amount):
		""" spend money if possible """
		if self.capital >= amount:
			return amount
		else:
			raise Exceptions.Impossible(settings.str_not_enough_money)
		
	def get_balance(self) -> int:
		""" Return capital balance """
		return self.capital
		
