from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from random import randint
import copy

import actions
import color
import settings
import entity_factories
import components.inventory
import components.ai

from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
	ActionOrHandler,
	AreaRangedAttackHandler,
	SingleRangedAttackHandler,
	ChestInventoryHandler,
	MainGameEventHandler,
	AskSelectionHandler,
)
if TYPE_CHECKING:
	from entity import Actor, Item
		

class Consumable(BaseComponent):
	""" Consumable can be used """
	parent: Item
	
	def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
		""" Try to return the action for this item. """
		return actions.ItemAction(consumer, self.parent)
		
	def activate(self, action: actions.ItemAction) -> None:
		""" Invoke this items ability. action is the context for this activation. """
		raise NotImplementedError()

	def consume(self) -> None:
		""" Remove the consumed item from its inventory. """
		entity = self.parent
		inventory = entity.parent
		if isinstance(inventory, components.inventory.Inventory):
			inventory.items.remove(entity)

	def encrypt_name(self, encrypted_name):
		""" Checks if encrypted name exists, if not generates one and returns it """
		if encrypted_name == "":
			encrypted_name = self.parent.encrypted_name()
		self.parent.name = encrypted_name
		return encrypted_name


class MoneyConsumable(Consumable):
	def initialize(self):
		""" Initialize the Money to a random value between 1 and 10 """
		self.parent.value = randint(1, 10)

class GemConsumable(Consumable):
	""" This is the base for everthing like rock, gems, etc. """
	def get_action(self, consumer: Actor):
		return None

class ConfusionConsumalbe(Consumable):
	""" Used by the confusion scroll """
	def __init__(self, number_of_turns: int):
		""" Sets the number of turns the effect will take place """
		self.number_of_turns = number_of_turns
	
	def initialize(self):
		""" get the encrypted name at initialization """
		settings.str_confusion_scroll_name_enc = self.encrypt_name(settings.str_confusion_scroll_name_enc)

	def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
		""" The input handler to select the target """
		self.engine.message_log.add_message(settings.str_select_target, color.needs_target)
		return SingleRangedAttackHandler(
			self.engine,
			callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		return None
		
	def activate(self, action: actions.ItemAction) -> None:
		""" The actions taken when activated """
		consumer = action.entity
		target = action.target_actor
		
		""" Some checks before execution """
		if not self.engine.game_map.visible[action.target_xy]:
			raise Impossible(settings.str_target_not_visible)
		if not target:
			raise Impossible(settings.str_must_select_target)
		if target is consumer:
			""" Reveal the real name of the scroll, even if it can't be cast on yourself """
			for item in self.engine.spawned_items:
				if item.name == settings.str_confusion_scroll_name_enc:
					item.name = settings.str_confusion_scroll_name
			raise Impossible(settings.str_cant_confuse_yourself)

		""" If skills component is used, check wether the skill is availible """
		if consumer.skills:
			consumer.skills.requires_skill(["Reading"])
			""" Stop execution in case consumer is dumb """
			if "Dumb" in consumer.skills.skills:
				raise Impossible(settings.str_dumb)
		
		""" finally do everything to confuse someone """
		self.engine.message_log.add_message(
			f"{target.name}" + settings.str_target_confused,
			color.status_effect_applied,
		)

		target.ai = components.ai.ConfusedEnemy(
			entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
		)

		""" Change Name for every spawned item to decrypted name """
		for item in self.engine.spawned_items:
			if item.name == settings.str_confusion_scroll_name_enc:
				item.name = settings.str_confusion_scroll_name

		""" Remove scroll from inventory and the game """
		self.consume()

class DumbConsumable(Consumable):
	""" used by dumb scroll """
	def __init__(self, number_of_turns: int):
		""" Sets the number of turns the effect will take place """
		self.number_of_turns = number_of_turns

	def initialize(self):
		""" get the encrypted name at initialization """
		settings.str_dumb_scroll_enc = self.encrypt_name(settings.str_dumb_scroll_enc)

	def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
		""" The input handler to select the target """
		self.engine.message_log.add_message(settings.str_select_target, color.needs_target)
		return SingleRangedAttackHandler(self.engine, callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),)
		return None

	def activate(self, action: actions.ItemAction) -> None:
		""" Activate the scroll """
		consumer = action.entity
		target = action.target_actor

		""" Some checks before execution """
		if not self.engine.game_map.visible[action.target_xy]:
			raise Impossible(settings.str_target_not_visible)
		if not target:
			raise Impossible(settings.str_must_select_target)
		if not target.skills:
			raise Impossible(settings.str_cant_be_cast.format(self.parent.name, target.name))
		
		""" If skills component is used, check wether the skill is availible """
		if consumer.skills:
			consumer.skills.requires_skill(["Reading"])
			""" Stop execution in case consumer is dumb """
			if "Dumb" in consumer.skills.skills:
				raise Impossible(settings.str_dumb)
		
		if target is consumer:
			target.skills.add_skill("Dumb", self.number_of_turns)
			self.engine.message_log.add_message(settings.str_dumb, color.yellow)
		else:
			self.engine.message_log.add_message(f"{target.name} {settings.str_is_dumb}")
		
		""" Change Name for every spawned item to decrypted name """
		for item in self.engine.spawned_items:
			if item.name == settings.str_dumb_scroll_enc:
				item.name = settings.str_dumb_scroll

		""" Remove scroll from inventory and the game """
		self.consume()
			
