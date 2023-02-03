from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent

import settings

if TYPE_CHECKING:
	pass

""" This class is holding hands


Hand: Basic hand as a basis
Humanoid Hand: Enables Melee, Manipulating, Lockpicking
Dragon Wing: Enables Melee, Flying
"""

class Hand(BaseComponent):
	""" Generic hand """
	parent: Entity
	
	def __init__(
		self,
		name = "Hand",
		long_name = "<Unknown Long name Hand>",
		weight = 5,
		permit_skills = [],
		forbit_skills = [],
		):
		self._name = name
		self._weight = weight
		self._permit_skills = permit_skills
		self._forbit_skills = forbit_skills
	
	@property
	def name(self) -> str:
		""" Returns the Shortname of the hand, used in the codebase """
		return self._name
	
	@property
	def long_name(self) -> str:
		""" Returns the Longname of the hand, used for display """
		return self._long_name
		
	@property
	def weight(self) -> int:
		""" Returns the weight of the hand """
		return self._weight
		
	@property
	def permit_skills(self) -> str:
		""" Returns which skills are enabled when hand is attached """
		return self._permit_skills
		
	@property
	def forbit_skills(self) -> str:
		""" Returns which skills are forbidden when hand is attached, usally nothing """
		return self._forbit_skills

class Humanoid_Hand(Hand):
	""" A Humanoid-like hand, having fingers and a thumb """
	def __init__(
		self,
		long_name = "Humanoid hand",
		permit_skills = ["Melee", "Manipulating", "Lockpicking"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills

class Dragon_Wing(Hand):
	""" A dragon wing, having claws and and enables flying """
	def __init__(
		self,
		long_name = "Dragon Wing (having claws)",
		permit_skills = ["Melee", "Flying"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills
