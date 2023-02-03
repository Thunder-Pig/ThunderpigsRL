from __future__ import annotations
from typing import TYPE_CHECKING

from components.base_component import BaseComponent			# Importiert Basisobjekt

import settings

if TYPE_CHECKING:
	pass


""" Class holds the Hand informations of the entity

Foot: A basic foot
Humanoid Foot: Walking, Jumping
Doglike Foot: Walking, Melee, Jumping
Insect Foot: Walking, Melee, Jumping
Dragon Foot: Walking
Fin: Swimming, Forbids Walking
"""

class Foot(BaseComponent):
	""" A basic foot """
	parent: Entity
	
	def __init__(
		self,
		name = "Foot",
		long_name = "<Unknown Long name Foot>",
		weight = 5,
		permit_skills = [],
		forbit_skills = [],
		):
		self._name = name
		self._long_name = long_name
		self._weight = weight
		self._permit_skills = permit_skills
		self._forbit_skills = forbit_skills

	@property
	def name(self) -> str:
		""" Returns the shortname of the foot, used in the codebase """
		return self._name

	@property
	def long_name(self) -> str:
		""" Returns the longname of the foot, used for display """
		return self._long_name

	@property
	def weight(self) -> int:
		""" Returns the weight of the foot """
		return self._weight

	@property
	def permit_skills(self) -> str:
		""" Returns which skills are enabled, when foot is attached """
		return self._permit_skills
		
	@property
	def forbit_skills(self) -> str:
		""" Returns which skills are forbidden, when foot is attached, usually nothing """
		return self._forbit_skills

class Humanoid_Foot(Foot):
	""" A Humanoid foot, having toes """
	def __init__(
		self,
		long_name = "Humanoid foot",
		permit_skills = ["Walking", "Jumping",],
		forbit_skills = ["Lava(justatest)"],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills
		self._forbit_skills = forbit_skills
		
class Doglike_Foot(Foot):
	""" A Doglike (animal) foot, having claws """
	def __init__(
		self,
		long_name = "Doglike foot (having claws)",
		permit_skills = ["Walking", "Melee", "Jumping"],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills

class Insect_Foot(Foot):
	""" A Insect foot, having claws """
	def __init__(
		self,
		long_name = "Insect foot (having claws)",
		permit_skills = ["Walking", "Melee", "Jumping"],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills


class Dragon_Foot(Foot):
	""" A Foot from a dragon """
	def __init__(
		self,
		long_name = "Dragon foot",
		permit_skills = ["Walking"],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills
		
class Fin(Foot):
	""" A fin of a fish, enables swimming"""
	def __init__(
		self,
		long_name = "Fin",
		permit_skills = ["Swimming"],
		forbit_skills = ["Walking"],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills
		self._forbit_skills = forbit_skills
