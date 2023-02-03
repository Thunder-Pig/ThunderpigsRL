from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING
from random import randint

import os
import lzma
import pickle

import color
import exceptions
import tile_types
import settings

from game_map import GameMap, GameWorld
import tile_types

if TYPE_CHECKING:
	from engine import Engine
	from entity import Actor, Entity, Item

class Action:
	""" The prototype for all actions """
	def __init__(self, entity: Actor) -> None:
		super().__init__()
		self.entity = entity
		
	@property
	def engine(self) -> Engine:
		""" Return the engine this action belongs to."""
		return self.entity.gamemap.engine
		
	def perform(self) -> None:
		"""Perform this action with the objects needed to determine its scope.
		
		self.engine is the scope this action is being performed in.
		self.entity is the object performing the action
		
		This method must be overridden by Action subclasses.
		"""
		raise NotImplementedError()

class PickupAction(Action):
	""" Pickup an item and add it to the inventory, if there is room for it. """
	
	def __init__(self, entity: Actor):
		super().__init__(entity)
		
	def perform(self) -> None:
		actor_location_x = self.entity.x
		actor_location_y = self.entity.y
		inventory = self.entity.inventory
		
		for item in self.engine.game_map.items:
			if actor_location_x == item.x and actor_location_y == item.y:
				
				""" Add money to the entities coins, not the inventory, if banking component is attached """
				if item.name == settings.str_money:
					if self.entity.banking:
						self.entity.banking.capital += item.value
						self.engine.game_map.entities.remove(item)
						self.engine.message_log.add_message(settings.str_pickup + f" {item.value} {item.name}!")
						return
					else:
						pass
				
				elif item.name == settings.str_arrow:
					""" Check wether arrows are already picked up, if so, increase number, otherwise take new """ 

					for i in range(len(inventory.items)):
						if item.name in inventory.items[i].name:
							inventory.items[i].value += item.value
							self.engine.message_log.add_message(settings.str_pickup + f" {item.value} {item.name}!")
							self.engine.game_map.entities.remove(item)
							return
						else:
							""" If arrows are picked up the first time, take them as normal """
							pass
						
				""" Check if there is space in the inventory """
				if len(inventory.items) >= inventory.capacity:
					raise exceptions.Impossible(settings.str_inventory_full)
				
				""" Pick up item and add to the inventory """	
				self.engine.game_map.entities.remove(item)
				item.parent = self.entity.inventory
				inventory.items.append(item)
				self.engine.message_log.add_message(settings.str_pickup + f" {item.name}!")

				return
				
		raise exceptions.Impossible(settings.str_nothing_to_pickup)
		

class ItemAction(Action):
	def __init__(
		self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
	):
		super().__init__(entity)
		self.item = item
		if not target_xy:
			target_xy = entity.x, entity.y
		self.target_xy = target_xy
	
	@property
	def target_actor(self) -> Optional[Actor]:
		""" Return the actor at this action destination. """
		return self.engine.game_map.get_actor_at_location(*self.target_xy)
	
	@property
	def target_entity(self) -> Optional[Entity]:
		""" Return the entity at this action destination. """
		return self.engine.game_map.get_entity_at_location(*self.target_xy)	
		
	def perform(self) -> None:
		""" Invoke the items ability, this action will be given to provide context."""
		if self.item.consumable:
			self.item.consumable.activate(self)
				

class DropItem(ItemAction):
	""" Drop an item from the inventory to the floor """
	def perform(self) -> None:
		if self.entity.equipment.item_is_equipped(self.item):
			self.entity.equipment.toggle_equip(self.item)
			
		self.entity.inventory.drop(self.item)
		

class EquipAction(Action):
	""" Equip an item from the inventory to the entities slot """
	def __init__(self, entity: Actor, item: Item):
		super().__init__(entity)
		
		self.item = item
	
	def perform(self) -> None:
		self.entity.equipment.toggle_equip(self.item)

class WaitAction(Action):
	""" Just do nothing except waiting """
	def perform(self) -> None:
		pass

