from __future__ import annotations
from typing import TYPE_CHECKING
from exceptions import Impossible
from random import randint

from components.base_component import BaseComponent
from equipment_types import EquipmentType

import color
import settings

if TYPE_CHECKING:
	from entity import Item
	

class Equippable(BaseComponent):
	""" Equippable are Items which can be taken and equipped, like weapons and armor """
	parent: Item
	
	def __init__(
		self,
		equipment_type: EquipmentType,
		combat: str = "<Unknown>",
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		armor_class_bonus: int = 0,
		damage: str = "0d0",
		damage_type: list = ["<Unknown Damage>"],
		initiative_bonus: int = 0,
		criticals: int =[20,],
		criticals_multi: int = 2,
		max_dex_bonus: int = 0,
		maximum_range: int = 0,
	):
		self.equipment_type = equipment_type
		self.combat = combat
		self.strength_bonus = strength_bonus
		self.dexterity_bonus = dexterity_bonus
		self.constitution_bonus = constitution_bonus
		self.intelligence_bonus = intelligence_bonus
		self.wisdom_bonus = wisdom_bonus
		self.charisma_bonus = charisma_bonus
		self.armor_class_bonus = armor_class_bonus
		self.damage = damage
		self.damage_type = damage_type
		self.initiative_bonus = initiative_bonus
		self.criticals = criticals
		self.criticals_multi = criticals_multi
		self.max_dex_bonus = max_dex_bonus
		self.maximum_range = maximum_range


""" Ranged Weapons (under Construction) """
class Bow (Equippable):
	def __init__(
		self,
		combat: str = "Ranged",
		damage: str = "1d4",
		damage_type: list = [settings.str_piercing],
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		criticals: list = [20,],
		criticals_multi: int = 2,
		maximum_range: int = 0,

		) -> None:
		super().__init__(
			equipment_type=EquipmentType.WEAPON,
			combat = combat,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			damage_type=damage_type,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			criticals=criticals,
			criticals_multi=criticals_multi,
			maximum_range=maximum_range,
			)

class Arrow (Equippable):
	def __init__(
		self,
		criticals: list = [20,],
		criticals_multi: int = 2,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.QUIVER,
			)

	def initialize(self):
		""" Set the no of arrows of this batch randomly """
		self.parent.value = randint(1, 3)


""" Meelee Weapons """	
class Club (Equippable):
	def __init__(
		self,
		combat: str = "Melee",
		damage: str = "1d4",
		damage_type: list = [settings.str_bludgeoning],
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		criticals: list = [20,],
		criticals_multi: int = 2,

		) -> None:
		super().__init__(
			equipment_type=EquipmentType.WEAPON,
			combat = combat,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			damage_type = damage_type,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			criticals=criticals,
			criticals_multi=criticals_multi,
			)

			
class Sword(Equippable):
	def __init__(
		self,
		combat: str = "Melee",	
		damage: str = "0d0",
		damage_type: list = [settings.str_piercing, settings.str_slashing],
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		criticals: int = [20,],
		criticals_multi: int = 2,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.WEAPON,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			combat=combat,
			damage=damage,
			damage_type=damage_type,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			criticals=criticals,
			criticals_multi=criticals_multi,
			)

class Spear(Equippable):
	def __init__(
		self,
		damage: str = "1d6",
		damage_type: list = [settings.str_piercing],
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		criticals: int = [20,],
		criticals_multi: int = 2,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.WEAPON,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			damage_type=damage_type,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			criticals=criticals,
			criticals_multi = criticals_multi,
		)

class Axe(Equippable):
	def __init__(
		self,
		damage: str = "1d6",
		damage_type: list = [settings.str_slashing],
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		criticals: int = [20,],
		criticals_multi: int = 2,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.WEAPON,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			damage_type=damage_type,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			criticals=criticals,
			criticals_multi = criticals_multi,
		)



""" Armor """
class Armor(Equippable):
	def __init__(
		self,
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		damage: str = None,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		max_dex_bonus: int = 0,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.ARMOR,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			max_dex_bonus=max_dex_bonus,
			)

class Shield(Equippable):
	def __init__(
		self,
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		damage: str = None,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		max_dex_bonus: int = 0,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.SHIELD,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			max_dex_bonus=max_dex_bonus,
			)

class Hat(Equippable):
	def __init__(
		self,
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		damage: str = None,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		max_dex_bonus: int = 0,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.HAT,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			max_dex_bonus=max_dex_bonus,
			)

class Boots(Equippable):
	def __init__(
		self,
		strength_bonus: int = 0,
		dexterity_bonus: int = 0,
		constitution_bonus: int = 0,
		intelligence_bonus: int = 0,
		wisdom_bonus: int = 0,
		charisma_bonus: int = 0,
		damage: str = None,
		armor_class_bonus: int = 0,
		initiative_bonus: int = 0,
		) -> None:
		super().__init__(
			equipment_type=EquipmentType.BOOTS,
			strength_bonus=strength_bonus,
			dexterity_bonus=dexterity_bonus,
			constitution_bonus=constitution_bonus,
			intelligence_bonus=intelligence_bonus,
			wisdom_bonus=wisdom_bonus,
			charisma_bonus=charisma_bonus,
			damage=damage,
			armor_class_bonus=armor_class_bonus,
			initiative_bonus=initiative_bonus,
			)
