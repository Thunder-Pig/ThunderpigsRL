from __future__ import annotations

import os
import glob
import lzma
import pickle

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

from copy import deepcopy

import tcod.event
import tile_types

from actions import (
	Action,
	BumpAction,
	DropItem,
	EquipAction,
	MoveItem,
	PickupAction,
	WaitAction,
	RangedAttackAction,
	LoadPlayerAction,
	SavePlayerAction,
	LockpickAction,
	DestroyFurniture,
	SearchAction,
	TakeStairsAction,
)

import settings
import color
import exceptions


if TYPE_CHECKING:
	from engine import Engine
	from entity import Item

MOVE_KEYS= {
	# Arrow keys.
	tcod.event.K_UP: (0, -1),
	tcod.event.K_DOWN: (0, 1),
	tcod.event.K_LEFT: (-1, 0),
	tcod.event.K_RIGHT: (1, 0),
	tcod.event.K_HOME: (-1, -1),
	tcod.event.K_END: (-1, 1),
	tcod.event.K_PAGEUP: (1, -1),
	tcod.event.K_PAGEDOWN: (1, 1),
	# Numpad keys.
	tcod.event.K_KP_1: (-1, 1),
	tcod.event.K_KP_2: (0, 1),
	tcod.event.K_KP_3: (1, 1),
	tcod.event.K_KP_4: (-1, 0),
	tcod.event.K_KP_6: (1, 0),
	tcod.event.K_KP_7: (-1, -1),
	tcod.event.K_KP_8: (0, -1),
	tcod.event.K_KP_9: (1, -1),
	# Doom keys.
	tcod.event.K_a: (-1, 0),
	tcod.event.K_x: (0, 1),
	tcod.event.K_w: (0, -1),
	tcod.event.K_d: (1, 0),
	tcod.event.K_q: (-1, -1),
	tcod.event.K_e: (1, -1),
	tcod.event.K_y: (-1, 1),
	tcod.event.K_c: (1, 1),
}

WAIT_KEYS = {
	tcod.event.K_PERIOD,
	tcod.event.K_KP_5,
	tcod.event.K_s,
}
	
CONFIRM_KEYS = {
	tcod.event.K_RETURN,
	tcod.event.K_KP_ENTER,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]
""" An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
if an action is returned it will be attempted and if its valid then MainGameEventHandler will
become the active handler.
"""

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
	def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
		""" Handle an event and return the next active event handler. """
		state = self.dispatch(event)
		if isinstance(state, BaseEventHandler):
			return state
		assert not isinstance(state, Action), f"{self!r} can not handle actions."
		return self
	
	def on_render(self, console: tcod.Console) -> None:
		raise NotImplementedError()
		
	def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
		raise SystemExit()
		
class PopupMessage(BaseEventHandler):
	""" Display a popup text window. """
	
	def __init__(self, parent_handler: BaseEventHandler, text: str):
		self.parent = parent_handler
		self.text = text
		
	def on_render(self, console: tcod.Console) -> None:
		""" Render the parent and dim the result, then print the message on top. """
		self.parent.on_render(console)
		console.tiles_rgb["fg"] //= 8
		console.tiles_rgb["bg"] //= 8
		
		console.print(
			console.width // 2,
			console.height // 2,
			self.text,
			fg=color.white,
			bg=color.black,
			alignment=tcod.CENTER,
		)
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
		""" Any key returns to the parent handler. """
		return self.parent
		


class EventHandler(BaseEventHandler):
	""" Handles events """
	def __init__(self, engine: Engine):
		self.engine = engine
		
	def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
		""" Handle events for input handlers with an engine. """
		
		action_or_state = self.dispatch(event)
		if isinstance(action_or_state, BaseEventHandler):
			return action_or_state
		if self.handle_action(action_or_state):
			# A valid action was performed
			if not self.engine.player.is_alive:
				# The player was killed sometime during or after the action.
				return GameOverEventHandler(self.engine)
			elif self.engine.player.level.requires_level_up:
				# The player needs to level up
				return LevelUpEventHandler(self.engine)
			return MainGameEventHandler(self.engine) # Return to the main handler
		return self
		
	def handle_action(self, action: Optional[Action]) -> bool:
		""" Handle actions returned from event methods.	Returns true if the action
		will advance a turn. """
		
		if action is None:
			return False
			
		try:
			action.perform()
		
		except exceptions.Impossible as exc:
			self.engine.message_log.add_message(exc.args[0], color.impossible)
			return False # Skip enemy turn on exceptions.
			
		""" Perform enemy turns and update fov in case a vaild action was performed """
		self.engine.handle_enemy_turns()
		self.engine.update_fov()
		return True
		

	def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
		if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
			self.engine.mouse_location = event.tile.x, event.tile.y
		
	def on_render(self, console: tcod.Console) -> None:
		self.engine.render(console)

class AskUserEventHandler(EventHandler):
	""" Handles user input for actions which require special input. """
	
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		""" By default any key exits this input handler. """
		if event.sym in { # Ignore modifier keys
			tcod.event.K_LSHIFT,
			tcod.event.K_RSHIFT,
			tcod.event.K_LCTRL,
			tcod.event.K_RCTRL,
			tcod.event.K_LALT,
			tcod.event.K_RALT,
		}:
			return None
		return self.on_exit()
		
	def ev_mousebuttondown(
		self,
		event: tcod.event.MouseButtonDown
	) -> Optional[ActionOrHandler]:
		""" By default any mouse click exits this input handler. """
		return self.on_exit()
		
	def on_exit(self) -> Optional[ActionOrHandler]:
		""" Called when the user is trying to exit or cancel an action. By default
		this returns to the main event handler. """
		return MainGameEventHandler(self.engine)


