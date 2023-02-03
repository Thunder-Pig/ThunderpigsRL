from __future__ import annotations

from typing import TYPE_CHECKING

from random import randint

from components.base_component import BaseComponent			# Importiert Basisobjekt

import exceptions
import settings

if TYPE_CHECKING:
	pass

""" This modules stores all skill informations

Skill point not included yet

Availiable Skills (partially implemented):

Lockpicking:	Cost:	24 SkillP	- enables picking locks
Archery:		Cost:	24 SkillP	- shooting bows
Melee:			Cost:	02 SkillP	- Close Combat
Reading:		Cost:	12 SkillP	- reading
HealingMagic
AttackMagic
InfoMagic
Searching							- finding Traps and open doors

"""

class Skills(BaseComponent):
	parent: Entity
	
	def __init__(
		self,
		skills = [],
		forbit_skills = [],
		temp_skills = [],
		):
		
		self._skills = skills
		self._forbit_skills = forbit_skills
		self._temp_skills = temp_skills
	
	@property
	def skills(self) -> str:
		""" Return the permit skills stored in the skill component, if body is attached
		including the skills from the body """
		
		# Todo should be renamed to permit_skills
		
		temp_skills = []
		for skill in self._temp_skills:
				temp_skills.append(skill[0])
		if self.parent.body:
			return self._skills + self.parent.body.permit_skills + temp_skills
		else:
			return self._skills + temp_skills
	
	@property
	def forbit_skills(self) -> str:
		""" Return the forbit skills stored in the skills component, if body is attached
		including the forbit skills from the body """
		if self.parent.body:
			return self._forbit_skills
	
	def add_skill(self, skill: str, duration: Optional[int] = 0) -> None:
		""" Add temporary skills (when duration is provided) to self._temp_skills, others to self.skills """
		
		if duration > 0:
			self._temp_skills.append((skill, self.gamemap.engine.tick + duration),)
		else:
			self._skills.append(skill)
		return

	def remove_skill(self, skill: str, tick: Optional[int] = 0) -> None:
		""" Checks when temporary skill must be removed """

		""" TODO: rewrite """
		if tick > 0:
			for skill in self._temp_skills:
				if skill[1] == tick:
					self._temp_skills.remove(skill)
					if skill[0] == settings.str_fov_change:
						self.parent.fov = self.parent.previous_fov
						self.parent.previous_fov = 0
		else:
			if skill in self._skills:
				self._skills.remove(skill)
		return
	
	def requires_skill(self, skill: list) -> None:
		""" check if skill is availible """
		for i in skill:
			if i not in self.skills:
				raise exceptions.Impossible(f"{i} is not possible!")

