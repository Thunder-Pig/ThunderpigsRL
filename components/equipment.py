from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

import settings

if TYPE_CHECKING:
	from entity import Actor, Item
	
	
class Equipment(BaseComponent):
	parent: Actor
	
	def __init__(
		self,
		weapon: Optional[Item] = None,
		armor: Optional[Item] = None,
		hat: Optional[Item] = None,
		shield: Optional[Item] = None,
		boots: Optional[Item] = None,
		quiver: Optional[Item] = None,
		
	):
		self.weapon = weapon
		self.armor = armor
		self.hat = hat
		self.shield = shield
		self.boots = boots
		self.quiver = quiver
	
		
	@property
	def strength_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.strength_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.strength_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.strength_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.strength_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.strength_bonus
			
		return bonus
		
	@property
	def dexterity_bonus(self) -> int:
		bonus = 0
		max_bonus = []
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.dexterity_bonus
			max_bonus.append(self.weapon.equippable.max_dex_bonus)
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.dexterity_bonus
			max_bonus.append(self.armor.equippable.max_dex_bonus)
	
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.dexterity_bonus
			max_bonus.append(self.hat.equippable.max_dex_bonus)
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.dexterity_bonus
			max_bonus.append(self.shield.equippable.max_dex_bonus)
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.dexterity_bonus
			max_bonus.append(self.boots.equippable.max_dex_bonus)
		
		""" Kleinsten max_dex_bonus Wert zurückgeben """
		result = list(set(max_bonus))
		if 0 in result:
			result.remove(0)
		
		if len(result) > 0:
			# Wenn max_dex_bonus wert vorhanden, diesen ausgeben, falls kleiner als tat. bonus ist, sonst bonus ausgeben
			if bonus < min(result):
				return bonus
			else:
				return (min(result))
		else:
			# Wenn kein max_dex_bonus wert vorhanden, bonus ausgeben
			return bonus
		
	@property
	def constitution_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.constitution_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.constitution_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.constitution_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.constitution_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.constitution_bonus
			
		return bonus

	@property
	def intelligence_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.intelligence_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.intelligence_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.intelligence_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.intelligence_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.intelligence_bonus
			
		return bonus

	@property
	def wisdom_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.wisdom_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.wisdom_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.wisdom_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.wisdom_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.wisdom_bonus
			
		return bonus

	@property
	def charisma_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.charisma_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.charisma_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.charisma_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.charisma_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.charisma_bonus
			
		return bonus
		
	@property
	def armor_class_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.armor_class_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.armor_class_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.armor_class_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.armor_class_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.armor_class_bonus
			
		return bonus

	@property
	def initiative_bonus(self) -> int:
		bonus = 0
		
		if self.weapon is not None and self.weapon.equippable is not None:
			bonus += self.weapon.equippable.initiative_bonus
			
		if self.armor is not None and self.armor.equippable is not None:
			bonus += self.armor.equippable.initiative_bonus
		
		if self.hat is not None and self.hat.equippable is not None:
			bonus += self.hat.equippable.initiative_bonus
		
		if self.shield is not None and self.shield.equippable is not None:
			bonus += self.shield.equippable.initiative_bonus
			
		if self.boots is not None and self.boots.equippable is not None:
			bonus += self.boots.equippable.initiative_bonus
			
		return bonus

	@property
	def damage(self) -> str:
		damage = "0d0"
		
		if self.weapon is not None and self.weapon.equippable is not None:
			damage = self.weapon.equippable.damage
		
		return damage

	@property
	def criticals(self) -> int:
		criticals = [20,]
		if self.weapon is not None and self.weapon.equippable is not None:
			criticals = self.weapon.equippable.criticals
		return criticals

	@property
	def criticals_multi(self) -> int:
		criticals_multi = 2
		if self.weapon is not None and self.weapon.equippable is not None:
			criticals_multi = self.weapon.equippable.criticals_multi
		return criticals_multi



	def item_is_equipped(self, item: Item) -> bool:
		return self.weapon == item or self.armor == item or self.hat == item or self.shield == item or self.boots == item or self.quiver == item
		
	def unequip_message(self, item_name: str) -> None:
		self.parent.gamemap.engine.message_log.add_message(
			settings.str_unequip + f"{item_name}."
		)
		
	def equip_message(self, item_name: str) -> None:
		self.parent.gamemap.engine.message_log.add_message(
			settings.str_equip + f"{item_name}."
		)
		
	def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
		current_item = getattr(self, slot)
		if current_item is not None:
			self.unequip_from_slot(slot, add_message)
			
		setattr(self, slot, item)
		
		if add_message:
			self.equip_message(item.name)
			
	def unequip_from_slot(self, slot: str, add_message: bool) -> None:
		current_item = getattr(self, slot)
		
		if add_message:
			self.unequip_message(current_item.name)
			
		setattr(self, slot, None)
		
	def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
		# print(f"Angelegt: {equippable_item.name}, Wert: {equippable_item.value}, Gewicht: {equippable_item.weight} angelegt.")
		if (
			equippable_item.equippable
			and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
		):
			slot = "weapon"
			
			if (equippable_item.dimensions.hands == 2):
				if getattr(self, "shield") is not None:
					self.unequip_from_slot("shield", add_message)
			else:
				pass
				
			if getattr(self, "shield") is not None:
				if (self.shield.hands == 2):
					self.unequip_from_slot("shield", add_message)
				
		elif (
			equippable_item.equippable
			and equippable_item.equippable.equipment_type == EquipmentType.ARMOR
		):
			slot = "armor"
		elif (
			equippable_item.equippable
			and equippable_item.equippable.equipment_type == EquipmentType.HAT
		):
			slot = "hat"
		elif (
			equippable_item.equippable
			and equippable_item.equippable.equipment_type == EquipmentType.SHIELD
		):
			slot = "shield"	
			
			if (equippable_item.hands == 2):
				if getattr(self, "weapon") is not None:
					self.unequip_from_slot("weapon", add_message)
			else:
				pass
			
			if getattr(self, "weapon") is not None:
				if (self.weapon.hands == 2):
					self.unequip_from_slot("weapon", add_message)
			
		elif (
			equippable_item.equippable
			and equippable_item.equippable.equipment_type == EquipmentType.QUIVER
		):
			slot = "quiver"
			
		else:
			slot = "boots"
			
		if getattr(self, slot) == equippable_item:
			self.unequip_from_slot(slot, add_message)
		else:
			self.equip_to_slot(slot, equippable_item, add_message)
			
