from __future__ import annotations

import copy
import math

from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union
from random import randint, choice

from render_order import RenderOrder

import settings
import color

if TYPE_CHECKING:
	from components.ai import BaseAI
	from components.consumable import Consumable
	from components.equipment import Equipment
	from components.equippable import Equippable
	from components.usable import Usable, Ironbar
	from components.fighter import Fighter
	from components.inventory import Inventory
	from components.level import Level
	from components.banking import Banking
	from components.race import Race
	from components.clas import Clas
	from components.body import Body
	from components.dimensions import Dimensions
	from components.lock import Lock
	from components.description import Description
	from game_map import GameMap
	
T = TypeVar("T", bound="Entity")


class Entity:
	""" Basic object where all other object refer to """
	parent: Union[GameMap, Inventory]

	def __init__(
		self,
		parent: Optional[GameMap] = None,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed>",
		speed_points : int = 100,
		blocks_movement: bool = False,
		render_order: RenderOrder = RenderOrder.CORPSE,
	):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.speed_points = speed_points
		self.blocks_movement = blocks_movement
		self.render_order = render_order
				
		if parent:
			""" Set entities paren in case it is provided """
			self.parent = parent
			parent.entities.add(self)
	
	@property
	def gamemap(self) -> GameMap:
		return self.parent.gamemap
		
	def encrypted_name(self) -> str:
		""" Generate an encrypted name """
		_encrypted_name = ""
		_list = ("a", "b", "c", "d", "e", "f", "g", "h","i","j","k","l","m","n","o","p","q","q","r","s","t","u","v","w","x","y", "z")
		words = randint(2,3)
		x = 0
		while x < words:
			letters = randint(3, 6)
			y = 0
			while y < letters:
				_encrypted_name += choice(_list)
				y += 1
				
			_encrypted_name += " "
			x += 1
		return _encrypted_name


	def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
		""" Spawn a copy of this instance at the given location.
		
		call initialize() to randomize/ initialize the clone after deepcopy """
		
		clone = copy.deepcopy(self)
		
		""" Check witch modules the entity has and initialize them if possible """
		if hasattr(clone, "consumable"):
			try:
				clone.consumable.initialize()
			except:
				pass	
		if hasattr(clone, "fighter"):
			try:
				clone.fighter.initialize()
			except:
				pass
		if hasattr(clone, "equippable"):
			try:
				clone.equippable.initialize()
			except:
				pass
		if hasattr(clone, "usable"):
			try:
				clone.usable.initialize()
			except:
				pass
		
		""" Set x,y coords and add clone to gamemaps entity list """
		clone.x = x
		clone.y = y
		clone.parent = gamemap	
		gamemap.entities.add(clone)

		""" In case entity has inventory, add all inventory items to spawned_items list. list is used for decoding scrolls
		as well as populating chests """
		if clone.inventory:
			for item in clone.inventory.items:
				gamemap.engine.spawned_items.append(item)
		
		""" Add clone to list of spawned items """			
		if isinstance(clone, Item):
			gamemap.engine.spawned_items.append(clone)

		return clone
		

	def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
		""" Place the entity at a new location, used for moving entities between game_maps """
		
		self.x = x
		self.y = y
		
		""" Remove entity from game_map list in case it is """
		if gamemap:
			if hasattr(self, "parent"): # Possibly uninitalized.
				if self.parent is self.gamemap:
					self.gamemap.entities.remove(self)

			self.parent = gamemap
			gamemap.entities.add(self)


	def distance(self, x: int, y: int) -> float:
		""" Return the distance between the current entity and the given (x,y) coordinate """
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	def move(self, dx: int, dy: int) -> None:
		""" Move entity by dx, dy offset """
		self.x += dx
		self.y += dy

	"""
	def randomize(self, min: int, max: int) -> int:
		# Return random number between min and max
		return randint(min, max)
	"""

	def generate_name(self, syllables = 4) -> str:
		""" Generates a random name based on the given number of syllables """
		syllable = 0
		name = ""
		syllables_list = ("me", "co", "tur", "ban", "har", "so", "gat", "ly", "fer", "tro", "bun", "tir")
		
		while syllable < syllables:
			name += choice(syllables_list)
			syllable += 1

		return name.capitalize()


