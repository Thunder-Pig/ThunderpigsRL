from __future__ import annotations

from typing import TYPE_CHECKING
from random import randint, choice
from copy import deepcopy

import entity_factories
import tile_types

from components.base_component import BaseComponent
from equipment_types import EquipmentType
from exceptions import Impossible
from input_handlers import ActionOrHandler, ChestInventoryHandler, AskSelectionHandler, MainGameEventHandler, GameSuccess
from actions import DestroyFurniture, UnlockFurniture, LockpickAction

import color
import settings

if TYPE_CHECKING:
	from entity import Item
	

class Usable(BaseComponent):
	""" The basic component for usable furniture """
	parent: Furniture

	def __init__(self):
		pass

	def get_action(self, target: target, actor: actor,) -> Optional[ActionOrHandler]:
		""" Return action. Basic (no real action) is you run into... """
		self.engine.message_log.add_message(settings.str_run_into.format(actor.name, target.name))
		return MainGameEventHandler(self.engine)

	def get_info(self, actor) -> None:
		""" Code performed when step onto Usable """
		pass
	
	def reveal(self) -> None:
		""" Code performed when object is revealed from hidden state """
		pass

	
	def calculate_damage(self, dice_roll):
		""" Calculate the dealed damage by an dice roll string like 3d6+5. Used e.g by traps """
		
		dealed_damage = 0
		""" slice the dice string """
		if "+" in dice_roll:
			temp, modifier = dice_roll.split("+")
			no_of_dice, faces = temp.split("d")
		else:
			no_of_dice, faces = dice_roll.split("d")
			modifier = 0
		
		""" roll the dice """
		for i in range(int(no_of_dice)):
			dealed_damage += randint(1, int(faces))
		
		""" Add modifier and return """
		return dealed_damage + int(modifier)
	

		
class Ironbar(Usable):
	""" Ironbars block movement of player but not FOV. At the moment, monsters can pass them """
	def get_action(self, target, actor):
		self.target = target
		self.actor = actor

		""" When locked, give possibility to open """
		if self.parent.lock:
			if (self.parent.lock.locked == True) and (self.parent.dimensions.broken == False):
				return AskSelectionHandler(self.engine, actor, target,callback = self.get_into, option1 = "Lockpick", option2 = "Destroy",)
		else:
			return DestroyFurniture(self.parent, self.actor)

	def get_into(self, choice) -> None:
		""" When stepped onto, should not happen """
		if choice == 1:
			return LockpickAction(self.parent, self.actor, callback = self.picked)
		else:
			return DestroyFurniture(self.parent, self.actor)

	def picked(self, locked) -> None:
		""" When unlocked, remove from map """
		if locked == False:
			self.engine.game_map.entities.remove(self.target)
			self.engine.game_map.tiles[(self.target.x, self.target.y)] = tile_types.floor

class Tree(Usable):
	""" The tree can heal the player or cause damage """
	def get_action(self, target, actor) -> AskSelectionHandler:
		""" Trees can be kicked """
		""" TODO: Check for legs to kick """
		self.target = target
		self.actor = actor
		
		self.engine.message_log.add_message(settings.str_kick_tree_perform)
		result = randint(0,100)
		if result < 50:
			""" Hit by branch """
			damage = randint(1,3)
			self.engine.message_log.add_message(settings.str_hit_by_branch.format(damage))
			actor.fighter.hp -= damage
		elif result < 60:
			""" Get Health Potion """
			self.engine.message_log.add_message(settings.str_get_potion)
			healing = deepcopy(entity_factories.health_potion)
			healing.parent = actor.inventory
			actor.inventory.items.append(healing)
		elif result < 90:
			""" Do nothing """
			self.engine.message_log.add_message(settings.str_only_noise)
		elif result < 95:
			""" Destroy Tree """
			self.engine.message_log.add_message(settings.str_tree_collapse)
			target.dimensions.broken = True
			self.engine.game_map.entities.remove(target)
			self.engine.game_map.tiles[(target.x, target.y)] = tile_types.floor
		elif result < 98:
			""" Destroy Tree and deal damage """ 
			damage = randint(10,30)
			self.engine.message_log.add_message(settings.str_tree_damage.format(damage))
			actor.fighter.hp -= damage
			target.dimensions.broken = True
			self.engine.game_map.entities.remove(target)
			self.engine.game_map.tiles[(target.x, target.y)] = tile_types.floor
		else:
			""" Amputate Foot """
			damage = randint(5,10)
			self.engine.message_log.add_message(settings.str_amputate_foot.format(damage))
			actor.fighter.hp -= damage
			actor.body.amputate("Foot")

		self.engine.update_fov()

		return MainGameEventHandler(self.engine)