class CharacterScreenEventHandler(AskUserEventHandler):
	""" Display Character informations """
	TITLE = settings.str_character_info
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		y = 0
		width = 40
		
		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=38,
			title=self.TITLE,
			clear=True,
			fg=(255, 255, 255),
			bg=(0,0,0),
		)
		if self.engine.player.level:
			console.print(x=x + 1, y = y + 1, string= settings.str_player_level.ljust(24) + f" : {self.engine.player.level.current_level}")
			console.print(x=x + 1, y = y + 2, string= settings.str_xp_cur_level.ljust(24)+ f" : {self.engine.player.level.current_xp}")
			console.print(x=x + 1, y = y + 3, string= settings.str_xp_total.ljust(24) + f" : {self.engine.player.level.total_xp}")
			console.print(x=x + 1, y = y + 4, string= settings.str_xp_next_level.ljust(24) + f" : {self.engine.player.level.experience_to_next_level}")
			console.print(x=x + 1, y = y + 5, string= settings.str_skill_points.ljust(24) + f" : {self.engine.player.level.skill_points}")

		if self.engine.player.fighter:
			console.print(x=x + 1, y = y + 8, string= settings.str_strength.ljust(24) + f" : {self.engine.player.fighter.strength}")
			console.print(x=x + 1, y = y + 9, string= settings.str_dexterity.ljust(24) + f" : {self.engine.player.fighter.dexterity}")
			console.print(x=x + 1, y = y + 10, string= settings.str_constitution.ljust(24) + f" : {self.engine.player.fighter.constitution}")
			console.print(x=x + 1, y = y + 11, string= settings.str_intelligence.ljust(24) + f" : {self.engine.player.fighter.intelligence}")
			console.print(x=x + 1, y = y + 12, string= settings.str_wisdom.ljust(24) + f" : {self.engine.player.fighter.wisdom}")
			console.print(x=x + 1, y = y + 13, string= settings.str_charisma.ljust(24) + f" : {self.engine.player.fighter.charisma}")
			console.print(x=x + 1, y = y + 14, string= settings.str_armor_class.ljust(24) + f" : {self.engine.player.fighter.armor_class}")
			console.print(x=x + 1, y = y + 15, string= settings.str_initiative.ljust(24) + f" : {self.engine.player.fighter.initiative}")
		
		if self.engine.player.banking:
			console.print(x=x + 1, y = y + 18, string= settings.str_money + f" : {self.engine.player.banking.get_balance()}")
		
		if self.engine.player.race:
			console.print( x=x + 1, y = y + 19, string=settings.str_race.ljust(24) + f" : {self.engine.player.race.race}")
		
		if self.engine.player.clas:
			console.print( x=x + 1, y = y + 20, string=settings.str_class.ljust(24) + f" : {self.engine.player.clas.clas}")
		
		if self.engine.player.dimensions:
			console.print( x=x + 1, y = y + 21, string=settings.str_size.ljust(24) + f" : {self.engine.player.dimensions.size}")

		if self.engine.player.skills:
			skills = f"{self.engine.player.skills.skills[0]}\n"
			for skill in self.engine.player.skills.skills[1:]:
				skills += f"{skill}\n"
			console.print( x=x + 1, y = y + 23, string=settings.str_skills + f":\n{skills}")
		
		""" Display body parts """
		"""
		if self.engine.player.body:
			console.print( x=x + 1, y = y + 25, string=f"Koerper : {self.engine.player.body.kind}")
			console.print( x=x + 1, y = y + 26, string=f"Parts : {self.engine.player.body.parts}")
			# console.print( x=x + 1, y = y + 27, string=f"Skills : {self.engine.player.body.permit_skills}")
		"""

class ShopEventHandler(AskUserEventHandler):
	""" Display the Shopping Event Handler, not included yet """
	TITLE = settings.str_shop
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)

		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
		
		y = 0
		width = len(self.TITLE) + 24
		
		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=10,
			title=self.TITLE,
			clear=True,
			fg=(255, 255, 255),
			bg=(0,0,0),
		)
		
		console.print(x=x + 1, y = y + 1, string=f"Some day you'll be able to")
		console.print(x=x + 1, y = y + 2, string=f"buy and sell things here.")
		console.print(x=x + 1, y = y + 4, string=f"Your actual balance is:")
		console.print(x=x + 1 ,y = y + 5, string=f"{self.engine.player.banking.get_balance()} Coins.")
		console.print(x=x + 1, y = y + 8, string=f"Have a nice day!")



