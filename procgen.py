from __future__ import annotations

import random
import tcod
import copy

from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING

import settings
import entity_factories
import tile_types

from game_map import GameMap


if TYPE_CHECKING:
	from engine import Engine
	from entity import Entity

max_items_by_floor = [
	(1, 1),		# Floor Number, Max Number Items per room
	(2, 1),
	(3, 1),
	(4, 1),
	(6, 1),
	(8, 1),
	(10, 1),
]

max_monsters_by_floor = [
	(1, 1),		# Floor Number, Max Number Monsters per room
	(2, 1),
	(4, 1),
	(6, 1),
	(8, 2),
	(10, 4),
]

max_traps_by_floor = [
	(1, 1),		# Floor Number, Max Number of Traps per room
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
	0: [(entity_factories.arrow, 1), (entity_factories.health_potion, 1), (entity_factories.confusion_scroll, 5),(entity_factories.vision_scroll, 1),
		(entity_factories.money, 5),],
	2: [(entity_factories.arrow, 1), (entity_factories.hat, 5), (entity_factories.club, 2), (entity_factories.sm_wo_shield, 2),
		(entity_factories.lockpick, 1), (entity_factories.leather_armor, 2), (entity_factories.lockpick_scroll, 5), (entity_factories.blinded_scroll, 5),],
	3: [(entity_factories.arrow, 1),  (entity_factories.health_potion, 1), (entity_factories.dumb_scroll, 5), (entity_factories.hat, 1),
		(entity_factories.sm_wo_shield, 1), (entity_factories.wooden_bow, 1), (entity_factories.chain_mail, 1), (entity_factories.spear, 2)],
	4: [(entity_factories.arrow, 1), (entity_factories.amputation_scroll, 2), (entity_factories.lockpick_master, 1), (entity_factories.boots, 1),
		(entity_factories.leather_armor, 1)],
	5: [(entity_factories.arrow, 1), (entity_factories.health_potion, 1), (entity_factories.lightning_scroll, 5),
		(entity_factories.vision_scroll, 1), (entity_factories.la_wo_shield, 2), (entity_factories.sword, 1), (entity_factories.hat, 1),
		(entity_factories.wooden_bow, 1),],
	6: [(entity_factories.arrow, 1), (entity_factories.fireball_scroll, 5), (entity_factories.chain_mail, 10), (entity_factories.lightning_scroll, 5),
		(entity_factories.la_wo_shield, 2), (entity_factories.axe, 2)],
	7: [(entity_factories.arrow, 1), (entity_factories.health_potion, 1), (entity_factories.scale_armor, 5), (entity_factories.amputation_scroll, 5),
		(entity_factories.sword, 1), (entity_factories.wooden_bow, 1), (entity_factories.fireball_scroll, 5)],
	8: [(entity_factories.arrow, 1), (entity_factories.boots, 10), (entity_factories.scale_armor, 2), (entity_factories.sword, 5)],
	10: [(entity_factories.arrow, 1), (entity_factories.health_potion, 1), (entity_factories.money, 10), (entity_factories.tower_shield, 2)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
	0: [(entity_factories.minor_ant, 5), (entity_factories.ant, 5), (entity_factories.minor_rat, 5), (entity_factories.sheep, 5),],
	2: [(entity_factories.minor_rat, 5), (entity_factories.rat, 10), (entity_factories.dire_rat, 2)],	
	4: [(entity_factories.troll, 5),(entity_factories.orc, 10, (entity_factories.dire_rat), 2)],
	5: [(entity_factories.sm_zombie, 10), (entity_factories.orc, 10), (entity_factories.dog, 2)],
	7: [(entity_factories.sm_zombie, 30), (entity_factories.dog, 5), (entity_factories.dire_rat, 10)],
	8: [(entity_factories.dog, 30), (entity_factories.troll, 5), (entity_factories.dragon,2)],
	10: [(entity_factories.dragon, 30), (entity_factories.troll, 10), (entity_factories.sm_zombie, 10)],
}

trap_chances: Dict[int, List[Tuple[Entity, int]]] = {
	0: [(entity_factories.trap, 1)],
}


def get_max_value_for_floor(
	weighted_chances_by_floor: List[Tuple[int, int]], floor: int
) -> int:
	current_value = 0
	
	for floor_minimum, value in weighted_chances_by_floor:
		if floor_minimum > floor:
			break
		else:
			current_value = value
			
	return current_value

def get_entities_at_random(
	weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
	number_of_entities: int,
	floor: int,
) -> List[Entity]:
	entity_weighted_chances = {}
	
	for key, values in weighted_chances_by_floor.items():
		if key > floor:
			break
		else:
			for value in values:
				entity = value[0]
				weighted_chance = value[1]
				
				entity_weighted_chances[entity] = weighted_chance
				
	entities = list(entity_weighted_chances.keys())
	entity_weighted_chance_values = list(entity_weighted_chances.values())
	
	chosen_entities = random.choices(
		entities, weights=entity_weighted_chance_values, k=number_of_entities
	)
	
	return chosen_entities


class RectangularRoom:
	""" Everything will be spawned inside rooms, rectangular_map consists of real rooms, drunkjard_maps will
	be checked for open spaces which will be added to room list, but are rectangular rooms in reality """
	def __init__(self, x: int, y: int, width: int, height: int):
		self.x1 = x
		self.y1 = y
		self.x2 = x + width
		self.y2 = y + height
		self._roomtype = "<Unknown room>"
		
	@property
	def center(self) -> Tuple[int, int]:
		""" Returns the Center of the room """
		center_x = int((self.x1 + self.x2) / 2)
		center_y = int((self.y1 + self.y2) / 2)
		
		return center_x, center_y
	
	@property
	def roomtype(self) -> str:
		""" Returns the type of the room """
		return self._roomtype
		
	@roomtype.setter
	def roomtype(self, roomtype: str) -> None:
		""" Sets the type of the room """
		self._roomtype = roomtype
	
	@property
	def area(self) -> int:
		""" Returns the complete area of the room, eventually including outer walls """
		return (self.x2 - self.x1) * (self.y2 - self.y1)

	@property
	def height(self) -> int:
		return (self.y2 - self.y1)

	@property
	def width(self) -> int:
		return (self.x2 - self.x1)
	
	
	@property
	def complete(self) -> Tuple[int, int]:
		""" Return the complete area of this room as a 2D array index """
		return slice(self.x1, self.x2), slice(self.y1, self.y2)
		
	@property
	def inner(self) -> Tuple[slice, slice]:
		""" Return the inner area of this room as a 2D array index. """
		return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
		
	def intersects(self, other: RectangularRoom) -> bool:
		""" Return True if this room overlaps with another RectangularRoom """
		return (
			self.x1 <= other.x2
			and self.x2 >= other.x1
			and self.y1 <= other.y2
			and self.y2 >= other.y1
		)


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int, ) -> None:
	""" Place entities inside the room on the actual game map, needs floor_number to get how many to add """
	number_of_monsters = random.randint(0, get_max_value_for_floor(max_monsters_by_floor, floor_number))
	number_of_items = random.randint(0, get_max_value_for_floor(max_items_by_floor, floor_number))
	number_of_traps = random.randint(0, get_max_value_for_floor(max_traps_by_floor, floor_number))
	
	""" Get the entities which should be added to the map """
	monsters: List[Entity] = get_entities_at_random(enemy_chances, number_of_monsters, floor_number)
	items: List[Entity] = get_entities_at_random(item_chances, number_of_items, floor_number)			
	traps: List[Entity] = get_entities_at_random(trap_chances, number_of_traps, floor_number)
	
	""" Place entities, check if tile is floor and not occupied by another entity """			
	for entity in monsters + items + traps:
		x, y = 1, 1
		while (dungeon.tiles[x,y]["kind"]) != b"Floor":
			# Get new xy coord in room until not occupied by wall, should not happen anyway
			x = random.randint(room.x1 + 1, room.x2 - 1)
			y = random.randint(room.y1 + 1, room.y2 - 1)
		
		""" Place entity if not occupied by another entity """
		if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
			entity.spawn(dungeon, x, y)		