class Fountain(Usable):
	""" The fountain can heal the player or cause damage """
	def get_action(self, target, actor):
		""" you can drink from a fountain """
		""" TODO: Check for mouth """
		result = randint(0,100)
		if target.dimensions.broken == False:
			if result < 2:
				""" Perfect Healing, fountain will dry out """
				self.engine.message_log.add_message(settings.str_full_healing)
				actor.fighter.hp += 50
				target.dimensions.broken = True
				target.name = "Dry " + target.name
			elif result < 50:
				""" Little healing """
				self.engine.message_log.add_message(settings.str_healing)
				actor.fighter.hp += randint(1,5)
			elif result < 70:
				""" Deal Damage, fountain might dry out """
				self.engine.message_log.add_message(settings.str_dirty)
				actor.fighter.hp -= randint(1,5)
				chance = randint(0,3)
				if chance == 2:
					target.dimensions.broken = True
					target.name = "Dry " + target.name
			else:
				""" Nothing happens, but Fountain might dry out """
				self.engine.message_log.add_message(settings.str_quaff)
				chance = randint(0,3)
				if chance == 2:
					target.dimensions.broken = True
					target.name = settings.str_pre_dry + target.name
		else:
			self.engine.message_log.add_message(settings.str_fountain_dry)

		return MainGameEventHandler(self.engine)

class Cloud(Usable):
	""" The cloud is doing noting except blocking the FOV of the entity """
	def get_action(self, target, actor):
		pass
		
	def get_info(self, actor):
		self.engine.message_log.add_message(settings.str_cloud_step)
	
class Pillar(Usable):
	""" The pillar is doing nothing except blocking the FOV of the entity and looks nice """
	pass

class Button(Usable):
	""" The Button finishes the game """
	def get_action(self, target, actor):
		self.engine.message_log.add_message(settings.str_button_finish)
		return GameSuccess(self.engine)