class HelpScreen(AskUserEventHandler):
	""" The in-game short help """
	TITLE = settings.str_help
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		y = 0
		
		width = len(self.TITLE) + 20
		
		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=14,
			title=self.TITLE,
			clear=True,
			fg=(255, 255, 255),
			bg=(0,0,0),
		)
		
		console.print(x=x + 1, y = y + 1, string=settings.str_help_help)
		console.print(x=x + 1, y = y + 2, string=settings.str_help_pickup)
		console.print(x=x + 1, y = y + 3, string=settings.str_help_inventory)
		console.print(x=x + 1, y = y + 4, string=settings.str_help_character)
		console.print(x=x + 1, y = y + 5, string=settings.str_help_drop)
		console.print(x=x + 1, y = y + 6, string=settings.str_help_look)
		console.print(x=x + 1, y = y + 7, string=settings.str_help_history)
		console.print(x=x + 1, y = y + 8, string=settings.str_help_stairs)
		console.print(x=x + 1, y = y + 9, string=settings.str_help_shop)
		console.print(x=x + 1, y = y + 10, string=settings.str_help_search)
		console.print(x=x + 1, y = y + 11, string=settings.str_help_ranged)
		console.print(x=x + 1, y = y + 12, string=settings.str_help_inspect)
		

class GameSuccess(AskUserEventHandler):
	""" The End-Game Handler, just text, nothing special yet. In the future it should show some game statistics
	and a kind of ranking """

	TITLE = settings.str_success
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		x = 0	
		y = 0
		width = len(self.TITLE) + 66
		
		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=14,
			title=self.TITLE,
			clear=True,
			fg=(255, 255, 255),
			bg=(0,0,0),
		)
		
		console.print(x=int(width/2), y = y + 1, string=f"Du drueckst den Knopf und alles boese ist von der Welt verschwunden.", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 2, string=f"Jetzt geht es heim und zu einem kuehlen Bier!", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 3, string=f"---", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 4, string=f"You press the button and all evil is gone from this world.", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 5, string=f"Now, you are going home and celebreate with a cool beer!", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 6, string=f"", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 7, string=f"Gratulation!", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 8, string=f"Congratulations!", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 9, string=f"", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 10, string=f"Wenn du magst gib Feedback unter:", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 11, string=f"If you like give feedback at:", alignment=tcod.CENTER)
		console.print(x=int(width/2), y = y + 12, string=f"{settings.url}", alignment=tcod.CENTER)

		print(f"Feel free to give feedback at: {settings.url}")



class LevelUpEventHandler(AskUserEventHandler):
	""" The game handler for up-leveling """
	TITLE = settings.str_level
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		console.draw_frame(
			x=x,
			y=0,
			width=47,
			height=13,
			title=self.TITLE,
			clear=True,
			fg=(255,255,255),
			bg=(0,0,0),
		)
		
		console.print(x=x +1, y=1, string=settings.str_level_1)
		console.print(x=x +1, y=2, string=settings.str_level_2)		
		console.print(x= x+1,y=4,
			string=f"a) " + settings.str_strength + " (+1), "+settings.str_from + f" {self.engine.player.fighter.base_strength}",)
		console.print(x= x+1,y=5,
			string=f"b) " + settings.str_dexterity + " (+1), " + settings.str_from + f" {self.engine.player.fighter.base_dexterity}",)
		console.print(x= x+1,y=6,
			string=f"c) " + settings.str_constitution + " (+1), " + settings.str_from + f" {self.engine.player.fighter.base_constitution}",)
		console.print(x= x+1,y=7,
			string=f"d) " + settings.str_intelligence + " (+1), " + settings.str_from + f" {self.engine.player.fighter.base_intelligence}",)
		console.print(x= x+1,y=8,
			string=f"e) " + settings.str_wisdom + " (+1), " + settings.str_from + f" {self.engine.player.fighter.base_wisdom}",)
		console.print(x= x+1,y=9,
			string=f"f) " + settings.str_charisma + " (+1), " + settings.str_from + f" {self.engine.player.fighter.base_charisma}",)
		console.print(x= x+1,y=11,
			string= settings.str_hp_increase,)
		
		
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		""" Manage the key-press inside the handler to level up the player """
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a
		
		if 0 <= index <= 5:
			if index == 0:
				player.level.increase_strength()
			elif index == 1:
				player.level.increase_dexterity()
			elif index == 2:
				player.level.increase_constitution()
			elif index == 3:
				player.level.increase_intelligence()
			elif index == 4:
				player.level.increase_wisdom()
			else:
				player.level.increase_charisma()
		else:
			self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)
			
			return None
			
		return super().ev_keydown(event)
		
	def ev_mousebuttondown(
		self, event: tcod.event.MouseButtonDown
	) -> Optional[ActionOrHandler]:
		""" Dont allow the player to click to exit the menu, like normal."""
		return None
		
			
