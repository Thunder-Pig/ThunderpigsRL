from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent

import settings

if TYPE_CHECKING:
	pass

""" The class informations of the entity """

class Clas(BaseComponent):
	parent: Entity
	
	def __init__(
		self,
		clas = "<Unknown>",
		):
		
		self._clas = clas
		self._previous_clas = None
	
	@property
	def clas(self) -> str:
		return self._clas
	
	@clas.setter
	def clas(self, clas: str) -> None:
		self._previous_clas = self._clas
		self._clas = clas
		return

	def adjust_fighter(self) -> None:
		""" When called adjust the fighter component to the race specific values """
		if self._previous_clas is not None:
			""" Remove the previous adjustments in case of changing the race """
			if self._previous_clas == settings.str_barbarian:
				pass
			elif self._previous_clas == settings.str_bard:
				pass
			elif self._previous_clas == settings.str_druid:
				pass
			elif self._previous_clas == settings.str_sourcerer:
				pass
			elif self._previous_clas == settings.str_fighter:
				pass
			elif self._previous_clas == settings.str_cleric:
				pass
			elif self._previous_clas == settings.str_wizard:
				pass
			elif self._previous_clas == settings.str_monk:
				pass
			elif self._previous_clas == settings.str_paladin:
				pass
			elif self._previous_clas == settings.str_rouge:
				pass
			elif self._previous_clas == settings.str_ranger:
				pass
			else:
				pass
		
		""" Adjust the fighter component to the given clas """			
		if self.parent.fighter:
			if self._clas == settings.str_barbarian:
				self.parent.fighter.base_bab = 1
				self.parent.fighter._max_hp = 12
				self.parent.fighter._hp = 12
			elif self._clas == settings.str_bard:
				self.parent.fighter._max_hp = 6
				self.parent.fighter._hp = 6
			elif self._clas == settings.str_druid:
				self.parent.fighter._max_hp = 8
				self.parent.fighter._hp = 8
			elif self._clas == settings.str_sourcerer:
				self.parent.fighter._max_hp = 4
				self.parent.fighter._hp = 4
			elif self._clas == settings.str_fighter:
				self.parent.fighter.base_bab = 1
				self.parent.fighter._max_hp = 10
				self.parent.fighter._hp = 10
			elif self._clas == settings.str_cleric:
				self.parent.fighter._max_hp = 8
				self.parent.fighter._hp = 8
			elif self._clas == settings.str_wizard:
				self.parent.fighter._max_hp = 4
				self.parent.fighter._hp = 4
			elif self._clas == settings.str_monk:
				self.parent.fighter._max_hp = 8
				self.parent.fighter._hp = 8
			elif self._clas == settings.str_paladin:
				self.parent.fighter.base_bab = 1
				self.parent.fighter._max_hp = 10
				self.parent.fighter._hp = 10
			elif self._clas == settings.str_rouge:
				self.parent.fighter._max_hp = 6
				self.parent.fighter._hp = 6
			elif self._clas == settings.str_ranger:
				self.parent.fighter.base_bab = 1
				self.parent.fighter._max_hp = 8
				self.parent.fighter._hp = 8
			else:
				pass
		return
		
		
	def increase_skill_points(self) -> None:
			""" Adjust the levelling system based on the entities class """
			""" Calculte the skill points the entity receives after level upgrade """

			""" NOTE: skillpoints not used at the moment """
			
			""" Check if level component is in use """
			if self.parent.level:
				
				""" High intelligence gives extra skillpoints """
				int_modifier = (self.parent.fighter.intelligence - 10) // 2	
				
				""" Humans gain more skillpoints than other races """
				if self.parent.race.race == settings.str_human:
					race_modifier = 4
				else:
					race_modifier = 0
				
				""" Set the skill points depending on the Entities Class, Intelligence and Race """	
				if self._clas in [settings.str_barbarian, settings.str_monk, settings.str_druid]:
					self.parent.level.skill_points = (4 + int_modifier + race_modifier) * 4
				
				elif self._clas in [settings.str_bard, settings.str_ranger]:
					self.parent.level.skill_points = (6 + int_modifier + race_modifier) * 4
				
				elif self._clas in [settings.str_sourcerer, settings.str_fighter, settings.str_cleric,
						settings.str_wizard, settings.str_paladin]:
					self.parent.level.skill_points = (2 + int_modifier + race_modifier) * 4
			
				elif self._clas == settings.str_rouge:
					self.parent.level.skill_points = (8 + int_modifier + race_modifier) * 4
				else:
					pass
				
			return
	

	
		
	