class Chest(Usable):
	""" A chest is a chest, is a chest """	
	def initialize(self, engine):
		""" Populate the inventory with items """
		
		""" Setup everyting and get no of items to add """
		dungeon = engine
		self.parent.inventory.items = []
		no_of_items = randint(1,5)
		
		""" Select items from spawned items list and add to chest. Means chest will never hold novel items. """
		x = 1
		while x <= no_of_items:
			if dungeon.engine.spawned_items:
				source = choice(dungeon.engine.spawned_items)
				item = deepcopy(source)
			else:
				""" If no spawned items on map, add money """
				item = deepcopy(entity_factories.money)
			
			if len(self.parent.inventory.items) == 0:
				item.parent = self.parent.inventory
				self.parent.inventory.items.append(item)
				x += 1
			else:
				if item.name == settings.str_arrow:
					""" Check if already arrows in inventory, if so, increase number instead of adding new """
					found = -1

					for i in range(len(self.parent.inventory.items)):
						if item.name == self.parent.inventory.items[i].name:
							found = i

					if found > -1:
						self.parent.inventory.items[i].value += item.value
					else:
						item.parent = self.parent.inventory
						self.parent.inventory.items.append(item)
						
				elif item.name == settings.str_money:
					""" Check if already coins in inventory, if so, increase number instead of adding new """
					found = -1

					for i in range(len(self.parent.inventory.items)):
						if item.name == self.parent.inventory.items[i].name:
							found = i

					if found > -1:
						self.parent.inventory.items[found].value += item.value
					else:
						item.parent = self.parent.inventory
						self.parent.inventory.items.append(item)

				else:
					item.parent = self.parent.inventory
					self.parent.inventory.items.append(item)

				x += 1
				
				""" Check if added item must be initialized """
				if hasattr(item, "consumable"):
					try:
						item.consumable.initialize()
					except:
						pass
	

	def list_content(self):
		""" List content for debugging """
		print("Inhalt Kiste:")
		for i in self.parent.inventory.items:
			print(i)

						
	def get_action(self, target, actor) -> ChestInventoryHandler:
		""" Action when activated """
		self.target = target
		self.actor = actor

		""" If locked, allow lockpick or break. If unlocked, open inventory """
		if self.target.lock:
			if (self.target.lock.locked == False) or (self.target.dimensions.broken == True):
				return ChestInventoryHandler(self.engine, self.target, self.actor)
			else:
				return AskSelectionHandler(self.engine, self.actor, self.target, callback = self.get_into, option1 = "Lockpick", option2 = "Destroy",)

		else:
			return ChestInventoryHandler(self.engine, self.target, self.actor, callback = self.takeout)
		
	def get_into(self, choice) -> None:
		""" The Return from the input handler, to decide what to do... """
		if choice == 1:
			return LockpickAction(self.target, self.actor)
		else:
			return DestroyFurniture(self.target, self.actor, remove = False)

class Door(Usable):
	""" Door object, can be open, closed and hidden. The closed and hidden door can be locked """
	""" self.parent.value at initalization: 0 = open, 1 = closed, 2 = hidden """
	""" self.parent.value stores the difficulty of the hidden door (15 - 20) """

	def initialize(self, dungeon, x, y):
		""" Initialise the door to either open (0), closed (1) or hidden (2) """
		self.parent.value = randint(0,2)
		
		""" Get a random number for locked state """
		locked = randint(0,5)

		if self.parent.value == 0:
			""" Place open door. Never locked """
			self.parent.lock.locked = False
			self.parent.name = settings.str_door
			self.parent.char = "."
			self.parent.walkable = True
			dungeon.tiles[(x, y)] = tile_types.open_door_base

		elif self.parent.value == 1:
			""" Place closed door. Locked by chance """
			if locked == 5:
				self.parent.lock.locked = True
			else:
				self.parent.lock.locked = False
			
			self.parent.name = settings.str_door	
			self.parent.char = "+"
			self.parent.walkable = False
			dungeon.tiles[(x, y)] = tile_types.closed_door_base
			
		elif self.parent.value == 2:
			""" Place a hidden door """

			""" Set the difficulty of revealing it from hidden state. Everything above 2 is hidden """
			self.parent.value = randint(15,20)
			self.parent.dimensions._hidden = True
			
			""" Lock it by chance """
			if locked == 5:
				self.parent.lock.locked = True
			else:
				self.parent.lock.locked = False
			
			self.parent.name = ""

			# char set to ? is for debugging only
			self.parent.char = " "			
			#self.parent.char = " "
			
			self.parent.walkable = False
			dungeon.tiles[(x, y)] = tile_types.hidden_door_base
			

	def get_action(self, target, actor) -> AskSelectionHandler:
		""" Get the action for the door """
		self.target = target
		self.actor = actor
		

		if self.parent.value == 0:
			""" Close an open door """
			if self.parent.dimensions.broken == True:
				""" Destroyed doors can't be closed """
				self.engine.message_log.add_message(settings.str_door_broken)
			else:
				""" Close the door """
				self.engine.message_log.add_message(settings.str_close_door)
				self.parent.char = "+"
				self.parent.value = 1
				self.parent.walkable = False
				self.engine.game_map.tiles[(self.parent.x, self.parent.y)] = tile_types.closed_door_base
			
		elif self.parent.value == 1:
			""" Open a closed door """
			if self.parent.lock:
				""" Lockpick or break for locked, unbroken doors, otherwise open the door """
				if (self.parent.lock.locked == True) and (self.parent.dimensions.broken == False):
					return AskSelectionHandler(self.engine, actor, target,callback = self.get_into, option1 = settings.str_pick_lock, option2 = settings.str_break,)
				
				else:
					self.parent.char = "."
					self.parent.value = 0
					self.parent.walkable = True
					self.engine.game_map.tiles[(self.parent.x, self.parent.y)] = tile_types.open_door_base
					self.engine.message_log.add_message(settings.str_open_door)
		else:
			pass

		self.engine.update_fov()


		return MainGameEventHandler(self.engine)
	
	def get_into(self, choice) -> None:
		""" The Return from the input handler, to decide what to do... """
		if choice == 1:
			return LockpickAction(self.target, self.actor)
		else:
			return DestroyFurniture(self.target, self.actor, remove = True)
	
	def reveal(self) -> None:
		""" Reveal the secret door and turn it into a normal closed door """
		self.parent.name = settings.str_door
		self.parent.char = "+"
		self.parent.value = 1
		self.parent.walkable = False
		self.gamemap.tiles[(self.parent.x, self.parent.y)] = tile_types.closed_door_base