class InventoryEventHandler(AskUserEventHandler):
	""" This handler lets the user select an item inside an inventory. What happens depends on the subclass. """

	TITLE = "<missing title>"
	
	def on_render(self, console: tcod.Console) -> None:
		""" Render an inventory menu, which displays the items in the inventory, and the letter to select them.
		Will move to a different position based on where the player is located, so the player can always see where they are.
		"""
		super().on_render(console)
		number_of_items_in_inventory = len(self.engine.player.inventory.items)


		""" Set the Window height, position and width """
		height = number_of_items_in_inventory + 4
		
		if height <= 3:
			height = 3
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		y = 0
		
		width = len(self.TITLE) + 4
		
		console.draw_frame(
			x = x,
			y = y,
			width = width,
			height = height,
			title = self.TITLE,
			clear = True,
			fg = (255, 255, 255),
			bg = (0,0,0),
		)
		
		""" Display inventory items and calculate their total weight """
		total_weight = 0

		if number_of_items_in_inventory > 0:

			for i, item in enumerate(self.engine.player.inventory.items):
				
				""" If item has dimension module, it has a weight and it can be used """
				if item.dimensions:
					total_weight += item.dimensions.weight

				""" Add a character in front of item, check if equippend (add a "E" at the end)
				and display it inside the window) """

				item_key = chr(ord("a") + i)				
				item_string = f"({item_key}) {item.name}"

				is_equipped = self.engine.player.equipment.item_is_equipped(item)
				if is_equipped:
					item_string = f"{item_string} (E)"
					 
				console.print(x + 1, y + i + 1, item_string)
				
			console.print(x +1, y + i + 2, f"{settings.str_weight}: {self.engine.player.dimensions.payload} (Max:{self.engine.player.dimensions.max_payload})")
		else:
			console.print(x + 1, y + 2, "(" + settings.str_empty + ")")
			
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a
		
		if 0 <= index <= 26:
			try:
				selected_item = player.inventory.items[index]
			except IndexError:
				self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)
				return None
			return self.on_item_selected(selected_item)
		return super().ev_keydown(event)

	def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
		""" Called when the user selects a valid item. """
		raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
	""" Handles the activation of a selected item inside the inventory. """
		
	TITLE = settings.str_select_to_use
	
	def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
		""" Consume or equip the item """
		if item.consumable:
			return item.consumable.get_action(self.engine.player)
		elif item.equippable:
			return EquipAction(self.engine.player, item)
		else:
			return None

class InventoryInspectHandler(InventoryEventHandler):
	""" Handles the inspection of a carried item. """
	TITLE = settings.str_select_to_inspect
	
	def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
		""" Return the action for the selected item """
		return InspectEventHandler(self.engine, self.engine.player, item)
		
class InventoryDropHandler(InventoryEventHandler):
	""" Handle dropping an inventory item. """
	
	TITLE = settings.str_select_to_drop
	
	def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
		""" Drop this item. """
		return DropItem(self.engine.player, item)


class InspectEventHandler(AskUserEventHandler):
	""" Inspect a Item in Inventory, IMPROVE TO SHOW MORE DETAILS"""
	TITLE = settings.str_inspect_handler
	def __init__(self, engine: Engine, entity: Actor, item: Item):
		super().__init__(engine)

		self.entity = entity
		self.item = item			# Unpack the tuple		
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		y = 0
		
		width = len(self.TITLE) + 20
		
		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=12,
			title=self.TITLE,
			clear=True,
			fg=(255, 255, 255),
			bg=(0,0,0),
		)
		
		""" If description availible get it """
		if self.item.description:
			description = self.item.description.description_4lines
		else:
			description = [settings.str_no_description,]
		
		""" Show everything """
		console.print(x=x + 1, y = y + 2, string=f"[ {self.item.char} ] {self.item.name}")
		console.print(x=x + 1, y = y + 4, string=f"{settings.str_blocks_movement}: {self.item.blocks_movement}")

		console.print(x=x + 1, y = y + 5, string=f"{settings.str_material}: {self.item.dimensions.material}  {settings.str_weight}: {self.item.dimensions.weight}")
		for i in range(len(description)):
			console.print(x=x + 1, y = y + 7 + i, string=f"{description[i]}")
		



class SelectIndexHandler(AskUserEventHandler):
	""" Handles asking the user for an index on the map. """
	
	def __init__(self, engine: Engine):
		""" Sets the cursor to the player when this handler is constructed. """
		super().__init__(engine)
		player = self.engine.player
		engine.mouse_location = player.x, player.y
		
	def on_render(self, console: tcod.Console) -> None:
		""" Highlight the tile under the cursor. """
		super().on_render(console)
		x, y = self.engine.mouse_location
		console.tiles_rgb["bg"][x,y] = color.white
		console.tiles_rgb["fg"][x,y] = color.black
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		""" Check for key movement or confirmation keys """
		key = event.sym
		if key in MOVE_KEYS:
			modifier = 1	# Holding modifier keys will speed up key movement.
			if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
				modifier *= 5
			if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
				modifier *= 10
			if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
				modifier *= 20
				
			x, y = self.engine.mouse_location
			dx, dy = MOVE_KEYS[key]
			x += dx * modifier
			y += dy * modifier
			# Clamp the cursor index to the map size.
			x = max(0, min(x, self.engine.game_map.width -1 ))
			y = max(0, min(y, self.engine.game_map.height -1 ))
			self.engine.mouse_location = x, y
			return None
		elif key in CONFIRM_KEYS:
			return self.on_index_selected(*self.engine.mouse_location)
		return super().ev_keydown(event)
	
	def ev_mousebuttondown(
		self,
		event: tcod.event.MouseButtonDown
	) -> Optional[ActionOrHandler]:
		""" Left click confirms a selection """
		if self.engine.game_map.in_bounds(*event.tile):
			if event.button == 1:
				return self.on_index_selected(*event.tile)
		return super().ev_mousebuttondown(event)
		
	def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
		""" Called when an index is selected """
		raise NotImplementedError()


