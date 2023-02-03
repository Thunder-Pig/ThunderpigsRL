from enum import auto, Enum


""" defines which char is displayed on top of which """
class RenderOrder(Enum):
	CORPSE = auto()
	ITEM = auto()
	ACTOR = auto()
