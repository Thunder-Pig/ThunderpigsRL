from random import randint
import copy

from components.ai import HostileEnemy, ShopAI, FriendlyAI
from components import consumable, equippable
from components.usable import Usable, Ironbar, Tree, Cloud, Fountain, Pillar, Chest, Door, Trap, Button
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.banking import Banking
from components.dimensions import Dimensions
from components.race import Race
from components.clas import Clas
from components.skills import Skills
from components.body import Body
from components.lock import Lock
from components.description import Description

from entity import Actor, Item, Furniture

import settings
import color

""" The Player character """
""" ==================== """

player = Actor(
	char = "@",
	color = (255, 255, 255),
	name = settings.str_player_name,
	ai_cls = HostileEnemy,
	equipment=Equipment(),
	fighter = Fighter(hp=12, base_armor_class = 10, base_damage="1d3"),
	inventory = Inventory(capacity=26),
	level = Level(level_up_base=100),
	banking = Banking(capital = 1),
	dimensions = Dimensions(size=settings.str_medium),
	race = Race(race=settings.str_halfling),
	clas = Clas(clas=settings.str_barbarian),
	skills = Skills(skills=["Investigator"]),
	body = Body("Humanoid"),
	
)

""" The basic items """
""" =============== """

""" Money, value will be set randomly after initialization in MoneyConsumable """
money = Item(
	char = "$",
	color = (255, 255, 255),
	name = settings.str_money,
	value = 1,
	consumable=consumable.MoneyConsumable(),
)

""" Gem not used at the moment, should be used for first quest """
gem = Item(
	char = "*",
	color=(255, 255, 0),
	name="Quest Gem",
	consumable=consumable.GemConsumable(),
)

""" The stone which drops from the stonefall trap """
stone = Item(
	char = "*",
	color=(255,255,0),
	name=settings.str_stone,
	consumable=consumable.GemConsumable(),
	dimensions = Dimensions(size=settings.str_medium, weight = 50),
)

""" Friendly NPCs """
""" ============= """

""" Shopowner """
npc = Actor(
	char = "@",
	color = (63, 127, 63),
	name = settings.str_shopowner,
	attitute = "Friendly",
	pass_door = False,
	ai_cls = ShopAI,
	equipment = Equipment(),
	fighter = Fighter(hp_range=(1,4), base_strength=2, base_dexterity=15, base_constitution = 10, base_intelligence= 2, base_wisdom = 12, base_charisma = 2, base_armor_class = 10, base_damage="1d4"),
	inventory = Inventory(capacity=5),
	level = Level(xp_given=80),
	dimensions = Dimensions(size=settings.str_medium),
	skills = Skills(skills=[]),
	body = Body("Humanoid"),
)

""" Shopowner """
sheep = Actor(
	char = "Y",
	color = color.grey,
	name = settings.str_sheep,
	attitute = "Friendly",
	pass_door = False,
	ai_cls = FriendlyAI,
	equipment = Equipment(),
	fighter = Fighter(hp_range=(1,4), base_strength=2, base_dexterity=15, base_constitution = 10, base_intelligence= 2, base_wisdom = 12, base_charisma = 2, base_armor_class = 10, base_damage="1d4"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=50),
	dimensions = Dimensions(size=settings.str_medium),
	skills = Skills(skills=[]),
	body = Body("Doglike"),
)
	
""" Hostile NPCs """
""" ============ """

""" Mostly based on D&D3.5 """

""" Ant, dire- and minor-ant """
ant = Actor(
	char = "a",
	color = color.dark_green,
	name = settings.str_ant_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment=Equipment(),
	fighter = Fighter(hp_range=(1,3), base_strength=1, base_dexterity=15, base_constitution = 8, base_intelligence= 2, base_wisdom = 12, base_charisma = 6, base_armor_class = 8, base_damage="1d3"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=30),
	dimensions = Dimensions(size=settings.str_tiny),
	skills = Skills(skills=[]),
	body = Body("Insect")

)

dire_ant = copy.deepcopy(ant)
dire_ant.dire(1.5)

minor_ant = copy.deepcopy(ant)
minor_ant.dire(-1.5)