class ChooseDirectionHandler(AskUserEventHandler):
	""" Handles asking the user for an index on the map next to the player. """
	
	def __init__(self, engine: Engine):
		""" Sets the cursor to the player when this handler is constructed. """
		super().__init__(engine)
		player = self.engine.player
		engine.mouse_location = player.x, player.y
		
	def on_render(self, console: tcod.Console) -> None:
		""" Highlight the tile under the cursor. """
		super().on_render(console)
		x, y = self.engine.mouse_location
		console.tiles_rgb["bg"][x,y] = color.white
		console.tiles_rgb["fg"][x,y] = color.black
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		""" Check for key movement or confirmation keys """
		key = event.sym
		if key in MOVE_KEYS:
				
			x, y = self.engine.mouse_location
			dx, dy = MOVE_KEYS[key]
			# Clamp the cursor index to the map size.
			x = max(0, min(x, self.engine.game_map.width -1 ))
			y = max(0, min(y, self.engine.game_map.height -1 ))
			self.engine.mouse_location = x, y
			target_x = self.engine.player.x + dx
			target_y = self.engine.player.y + dy
			target_item = self.engine.game_map.get_entity_at_location(target_x, target_y)


			""" Check what is next to the player and give suitable feedback """
			if hasattr(target_item, "consumable"):
				self.engine.message_log.add_message(settings.str_needs_pickup.format(target_item.name))
				return super().ev_keydown(event)
			elif hasattr(target_item, "usable"):
				return target_item.usable.get_action(target_item, self.engine.player)
			elif hasattr(target_item, "fighter"):
				return target_item.fighter.get_action(target_item, self.engine.player)
				
		return super().ev_keydown(event)
	
	def ev_mousebuttondown(
		self,
		event: tcod.event.MouseButtonDown
	) -> Optional[ActionOrHandler]:
		""" Left click confirms a selection """
		if self.engine.game_map.in_bounds(*event.tile):
			if event.button == 1:
				return self.on_index_selected(*event.tile)
		return super().ev_mousebuttondown(event)
		
	def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
		""" Called when an index is selected """
		raise NotImplementedError()

		
class LookHandler(SelectIndexHandler):
	""" Lets the player look around using the keyboard. """
	
	def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
		""" Return to main handler. """
		return MainGameEventHandler(self.engine)
		
class SingleRangedAttackHandler(SelectIndexHandler):
	""" Handles targeting a single enemy. Only the enemy selected will be affected. """
	def __init__(
		self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
	):
		super().__init__(engine)
		
		self.callback = callback
		
	def on_index_selected(self, x: int, y: int) -> Optional[Action]:
		return self.callback((x, y))

class AreaRangedAttackHandler(SelectIndexHandler):
	""" Handles targeting an area within a given radius. Any entity within the area will be affected. """
	def __init__(
		self,
		engine: Engine,
		radius: int,
		callback: Callable[[Tuple[int, int]], Optional[Action]],
	):
		super().__init__(engine)
		
		self.radius = radius
		self.callback = callback
		
	def on_render(self, console: tcod.Console) -> None:
		""" Highlight the tile under the cursor. """
		super().on_render(console)
		
		x,y = self.engine.mouse_location
		
		# Draw a rectangle around the targeted area, so the player can see the affected area.
		console.draw_frame(
			x = x - self.radius - 1,
			y = y - self.radius - 1,
			width = self.radius ** 2,
			height = self.radius ** 2,
			fg = color.red,
			clear = False,
		)
		
	def on_index_selected(self, x: int, y: int) -> Optional[Action]:
		return self.callback((x,y))
					
class MainGameEventHandler(EventHandler):
	""" The event-handler running most of the time, managing the main game loop """

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		action: Optional[Action] = None

		key = event.sym					# get pressed button
		modifier = event.mod			# get modifier buttons
		player = self.engine.player		# player

		if key == tcod.event.K_PERIOD and modifier & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
			""" Use stairs to switch between levels """
			return TakeStairsAction(player)

		elif key == tcod.event.K_ESCAPE:
			""" Exit game and delete temp levels """
			level_files = glob.glob("*.lev")
			print("Deleting temporary levels.")
			for filePath in level_files:
				try:
					os.remove(filePath)	# Deletes the active save file
				except:
					print(f"Error while deleting file : {filePath}")
			raise SystemExit()

		elif key in MOVE_KEYS:
			""" Move around or wait. Moving will automatically attack enemies """
			dx, dy = MOVE_KEYS[key]
			action = BumpAction(player, dx, dy)
		elif key in WAIT_KEYS:
			action = WaitAction(player)

		elif key == tcod.event.K_v:
			""" Check history, get help or check charcter info"""
			return HistoryViewer(self.engine)
		elif key == tcod.event.K_h:
			return HelpScreen(self.engine)
		elif key == tcod.event.K_o:
			return CharacterScreenEventHandler(self.engine)

		elif key == tcod.event.K_g:
			""" Pickup items, or activate, inspect or drop somethin inside inventory """
			action = PickupAction(player)	
		elif key == tcod.event.K_i:
			return InventoryActivateHandler(self.engine)
		elif key == tcod.event.K_p:
			return InventoryDropHandler(self.engine)
		elif key == tcod.event.K_j:
			return InventoryInspectHandler(self.engine)

		elif key == tcod.event.K_l:
			""" Look around or search for hidden stuff """
			return LookHandler(self.engine)
		elif key == tcod.event.K_m:
			action = SearchAction(player)

		#elif key == tcod.event.K_1:
			""" Save or load the player file, for testing only """
			#action = SavePlayerAction(player)
		#elif key == tcod.event.K_2:
			#action = LoadPlayerAction(player)
		#elif key == tcod.event.K_9:
			#""" Print list of game entities to console, for debugging """
			#print(self.engine.game_map.entities)

		elif key == tcod.event.K_b:
			""" Check for sourround shop and activate it """
			
			""" Check wether player is next to a shop"""
			tmp1 = (self.engine.player.x-1, self.engine.player.y)
			tmp2 = (self.engine.player.x+1, self.engine.player.y)
			tmp3 = (self.engine.player.x, self.engine.player.y-1)
			tmp4 = (self.engine.player.x, self.engine.player.y+1)
			found = 0
			if self.engine.game_map.tiles["kind"][tmp1] == b"Shop":
				found =1
			if self.engine.game_map.tiles["kind"][tmp2] == b"Shop":
				found =1
			if self.engine.game_map.tiles["kind"][tmp3] == b"Shop":
				found =1
			if self.engine.game_map.tiles["kind"][tmp4] == b"Shop":
				found =1
			
			""" If shop found activate ShopEventHandler """
			if found == 1:
				return ShopEventHandler(self.engine)
			else:
				self.engine.message_log.add_message(settings.str_no_shop, color.player_atk)
				
		elif key == tcod.event.K_k:
			""" Ranged Attack """
			action = RangedAttackAction(player)

		elif key == tcod.event.K_COMMA:
			""" Interact with objects next to player """
			return ChooseDirectionHandler(self.engine)
		
		else:
			return
				
		return action


