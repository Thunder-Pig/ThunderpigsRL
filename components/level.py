from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent

import settings

if TYPE_CHECKING:
	from entity import Actor
	

class Level(BaseComponent):
	""" Level component """
	parent: Actor
	
	def __init__(
		self,
		current_level: int = 1,
		current_xp: int = 0,
		turns: int = 0,
		level_up_base: int = 100,
		level_up_factor: int = 100,
		xp_given: int = 0,
		skill_points: int = 0,
	):
		self.current_level = current_level
		self.current_xp = current_xp
		self.total_xp = self.current_xp
		self.turns = turns
		self.level_up_base = level_up_base
		self.level_up_factor = level_up_factor
		self.xp_given = xp_given
		self.skill_points = skill_points
	
	@property
	def experience_to_next_level(self) -> int:
		""" Experiencelevel like AD&D3.5, but not exactly the same """
		return self.current_level * self.level_up_base + (self.current_level - 1) * self.level_up_base
		
	@property
	def requires_level_up(self) -> bool:
		""" Returns True if levelup is needed """
		return self.current_xp > self.experience_to_next_level
		
	def add_xp(self, xp: int) -> None:
		""" Adds XP """
		if xp == 0 or self.level_up_base == 0:
			return
			
		self.current_xp += xp
		self.total_xp += xp
		
		self.engine.message_log.add_message(settings.str_gain_xp.format(xp))
		
		""" Check if Levelup is necessary """
		if self.requires_level_up:
			self.engine.message_log.add_message(
				settings.str_advance_level.format(self.current_level + 1)
			)
			""" Increase the entities skill points """
			if self.parent.level:
				self.parent.clas.increase_skill_points()
			
			""" Increase the entities hitpoints """
			self.increase_hp()
			
	def increase_level(self) -> None:
		""" Increases Level and Resets XP. Called from the defs below """
		self.current_xp -= self.experience_to_next_level
		self.current_level += 1
	
	def increase_strength(self, amount: int = 1) -> None:
		self.parent.fighter.base_strength += amount
		self.engine.message_log.add_message(settings.str_inc_strength)
		self.increase_level()
		
	def increase_dexterity(self, amount: int = 1) -> None:
		self.parent.fighter.base_dexterity += amount
		self.engine.message_log.add_message(settings.str_inc_dexterity)
		self.increase_level()

	def increase_constitution(self, amount: int = 1) -> None:
		self.parent.fighter.base_constitution += amount
		self.engine.message_log.add_message(settings.str_inc_condition)
		self.increase_level()
		
	def increase_intelligence(self, amount: int = 1) -> None:
		self.parent.fighter.base_intelligence += amount
		self.engine.message_log.add_message(settings.str_inc_intelligence)
		self.increase_level()
		
	def increase_wisdom(self, amount: int = 1) -> None:
		self.parent.fighter.base_wisdom += amount
		self.engine.message_log.add_message(settings.str_inc_wisdom)
		self.increase_level()
	
	def increase_charisma(self, amount: int = 1) -> None:
		self.parent.fighter.base_charisma += amount
		self.engine.message_log.add_message(settings.str_inc_charisma)
		self.increase_level()

	def increase_hp(self, amount: int = 1) -> None:
		""" Increase (or decrease) HP based on entities class """
		if self.parent.clas:
			if self.parent.clas.clas == settings.str_barbarian:
				dice = 12
			elif self.parent.clas.clas in [settings.str_paladin, settings.str_fighter]:
				dice = 10
			elif self.parent.clas.clas in [settings.str_druid, settings.str_cleric, settings.str_monk, settings.str_ranger]:
				dice = 8
			elif self.parent.clas.clas in [settings.str_bard, settings.str_rouge]:
				dice = 6
			else:
				dice = 4
		else:
			dice = 4
				
		""" Roll 2 dice, use the better """
		tmp_1 = randint(1,dice) + (self.parent.fighter.constitution - 10) // 2
		tmp_2 = randint(1,dice) + (self.parent.fighter.constitution - 10) // 2
		
		if amount > 0:
			""" Increase HP """
			if tmp_1 > tmp_2:
				self.parent.fighter._max_hp += tmp_1
				self.parent.fighter._hp += tmp_1
			else:
				self.parent.fighter._max_hp += tmp_2
				self.parent.fighter._hp += tmp_2
		else:
			if tmp_1 > tmp_2:
				""" Decrease HP """
				self.parent.fighter._max_hp -= tmp_1
				self.parent.fighter._hp -= tmp_1
			else:
				self.parent.fighter._max_hp -= tmp_2
				self.parent.fighter._hp -= tmp_2

		return