""" Dog """
dog = Actor(
	# http://www.dandwiki.com/wiki/SRD:
	char = "d",
	color = color.dark_green,
	name = settings.str_dog_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment=Equipment(),
	fighter = Fighter(hp_range=(3,6), base_strength=13, base_dexterity=17, base_constitution = 15, base_intelligence= 2, base_wisdom = 12, base_charisma = 6, base_armor_class = 15, base_damage="1d8"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=110),
	dimensions = Dimensions(size=settings.str_small),
	skills = Skills(skills=[]),
	body = Body("Doglike")
)


""" Dragon """
dragon = Actor(
	char = "D",
	color = (255, 50, 50),
	name = settings.str_dragon_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment = Equipment(),
	fighter = Fighter(hp_range=(4,24), base_strength=5, base_dexterity=6, base_damage="1d12"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=400),
	dimensions = Dimensions(size=settings.str_huge),
	skills = Skills(skills=[]),
	body = Body("Dragon"),
)


""" Rat, Dire- and Minor-rat """
rat = Actor(
	# http://www.dandwiki.com/wiki/SRD:
	char = "r",
	color = color.dark_green,
	name = settings.str_rat_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment=Equipment(),
	# for testing hp_range changed from 1,4 to 1,2
	fighter = Fighter(hp_range=(1,2), base_strength=2, base_dexterity=15, base_constitution = 10, base_intelligence= 2, base_wisdom = 12, base_charisma = 2, base_armor_class = 10, base_damage="1d4"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=80),
	dimensions = Dimensions(size=settings.str_tiny),
	skills = Skills(skills=[]),
	body = Body("Doglike")
)

dire_rat = copy.deepcopy(rat)
dire_rat.dire(1.5)

minor_rat = copy.deepcopy(rat)
minor_rat.dire(-1.5)


""" Orc """
orc = Actor(
	# http://www.dandwiki.com/wiki/SRD:
	char = "o",
	color = (63, 127, 63),
	name = settings.str_orc_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment=Equipment(),
	fighter = Fighter(hp_range=(2,9), base_strength=17, base_dexterity=11, base_constitution = 12, base_intelligence= 8, base_wisdom = 7, base_charisma = 6, base_armor_class = 13, base_damage="2d4"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=35),
	dimensions = Dimensions(size=settings.str_medium),
)


""" Small zombie """
sm_zombie = Actor(
	char = "z",
	color = (255, 50,50),
	name = settings.str_sm_zombie_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment = Equipment(),
	fighter = Fighter(hp_range=(4, 15), base_strength=11, base_dexterity=8, base_wisdom=10, base_charisma=1, base_damage="1d4"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given = 50),
	dimensions = Dimensions(size=settings.str_small),
	skills = Skills(skills=[]),
	body = Body("Humanoid"),
)


""" Troll """
troll = Actor(
	char = "T",
	color = (0, 127, 0),
	name = settings.str_troll_name,
	attitute = "Hostile",
	ai_cls = HostileEnemy,
	equipment = Equipment(),
	fighter = Fighter(hp_range=(2,12), base_strength=1, base_dexterity=4, base_armor_class = 4, base_damage="1d8"),
	inventory = Inventory(capacity=0),
	level = Level(xp_given=100),
	dimensions = Dimensions(size=settings.str_large),

)



""" Scrolls """
""" ======= """

amputation_scroll = Item(
	char="~",
	color=(207, 63, 255),
	name = settings.str_amputation_scroll,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.AmputationConsumable(),
)

blinded_scroll = Item(
	char = "~",
	color = (207, 63, 255),
	name = settings.str_blind_scroll,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.FovConsumable(number_of_turns=30, fov=1),
)

confusion_scroll = Item(
	char="~",
	color=(207, 63, 255),
	name=settings.str_confusion_scroll_name,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.ConfusionConsumalbe(number_of_turns=10),
)

dumb_scroll = Item(
	char = "~",
	color = (207, 63, 255),
	name = settings.str_dumb_scroll,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.DumbConsumable(number_of_turns=1),
)