class SetupRaceEventHandler(AskUserEventHandler):
	""" Sets the race of the player when starting a new game """
	TITLE = settings.str_setup_race
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		console.draw_frame(
			x=x,
			y=0,
			width=40,
			height=13,
			title=self.TITLE,
			clear=True,
			fg=(255,255,255),
			bg=(0,0,0),
		)
		
		""" Print the possibilities to choose """
		console.print(x= x+1, y=3, string=f"a) " + settings.str_human + " (no adjustments)",)
		console.print(x= x+1, y=4, string=f"b) " + settings.str_elv + " (+2 Dex, -2 Con)",)
		console.print(x= x+1, y=5, string=f"c) " + settings.str_dwarf + " (+2 Con, -2 Cha)",)
		console.print(x= x+1, y=6, string=f"d) " + settings.str_gnome + " (+2 Con, -2 Str)",)
		console.print(x= x+1, y=7, string=f"e) " + settings.str_halfling + " (+2 Dex, -2 Str)",)
		console.print(x= x+1, y=8, string=f"f) " + settings.str_halfelv + " (no adjustments)",)
		console.print(x= x+1, y=9, string=f"g) " + settings.str_halforc + " (+2 Str, -2 Cha)",)
	
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a
		
		""" Setup the player depending on selection """
		if player.race:
			if 0 <= index <= 6:
				if index == 0:
					player.race.race = settings.str_human	
				elif index == 1:
					player.race.race = settings.str_elv
				elif index == 2:
					player.race.race = settings.str_dwarf
				elif index == 3:
					player.race.race = settings.str_gnome
				elif index == 4:
					player.race.race = settings.str_halfling
				elif index == 5:
					player.race.race = settings.str_halfelv
				else:
					player.race.race = settings.str_halforc
			else:
				self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)
			
				return None
			
		""" Adjust the stats of the player """
		player.race.adjust_fighter()
		
		return SetupClassEventHandler(self.engine)
		
	def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
		""" Dont allow the player to click to exit the menu, like normal."""
		return None
		

class SetupClassEventHandler(AskUserEventHandler):
	""" Setup the class of the player when starting a new game """
	TITLE = settings.str_setup_class
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		console.draw_frame(
			x=x,
			y=0,
			width=40,
			height=16,
			title=self.TITLE,
			clear=True,
			fg=(255,255,255),
			bg=(0,0,0),
		)
		
		""" Print possiblities to choose from """
		console.print(x= x+1, y=3, string=f"a) " + settings.str_barbarian + " (+1 BAB, W12 Hit Dice)",)
		console.print(x= x+1, y=4, string=f"b) " + settings.str_bard + " (+0 BAB, W6 Hit Dice)",)
		console.print(x= x+1, y=5, string=f"c) " + settings.str_druid + " (+0 BAB, W8 Hit Dice)",)
		console.print(x= x+1, y=6, string=f"d) " + settings.str_sourcerer + " (+0 BAB, W4 Hit Dice)",)
		console.print(x= x+1, y=7, string=f"e) " + settings.str_fighter + " (+1 BAB, W10 Hit Dice)",)
		console.print(x= x+1, y=8, string=f"f) " + settings.str_cleric + " (+0 BAB, W8 Hit Dice)",)
		console.print(x= x+1, y=9, string=f"g) " + settings.str_wizard + " (+0 BAB, W4 Hit Dice)",)
		console.print(x= x+1, y=10, string=f"h) " + settings.str_monk + " (+0 BAB, W8 Hit Dice)",)
		console.print(x= x+1, y=11, string=f"i) " + settings.str_paladin + " (+1 BAB, W10 Hit Dice)",)
		console.print(x= x+1, y=12, string=f"j) " + settings.str_rouge + " (+0 BAB, W6 Hit Dice)",)
		console.print(x= x+1, y=13, string=f"k) " + settings.str_ranger + " (+1 BAB, W8 Hit Dice)",)
		
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a
		
		if 0 <= index <= 10:
			if index == 0:
				player.clas.clas = settings.str_barbarian
			elif index == 1:
				player.clas.clas = settings.str_bard
			elif index == 2:
				player.clas.clas = settings.str_druid
			elif index == 3:
				player.clas.clas = settings.str_sourcerer
			elif index == 4:
				player.clas.clas = settings.str_fighter
			elif index == 5:
				player.clas.clas = settings.str_cleric
			elif index == 6:
				player.clas.clas = settings.str_wizard
			elif index == 7:
				player.clas.clas = settings.str_monk
			elif index == 8:
				player.clas.clas = settings.str_paladin
			elif index == 9:
				player.clas.clas = settings.str_rouge
			else:
				player.clas.clas = settings.str_ranger
		else:
			self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)		
			return None
		
		""" Setup the HP according to clas """	
		player.clas.adjust_fighter()
		
		return CharacterScreenEventHandler(self.engine)
		
	def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
		""" Dont allow the player to click to exit the menu, like normal. """
		return None


