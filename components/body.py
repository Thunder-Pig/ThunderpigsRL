from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint, sample
from exceptions import Impossible

from components.base_component import BaseComponent
from components.hand import Hand, Humanoid_Hand, Dragon_Wing
from components.foot import Foot, Humanoid_Foot, Doglike_Foot, Insect_Foot, Fin, Dragon_Foot
from components.organs import Ear, Mouth, Eye, Nose, Dragon_Nose

import settings

if TYPE_CHECKING:
	pass

""" Class holds the Body informations of the entity

self._kind : "Humanoid", "Doglike", "Insect", "Ghost", "Fish", "Dragon"
self._permit_skills: Skills that CAN be done
self._forbit_skills: Skills that CANT be done (no checks implemented so far)
self._parts: List of Body Parts

"""


class Body(BaseComponent):
	""" The Basic body, specifies the kind of body of the entity """
	parent: Entity
	
	def __init__(
		self,
		kind = None
		):
		
		self._previous_kind = None				# If body is transformed, the former body type is stored here
		self._kind = kind						# The actual body type
		self._parts: List(_Parts) = []			# The organs etc. attached to the body as a list
		self._permit_skills = []				# The skills that CAN be done combined from the body parts
		self._forbit_skills = []				# The skills that CANT be done combined from the body parts
		
		self.construct_body()					# A function that attaches the body parts
	
	@property
	def kind(self) -> str:
		""" Returns the kind of the body """
		return self._kind
	
	@kind.setter
	def kind(self, kind: str) -> None:
		""" Sets a new body kind, saves the previous kind (if any) and constructs the body """
		if self._kind:
			self._previous_kind = self._kind
		self._kind = kind
		self.construct_body()
	
	def get_organs(self) -> list:
		""" Returns a list of the organs the entity should normally have, ignoring number of organs per entity """
		
		if self.kind == "Humanoid":
			organs = [Humanoid_Hand(), Humanoid_Foot(), Ear(), Mouth(), Eye(), Nose()]
		
		elif self.kind == "Doglike":
			organs = [Doglike_Foot(), Ear(), Mouth(), Eye(), Nose()]
		
		elif self.kind == "Insect":
			organs = [Insect_Foot(), Ear(), Eye(), Mouth(), Nose()]
		
		elif self.kind == "Ghost":
			""" Ghost is not yet included """
			pass
		
		elif self.kind == "Fish":
			organs = [Fin(), Mouth(), Eye(), Nose()]
		
		elif self.kind == "Dragon":
			organs = [Dragon_Foot(), Dragon_Wings(), Ear(), Mouth(), Eye(), Dragon_Nose()]
		
		return organs
		
	def construct_body(self) -> None:
		""" Constructs the body of the entity, depending on body.kind
		
		TODO: Function should be improved and simplified in the future """
		
		self._parts = []
		
		if self.kind == "Humanoid":
			hand = Humanoid_Hand()
			foot = Humanoid_Foot()
			ear = Ear()
			mouth = Mouth()
			eye = Eye()
			nose = Nose()
			self._parts.append(hand)
			self._parts.append(hand)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(ear)
			self._parts.append(mouth)
			self._parts.append(eye)
			self._parts.append(nose)
		
		elif self.kind == "Doglike":
			foot = Doglike_Foot()
			ear = Ear()
			mouth = Mouth()
			eye = Eye()
			nose = Nose()
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(ear)
			self._parts.append(mouth)
			self._parts.append(eye)
			self._parts.append(nose)
		
		elif self.kind == "Insect":
			foot = Insect_Foot()
			ear = Ear()
			mouth = Mouth()
			eye = Eye()
			nose = Nose()
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(ear)
			self._parts.append(mouth)
			self._parts.append(eye)
			self._parts.append(nose)

		elif self.kind == "Ghost":
			""" Ghost is not included yet """
			pass
			
		elif self.kind == "Fish":
			foot = Fin()
			mouth = Mouth()
			eye = Eye()
			nose = Nose()
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(mouth)
			self._parts.append(eye)
			self._parts.append(nose)
		
		elif self.kind == "Dragon":
			foot = Dragon_Foot()
			hand = Dragon_Wing()
			mouth = Mouth()
			nose = Dragon_Nose()
			eye = Eye()
			ear = Ear()
			self._parts.append(hand)
			self._parts.append(hand)
			self._parts.append(foot)
			self._parts.append(foot)
			self._parts.append(ear)
			self._parts.append(mouth)
			self._parts.append(eye)
			self._parts.append(nose)
		else:
			print(f"Can't create the body of type {self.kind}.")
			Impossible(f"Can't create the body of type {self.kind}.")
		
		""" Update the skills to the body kind """
		self.update_skills()
	
	@property
	def parts(self) -> str:
		""" Returns a string of all body parts, each part at a new line """
		names = ""
		for i, part in enumerate(self._parts):
			names += part.name
			names += "\n"
		return names
	
	@property	
	def permit_skills(self) -> list:
		""" Returns a list of all permitted skills, duplicates (caused from several organs of same type like foot) removed """
		return list(set(self._permit_skills))

	@property
	def forbit_skills(self) -> list:
		""" Returns a list of all forbidden skills, duplicates (caused from several organs of same type like foot) removed """
		return list(set(self._forbit_skills))

	def update_skills(self) -> None:
		""" Updates the body skills, used after amputation or transplantation of body parts """
		
		""" Clear permit and forbid skills """
		self._permit_skills = []
		self._forbit_skills = []
		
		""" Check body parts for their permit/forbit skills """
		for i, part in enumerate(self._parts):
			if part.permit_skills:
				""" append each permit_skill to self._permit_skills """
				for j in part.permit_skills:
					self._permit_skills.append(j)
			if part.forbit_skills:
				""" do the same for the forbit_skills """
				for j in part.forbit_skills:
					self._forbit_skills.append(j)
					
		"""
		 If at least 2 body parts exist which allow melee assume that this can enable 2-handed and ranged attacks
		 should be overwritten by either forbit_skills of body parts or skills component in case this makes no sense
		 e.g. a rat cant do a ranged attack but is having 4 feet, each allowing melee
		
		TODO: Rethink if forbid_skills should be removed from permit or kept seperate (eg. forbidden melee, keep in
		permit and forbid list, or remove from permit list only)
		"""
		
		if (self._permit_skills.count("Melee")) >= 2:
			self._permit_skills.append("Ranged")
			self._permit_skills.append("2Hand")
		
	
	def amputate(self, name: str) -> None:
		""" Amputate a specific body part from the entity, remove the first hit of the given name """
		for i, part in enumerate(self._parts):
			if part.name == name:
				""" Remove if found and update skills """
				self._parts.remove(part)
				self.update_skills()
				return
		else:
			Impossible("No suitable organ to amputate")
	
	def amputate_any(self) -> None:
		""" Amputate a random organ from the entity """

		""" Get organ list """
		organs = self._parts
		if len(organs) >= 1:
			""" shuffle organ list, amputate the winner, update the skills and return the organ """
			for x in sample(organs, len(organs)):
				self._parts.remove(x)
				self.update_skills()
				return x
		else:
			return None
	
	
	def transplant(self, name: str) -> None:
		""" Transplant an organ to an entity """

		""" TODO: Not really doing what it should, e.g. total no of legs,... etc. rewrite it """
				
		""" get availible organs for the specific kind of entity """
		organs = self.get_organs()

		""" loop through all the availible organs """
		for i, part in enumerate(organs):
			""" if organ name corresponds to given string, attach organ """
			if part.name == name:
				""" attach organ and update the skills """
				self._parts.append(part)
				self.update_skills()
			else:
				""" no organ found for the given name """
				print("No suitable organ found")