fireball_scroll = Item(
	char="~",
	color=(255, 0, 0),
	name= settings.str_fireball_scroll_name,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

lightning_scroll = Item(
	char="~",
	color=(255, 255, 0),
	name=settings.str_lightning_scroll_name,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_glas, hands=1, price=100),
	consumable=consumable.LightningDamageConsumable(damage= 20, maximum_range=5),
)

lockpick_scroll = Item(
	char="~",
	color = (207, 63, 255),
	name = settings.str_lockpick_scroll,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.LockpickConsumable(),
)	

vision_scroll = Item(
	char = "~",
	color = (207, 63, 255),
	name = settings.str_vision_scroll,
	kind = ("Scroll"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_paper, hands=1, price=150),
	consumable=consumable.FovConsumable(number_of_turns=30, fov=16),
)


""" Potions """
""" ======= """

health_potion = Item(
	char="!",
	color=(127,0,255),
	name=settings.str_health_potion_name,
	kind = ("Potion"),
	dimensions=Dimensions(size=settings.str_fine, weight=1, material=settings.str_glas, hands=1, price=100),
	consumable=consumable.HealingConsumable(amount=20),
)


""" Ranged Weapons and ammunition """
""" ============================= """

arrow = Item(
	char=")",
	color=(10, 140, 160),
	name=settings.str_arrow,
	kind = ("Arrow"),
	dimensions=Dimensions(size=settings.str_fine, material=settings.str_wood, price=1, weight=1),
	equippable=equippable.Arrow(),
	description=Description(description="Normal wooden arrows, nothing special."),
)

wooden_bow = Item(
	char=")",
	color=(139,69,19),
	name=settings.str_wodden_bow_name,
	kind = ("Weapon"),
	dimensions=Dimensions(size=settings.str_small, weight=5, material=settings.str_wood, hands=2, price=50),
	equippable=equippable.Bow(damage="3d6", maximum_range=6, combat="Ranged"),
	description=Description(description="A wooden bow used for hunting."),
)


""" Meelee Weapons """
""" ============== """

axe = Item(
	#D&D3.5 Player Manual
	char=")",
	color=(0,191,255),
	kind = ("Weapon"),
	name=settings.str_axe_name,
	dimensions=Dimensions(size=settings.str_small, weight=3, material=settings.str_metal, price=60),
	equippable=equippable.Axe(damage="1d6", criticals_multi = 3,),
	description=Description(description="It is not only used to chop down trees."),
)

club = Item(
	#D&D3.5 Player Manual
	char=")",
	color=(0,191,255),
	name=settings.str_club_name,
	kind = ("Weapon"),
	dimensions= Dimensions(size=settings.str_small, weight =3, material=settings.str_wood, price=5,),
	equippable=equippable.Club(damage="1d6",),
	description=Description(description="Already thousends of years ago this weapon was used to kill everything around you."),
)

dagger = Item(
	#D&D3.5 Player Manual
	char="/",
	color=(0,191,255),
	name=settings.str_dagger_name,
	kind = ("Weapon"),
	dimensions = Dimensions(size=settings.str_small, weight=1, material=settings.str_metal, price=20),
	equippable=equippable.Sword(damage="1d4",criticals= [19,20]),
	description=Description(description="A dagger is the basic weapon to explore all the dungeons."),
)

spear = Item(
	#D&D3.5 Player Manual
	char=")",
	color=(0,191,255),
	name=settings.str_spear_name,
	kind = ("Weapon"),
	dimensions=Dimensions(size=settings.str_medium, weight=9, material=settings.str_wood, price=50, hands=2,),
	equippable=equippable.Spear(damage="1d8", criticals_multi = 3,),
	description=Description(description="A spear can be a very dangerous weapon if used by the right owner."),

)

sword = Item(
	#D&D3.5 Player Manual
	char="/",
	color=(0,191,255),
	kind = ("Weapon"),
	name=settings.str_short_sword_name,
	dimensions=Dimensions(size=settings.str_small, weight=2, material=settings.str_metal, price=100),
	equippable=equippable.Sword(damage="1d6", criticals = [19,20]),
	description=Description(description="You feel like a knight when using this sword."),
)


""" Armor """
""" ===== """