class GameOverEventHandler(EventHandler):
	""" Handles the exit of the game """
	def on_quit(self) -> None:
		""" Handle exiting out of a finished game. """
		if os.path.exists(settings.save_file):
			print("Savefile deleted.")
			os.remove(settings.save_file)	# Deletes the active save file
		raise exceptions.QuitWithoutSaving()	# Avoid saving a finished game.
		
	def ev_quit(self, event: tcod.event.Quit) -> None:
		self.on_quit()

	def ev_keydown(self, event: tcod.event.KeyDown) -> None:
		if event.sym == tcod.event.K_ESCAPE:
			self.on_quit()
			
		
CURSOR_Y_KEYS= {
	tcod.event.K_UP: -1,
	tcod.event.K_DOWN: 1,
	tcod.event.K_PAGEUP: -10,
	tcod.event.K_PAGEDOWN: 10,
}

class HistoryViewer(EventHandler):
	""" Print the history on a larger window which can be navigated. """
	
	def __init__(self, engine: Engine):
		super().__init__(engine)
		self.log_length = len(engine.message_log.messages)
		self.cursor = self.log_length - 1
		
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)	# Draw the main state as the background.
		
		log_console = tcod.Console(console.width -6, console.height -6)
		
		""" Draw frame with a custom title """
		log_console.draw_frame(0,0, log_console.width, log_console.height)
		log_console.print_box(
			0, 0, log_console.width, 1, "┤" +settings.str_message_history + "├", alignment=tcod.CENTER
		)
		
		# Render the message log using the cursor parameter.
		self.engine.message_log.render_messages(
			log_console,
			1,
			1,
			log_console.width -2,
			log_console.height -2,
			self.engine.message_log.messages[: self.cursor + 1],
		)
		log_console.blit(console, 3, 3)
		
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
		# Fancy conditional movement to make it feed right.
		if event.sym in CURSOR_Y_KEYS:
			adjust = CURSOR_Y_KEYS[event.sym]
			if adjust < 0 and self.cursor == 0:
				# Only move form the top to the bottom when you are on the edge.
				self.cursor = self.log_length - 1
			elif adjust > 0 and self.cursor == self.log_length -1:
				# same with bottom to top movement.
				self.cursor = 0
			else:
				# Otherwise move while stying clamped to the bounds of the history
				self.cursor = max(0, min(self.cursor + adjust, self.log_length -1))
		elif event.sym == tcod.event.K_HOME:
			self.cursor = 0 # Move directly to top
		elif event.sym == tcod.event.K_END:
			self.cursor = self.log_length - 1 # move directly to last message
		else: # any other key moves bakc to the main game state.
			return MainGameEventHandler(self.engine)
		return None
		
