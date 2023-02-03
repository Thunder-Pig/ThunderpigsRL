from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent

# import color
import settings

if TYPE_CHECKING:
	pass

""" Dimensions holds size, weight, material, price, needed hands and (Items-)HP as an component

Size: Based on AD&D3.5, stored as string, from gargantuan till fine
Weight: the weight in kg
Material: the material
Price: the price
Hands: hands needed for usage
Broken: Bool; broken or not
HP: The Items hitpoints based on size and material, necessary to enable destruction etc...

"""

class Dimensions(BaseComponent):
	""" Dimension component holds all physical aspects of the entity """
	parent: Entity
	
	def __init__(
		self,
		size = "<Unknown>",
		weight = 0,
		payload = 0,
		material = "<Unknown material>",
		hands = 1,
		price = 10,
		broken = False,
		hidden = False,	
		hp = 1,
		):
		
		self._size = size
		self._weight = weight
		self._payload = payload
		self._material = material
		self._hands = hands
		self._price = price
		self._broken = broken
		self._hidden = hidden
		self._hp = self.max_hp
	
	@property
	def size(self) -> str:
		""" Returns the size of the entity """
		return self._size
	
	@size.setter
	def size(self, size) -> None:
		""" Sets the size of the property """
		self._size = size

	@property
	def size_factor(self) -> int:
		""" Returns the size factor (AD&D3.5 based). Medium is size factor zero """
		if self.size == settings.str_colossal:
			size_factor = -8
		elif self.size == settings.str_gargantuan:
			size_factor = -4
		elif self.size == settings.str_huge:
			size_factor = -2
		elif self.size == settings.str_large:
			size_factor = -1
		elif self.size == settings.str_small:
			size_factor = 2
		elif self.size == settings.str_tiny:
			size_factor = 4
		elif self.size == settings.str_diminutive:
			size_factor = 6
		elif self.size == settings.str_fine:
			size_factor = 8
		else:
			size_factor = 0	# medium size
		return size_factor
	
	@property
	def payload(self) -> int:
		""" Returns the weight of the carried items """
		self._payload = 0
		if self.parent.inventory:
			number_of_items_in_inventory = len(self.parent.inventory.items)
			if number_of_items_in_inventory > 0:
				for i, item in enumerate(self.parent.inventory.items):
					if item.dimensions:
						self._payload += item.dimensions.weight
		return self._payload
	
	@property
	def max_payload(self) -> int:
		""" Returns the maximum payload """
		if self.parent.fighter:
			return self.parent.fighter.strength * 9
		else:
			return 90
	
	@property
	def payload_malus(self) -> float:
		""" Returns the payload malus as a float """
		return self.payload / self.max_payload
	
	@property
	def weight(self) -> int:
		""" Returns the weight (without payload) """
		return self._weight
	
	@weight.setter
	def weight(self, weight) -> None:
		""" Sets the weight """
		self._weight = weight

	@property
	def hands(self) -> int:
		""" Returns no of hands necessary for usage """
		return self._hands
	
	@property
	def price(self) -> int:
		""" Returns the price """
		return self._price
	
	@price.setter
	def price(self, price) -> None:
		""" Sets the price """
		self._price = price

	@property
	def broken(self) -> bool:
		""" Returns if broken or not """
		return self._broken
	
	@broken.setter
	def broken(self, broken: bool) -> None:
		""" Sets if broken or not """
		self._broken = broken

	@property
	def hidden(self) -> bool:
		""" Returns if hidden or not """
		return self._hidden

	@hidden.setter
	def hidden(self, hidden: bool) -> None:
		""" Setis if hidden or not """
		self._hidden = hidden
		self.parent.reveal()

	@property
	def material(self) -> str:
		""" Returns the material """
		return self._material
	
	@material.setter
	def material(self, material) -> None:
		""" Sets the material """
		self._material = material

	@property
	def hardness(self) -> int:
		""" Returns the hardness of an item based on the material """
		if self._material in [settings.str_paper, settings.str_ice]:
			return 0
		elif self._material == settings.str_glas:
			return 1
		elif self._material == settings.str_leather:
			return 2
		elif self._material == settings.str_wood:
			return 5
		elif self._material == settings.str_stone:
			return 8
		elif self._material == settings.str_metal:
			return 10
		elif self._material == settings.str_mithril:
			return 15
		elif self._material == settings.str_adamant:
			return 20
		else:
			# Unknown Material will get hardness 5 by default
			return 5
	
	@property	
	def max_hp(self) -> int:
		""" Returns the max_hp of the item, calculated on base of size and hardness """
		hardness = self.hardness
		size = (self.size_factor + 10) * (self.size_factor + 10) / 32
			
		max_hp = int(hardness * 10 / size)
		if max_hp <= 0:
			max_hp = 1
			
		return max_hp
	
	def decrease_hp(self, amount) -> None:
		""" Decrease the items HP, return true when no hp left """
		self._hp -= amount
		if self._hp <= 0:
			return True
		return False