leather_armor = Item(
	#D&D3.5 Player Manual
	char="[",
	color=(129,69,19),
	name=settings.str_leather_armor_name,
	kind = ("Armory"),
	dimensions=Dimensions(size=settings.str_small, weight=15, material=settings.str_leather, price=100),
	equippable=equippable.Armor(armor_class_bonus=2, max_dex_bonus = 6),
	description=Description(description="The leather armor gives you basic protection."),
)

chain_mail = Item(
	#D&D3.5 Player Manual
	char="[",
	color=(139,69,19),
	name=settings.str_chain_mail_name,
	kind = ("Armory"),
	dimensions=Dimensions(size=settings.str_medium, weight=40, material=settings.str_metal, price=1500),
	equippable=equippable.Armor(armor_class_bonus=5, max_dex_bonus = 2),
	description=Description(description="A heavy armor with a high protection value, unfortuneatly very heavy."),
)

scale_armor = Item(
	#D&D3.5 Player Manual
	char="[",
	color=(129,69,19),
	name=settings.str_scale_armor_name,
	kind = ("Armory"),
	dimensions=Dimensions(size=settings.str_medium, weight=30, material=settings.str_metal, price=500),
	equippable=equippable.Armor(armor_class_bonus=4, max_dex_bonus = 3),
	description=Description(description="The scale armor isn't bad for your journey."),
)

""" Shields """
""" ======= """

la_wo_shield = Item(
	# AD&D 3.5e Players Manual
	char="O",
	color=(139,69,19),
	name=settings.str_la_wo_shield_name,
	kind = ("Shield"),
	dimensions=Dimensions(size=settings.str_medium, weight=10, material=settings.str_wood, price=70),
	equippable=equippable.Shield(armor_class_bonus = 2, max_dex_bonus = 0,),
	description=Description(description="A big wooden shield, it just works as expected."),
)

sm_wo_shield = Item(
	# AD&D 3.5e Players Manual
	char="O",
	color=(139,69,19),
	name=settings.str_sm_wo_shield_name,
	kind = ("Shield"),
	dimensions=Dimensions(size=settings.str_small, weight=5, material=settings.str_wood, price=30),
	equippable=equippable.Shield(armor_class_bonus = 1, max_dex_bonus = 0,),
	description=Description(description="The small wooden shield is a basic all-purpose shield."),
)

tower_shield = Item(
	# AD&D 3.5e Players Manual
	char="O",
	color=(139,69,19),
	name=settings.str_tower_shield_name,
	kind = ("Shield"),
	dimensions=Dimensions(size=settings.str_medium, weight=45, material=settings.str_wood, price=300),
	equippable=equippable.Shield(armor_class_bonus = 4, max_dex_bonus = 2,),
	description=Description(description="The tower shild is a very huge shield and very heavy. But gives a maximum of protection."),
)

""" Hats & Helmets """
""" ============== """

hat = Item(
	# NOT FOUND IN D&D3.5
	char="p",
	color=(139,69,19),
	name=settings.str_leather_hat_name,
	kind = ("Hat"),
	equippable=equippable.Hat(armor_class_bonus=1),
	dimensions=Dimensions(size=settings.str_small, weight=5, material=settings.str_leather, hands=1, price=200),
	description=Description(description="This is a nice leather hat."),
)

""" Boots """
""" ===== """

boots = Item(
	# NOT FOUND IN D&D3.5
	char="b",
	color=(139,69,19),
	name=settings.str_leather_boots_name,
	kind = ("Boots"),
	equippable=equippable.Boots(dexterity_bonus=1),
	dimensions=Dimensions(size=settings.str_small, weight=5, material=settings.str_leather, hands=1, price=200),
	description=Description(description="These are nice leather boots."),
)

	
""" Utilities """
""" ========= """

lockpick = Item(
	char = "(",
	color = (50,130,150),	# magenta
	kind = ("Lockpick"),
	name= settings.str_lockpick,
	value  = 3,				# Stores the Lockpick Bonus value
	dimensions=Dimensions(size=settings.str_fine, weight = 1, material=settings.str_metal, price=25, hands=2),
	description=Description(description="This is a basic lockpick tool. You can use it to open doors, locks and anything else you can image."),
)