def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
	""" Return a L-shaped tunnel between two points. Used for connecting rooms."""
	x1, y1 = start
	x2, y2 = end
	if random.random() < 0.5: # 50% chance
		# Move horizontally, then vertically
		corner_x, corner_y = x2, y1
	else:
		# Move vertically, then horizontally
		corner_x, corner_y = x1, y2
		
	# Generate the coordinates for this tunnel
	for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
		yield x, y
	for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
		yield x, y

def bitmasking( dungeon: GameMap, x: int, y: int, kind: str) -> int:
	""" 
	+---+---+---+	8-bit bitmasking of surrounding tiles, used for checking
	| 1 | 2 | 4 |   places were doors can be inserted
	+---+---+---+
	|128|   | 8 |
	+---+---+---+
	| 64| 32| 16|
	+---+---+---+
	"""
	result = 0
	# NW
	if (dungeon.tiles[x-1, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 1
	# N
	if (dungeon.tiles[x, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 2
	# NE
	if (dungeon.tiles[x+1, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 4
	# E
	if (dungeon.tiles[x+1, y]["kind"] == bytes(kind, "utf-8")):
		result += 8
	# SE
	if (dungeon.tiles[x+1, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 16
	# S
	if (dungeon.tiles[x, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 32
	# SW
	if (dungeon.tiles[x-1, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 64
	# W
	if (dungeon.tiles[x-1, y]["kind"] == bytes(kind, "utf-8")):
		result += 128
	
	return result

def bitmasking24bit( dungeon: GameMap, x: int, y: int, kind: str) -> int:
	"""
	Bitmasking of 5x5 area, used for checking open spaces in drunkjard maps to find suitable places for rooms
	+--------+-------+-------+-------+-------+
	|   WWNN |  WNN  |  NN   |  ENN  |  EENN |
	|  0x100 | 0x200 | 0x400 | 0x800 |0x1000 |
	+--------+-------+-------+-------+-------+
	|    WWN |   WN  |   N   |   EN  |  EEN  |	
	|0x800000|  0x1  |  0x2  |  0x4  |0x2000 |
	+--------+-------+-------+-------+-------+
	|    WW  |   W   |       |   E   |   EE  |
	|0x400000|  0x80 |       |  0x8  |0x4000 |
	+--------+-------+-------+-------+-------+
	|   WWS  |  WS   |   S   |  ES   |  EES  |
	|0x200000|  0x40 |  0x20 |  0x10 |0x8000 |
	+--------+-------+-------+-------+-------+
	|  WWSS  |  WSS  |  SS   |  ESS  |  EESS |
	|0x100000|0x80000|0x40000|0x20000|0x10000|
	+--------+-------+-------+-------+-------+
	
	0x  0   0   0   0   .  0   0   0   0   .  0   0  0    0   .  0   0  0   0   .  0  0  0  0  .  0  0  0  0
       WWN  WW WWS WWSS . WSS  SS ESS EESS . EES EE EEN  EENN . ENN NN WNN WWNN .  W  WS S ES  .  E  EN N  WN

	5x5 large:	 	1111 1111 1111 1111 1111 1111	0xFFFFFF
	3x3 Middle: 	0000 0000 0000 0000 1111 1111	0x0000FF
	5x3 3wide:		0000 1110 0000 1110 1111 1111	0x0E0EFF
	5x3 5wide:		1110 0000 1110 0000 1111 1111	0xE0E0FF
		"""

	result = 0
	if (dungeon.tiles[x-1, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 0x1
	if (dungeon.tiles[x, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 0x2
	if (dungeon.tiles[x+1, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 0x4
	if (dungeon.tiles[x+1, y]["kind"] == bytes(kind, "utf-8")):
		result += 0x8
	if (dungeon.tiles[x+1, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 0x10
	if (dungeon.tiles[x, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 0x20
	if (dungeon.tiles[x-1, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 0x40
	if (dungeon.tiles[x-1, y]["kind"] == bytes(kind, "utf-8")):
		result += 0x80
	if (dungeon.tiles[x-2, y-2]["kind"] == bytes(kind, "utf-8")):
		result += 0x100
	if (dungeon.tiles[x-1, y-2]["kind"] == bytes(kind, "utf-8")):
		result += 0x200
	if (dungeon.tiles[x, y-2]["kind"] == bytes(kind, "utf-8")):
		result += 0x400
	if (dungeon.tiles[x+1, y-2]["kind"] == bytes(kind, "utf-8")):
		result += 0x800
	if (dungeon.tiles[x+2, y-2]["kind"] == bytes(kind, "utf-8")):
		result += 0x1000
	if (dungeon.tiles[x+2, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 0x2000
	if (dungeon.tiles[x+2, y]["kind"] == bytes(kind, "utf-8")):
		result += 0x4000
	if (dungeon.tiles[x+2, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 0x8000
	if (dungeon.tiles[x+2, y+2]["kind"] == bytes(kind, "utf-8")):
		result += 0x10000
	if (dungeon.tiles[x+1, y+2]["kind"] == bytes(kind, "utf-8")):
		result += 0x20000
	if (dungeon.tiles[x, y+2]["kind"] == bytes(kind, "utf-8")):
		result += 0x40000
	if (dungeon.tiles[x-1, y+2]["kind"] == bytes(kind, "utf-8")):
		result += 0x80000
	if (dungeon.tiles[x-2, y+2]["kind"] == bytes(kind, "utf-8")):
		result += 0x100000
	if (dungeon.tiles[x-2, y+1]["kind"] == bytes(kind, "utf-8")):
		result += 0x200000
	if (dungeon.tiles[x-2, y]["kind"] == bytes(kind, "utf-8")):
		result += 0x400000
	if (dungeon.tiles[x-2, y-1]["kind"] == bytes(kind, "utf-8")):
		result += 0x800000

	return result

def random_tile_in_map(dungeon, map_width, map_height, tile) -> Tuple:
	""" Randomly tests places on the map if they are of the given kind. If so return it. Starts at random location
	BUG to fix: Might go into an endless loop in case no tile of that kind is present """

	start_point = (random.randint(0, map_width-1), random.randint(0, map_height-1))
	while (dungeon.tiles[start_point]["kind"]) != tile:
		start_point = (random.randint(0, map_width-1), random.randint(0, map_height-1))
	
	return start_point


def random_turn(heading) -> Tuple:
	""" Returns either a left or a right turn for the given heading. Used in drunkjards walk.
		-1,-1  0,-1  1,-1
		-1,0    x    1,0
		-1,1   0,1   1,1 
	"""
	if heading == (-1, 0):
		new_heading = random.choice(((-1,-1), (-1,1),))
	elif heading == (-1, 1):
		new_heading = random.choice(((-1,0), (0,1),))
	elif heading == (0, 1):
		new_heading = random.choice(((-1,1), (1,1),))
	elif heading == (1, 1):
		new_heading = random.choice(((0,1), (1,0),))
	elif heading == (1, 0):
		new_heading = random.choice(((1,1), (1,-1),))
	elif heading == (1, -1):
		new_heading = random.choice(((1,0), (0,-1),))
	elif heading == (0, -1):
		new_heading = random.choice(((-1,-1), (1,-1),))
	elif heading == (-1, -1):
		new_heading =random.choice(((-1,0), (0,-1),))
	else:
		print(f"Heading Error! {type(heading)}")
	return new_heading

def remove_single_walls(dungeon, map_width, map_height) -> None:
	""" Remove single walls (pillars) from the map """
	for i in range(1, map_width-1):
		for j in range(1, map_height-1):
			result = 0
			if (dungeon.tiles[i, j]["kind"]) == b"Wall":
				result = bitmasking(dungeon, i, j, "Floor")
				if result == 255:
					dungeon.tiles[i,j] = tile_types.floor
	return


def randomize_tiles(dungeon, map_width, map_height) -> None:
	""" Get the walls and the floor a more random look by changing their color slightly """
	for i in range(1, map_width-1):
		for j in range(1, map_height-1):
			if (dungeon.tiles[i, j]["kind"]) == b"Wall":
				dungeon.tiles[i, j][3][2][0] += random.randint(-5, 5)
				dungeon.tiles[i, j][3][2][1] += random.randint(-5, 5)
				dungeon.tiles[i, j][3][2][2] += random.randint(-5, 5)
			elif (dungeon.tiles[i, j]["kind"]) == b"Floor":
				dungeon.tiles[i, j][3][2][0] += random.randint(-3, 3)
				dungeon.tiles[i, j][3][2][1] += random.randint(-3, 3)
				dungeon.tiles[i, j][3][2][2] += random.randint(-3, 3)
	return

def place_ironbars(dungeon, map_width, map_height) -> None:
	""" Place Ironbars with a 1/10 chance in 1 tile wide walls """
	iron_bars = copy.deepcopy(entity_factories.iron_bars)
	
	for i in range(1, map_width-1):
		for j in range(1, map_height-1):
			result = 0
			if (dungeon.tiles[i, j]["kind"]) == b"Wall":
				result = bitmasking(dungeon, i, j, "Wall")
			# Possilbe place found, place with 1/10 chance:
			if result == 34 or result == 136:
				x = random.randint(0, 10)
				if x == 5:
					# Place Iron Bars (Furniture) together with its base
					dungeon.tiles[i,j] = tile_types.window_base
					iron_bars.spawn(dungeon, i,j)
	return


def place_doors(dungeon, map_width, map_height) -> None:
	""" Place Doors between rooms and tunnels"""
	door = copy.deepcopy(entity_factories.door)

	for i in range(1, map_width-1):
		for j in range(1, map_height-1):
			result = 0
			if (dungeon.tiles[i, j]["kind"]) == b"Floor":
				result = bitmasking(dungeon, i, j, "Wall")
			# Place doors on suitable locations
			if result == 99 or result == 54 or result == 141 or result == 216:
				door.parent = dungeon
				door.usable.initialize(dungeon, i, j)
				door.spawn(dungeon, i,j)
	return

def remove_doors_at_intersection(dungeon, map_width, map_height) -> None:
	""" Remove doors at Intersections to avoid up to 4 doors by intersecting tunnels """
	for i in range(1, map_width-1):
		for j in range(1, map_height-1):
			result = 0
			if (dungeon.tiles[i, j]["kind"]) == b"Floor":
				result = bitmasking(dungeon, i, j, "Door")
				
			if result == 170 or result == 138 or result == 42 or result == 162 or result == 168:
				if (dungeon.tiles[i, j-1]["kind"]) == b"Door":
					dungeon.entities.remove(dungeon.get_entity_at_location(i, j-1))
					dungeon.tiles[i,j-1] = tile_types.floor
					
				if (dungeon.tiles[i-1, j]["kind"]) == b"Door":
					dungeon.entities.remove(dungeon.get_entity_at_location(i-1, j))
					dungeon.tiles[i-1,j] = tile_types.floor
					
				if (dungeon.tiles[i, j+1]["kind"]) == b"Door":
					dungeon.entities.remove(dungeon.get_entity_at_location(i, j+1))
					dungeon.tiles[i,j+1] = tile_types.floor
					
				if (dungeon.tiles[i+1, j]["kind"]) == b"Door":
					dungeon.entities.remove(dungeon.get_entity_at_location(i+1, j))
					dungeon.tiles[i+1,j] = tile_types.floor
	return

def search_rooms_in_dungeon_5x5(dungeon, map_width, map_height, rooms) -> List:
	""" search for floors in sizes 5x5, 3x5, 5x3 and 3x3 and set them to rectangular_room, final room sizes
	are larger to calculate properly the inner and area function (expects walls around rooms) """
	for i in range(2, map_width-2):
		for j in range(2, map_height-2):
			result = 0
			if (dungeon.tiles[i, j]["kind"]) == b"Floor":
				result = bitmasking24bit(dungeon, i, j, "Floor")
				if result == 0xFFFFFF:
					new_room = RectangularRoom(i-3,j-3, 6, 6)		# room 5x5
				elif result & 0xE0EFF == 0xE0EFF:
					new_room = RectangularRoom(i-2,j-3, 4, 6)		# room 3x5				
				elif result & 0xE0E0FF== 0xE0E0FF:
					new_room = RectangularRoom(i-3,j-2, 6, 4)		# room 5x3
				elif result & 0xFF == 0xFF:
					new_room = RectangularRoom(i-2, j-2, 5, 5)		# room 3x3		
				else:
					new_room = False

				""" Check wether new room intersects with existing room, if not, append to room list """
				if new_room:
					if not any(new_room.intersects(other_room) for other_room in rooms):
						rooms.append(new_room)
					else:
						pass
	return rooms


def decorate_room(dungeon, rooms, current_floor) -> None:
	""" Decorates rooms based on roomtype list, each room will only be used once per floor """
	roomtypes = ["Empty", "Treeroom", "Fountainroom", "Cloudroom", "Pillarroom", "Chestroom"]

	""" Decorate each room in roomlist """
	for room in rooms:
		""" Set first room to start, last room to end and place stairs. On floor 10 a end-game button instead of
		stairs will be added """
		if room == rooms[0]:
			# Place Upstairs in first room
			room.roomtype = "Start"
			dungeon.tiles[room.center] = tile_types.up_stairs
			dungeon.upstairs_location = room.center
		elif room == rooms[len(rooms)-1]:
			if current_floor == 10:
				# Place finish-game-button for testing
				button = copy.deepcopy(entity_factories.button)
				button.parent = dungeon
				button.spawn(dungeon, room.center[0], room.center[1])
			else:
				# Place Downstairs in last room
				room.roomtype = "End"
				dungeon.tiles[room.center] = tile_types.down_stairs
				dungeon.downstairs_location = room.center
		else:
			""" For rest of the rooms, choose from list """
			choice = random.choice(roomtypes)

			""" all roomtypes except emtpy will be removed from list after placement """
			if choice != "Empty":
				roomtypes.remove(choice)
				
				if choice == "Shoproom":
					""" Shoproom: Place Shopkeeper inside room, not used at the moment  """
					x = random.randint(room.x1 + 2, room.x2 - 2)
					y = random.randint(room.y1 + 2, room.y2 - 2)					
					shopkeeper = copy.deepcopy(entity_factories.npc)
		
					""" Place shopkeeper: BUG: place shopkeeper on a diffent location in case space is occupied """
					if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
						shopkeeper.spawn(dungeon, x, y)
				
				elif choice == "Fountainroom":
					""" Fountainroom: Place a Fountain inside room, never placed directly at the walls (x,y +/-2) """					
					fountain = copy.deepcopy(entity_factories.fountain)

					x, y = 0, 0
					while (dungeon.tiles[x,y]["kind"]) != b"Floor":
						x = random.randint(room.x1 + 2, room.x2 - 2)
						y = random.randint(room.y1 + 2, room.y2 - 2)

					""" BUG: like shopkeeper """
					if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
						fountain.spawn(dungeon, x, y)
				
				elif choice == "Treeroom":
					""" Place Trees inside room, one tree per 10 tiles of room area. Never placed directly at the walls
					(x,y +/-2) not to block doors """
					trees = room.area // 10
					tree = copy.deepcopy(entity_factories.tree)

					""" TODO: add while loop like above """
					for i in range(trees):
						x = random.randint(room.x1 + 2, room.x2 - 2)
						y = random.randint(room.y1 + 2, room.y2 - 2)
		
						if not any(entity.x == x and entity.y == y for entity in dungeon.entities):							
							tree.spawn(dungeon, x, y)
							dungeon.tiles[(x, y)] = tile_types.fake_wall
							
				elif choice == "Cloudroom":
					""" Place clouds inside room (3x3). Not nice, but ok for the moment """
					cloud = copy.deepcopy(entity_factories.cloud)

					x = random.randint(room.x1 + 2, room.x2 - 2)
					y = random.randint(room.y1 + 2, room.y2 - 2)

					cloud.spawn(dungeon, x,y)
					dungeon.tiles[(x, y)] = tile_types.fake_cloud
					cloud.spawn(dungeon, x+1,y+1)
					dungeon.tiles[(x+1, y+1)] = tile_types.fake_cloud					
					cloud.spawn(dungeon, x+1,y)
					dungeon.tiles[(x+1, y)] = tile_types.fake_cloud
					cloud.spawn(dungeon, x-1,y-1)
					dungeon.tiles[(x-1, y-1)] = tile_types.fake_cloud					
					cloud.spawn(dungeon, x-1,y)
					dungeon.tiles[(x-1, y)] = tile_types.fake_cloud
					cloud.spawn(dungeon, x,y+1)
					dungeon.tiles[(x, y+1)] = tile_types.fake_cloud
					cloud.spawn(dungeon, x,y-1)
					dungeon.tiles[(x, y-1)] = tile_types.fake_cloud
					cloud.spawn(dungeon, x-1,y+1)
					dungeon.tiles[(x-1, y+1)] = tile_types.fake_cloud					
					cloud.spawn(dungeon, x+1,y-1)
					dungeon.tiles[(x+1, y-1)] = tile_types.fake_cloud					
		
				elif choice == "Pillarroom":
					""" Place 4 pillars inside room """
					pillar = copy.deepcopy(entity_factories.pillar)

					x,y = room.center

					pillar.spawn(dungeon, x-1, y-1)
					dungeon.tiles[(x-1, y-1)] = tile_types.fake_wall					
					pillar.spawn(dungeon, x+1, y+1)
					dungeon.tiles[(x+1, y+1)] = tile_types.fake_wall					
					pillar.spawn(dungeon, x+1, y-1)
					dungeon.tiles[(x+1, y-1)] = tile_types.fake_wall					
					pillar.spawn(dungeon, x-1, y+1)
					dungeon.tiles[(x-1, y+1)] = tile_types.fake_wall					
					
				elif choice == "Chestroom":
					""" Place a chest inside the room and fill with stuff """
					chest = copy.deepcopy(entity_factories.chest)
					x,y = room.center
					chest.usable.initialize(dungeon)
					chest.spawn(dungeon, x, y)
					#chest.usable.list_content()							
	
			room.roomtype = choice

			"""
			# BUG: Many rooms with <unknown room> inside list 
			for room in rooms:
				print(f"Roomtype: {room.roomtype}")
			"""
	return

def drunkwalk(dungeon, map_width, map_height, drunks_min, drunks_max, turns_min, turns_max, steps_min, steps_max) -> None:
	""" The drunkwalk loop lets the drunken dwarf run and smash stones.
	drunks min/max: how often the dwarf starts, turns min/max: how often he turns, steps min/max: how many steps he will
	make straight  """
	
	map_center = (int(map_width/2), int(map_height/2))

	""" Relative x,y values (8-way) where the dwarf might go """
	directions = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
	
	""" Get random number of drunks and dig out the middle of the map"""
	drunks = random.randint(drunks_min, drunks_max)
	dungeon.tiles[map_center] = tile_types.floor

	""" The drunkwalk loop """
	current_drunk = 0
	while current_drunk < drunks:
		""" Get a random start direction and a random start point (1st drunk it will be the map center) and store the
		actual pos of the dwarf """
		direction = random.choice(directions)
		start_pos = random_tile_in_map(dungeon, map_width, map_height, b"Floor")
		act_pos = start_pos

		""" The drunkjards turn loop """
		current_turn = 0
		turns = random.randint(turns_min, turns_max)

		while current_turn < turns:
			
			""" The drunkjards step loop, get no of steps and a new direction """
			current_step = 0
			steps = random.randint(steps_min, steps_max)
			direction = random_turn(direction)

			while current_step < steps:
				next_pos = (act_pos[0] + direction[0], act_pos[1] + direction[1])

				""" Check if next step is inside map boundaries	"""
				if 1 <= next_pos[0] <= (map_width -2) and 1 <= next_pos[1] <= (map_height -2):
					dungeon.tiles[next_pos] = tile_types.floor
					act_pos = next_pos
					current_step += 1
				else:
					break

			current_turn += 1
		current_drunk += 1



def generate_drunkjard(
	map_width: int,
	map_height: int,
	steps_min: int,
	steps_max: int,
	walks_min: int,
	walks_max: int,
	drunks_min: int,
	drunks_max: int,
	engine: Engine,
	current_floor: int,
) -> GameMap:
	""" generate a dungeon map based on drunkjards walk, details see drunkwalk. called from game_map.py """

	"""	Set up player, dungeon, room list. Add player to maps entities """
	player = engine.player
	dungeon = GameMap(engine, map_width, map_height, entities=[player])
	rooms: List[RectangularRoom] = []

	""" Generate new drunkjard maps until one with at least 4 rooms is created, to have start- and endroom and at least
	two more """

	while (len(rooms) < 4):
		""" Dig out the Map """
		drunkwalk(dungeon, map_width, map_height, drunks_min, drunks_max, walks_min, walks_max, steps_min, steps_max)

		""" Remove single walls (pillars) and randomize floors & walls """
		remove_single_walls(dungeon, map_width, map_height)
		randomize_tiles(dungeon, map_width, map_height)

		""" Generate (search) rooms and place entities """
		rooms = search_rooms_in_dungeon_5x5(dungeon, map_width, map_height, rooms)
		for room in rooms:
			place_entities(room, dungeon, engine.game_world.current_floor)

		""" Place doors, decorate rooms and add ironbars on single-tile walls (not many in drunkjard). """
		place_doors(dungeon, map_width, map_height)
		decorate_room(dungeon, rooms, current_floor)
		place_ironbars(dungeon, map_width, map_height)

		#print(f"{len(rooms)} rooms found in drunkjards walk.")


	""" Place player in first rooms center pos. """
	player.place(*((rooms)[0].center), dungeon)

	return dungeon


def generate_dungeon(
	max_rooms: int,
	room_min_size: int,
	room_max_size: int,
	map_width: int,
	map_height: int,
	engine: Engine,
	current_floor: int,
) -> GameMap:
	""" Generate a new dungeon map based on rectangular rooms connected by floors"""

	""" Set up player, dungeon, room list """
	player = engine.player
	dungeon = GameMap(engine, map_width, map_height, entities=[player])

	rooms: List[RectangularRoom] = []
	
	center_of_last_room = (0,0)
	center_of_first_room = (0,0)
	
	""" Room creation loop """
	for r in range(max_rooms):
		""" Get random room dimensions and room coord. so that there is always at least
		one tile wall at the edges of the map """
		room_width = random.randint(room_min_size, room_max_size)
		room_height = random.randint(room_min_size, room_max_size)
		
		x = random.randint(0, dungeon.width - room_width -1)
		y = random.randint(0, dungeon.height - room_height -1)
		
		""" Create the room and check wether it is not intersecting any other room """
		new_room = RectangularRoom(x,y, room_width, room_height)
		
		if any(new_room.intersects(other_room) for other_room in rooms):
			continue	# room intersects, start loop again to get a new room
		# no intersection, go on...
		
		""" Dig out the room """
		dungeon.tiles[new_room.inner] = tile_types.floor
		
		""" Dig tunnels between rooms """
		if len(rooms) == 0:
			pass		
			""" No tunnel needed for first room.
			Place some stuff for testing here, so that it is always in the start room """
	
			# Place a Shop for Testing purposes
			# dungeon.tiles[(center_of_first_room[0]+1, center_of_first_room[1]+1)] = tile_types.shop
			
			# Place a Door for testing purposes
			# door = copy.deepcopy(entity_factories.door)
			# door.parent = dungeon
			# door.usable.initialize(dungeon,center_of_first_room[0]+1, center_of_first_room[1]+1 )
			# door.spawn(dungeon, center_of_first_room[0]+1, center_of_first_room[1]+1)
			
			# Place finish-game-button for testing
			# button = copy.deepcopy(entity_factories.button)
			# button.parent = dungeon
			# button.spawn(dungeon, center_of_first_room[0]+1, center_of_first_room[1]+1)

		else:
			""" Dig tunnel between rooms """
			for x,y in tunnel_between(rooms[-1].center, new_room.center):
				dungeon.tiles[x,y] = tile_types.floor
				
			center_of_last_room = new_room.center
		
		""" Append room to Room list and place entities inside room """
		rooms.append(new_room)		
		place_entities(new_room, dungeon, engine.game_world.current_floor)

	""" Individual room creation complete, the rest of the stuff for all rooms together """

	""" Decorate Rooms, Place doors at suitable places, remove excess doors at intersections"""
	decorate_room(dungeon, rooms, current_floor)
	place_doors(dungeon, map_width, map_height)
	remove_doors_at_intersection(dungeon, map_width, map_height)

	""" Give walls and floors more random look and place ironbars in one-tile wide walls """
	randomize_tiles(dungeon, map_width, map_height)
	place_ironbars(dungeon, map_width, map_height)
	
	""" Place player in first rooms center pos. """
	player.place(*((rooms)[0].center), dungeon)

	return dungeon