class TakeStairsAction(Action):
	def perform(self) -> None:
		""" Take the stairs, if any exist at the entitys location. """
		
		""" Check if player on downstairs location """
		if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
			""" Try to load floor, otherwise create new one """
			if os.path.exists(str(self.engine.game_world.current_floor + 1) + ".lev"):
				self.engine.game_world.load_next_floor()
			else:
				self.engine.game_world.generate_floor()
				
				""" Place player on newly created map """
				place_x = self.engine.new_map.upstairs_location[0]
				place_y = self.engine.new_map.upstairs_location[1]
				self.engine.player.place(place_x, place_y, self.engine.new_map)

				""" Check if player is removed from current map """
				assert self.engine.player not in self.engine.game_map.entities

				""" Save actual dungeon level """
				filename = str(self.engine.game_world.current_floor -1) + ".lev"
				save_level = lzma.compress(pickle.dumps(self.engine.game_map))
				with open(filename, "wb") as f:
					f.write(save_level)

				""" Set up generated map as the active one """
				self.engine.game_map = self.engine.new_map
				self.engine.game_map.engine = self.engine

				# check wether engine is valid
				assert self.engine.game_map.engine is self.engine

				self.engine.update_fov()
			
			self.engine.message_log.add_message(settings.str_downstairs, color.descend)

		elif (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
			""" Check if player on upstairs location """			

			""" Upwards level are always present, so no need to generate new ones """			
			if self.engine.game_world.current_floor == 1:
				"""Dont' allow the player to leave the dungeons """
				raise exceptions.Impossible(settings.str_back_to_light)
			else:
				""" Loading the previous floor and go upwards """
				self.engine.game_world.load_previous_floor()
				self.engine.message_log.add_message(settings.str_upstairs, color.descend)

		else:
			""" No stairs """
			raise exceptions.Impossible(settings.str_no_stairs)
			

class ActionWithDirection(Action):
	""" Actions which need a direction to work """
	def __init__(self, entity: Actor, dx: int, dy: int):
		super().__init__(entity)
		
		self.dx = dx
		self.dy = dy
	
	@property
	def dest_xy(self) -> Tuple[int, int]:
		""" Returns this actions destination. """
		return self.entity.x + self.dx, self.entity.y + self.dy
		
	@property
	def blocking_entity(self) -> Optional[Entity]:
		""" Return the blocking entity at this actions destination """
		return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
		
	@property
	def target_actor(self) -> Optional[Entity]:
		""" Return the actor at this actions destination. """
		return self.engine.game_map.get_actor_at_location(*self.dest_xy)
		

	def perform(self) -> None:
		raise NotImplementedError()

class SwapPlaceAction(Action):
	""" Swap places with other entity"""
	def __init__(self, actor, target):
		self.actor = actor
		self.target = target

	def perform(self) -> None:
		self.actor.x, self.target.x = self.target.x, self.actor.x
		self.actor.y, self.target.y = self.target.y, self.actor.y

		
class MeleeAction(ActionWithDirection):
	""" Perform a melee attack. Smash, boom, bang! """

	def perform(self) -> None:
		""" Validate target """
		target = self.target_actor
		if not target:
			raise exceptions.Impossible(settings.str_no_target)

		# print(f"Target {target.name} HP: {str(target.fighter.hp)}")

		""" If skills component is used, check wether actor has melee skill availible """
		if self.entity.skills:
			self.entity.skills.requires_skill(["Melee"])
		
		""" Generate attack log and colorize it """
		attack_desc = settings.str_attack.format(self.entity.name, target.name)
		if self.entity is self.engine.player:
			attack_color = color.player_atk
		else:
			attack_color = color.enemy_atk
		
		""" Combat: following AD&D3.5 battle rules """
		""" ====================================== """

		""" Get attack dice and total attack value from fighter component """
		attack_dice, attack_value = self.entity.fighter.attack_value()
		
		""" A valid attack needs attack_dice above 1 and attack value higher then targets armor class """
		if attack_dice > 1 and attack_value >= target.fighter.armor_class:
			""" Calculate hitpoints, check if critical hit was dealed (criticals multi stored in fighter class)"""
			hit_points = self.entity.fighter.hp_dealed()
							
			if attack_dice in self.entity.fighter.criticals:
				""" Multipy hit points in case of critical hit """
				hit_points *= int(self.entity.fighter.criticals_multi)
				self.engine.message_log.add_message(settings.str_critical_hit, attack_color)
				
			self.engine.message_log.add_message(
				f"{attack_desc}" + settings.str_hits_target.format(hit_points), attack_color)
			
			target.fighter.hp -= hit_points	

		else:
			self.engine.message_log.add_message(
				attack_desc + settings.str_no_damage, attack_color)
		
class MovementAction(ActionWithDirection):
	""" Move the entity somewhere, bevore MovementAction, BumpAction is called """
	def perform(self) -> None:
		dest_x, dest_y = self.dest_xy
		
		
		""" Check if entity is able to walk in case skills component is active """
		if self.entity.skills:
			if not "Walking" in self.entity.skills.skills:
				raise exceptions.Impossible(settings.str_not_walking)
		
		""" Check if target is inside map and is walkable """
		if not self.engine.game_map.in_bounds(dest_x, dest_y):
			raise exceptions.Impossible(settings.str_blocked)
			
		if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
			raise exceptions.Impossible(settings.str_blocked)
		
		""" Check if entity is allowed to pass doors (to prevent running everywhere, e.g. keep shopkeeper inside shop) """
		if (self.entity.pass_door == False and
				self.engine.game_map.tiles["kind"][dest_x, dest_y] == b"Door"):
			raise exceptions.Impossible(settings.str_no_door_passage)
		
		""" If something is standing on destination, check if it can be activated """
		walkable = True
		if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
			entity = self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
			if hasattr(entity, "usable"):
				entity.usable.get_info(self.entity)
				walkable = entity.walkable
			else:
				raise exceptions.Impossible(settings.str_blocked_by_something)
		
		""" Finally walk, thereby darken the floor slightly """
		if walkable == True:
			self.engine.game_map.tiles[dest_x, dest_y][3][2][0] *= .97
			self.engine.game_map.tiles[dest_x, dest_y][3][2][1] *= .97
			self.engine.game_map.tiles[dest_x, dest_y][3][2][2] *= .97		
		
			self.entity.move(self.dx, self.dy)
		


class BumpAction(ActionWithDirection):
	""" Action called before movement """
	def perform(self) -> None:
		
		""" Check wether Entity is carrying to much, depending on overload, insert more or less wait actions """
		delay = 0
		if self.entity.dimensions.payload_malus > 1:
			delay = 1
		elif self.entity.dimensions.payload_malus > 0.66:
			delay = randint(1,5)
		elif self.entity.dimensions.payload_malus > 0.33:
			delay = randint(1,10)
		
		if delay == 1:
			self.engine.message_log.add_message(settings.str_to_heavy, color.yellow)
			return WaitAction(self.entity)
		
		""" Don't move if blocked skill is applied """
		if self.entity.skills:
			if "Blocked" in self.entity.skills.skills:
				self.engine.message_log.add_message(settings.str_unable_to_move, color.yellow)
				return WaitAction(self.entity)
		
		
		""" Distinguish between Friendly and Hostile entities, and choose the correct action """
		if self.target_actor:
			if self.target_actor.attitute == "Hostile":
				return MeleeAction(self.entity, self.dx, self.dy).perform()
			if self.target_actor.attitute == "Friendly":
				""" This placeholder should be filled with shopping, talking, etc.... """
				self.engine.message_log.add_message(settings.str_is_friendly.format(self.target_actor.name), color.player_atk)		
		else:
			return MovementAction(self.entity, self.dx, self.dy).perform()
			

class RangedAttackAction(Action):
	""" Performs a ranged attack using quiver and a ranged weapon """
	def perform(self):
		
		""" Check wether the required skill is availible """
		if self.entity.skills:
			self.entity.skills.requires_skill(["Ranged"])
		
		""" Colorize the log output accordingly """
		if self.entity is self.engine.player:
			attack_color = color.player_atk
		else:
			attack_color = color.enemy_atk
		
		""" Check for ranged weapon equipped and filled quiver """
		if self.entity.equipment.weapon is None:
			raise exceptions.Impossible(settings.str_no_weapon)

		if self.entity.equipment.weapon.equippable.combat != "Ranged":
			raise exceptions.Impossible(settings.str_no_ranged_weapon)
		
		if self.entity.equipment.quiver is None:
			raise exceptions.Impossible(settings.str_no_arrows)
		
		
		""" Automatically shoot at the closest target """
		target = None
		closest_distance = self.entity.equipment.weapon.equippable.maximum_range + 1.0
		
		""" Loop trough actors and find suitable target, store the closest target """
		for actor in self.engine.game_map.actors:
			if actor is not self.entity and self.entity.gamemap.visible[actor.x, actor.y]:
				distance = self.entity.distance(actor.x, actor.y)
				
				if distance < closest_distance:
					target = actor
					closest_distance = distance
					
		""" Target found, shoot at it """		
		if target:
			""" Remove oen arror, create attack descr. and roll attack dice """
			self.entity.equipment.quiver.value -= 1
			attack_desc = settings.str_attack.format(self.entity.name, target.name)
			attack_dice = randint(1,20)

			""" Calculate distance penalty based of distance to shoot """
			""" (different calculation than in D&D3.5)"""

			act_range = int(distance / self.entity.equipment.weapon.equippable.maximum_range *100)
			range_penalty = 0 
			
			if act_range > 66:
				range_penalty = -2
			elif act_range > 33:
				range_penalty = -1
			else:
				range_penalty = 0
		
			""" Calculate size modifier, larger is easier to shoot at """
			if self.entity.dimensions:
				size_modifier = self.entity.dimensions.size_factor
			else:
				size_modifier = 0
			
			""" Calculate dexterity modifier """
			dex_modifier = (self.entity.fighter.dexterity-10) // 2
		
			""" Calculate attack value and normalize into values between 1 and 20 """
			attack_value = attack_dice + self.entity.fighter.bab + size_modifier + dex_modifier + range_penalty
			
			if attack_value < 1:
				attack_value = 1
			if attack_value > 20:
				attack_value = 20

			# for debugging:
			# print(f"Size Mod: {size_modifier}, BAB: {self.entity.fighter.bab}, Dex Mod: {dex_modifier},Range Penalty: {range_penalty}")
			# print (f"{self.entity.name} - Dice: {attack_dice}, Total: {attack_value}, AC Ziel: {target.fighter.armor_class}, HP Ziel: {target.fighter.hp}, Schaden: {self.entity.fighter.damage}")

			""" Calculate hit and damage """
			if attack_dice > 1 and attack_value >= target.fighter.armor_class:
			
				""" Successful hit, calculate damage """
				hit_points_dice = self.entity.fighter.damage.split("d")
				hit_points = 0
				for i in range(int(hit_points_dice[0])):
					hit_points += randint(1, int(hit_points_dice[1]))
				
				""" Check if critical hit was performed """			
				if attack_dice in self.entity.fighter.criticals:
					hit_points *= int(self.entity.fighter.criticals_multi)
					self.engine.message_log.add_message(
						settings.str_critical_hit, color.player_atk) 
			
				""" Display log and deal damage """
				self.engine.message_log.add_message(
						attack_desc + settings.str_hits_target.format(hit_points), attack_color)
				target.fighter.take_damage(hit_points)	

			else:
				""" No damage """
				self.engine.message_log.add_message(
					attack_desc + settings.str_no_damage, attack_color)

			""" Unequip arrows in case last arrow was shoot """		
			if self.entity.equipment.quiver.value == 0:
				""" Remove the consumed item from the inventory. """
				self.entity.inventory.items.remove(self.entity.equipment.quiver)
				self.entity.equipment.unequip_from_slot("quiver", False)		# False: Hiding unequip message
				raise exceptions.Impossible(settings.str_no_arrows_left)

		else:
			raise exceptions.Impossible(settings.str_no_target)
	
	
class LoadPlayerAction(Action):
	""" Loads a player entity and replaces everything listed below for the actual player. Function is quick and dirty
	and must be configured in case the entitys components etc. changes. No use in the real game (yet)
	"""
	def perform(self):
		print("Player entity loaded.")
		""" Load everything of saved player except xy coords. """
		with open("player.sav", "rb") as f:
			player_tmp = pickle.loads(lzma.decompress(f.read()))
			self.engine.player.fighter = player_tmp.fighter
			self.engine.player.inventory = player_tmp.inventory
			self.engine.player.banking = player_tmp.banking
			self.engine.player.level = player_tmp.level
			self.engine.player.equipment = player_tmp.equipment
			self.engine.player.size = player_tmp.size
			self.engine.player.name = player_tmp.name
			self.engine.player.race = player_tmp.race
			self.engine.player.clas = player_tmp.clas
		return				

class SavePlayerAction(Action):
	""" Saves the player entity, used for development, no use in the actual game """
	def perform(self):
		print("Player entity saved.")
		save_player = lzma.compress(pickle.dumps(self.engine.player))
		with open("player.sav", "wb") as f:
			f.write(save_player)

class LockpickAction(Action):
	""" Lockpick object to open them """
	def __init__(self, target, actor, callback: Callable[Optional[Action]] = None):
		self.target = target
		self.entity = actor
		self.callback = callback
		
	def perform(self) -> None:
		""" Check if target exists """
		if not self.target:
			raise exceptions.Impossible(settings.str_no_target)
		
		""" Check if lock exists on target """
		if self.target.lock:
			self.target.lock.pick_lock(self.entity)
		else:
			raise exceptions.Impossible(settings.str_no_lock.format(target.name))
		
		if self.callback:
			""" Get control back """
			return self.callback(self.target.lock.locked)


class UnlockFurniture(Action):
	""" Lockpick object """
	def perform(engine, target, actor) -> None:
		 
		""" Check if target has lock """
		if not target:
			raise exceptions.Impossible(settings.str_no_target)
		
		if target.lock:
			""" Unlock will be set to 1 for successful unlock """
			unlocked = target.lock.pick_lock(actor)
			if unlocked:
				target.dimensions.locked = False
				engine.game_map.entities.remove(target)
				engine.game_map.tiles[(target.x, target.y)] = tile_types.floor				
		else:
			raise exceptions.Impossible(settings.str_no_lock.format(target.name))


class DestroyFurniture(Action):
	""" Break objects by a melee attack, specify by remove = False that destroyed furniture
	should stay on the map, otherwise removed """
	def __init__(self, target, actor, callback: Callable[Optional[Action]] = None, remove: Optional[bool] = True):

		self.entity = actor
		self.target = target
		self.actor = actor
		self.callback = callback
		self.remove = remove
	
	def perform(self) -> None:
		""" check if target is provided """
		if not self.target:
			raise exceptions.Impossible(settings.str_no_target)
		
		""" Target need dimension module to be breakable """
		if not self.target.dimensions:
			raise exceptions.Impossible(settings.str_no_destroy.format(self.target.name))
		
		""" Melee is necessary to break furniture """
		if self.actor.skills:
			self.actor.skills.requires_skill(["Melee"])
		
		""" TODO: Move following code to equippable """
		
		# BUG: Destroy paper with hands will be canceled on first if

		""" Melee weapon is necessary to destroy furniture """
		if self.actor.equipment.weapon is not None:
			if self.actor.equipment.weapon.equippable.combat != "Melee":
				raise exceptions.Impossible(settings.str_melee_needed)
		
		""" Paper can be destroyed by hand """
		if self.actor.equipment.weapon is None and self.target.dimensions.material is not settings.str_paper:
			raise exceptions.Impossible("You need a weapon to destroy anything but paper.")
		
		""" Check wether the weapon equipped is suitable for the objects material """
		if self.actor.equipment.weapon.equippable:
			if self.target.dimensions.material in [settings.str_leather]:
				""" Leather needs piercing or slashing """
				if settings.str_slashing not in self.actor.equipment.weapon.equippable.damage_type:
					if settings.str_piercing not in self.actor.equipment.weapon.equippable.damage_type:
						raise exceptions.Impossible(settings.str_weapon_type.format(settings.str_slashing))				
			
			elif self.target.dimensions.material in [settings.str_ice, settings.str_wood, settings.str_glas]:
				""" Ice , Glas and Wood needs slashing or bludgeoning """			
				if settings.str_slashing not in self.actor.equipment.weapon.equippable.damage_type:
					if settings.str_bludgeoning not in self.actor.equipment.weapon.equippable.damage_type:
						raise exceptions.Impossible(settings.str_weapon_type.format((settings.str_slashing + (settings.str_bludgeoning))))
										
			elif self.target.dimensions.material in [settings.str_stone]:
				""" Stone needs bludgeoning """
				if settings.str_bludgeoning not in self.actor.equipment.weapon.equippable.damage_type:
					raise exceptions.Impossible(settings.str_weapon_type.format(settings.str_bludgeoning))
					
			elif self.target.dimensions.material == settings.str_metal:
				""" Metal should be destroyable in the future """
				raise exceptions.Impossible(f"I have no idea what the best weapon to destroy {self.target.dimensions.material} is.")
			elif self.target.dimensions.material == settings.str_mithril:
				""" Mithril can't be destroyed """
				raise exceptions.Impossible(settings.str_cant_be_destroyed.format(self.target.dimensions.material))
			elif self.target.dimensions.material == settings.str_adamant:
				""" Adamant can't be destroyed """
				raise exceptions.Impossible(settings.str_cant_be_destroyed.format(self.target.dimensions.material))
			else:
				""" Everything else can't be destroyed """
				raise exceptions.Impossible(f"{self.target.dimensions.material} cant be destroyed by any weapon yet.")
						
		""" Create attack description for log window and colorize it """
		attack_desc = settings.str_attack.format(self.actor.name, self.target.name)
		
		if self.actor is self.engine.player:
			attack_color = color.player_atk
		else:
			attack_color = color.enemy_atk
		
		""" Attacking, using AD&D3.5 Battle System """
		
		""" Calculate attack dice and total attack value using fighter component """
		attack_dice, attack_value = self.actor.fighter.attack_value()
		
		""" Calculate armor class of the object """
		""" AC = 10 + Size Mod + Dex Mod (Dex Mod for Objects is -7 (page 200 manual) """

		target_ac = 10 + self.target.dimensions.size_factor - 7		
		
		if attack_dice > 1 and attack_value >= target_ac:
			""" Attack is successful if hit dice > 1 and overall attack value >= targets armour class """
			
			""" calculate hit points and set chance. If chance is 1 items in targets inventory might be destroyed """
			hit_points = self.actor.fighter.hp_dealed()
			chance = 0		
			
			""" Destroy by chance the inventory of the furniture """
			if self.target.inventory:
				""" Go trough all items in inventory """
				for i, item in enumerate(self.target.inventory.items):
					if item.dimensions:
						if item.dimensions.material in [settings.str_glas, settings.str_ice]:
							""" Glass and ice items may break """
							self.engine.message_log.add_message(settings.str_shake.format(self.target.name), attack_color)
							chance = randint(1,4)
							if (item.dimensions.broken == False) and (chance == 3):
								""" Break the item """
								self.engine.message_log.add_message(settings.str_something_breake.format(self.target.name), attack_color)
								item.name = item.name + settings.str_broken
								item.dimensions.broken = True

			""" Print attack message """
			self.engine.message_log.add_message(
				f"{attack_desc}" + settings.str_hits_target.format(hit_points))
			
			""" Broken will be true when hitpoints reach zero, makes sense? """
			broken = self.target.dimensions.decrease_hp(hit_points)
			if broken:
				self.target.dimensions.broken = True
				self.engine.message_log.add_message(f"{attack_desc}" + settings.str_obj_destroyed)
				""" If furniture should be removed in case it is broken: """
				if self.remove == True:
					self.engine.game_map.entities.remove(self.target)
					self.engine.game_map.tiles[(self.target.x, self.target.y)] = tile_types.floor

		else:
			self.engine.message_log.add_message(
				attack_desc + settings.str_no_damage, attack_color)

				
class MoveItem(Action):
	""" Move an item from one inventory into another inventory """
	def __init__(self, source: Item, target: Actor, item: Item):
		self.source = source
		self.target = target
		self.item = item
		self.entity = target
		
	def perform(self) -> None:
		""" Unequip equipped item before moving """
		if hasattr(self.source, "equipment"):
			if self.source.equipment.item_is_equipped(self.item):
				self.source.equipment.toggle_equip(self.item)
		
		""" Remove item from source inventory """
		self.source.inventory.items.remove(self.item)
				
		""" If target has banking component, add money to targets balance """		
		if self.item.name == settings.str_money:
			if hasattr(self.target, "banking"):
				self.target.banking.capital += self.item.value
				self.entity.gamemap.engine.message_log.add_message(settings.str_take_money.format(self.item.value, self.item.name, self.source.name))
				return
			else:
				""" If no banking component, take money as a regular item """
				pass
		
		elif self.item.name == settings.str_arrow:
			""" If target has arrows, increase their amount instead adding another arrow item """
			""" check if arrows are in targets inventory, if so, add more """
			for i in range(len(self.target.inventory.items)):
				if self.item.name in self.target.inventory.items[i].name:
					self.target.inventory.items[i].value += self.item.value
					self.engine.message_log.add_message(settings.str_pickup + f" {self.item.value} {self.item.name}!")
					return
				else:
					""" If no arrows in inventory, take them as a regular item """
					pass
						
		""" Check the targets inventory space """
		if len(self.target.inventory.items) >= self.target.inventory.capacity:
			""" If full, place item back into source inventory """
			self.source.inventory.items.append(self.item)
			raise exceptions.Impossible(settings.str_inventory_full)
			
		""" Add item to targets inventory """	
		self.item.parent = self.target.inventory
		self.target.inventory.items.append(self.item)
		
		""" Up to now no other way found to keep the inventory open until ESC is pressed """		
		raise exceptions.Impossible(settings.str_place_item.format(self.item.name, self.target.name))


class SearchAction(Action):
	""" Search the sourrounding fields of the entity for any hidden stuff """
	def perform(self):
		self.entities = []
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x-1, self.entity.y-1))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x, self.entity.y-1))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x+1, self.entity.y-1))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x-1, self.entity.y))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x, self.entity.y))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x+1, self.entity.y))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x-1, self.entity.y+1))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x, self.entity.y+1))
		self.entities.append(self.engine.game_map.get_entity_at_location(self.entity.x+1, self.entity.y+1))
		
		""" Trial is the chance to find something, the higher, the better """
		trial = 0

		""" Increase trial for special races """
		if self.entity.race:
			if self.entity.race.race == settings.str_elv:
					trial += 2
			elif self.entity.race.race == settings.str_halfelv:
					trial += 1
		
		""" Increase trial for Investigator skill """
		if self.entity.skills:
			if "Investigator" in self.entity.skills.skills:
				trial += 2
				
		""" Trial is affected by intelligence """
		trial += (self.entity.fighter.intelligence-10) // 2

		""" Roll dice """
		trial += randint(1,20)
		
		""" Cycle trough sourrounding entities """
		for entity in self.entities:
			if (entity is not None) and entity is not self.entity:
				""" Check all entites except self """
				if entity.dimensions:
					if entity.dimensions.hidden == True:
						""" If entity has dimension component and is hidden, search for it """
						""" the higher entity.value is, the harder to find """
						if trial >= entity.value:
							entity.dimensions.hidden = False
							self.engine.message_log.add_message(settings.str_found.format(entity.name))