lockpick_master = Item(
	char = "(",
	color = (50,130,150),	# magenta
	kind = ("Lockpick"),
	name=settings.str_master + settings.str_lockpick,
	value  = 6,				# Stores the Lockpick Bonus value
	dimensions=Dimensions(size=settings.str_fine, weight = 1, material=settings.str_metal, price=50, hands=2),
	description=Description(description="This is the Master lockpick tool. You can use it to open doors, etc. It is much better than the basic tool."),

)



""" Furniture """
""" ========= """

""" The Alpha-Version-End-Game-Button """
button = Furniture(
	char = "o",
	name = settings.str_button,
	color = (255, 50, 50),
	kind=("Button"),
	walkable=False,
	transparent=True,
	usable=Button(),
	dimensions=Dimensions(size=settings.str_small, weight = 20, material = settings.str_metal),
)

""" Chests can hold precious things """
chest = Furniture(
	# created from scratch, based on AD&D3.5
	char="(",
	color=(135,60,35),		# brown
	name=settings.str_wo_chest_name,
	kind = ("Chest"),
	walkable=True,
	transparent=True,
	dimensions=Dimensions(size=settings.str_small, weight=50, material=settings.str_wood, broken=False),
	inventory=Inventory(capacity=5),
	usable=Chest(),
	lock=Lock(difficulty=20, locked=False, breakable=False),
	description=Description(description="This is a wooden chest."),
)

""" Clouds blocking FOV """
cloud = Furniture(
	char = "#",
	name = settings.str_cloud,
	color = (150,150, 30),		# grey
	kind=("Cloud"),
	walkable=True,
	transparent=False,
	usable=Cloud(),
	dimensions=Dimensions(size=settings.str_huge, weight = 1, material=settings.str_ice),
)

""" Doors can be open, closed, locked and hidden """
door = Furniture(
	char = " ",
	name = settings.str_door,
	color = (135,60,35),		# brown
	kind=("Door"),
	value = 2,
	walkable=True,
	transparent=False,
	usable=Door(),
	dimensions=Dimensions(size=settings.str_huge, weight = 100, material=settings.str_wood),
	lock=Lock(difficulty=20, locked=True, breakable=False),
)

""" Fountains usually regenerate some HP """
fountain = Furniture(
	char = "{",
	name = settings.str_fountain,
	color = (10,140, 160),
	kind=("Fountain"),
	walkable=False,
	transparent=True,
	usable=Fountain(),
	dimensions=Dimensions(size=settings.str_huge, weight = 1000, material=settings.str_stone),
)

""" Iron bars block movement, but not sight. Like windows """
iron_bars = Furniture(
	char = "#",
	name = settings.str_ironbar,
	color = (10,140, 160),
	kind=("Ironbar"),
	walkable=False,
	transparent=True,
	usable=Ironbar(),
	dimensions=Dimensions(size=settings.str_huge, weight = 100, material=settings.str_metal),
	#lock=Lock(difficulty=20, locked=True, breakable=False),
)

""" Pillars blocking movement and sight """
pillar = Furniture(
	char = "O",
	name = settings.str_pillar,
	color = (127,127, 127),
	kind=("Pillar"),
	walkable=False,
	transparent=False,
	usable=Pillar(),
	dimensions=Dimensions(size=settings.str_huge, weight = 1000, material=settings.str_stone),	
)

""" Traps exists as a plenty of kinds. Usually hurts the player """
trap = Furniture(
	char = "^",
	name = settings.str_trap,
	color = (10,140, 160),
	kind=("Trap"),
	walkable=True,
	transparent=True,
	usable=Trap(),
	lock=Lock(difficulty=20, locked=True, breakable=False),
	dimensions=Dimensions(size=settings.str_huge, weight = 20, material=settings.str_wood),
)

""" Trees blocking movement and sight, can drop potions """
tree = Furniture(
	char = "P",
	name = settings.str_tree,
	color = (10,150, 30),		# green
	kind=("Tree"),
	walkable=False,
	transparent=False,
	usable=Tree(),
	dimensions=Dimensions(size=settings.str_huge, weight = 1000, material=settings.str_wood),
)