class FovConsumable(Consumable):
	def __init__(self, number_of_turns: int, fov: int):
		""" Sets the number of turns the effect will take place and the size of the FOV"""
		self.number_of_turns = number_of_turns
		self.fov = fov

	def initialize(self):
		""" get the encrypted name at initialization """
		settings.str_vision_scroll_enc = self.encrypt_name(settings.str_vision_scroll_enc)

	def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
		""" The input handler to select the target """
		self.engine.message_log.add_message(settings.str_select_target, color.needs_target
		)
		return SingleRangedAttackHandler(self.engine, callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),)
		return None
		
	def activate(self, action: actions.ItemAction) -> None:
		""" Activate the scroll and do everything necessary """
		consumer = action.entity
		target = action.target_actor
		
		""" Some checks before execution """
		if not self.engine.game_map.visible[action.target_xy]:
			raise Impossible(settings.str_target_not_visible)
		if not target:
			raise Impossible(settings.str_must_select_target)
		if not target.skills:
			raise Impossible(settings.str_cant_be_cast.format(self.parent.name, target.name))
		
		""" If skills component is used, check wether the skill is availible """
		if consumer.skills:
			consumer.skills.requires_skill(["Reading"])		
			""" Stop execution in case consumer is dumb """
			if "Dumb" in consumer.skills.skills:
				raise Impossible(settings.str_dumb)
		
		""" Change the targets FOV, store previous FOV to convert back later """
		target.previus_fov = target.fov
		target.fov = self.fov

		""" If target is player """
		if target is consumer:		
			target.skills.add_skill(settings.str_fov_change, self.number_of_turns)
			if target.fov < target.previous_fov:
				self.engine.message_log.add_message(settings.str_vision_reduced, color.yellow)
			else:
				self.engine.message_log.add_message(settings.str_vision_improved, color.green)
		
		else:
			""" If cast onto others """
			if target.fov < target.previous_fov:
				""" Since only player has an FOV (at the moment), the blindness is performed by changing the entities
				AI to be confused """
				target.ai = components.ai.ConfusedEnemy(
					entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,)
				self.engine.message_log.add_message(settings.str_npc_vision_reduced.format(target.name))
			else:
				""" Improved FOV of NPCs does nothing, just printing a message. NPC don't have a FOV """
				self.engine.message_log.add_message(settings.str_npc_vision_improved.format(target.name))
		
		""" Change Name for every spawned item to decrypted name """
		for item in self.engine.spawned_items:
			if item.name == settings.str_vision_scroll_enc:
				item.name = settings.str_vision_scroll
		
		""" Remove scroll from inventory of consumer and the game """
		self.consume()