class ChestInventoryHandler(AskUserEventHandler):
	""" Input handler to move things from e.g. chest inventory to the players inventory """
	
	parent: Item
	TITLE = settings.str_content

	def __init__(self, engine: Engine, target: Item, consumer: Player, callback: Callable[Optional[Action]] = None):
		super().__init__(engine)

		self.target = target
		self.consumer = consumer
		self.callback = callback
	
	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		target_number_of_items_in_inventory = len(self.target.inventory.items)
		consumer_number_of_items_in_inventory = len(self.consumer.inventory.items)

		height = self.target.inventory.capacity + self.consumer.inventory.capacity + 6	
		
		""" List content for debugging on terminal """
		#self.target.usable.list_content()
			
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		y = 0
		
		width = len(self.TITLE) + 30	
		console.draw_frame(x = x, y = y, width = width, height = height, title = self.TITLE, clear = True, fg = (255, 255, 255), bg = (0,0,0),)
		
		#Display inventory items and calculate the total weight
		chest_total_weight = 0
		player_total_weight = 0
		
		console.print(x + 1, y + 1, f"{settings.str_content} {self.target.name}")

		""" Cycle trough content of target inventory """
		if target_number_of_items_in_inventory > 0:
			""" Remove the Chest from the list in case it is carried, not to place it into itself
			No idea anymore if this makes any sense """
			inventory_items = self.target.inventory.items
			
			part_of_inventory = 0
			if self.target in inventory_items:
				inventory_items.pop(inventory_items.index(self.target))
				part_of_inventory = 1
			
			""" Cycle trough items and show as a list including weight and calculate total weight """
			for i, item in enumerate(inventory_items):
				if item.dimensions:
					chest_total_weight += item.dimensions.weight
					item_string = f"{item.name} ({settings.str_weight}: {item.dimensions.weight})"
				else:
					item_string = f"{item.name}"

				item_key = chr(ord("1") + i)				
				item_string = f"({item_key}) {item_string}"
				console.print(x + 1, y + i + 2, item_string)
			
			if part_of_inventory == 1:
				inventory_items.append(self.target)
			
		else:
			console.print(x + 1, y + 2, "(" + settings.str_empty + ")")

		""" Display consumers inventory """
		console.print(x + 1, y + self.target.inventory.capacity + 3, f"{settings.str_content} {self.consumer.name}")
		
		if consumer_number_of_items_in_inventory > 0:

			""" Remove the Chest from the list in case it is carried, not to place it into itself """
			inventory_items = self.consumer.inventory.items
			part_of_inventory = 0
			if self.target in inventory_items:
				inventory_items.pop(inventory_items.index(self.target))
				part_of_inventory = 1

			""" Cycle trough items and show as a list including weight and calculate total weight """
			for i, item in enumerate(inventory_items):
				if item.dimensions:
					player_total_weight += item.dimensions.weight
					item_string = f"{item.name} ({settings.str_weight}: {item.dimensions.weight})"
				else:
					item_string = f"{item.name}"

				item_key = chr(ord("a") + i)				
				item_string = f"({item_key}) {item_string}"
				console.print(x + 1, y + self.target.inventory.capacity + 3 + i + 2, item_string)

			
			"""
				if item.dimensions:
					player_total_weight += item.dimensions.weight
				item_key = chr(ord("a") + i)
								
				item_string = f"({item_key}) {item.name}"
					 
				console.print(x + 1, y + i + self.target.inventory.capacity + 5, item_string)
			#print(f"Gewicht: {player_total_weight}")
			
			"""


			if part_of_inventory == 1:
				inventory_items.append(self.target)
			
		else:
			console.print(x + 1, y + self.target.inventory.capacity + 5, "(" + settings.str_empty + ")")
		
		
		
	def ev_mousebuttondown(
		self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
		""" Dont allow the player to click to exit the menu, like normal. """
		return None
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		""" Move stuff between inventories """
		player = self.engine.player
		key = event.sym

		index1 = key - tcod.event.K_1
		index2 = key - tcod.event.K_a
		
		if key == tcod.event.K_ESCAPE:
			return MainGameEventHandler(self.engine)
		
		if 0 <= index1 <= len(self.target.inventory.items):
			try:
				selected_item = self.target.inventory.items[index1]
				source = self.target
				target = self.consumer
			except IndexError:
				self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)
				return None
			return self.on_item_selected(source, target, selected_item)

		elif 0 <= index2 <= len(self.consumer.inventory.items):
			try:
				selected_item = self.consumer.inventory.items[index2]
				source = self.consumer
				target = self.target
			except IndexError:
				self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)
				return None			
			
			return self.on_item_selected(source, target, selected_item)

	def on_item_selected(self, source: Entity, target: Entity, item: Item) -> Optional[ActionOrHandler]:
		""" Called when the user selects a valid item. """
		return MoveItem(source = source, target = target, item = item)

class AskSelectionHandler(AskUserEventHandler):
	""" Handler to show different possibilites to choose from """
	def __init__(self, engine: Engine, actor: Actor, target: Target, callback: Callable[Optional[Action]], option1: Optional[str] = None, option2: Optional[str] = None, option3: Optional[str] = None,):
		super().__init__(engine)

		self.callback = callback
		self.option1 = option1
		self.option2 = option2
		self.option3 = option3
		self.actor = actor
		self.target = target
		self.title = self.target.name

	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)
		
		""" Render either on left or right side of the screen, depending on player position """
		if self.engine.player.x <= 30:
			x = 40
		else:
			x = 0
			
		console.draw_frame(x=x, y=0, width=40, height=13, title=self.title, clear=True, fg=(255,255,255), bg=(0,0,0),)
		
		""" Show up to 3 options as well as a cancel option """
		console.print(x= x+1, y=3, string=settings.str_decicion,)
		if self.option1:
			console.print(x= x+1, y=5, string=f"a) {self.option1}",)
		if self.option2:
			console.print(x= x+1, y=6, string=f"b) {self.option2}",)
		if self.option3:
			console.print(x= x+1, y=7, string=f"c) {self.option3}",)
		
		if self.option3:
			prefix = "d)"
		elif self.option2:
			prefix = "c)"
		elif self.option1:
			prefix = "b)"
		else:
			prefix = "a)"
				
		console.print(x= x+1, y=9, string=prefix +" " + settings.str_do_nothing,)
		
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a
		
		if player.race:
			if 0 <= index <= 4:
				if index == 0:
					return self.callback(1)

				elif index == 1:
					return self.callback(2)

				elif index == 2:
					return MainGameEventHandler(self.engine)
			else:
				self.engine.message_log.add_message(settings.str_invalid_entry, color.invalid)
			
				return MainGameEventHandler(self.engine)
			
		return None
		
	def ev_mousebuttondown(
		self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
		""" Dont allow the player to click to exit the menu, like normal. """
		return None

