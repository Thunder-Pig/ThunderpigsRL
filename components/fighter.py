from __future__ import annotations
from typing import TYPE_CHECKING
from random import randint

from input_handlers import AskSelectionHandler
from actions import MeleeAction, SwapPlaceAction
from components.base_component import BaseComponent
from components.ai import HostileEnemy
from render_order import RenderOrder

import color
import settings

if TYPE_CHECKING:
	from entity import Actor

class Fighter(BaseComponent):
	""" The fighter component, enable battle of all kinds """
	parent: Actor
	
	def __init__(
		self,
		
		hp_range = (0,0),
		hp: int = 5,
		
		base_strength: int = 10,
		base_dexterity: int = 10, 
		base_constitution: int = 10,
		base_intelligence: int = 10,
		base_wisdom: int = 10,
		base_charisma: int = 10,
		base_armor_class: int = 1,
		base_initiative: int = 0,
		base_damage: str = "1d2",
		base_bab: int = 0,
		):
		
		self.base_strength = base_strength
		self.base_dexterity = base_dexterity
		self.base_constitution = base_constitution
		self.base_intelligence = base_intelligence
		self.base_wisdom = base_wisdom
		self.base_charisma = base_charisma
		
		self.base_armor_class = base_armor_class
		self.base_initiative = base_initiative
		self.base_damage = base_damage
		self.base_bab = base_bab
		
		self.hp_range = hp_range
		self._max_hp = hp
		self._hp = hp
	
	@property
	def hp(self) -> int:
		""" TODO: Check which formula is correct """
		return self._hp
		# return self._hp + (self.constitution - 10) // 2
	
	@property
	def max_hp(self) -> int:
		return self._max_hp  + (self.constitution - 10) // 2
		
	@hp.setter
	def hp(self, value: int) -> None:
		self._hp = max(0, min(value, self.max_hp))
		if self.hp == 0 and self.parent.ai:
			self.die()
	
	@property
	def strength(self) -> int:
		return self.base_strength + self.strength_bonus
		
	@property
	def dexterity(self) -> int:
		return self.base_dexterity + self.dexterity_bonus
	
	@property
	def constitution(self) -> int:
		return self.base_constitution + self.constitution_bonus
	
	@property
	def intelligence(self) -> int:
		return self.base_intelligence + self.intelligence_bonus
	
	@property
	def wisdom(self) -> int:
		return self.base_wisdom + self.wisdom_bonus
		
	@property
	def charisma(self) -> int:
		return self.base_charisma + self.charisma_bonus
		
	@property
	def armor_class(self) -> int:
		return self.base_armor_class + self.armor_class_bonus
		
	@property
	def initiative(self) -> int:
		return self.base_initiative + self.initiative_bonus
	
	@property
	def damage(self) -> str:
		""" Return either weapons damage or base (unarmed) damage """
		if self.parent.equipment.damage != "0d0":
			return self.parent.equipment.damage
		else:
			return self.base_damage
	
	@property
	def criticals(self) -> int:
		if self.parent.equipment.criticals is not None:
			return self.parent.equipment.criticals
		else:
			"""Return criticals at fighter class error """
			return 0
			
	@property
	def criticals_multi(self) -> int:
		if self.parent.equipment.criticals is not None:
			return self.parent.equipment.criticals_multi
		else:
			""" Return Criticals Multis at fighter class error """
			return 0
	
	def attack_value(self) -> int:
		""" Calculate the attack values, value between 1 and 20 """
		attack_dice = randint(1,20)
		
		""" Size Modifier """
		if self.parent.dimensions:
			size_modifier = self.parent.dimensions.size_factor
		else:
			size_modifier = 0
		
		attack_value = attack_dice + self.bab + self.strength_modifier + size_modifier
		
		if attack_value < 1:
			attack_value = 1
		if attack_value > 20:
			attack_value = 20
			
		return attack_dice, attack_value
	
	def hp_dealed(self) -> int:
		""" Calculate dealed HP based on form no_of_dice_x_faces_+_modifier(opt)
		e.g. 2d8+3 """ 
		no_of_dice, faces = self.damage.split("d")
		if "+" in faces:
			faces, modifier = faces.split("+")
		else:
			modifier = 0

		hit_points = 0
		for i in range(int(no_of_dice)):
			hit_points += (randint(1, int(faces) + int(modifier)))
				
		return hit_points
	
	@property
	def bab(self) -> int:
		""" Base attack bonus """
		return self.base_bab
	
	@property
	def strength_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.strength_bonus
		else:
			return 0
			
	@property
	def dexterity_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.dexterity_bonus
		else:
			return 0
	
	@property
	def constitution_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.constitution_bonus
			
	@property
	def intelligence_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.intelligence_bonus
		else:
			return 0
			
	@property
	def wisdom_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.wisdom_bonus
		else:
			return 0
	
	@property
	def charisma_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.charisma_bonus
		else:
			return 0
	
	@property
	def strength_modifier(self) -> int:
		return int(self.strength-10) // 2
	
	@property
	def dexterity_modifier(self) -> int:
		return int(self.dexterity-10) // 2
			
	@property
	def armor_class_bonus(self) -> int:
		""" Get size factor from dimensions component if availible """
		if self.parent.dimensions:
			size_factor = self.parent.dimensions.size_factor
		else:
			size_factor = 0
		
		if self.parent.equipment:
			""" Try to get armor class bonus from worn armor """
			return self.parent.equipment.armor_class_bonus + size_factor + self.dexterity_modifier
		else:
			""" Return only natural bonus """
			return size_factor + self.dexterity_modifier
			
	@property
	def initiative_bonus(self) -> int:
		if self.parent.equipment:
			return self.parent.equipment.initiative_bonus
		else:
			return 0

	def initialize(self) -> None:
		""" Initialize the HP to a random value """
		self._max_hp = randint(self.hp_range[0], self.hp_range[1])
		self._hp = self._max_hp
		
		return 0
	
	
	def die(self) -> None:
		""" Let the entity die....  RIP """
		if self.engine.player is self.parent:
			death_message = settings.str_died
			death_message_color = color.player_die
		else:
			death_message = f"{self.parent.name}" + settings.str_killed
			death_message_color = color.enemy_die
			self.engine.player.level.add_xp(self.parent.level.xp_given)

		self.parent.char = "%"
		self.parent.color = (color.red)
		self.parent.blocks_movement = False
		self.parent.ai = None
		self.parent.name = settings.str_remains + f"{self.parent.name}"
		self.parent.render_order = RenderOrder.CORPSE
		
		self.engine.message_log.add_message(death_message, death_message_color)

		
	def heal(self, amount: int) -> int:
		""" TODO: Rewrite """
		if self.hp == self.max_hp:
			return 0
			
		new_hp_value = self.hp + amount
		
		if new_hp_value > self.max_hp:
			new_hp_value = self.max_hp
			
		amount_recovered = new_hp_value - self.hp
		
		self.hp = new_hp_value
		
		return amount_recovered
		
	def take_damage(self, amount: int, damage_type = "<Unknown Damage>") -> None:
		""" TODO: Insert to check wether there are resistences against damage types """
		self.hp -= amount
		
	def get_action(self, target, actor) -> AskSelectionHandler:
		self.target = target
		self.actor = actor
		
		self.dx = self.target.x - self.actor.x
		self.dy = self.target.y - self.actor.y
		
		if self.target.attitute == "Hostile":
			
			return AskSelectionHandler(self.engine, actor, target,callback = self.interact, option1 = settings.str_attack_dialog,)
		elif self.target.attitute == "Friendly":
			return AskSelectionHandler(
				self.engine, actor, target,callback = self.interact,
				option1 = settings.str_attack_dialog, option2 = settings.str_swap_place,)

	def interact(self, choice) -> None:
		""" The Return from the input handler, to decide what to do... """
		if choice == 1:
			""" Attacking a friendly npc will make it hostile """
			if self.target.attitute == "Friendly":
				self.target.attitute = "Hostile"
				print(self.target.ai)
				self.target.ai = HostileEnemy(self.target)
			return MeleeAction(self.actor, self.dx, self.dy)
		else:
			return SwapPlaceAction(self.actor, self.target)