class LockpickConsumable(Consumable):
	""" Used by the lockpick scroll """
	def __init__(self):
		pass

	def initialize(self):
		""" get the encrypted name at initialization """
		settings.str_lockpick_scroll_enc = self.encrypt_name(settings.str_lockpick_scroll_enc)
		
	def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
		""" The input handler to select the target """
		self.engine.message_log.add_message(settings.str_select_target, color.needs_target)
		return SingleRangedAttackHandler(
			self.engine,
			callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		return None
		
	def activate(self, action: actions.ItemAction) -> None:
		""" Activate the scroll and do everything necessary """
		consumer = action.entity
		target = action.target_entity
		
		""" Some checks before execution """
		if consumer.skills:
			consumer.skills.requires_skill(["Reading"])
			""" Stop execution in case consumer is dumb """
			if "Dumb" in consumer.skills.skills:
				raise Impossible(settings.str_dumb)
		
		""" Change Name for every spawned item to decrypted name """
		for item in self.engine.spawned_items:
			if item.name == settings.str_lockpick_scroll_enc:
				item.name = settings.str_lockpick_scroll

		""" Check if target is locked, unlock it """
		if hasattr(target, "lock"):
			if target.lock.locked:
				target.lock.locked = False
				self.engine.message_log.add_message(settings.str_lockpick_success)				
				self.consume()
				return
			else:
				self.engine.message_log.add_message(settings.str_not_locked.format(target.name))
				return
		else:
			raise Impossible(settings.str_no_lock.format(target.name))
			return

class AmputationConsumable(Consumable):
	""" Consumable which will amputate an organ """
	def __init__(self):
		pass
		
	def initialize(self):
		""" get the encrypted name at initialization """
		settings.str_amputation_scroll_enc = self.encrypt_name(settings.str_amputation_scroll_enc)

	def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
		""" The input handler to select the target """
		self.engine.message_log.add_message(settings.str_select_target, color.needs_target
		)
		return SingleRangedAttackHandler(
			self.engine,
			callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		return None
		
	def activate(self, action: actions.ItemAction) -> None:
		""" Activate the scroll and do everything necessary """
		consumer = action.entity
		target = action.target_actor
		
		""" Some checks before execution """
		if not self.engine.game_map.visible[action.target_xy]:
			raise Impossible(settings.str_target_not_visible)
		if not target:
			raise Impossible(settings.str_must_select_target)
		
		if consumer.skills:
			consumer.skills.requires_skill(["Reading"])		
			""" Stop execution in case consumer is dumb """
			if "Dumb" in consumer.skills.skills:
				raise Impossible(settings.str_dumb)

		""" Change Name for every spawned item to decrypted name """
		for item in self.engine.spawned_items:
			if item.name == settings.str_amputation_scroll_enc:
				item.name = settings.str_amputation_scroll

		""" Amputate an organ by random if body component is availible """
		if target.body:
			organ = target.body.amputate_any()
			if organ is not None:
				self.engine.message_log.add_message(
					settings.str_amputate.format(target.name, organ.long_name), color.status_effect_applied)
				target.body.update_skills()
				self.consume()
			else:
				raise Impossible(settings.str_no_organ)
		else:
			raise Impossible(settings.str_no_amputate)


class HealingConsumable(Consumable):
	""" Healing Potion uses this """
	def __init__(self, amount: int):
		self.amount = amount
		
	def activate(self, action: actions.ItemAction) -> None:
		""" Do everything necessary for activation """
		consumer = action.entity
		
		""" Check if broken, if so give a negative ammount (means hurting) """
		if self.parent.dimensions:
			if self.parent.dimensions.broken == True:
				self.amount *= -1
		
		""" Calculate the HP to recover """
		amount_recovered = consumer.fighter.heal(self.amount)
		
		""" Generate the Message text """
		if amount_recovered > 0:
			self.engine.message_log.add_message(
				f"{amount_recovered}" + settings.str_hp_recovered + f"{self.parent.name}",
				color.health_recovered,
			)
			self.consume()

		elif consumer.fighter.max_hp == consumer.fighter.hp:
			raise Impossible(settings.str_health_full)
		else:
			self.engine.message_log.add_message(settings.str_use_broken.format(self.parent.name), color.health_recovered)
			self.consume()
			
class FireballDamageConsumable(Consumable):
	""" Fireball """
	def __init__(self, damage: int, radius: int):
		self.damage = damage
		self.radius = radius
		
	def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
		""" The input handler to select the target """
		self.engine.message_log.add_message(
			settings.str_select_target, color.needs_target
		)
		return AreaRangedAttackHandler(
			self.engine,
			radius = self.radius,
			callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		
	def activate(self, action: actions.ItemAction) -> None:
		target_xy = action.target_xy
		
		if not self.engine.game_map.visible[target_xy]:
			raise Impossible(settings.str_target_not_visible)
			
		targets_hit = False
		for actor in self.engine.game_map.actors:
			if actor.distance(*target_xy) <= self.radius:
				self.engine.message_log.add_message(
					f"{self.damage}" + settings.str_explosion + f"{actor.name}",
				)
				actor.fighter.take_damage(self.damage)
				targets_hit = True
		
		if not targets_hit:
			raise Impossible(settings.str_no_target_in_radius)
		self.consume()
		

class LightningDamageConsumable(Consumable):
	def __init__(self, damage: int, maximum_range: int):
		self.damage = damage
		self.maximum_range = maximum_range
		
	def activate(self, action: actions.ItemAction) -> None:
		""" Do everything necessary for activation """
		consumer = action.entity
		target = None
		closest_distance = self.maximum_range + 1.0
		
		""" Fireball checks for closest target and selects it """
		for actor in self.engine.game_map.actors:
			if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
				distance = consumer.distance(actor.x, actor.y)
				
				if distance < closest_distance:
					target = actor
					closest_distance = distance
		
		""" Fire if target found """		
		if target:
			self.engine.message_log.add_message(
				f"{self.damage}" + settings.str_lightning + f"{actor.name}",
			)
			target.fighter.take_damage(self.damage)
			self.consume()
		else:
			raise Impossible(settings.str_no_target_close_enough)
			