class Trap(Usable):
	""" The trap will cause damage when stepped onto it """
	def initialize(self):
		
		self.damage_type = "<Unknown damage>"
		self.damage = "Nothing"
		
		""" List of possible trap types """
		self.trap_types = [
			settings.str_trap_water, settings.str_trap_fire, settings.str_trap_land_mine, settings.str_trap_dart,
			settings.str_trap_arrow, settings.str_trap_bolt, settings.str_trap_bear, settings.str_trap_falling_rock,
			settings.str_trap_web, settings.str_trap_hole, settings.str_trap_spike,
			]
				
		""" BUG: Hiden trap name must be "", see doors """
		
		""" Choose one of the availible Traps, add name and type """
		self.trap_type = choice(self.trap_types)
		self.parent.name = f"{self.parent.name} ({self.trap_type})"

		""" Initialize the traps accordingly """
		if self.trap_type == settings.str_trap_water:
			self.damage_type = settings.str_water_damage
			self.damage = "1d6+2"
		elif self.trap_type == settings.str_trap_fire:
			self.damage_type = settings.str_fire_damage
			self.damage = "2d6+3"
		elif self.trap_type == settings.str_trap_land_mine:
			self.damage_type = settings.str_explosion_damage
			self.damage = "3d8+4"
		elif self.trap_type == settings.str_trap_dart:
			self.damage_type = settings.str_piercing
			self.damage = "2d2"
		elif self.trap_type == settings.str_trap_arrow:
			self.damage_type = settings.str_piercing
			self.damage = "2d4"
		elif self.trap_type == settings.str_trap_bolt:
			self.damage_type = settings.str_piercing
			self.damage = "2d6"
		elif self.trap_type == settings.str_trap_spike:
			self.damage_type = settings.str_piercing
			self.damage = "3d6"
		elif self.trap_type == settings.str_trap_bear:
			self.damage_type = settings.str_slashing
			self.damage = "3d6"
		elif self.trap_type == settings.str_trap_falling_rock:
			self.damage_type = settings.str_bludgeoning
			self.damage = "2d8"
	
	
	def get_action(self, target, actor) -> AskSelectionHandler:
		""" Get the action when used by entity """
		
		self.target = target
		self.actor = actor
		
		""" Check wether Trap is locked or not, display options accordingly """
		if self.parent.lock and self.parent.lock.locked == True:
			return AskSelectionHandler(
					self.engine, self.actor, self.target, callback = self.get_into, option1 = settings.str_destroy,
					option2 = settings.str_lockpick_action)
		else:
			return AskSelectionHandler(self.engine, self.actor, self.target, callback = self.get_into, option1 = settings.str_destroy)

	def mark_unlocked(self):
		""" Change Name and Color when deactivated """
		self.parent.name = f"{self.parent.name} {settings.str_unlocked}"
		self.parent.color = color.grey
		
	def get_into(self, choice) -> None:
		""" The Return from the input handler, to decide what to do... """
		if choice == 2:
			return LockpickAction(self.target, self.actor)
		else:
			return DestroyFurniture(self.target, self.actor, remove = True)	
	
	
	def get_info(self, actor):
		""" Deal everything when stepped onto the trap """
		
		""" A locked trap is charged, an unlocked trap is uncharged """
		if self.parent.lock and self.parent.lock.locked == False:		
			self.engine.message_log.add_message(settings.str_uncharged.format(self.parent.name))
		
		else:
			""" TODO: Insert that the trap isn't causing always damage, give a chance not to hit """

			""" Check if trap type is causing damage """
			if self.damage != "Nothing":
				""" Calculate damage, deal damage to actor and show message """
				hit_points = self.calculate_damage(self.damage)
				actor.fighter.take_damage(hit_points, self.damage_type)
				self.engine.message_log.add_message(settings.str_trap_damage.format(self.parent.name, hit_points, self.damage_type))

			""" Remove Landmine once stepped onto it """
			if self.trap_type == settings.str_trap_land_mine:
				self.engine.game_map.entities.remove(self.parent)

			""" Remove stonefall trap and place a boulder instead """
			if self.trap_type == settings.str_trap_falling_rock:
				rock = deepcopy(entity_factories.stone)
				rock.parent = self.engine.game_map
				rock.spawn(self.engine.game_map, self.parent.x, self.parent.y)
				self.engine.message_log.add_message(settings.str_rock_drop.format(rock.name))		
				self.engine.game_map.entities.remove(self.parent)

			""" Hold actor several turns """
			if self.trap_type == settings.str_trap_web:
				if actor.skills:
					actor.skills.add_skill("Blocked", randint(1,10))
		
			if self.trap_type == settings.str_trap_hole:
				if actor.skills:
					actor.skills.add_skill("Blocked", randint(1,15))
		
			if self.trap_type == settings.str_trap_spike:
				if actor.skills:
					actor.skills.add_skill("Blocked", randint(1,5))		
		
			""" Teleport player trough the dungeon if stepped onto teleporter trap """
			""" BUG: landing pos not exact because of MovementAction """
			if self.trap_type == settings.str_trap_teleporter:
				while True:
					x = randint(1, self.engine.game_map.width - 1)
					y = randint(1, self.engine.game_map.height - 1)
					if self.engine.game_map.tiles[x, y]["kind"] == b"Floor":
						self.engine.message_log.add_message(settings.str_teleported)
						print(f"Teleportiere zu {x}, {y}.")
						actor.x, actor.y = x, y
						break
					else:
						pass
		
			""" Amputate an organ by chance of beartrap """
			if self.trap_type == settings.str_trap_bear:
				if actor.body:
					chance = randint(1,5)
					if chance == 1:
						actor.body.amputate("Foot")
						self.engine.message_log.add_message(settings.str_foot_cutoff.format(self.parent.name))
			
			
			""" Generate an arrow by chance """
			if self.trap_type == settings.str_trap_arrow:
				if hit_points < 3:
					arrow = deepcopy(entity_factories.arrow)
					arrow.parent = self.engine.game_map
					arrow.spawn(self.engine.game_map, actor.x, actor.y)
					self.engine.message_log.add_message(settings.str_drops_next.format(arrow.name))

		return MainGameEventHandler(self.engine)

