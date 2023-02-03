from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent	

import settings


"""
Example component:

can be used as follows:

entity_factories.py:
from components import Dimensions
...
dagger = Item(
	dimensions = Dimensions(),
	
entity.py:
class item(
	def __init__(
		...
		dimensions = Optional[Dimensions] = None,
	):
	
	self.dimensions = dimensions
	if self.dimensions:
		self.dimensions.parent = self
"""

if TYPE_CHECKING:
	pass


class Race(BaseComponent):
	""" The race of the entity """
	parent: Entity
	
	def __init__(
		self,
		race = "<Unknown>",
		):
		
		""" To change the race and back again, _previous_race is used """
		self._race = race
		self._previous_race = None
	
	@property
	def race(self) -> str:
		""" Returns the race """
		return self._race
	
	@race.setter
	def race(self, race: str) -> None:
		""" Sets the race, stores the previous race """
		self._previous_race = self._race
		self._race = race
		return

	def adjust_fighter(self) -> None:
		""" When called adjust the fighter component to the race specific values """
		if self._previous_race is not None:
			""" Remove modifiers from previous race """
			if self._previous_race == settings.str_human:
				pass
			elif self._previous_race == settings.str_elv:
				self.parent.fighter.base_dexterity -= 2
				self.parent.fighter.base_constitution += 2
			elif self._previous_race == settings.str_dwarf:
				self.parent.fighter.base_constitution -= 2
				self.parent.fighter.base_charisma += 2
			elif self._previous_race == settings.str_gnome:
				self.parent.fighter.base_constitution -= 2
				self.parent.fighter.base_strength += 2
			elif self._previous_race == settings.str_halfling:
				self.parent.fighter.base_dexterity -= 2
				self.parent.fighter.base_strength += 2
			elif self._previous_race == settings.str_halfelv:
				pass
			elif self._previous_race == settings.str_halforc:
				self.parent.fighter.base_strength -= 2
				self.parent.fighter.base_charisma += 2
			else:
				pass
		
		""" Sets modifiers for the newly applied race """			
		if self.parent.fighter:
			if self._race == settings.str_human:
				pass
			elif self._race == settings.str_elv:
				self.parent.fighter.base_dexterity += 2
				self.parent.fighter.base_constitution -= 2
			elif self._race == settings.str_dwarf:
				self.parent.fighter.base_constitution += 2
				self.parent.fighter.base_charisma -= 2
			elif self._race == settings.str_gnome:
				self.parent.fighter.base_constitution += 2
				self.parent.fighter.base_strength -= 2
			elif self._race == settings.str_halfling:
				self.parent.fighter.base_dexterity += 2
				self.parent.fighter.base_strength -= 2
			elif self._race == settings.str_halfelv:
				pass
			elif self._race == settings.str_halforc:
				self.parent.fighter.base_strength += 2
				self.parent.fighter.base_charisma -= 2
			else:
				pass
		return
	

	
		
	
