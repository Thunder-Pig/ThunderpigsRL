from __future__ import annotations
from typing import TYPE_CHECKING
from textwrap import wrap

from components.base_component import BaseComponent

import settings

if TYPE_CHECKING:
	pass

""" Class holds the Description Text of the Entity """

class Description(BaseComponent):
	parent: Entity
	
	def __init__(
		self,
		description = "<Unknown Description Text>",
		
		):
		self._description = description
	
	@property
	def description(self) -> str:
		""" Returns the complete description text """
		return self._description
	
	@property
	def description_4lines(self) -> list:
		""" Returns the description , separatet into a 4-line list """
		return wrap(self._description, 34)
		
