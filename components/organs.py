from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from components.base_component import BaseComponent

import settings

if TYPE_CHECKING:
	pass

""" Class holds the Body informations of the entity and enables different skills """
"""
Nose: Smelling
Eyes: Seeing, Reading
Mouth: Talking
Ears: Listening
"""


class Organ(BaseComponent):
	""" Base organ """
	parent: Entity
	
	def __init__(
		self,
		name = "Organ",
		long_name = "<Unknown Long Name Organ>",
		weight = 1,
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
		""" Returns the Shortname of the Organ, used in the codebase """
		return self._name

	@property
	def long_name(self) -> str:
		""" Returns the Longname of the Organ, used for display """
		return self._long_name

	@property
	def weight(self) -> int:
		""" Returns the weight of the Organ """
		return self._weight
		
	@property
	def permit_skills(self) -> str:
		""" Returns which skills are enabled when Organ is attached """
		return self._permit_skills
		
	@property
	def forbit_skills(self) -> str:
		""" Returns which skills are forbidden when organ is attached, usually nothing """
		return self._forbit_skills
		

class Ear(Organ):
	""" A basic ear """
	
	def __init__(
		self,
		long_name = "Ears",
		permit_skills = ["Listening"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills

class Eye(Organ):
	""" A Basic eye """
	
	def __init__(
		self,
		long_name = "Eyes",
		permit_skills = ["Reading", "Seeing"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills
		
class Mouth(Organ):
	""" A basic mouth """
	
	def __init__(
		self,
		long_name = "Mouth",
		permit_skills = ["Talking"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills

class Nose(Organ):
	""" A basic nose """
	
	def __init__(
		self,
		long_name = "Nose",
		permit_skills = ["Smelling"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills

class Dragon_Nose(Organ):
	""" A dragons nose, can cast fire. Cast_Fire not implemented yet """
	parent: Entity
	
	def __init__(
		self,
		long_name = "Dragon Nose",
		permit_skills = ["Smelling", "Cast_Fire"],
		forbit_skills = [],
		):
		super().__init__()
		self._long_name = long_name
		self._permit_skills = permit_skills