class Actor(Entity):
	""" Actor is a moving entity """
	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255,255,255),
		name: str ="<Unnamed Actor>",
		attitute: str="<Unknown>",
		pass_door = True,
		fov = 8,
		ai_cls: Type[BaseAI],
		equipment: Optional[Equipment] = None,
		fighter: Optional[Fighter] = None,
		inventory: Optional[Inventory] = None,
		level: Optional [Level] = None,
		banking: Optional[Banking] = None,
		dimensions: Optional[Dimensions] = None,
		race: Optional[Race] = None,
		clas: Optional[Clas] = None,
		skills: Optional[Skills] = None,
		body: Optional[Body] = None,
		description: Optional[Description] = None,
	):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=True,
			render_order=RenderOrder.ACTOR,
		)
		
		""" Set up the actors stats """
		self.attitute = attitute			# Friendly or not
		self.pass_door = pass_door			# allowed to pass doors (open) or not
		
		self.fov = fov						# Stores the actual FOV distance
		self.previous_fov = fov				# Stores the FOV distance before it changed
		self.normal_fov = fov				# Stores the normal FOV distance, needed in case several FOV changes happened one after the other
		
		self.ai: Optional[BaseAI] = ai_cls(self)	# the AI used
		
		""" Set up modules which might be attached """
		self.equipment: Equipment = equipment
		if self.equipment:
			self.equipment.parent = self
		
		self.fighter = fighter
		if self.fighter:
			self.fighter.parent = self
		
		self.inventory = inventory
		if self.inventory:
			self.inventory.parent = self
		
		self.level = level
		if self.level:
			self.level.parent = self
		
		self.banking = banking
		if self.banking:
			self.banking.parent = self
		
		self.dimensions = dimensions
		if self.dimensions:
			self.dimensions.parent = self
		
		self.race = race
		if self.race:
			self.race.parent = self
			
		self.clas = clas
		if self.clas:
			self.clas.parent = self
			
		self.skills = skills
		if self.skills:
			self.skills.parent = self
			
		self.body = body
		if self.body:
			self.body.parent = self
			
		self.description = description
		if self.description:
			self.description.parent = self
			
	@property
	def is_alive(self) -> bool:
		""" Retruns True as long as this actor can perform actions."""
		return bool(self.ai)

	def dire(self, factor) -> None:
		""" Generate a dire or a minor version of the actor. Negative factor will create minor version. See
		examples at entity_factories.py """

		""" TODO: base_damage should be improved in the future to give more flexible output,
		e.g. based on the dice no of sides """
		
		if factor > 0:
			""" Dire version """
			self.name = f"{settings.str_dire} {self.name}"
			self.color = color.bordeaux
			self.level.increase_hp()
			self.fighter.base_damage = str(self.fighter.base_damage + "+2")
			self.level.xp_given = int(self.level.xp_given * factor)
			self.fighter.base_strength = int(self.fighter.base_strength * factor)
			self.fighter.base_constitution = int(self.fighter.base_constitution * factor)
			self.fighter.base_armor_class = int(self.fighter.base_armor_class  * factor)

		else:
			""" Minor version """
			self.name = f"{settings.str_minor} {self.name}"
			self.color = color.grey
			self.level.increase_hp(amount = -1)
			self.fighter.base_damage = str(self.fighter.base_damage + "+-2")
			self.level.xp_given = int(self.level.xp_given / factor * -1)
			self.fighter.base_strength = int(self.fighter.base_strength / factor)
			self.fighter.base_constitution = int(self.fighter.base_constitution / factor)
			self.fighter.base_armor_class = int(self.fighter.base_armor_class  / factor)
		
		return

class Item(Entity):
	""" Items can be picked up """

	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed Item>",
		kind: str = "<Unknown kind>",
		value: int = 1,
		price: int = 0,
		hands: int = 1,
		consumable: Optional[Consumable] = None,
		equippable: Optional[Equippable] = None,
		dimensions: Optional[Dimensions] = None,
		inventory: Optional[Inventory] = None,
		description: Optional[Description] = None,
		lock: Optional[Lock] = None,
	):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=False,
			render_order=RenderOrder.ITEM,
		)
		
		self.kind = kind		# Kind of item (scroll, etc.,,,)
		self.value = value		# Value is used for different things, like the number of arrows or the amount of coins
		self.hands = hands		# No of hands necessary

		""" Setup optional modules """
		self.consumable = consumable
		if self.consumable:
			self.consumable.parent = self		
		
		self.equippable = equippable
		if self.equippable:
			self.equippable.parent = self
		
		self.dimensions = dimensions
		if self.dimensions:
			self.dimensions.parent = self
			
		self.inventory = inventory
		if self.inventory:
			self.inventory.parent = self
			
		self.lock = lock
		if self.lock:
			self.lock.parent = self
			
		self.description = description
		if self.description:
			self.description.parent = self
			
			
class Furniture(Entity):
	""" Furniture can be used but not picked up """

	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed Furniture>",
		kind: str = "<Unknown kind>",
		walkable: bool = False,
		transparent: bool = False,
		value: int = 1,
		dimensions: Optional[Dimensions] = None,
		inventory: Optional[Inventory] = None,
		description: Optional[Description] = None,
		usable: Optional[Usable] = None,
		lock: Optional[Lock] = None,
	):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=True,
			render_order=RenderOrder.ITEM,
		)
		
		self.value = value					# Value is used internal to distinguish different types (e.g. hidden, normal door)
		self.kind = kind					# Kind of furniture
		self.walkable = walkable			# can be walked on or not
		self.transparent = transparent		# blocks FOV or not
		

		""" Initialize optional modules """
		self.dimensions = dimensions
		if self.dimensions:
			self.dimensions.parent = self
			
		self.inventory = inventory
		if self.inventory:
			self.inventory.parent = self

		self.description = description
		if self.description:
			self.description.parent = self
			
		self.lock = lock
		if self.lock:
			self.lock.parent = self
			
		self.usable = usable
		if self.usable:
			self.usable.parent = self

	def reveal(self) -> None:
		""" When hidden furniture is found """
		if self.usable:
			self.usable.reveal()


