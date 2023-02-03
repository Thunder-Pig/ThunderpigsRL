from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent

import settings
import color
import exceptions

if TYPE_CHECKING:
	pass

""" This is a generic lock object, can be attached to anything... """

"""
Difficulty based on AD&D3.5

very simple: 	20
moderate: 		25
good:			30
excellent: 		40

Locked state (bool) tells wether lock is closed or not, breakable (bool) if lock can be destroyed or not.
Breakable is not in use, therefore the object carrying the lock can be destroyed or not.
Maybe useful in the future, to lock something somewhere, or choose to destroy the lock (nothing else will break) or
to destroy e.g. the chest, which might brake something inside.

"""

class Lock(BaseComponent):
	""" A basic lock """
	parent: Entity
	
	def __init__(
		self,
		name = "Lock",
		long_name = "<Unknown Long lock name>",
		weight = 1,
		difficulty = 10,
		locked = True,
		breakable = False,
		):
		self._name = name
		self._long_name = long_name
		self._weight = weight
		self._difficulty = difficulty
		self._locked = locked
		self._breakable = breakable

	@property
	def name(self) -> str:
		""" Returns the shortname of the lock, used in the codebase """
		return self._name

	@property
	def long_name(self) -> str:
		""" Returns the longname of the lock, used for display """
		return self._long_name

	@property
	def weight(self) -> int:
		""" Returns the weight """
		return self._weight

	@property
	def difficulty(self) -> int:
		""" Returns the difficulty of the lock """
		return self._difficulty
		
	@property
	def locked(self) -> bool:
		""" Returns if the lock is locked or not """
		return self._locked
	
	@locked.setter
	def locked(self, state: bool) -> None:
		""" Sets the locked state """
		self._locked = state
		return
		
	@property
	def breakable(self) -> bool:
		""" Return wether the lock is breakable or not """
		return self._breakable

	def pick_lock(self, actor) -> bool:
		""" Pick the lock, return True if successful """
		self.entity = actor
		
		""" Check if actor is able to pick locks, just the ability, not the tool """
		if self.entity.skills:
			self.entity.skills.requires_skill(["Lockpicking"])
		
		""" Check for a suitable tool """

		""" TODO: Check for the best tool """
		tool_mod = 0		
		for i in range(len(self.entity.inventory.items)):
			if "Lockpick" in self.entity.inventory.items[i].kind:
				if self.entity.inventory.items[i].value > tool_mod:
					tool_mod = self.entity.inventory.items[i].value
		
		if tool_mod == 0:
			raise exceptions.Impossible(settings.str_no_lockpick_set)
		
		""" Try to pick """
		trial = randint(1,20) + self.entity.fighter.dexterity_modifier + tool_mod

		
		""" Check for success """
		if trial >= self.difficulty:
			if settings.str_trap in self.parent.name:
				""" Special message for traps """
				self.engine.message_log.add_message(settings.str_trap_unlocked.format(self.parent.name), color.player_atk)
				self.parent.usable.mark_unlocked()
			else:
				self.engine.message_log.add_message(settings.str_lockpick_success, color.player_atk)
			
			self.locked = False
			return True
		else:
			self.engine.message_log.add_message(settings.str_lockpick_fail, color.player_atk)
			return False
		
		
	def break_lock(self, actor) -> bool:
		""" Break the lock, return True if successful. Not implemented yet."""
		pass
		
		
