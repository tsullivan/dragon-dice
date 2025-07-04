# Unit data for Dragon Dice species
# Each unit defined as a UnitModel instance

from models.species_model import SPECIES_DATA
from models.unit_model import UnitModel

UNIT_DATA = [
    UnitModel(
        unit_id="amazon_battle_rider",
        name="Battle Rider",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_centaur",
        name="Centaur",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Kick",
                "description": "During a melee attack, target one unit in the defending army. The target takes four points of damage.\n* During a save roll, Kick generates four save results.\n* During a dragon attack, Kick generates four melee and four save results.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Kick",
                "description": "During a melee attack, target one unit in the defending army. The target takes four points of damage.\n* During a save roll, Kick generates four save results.\n* During a dragon attack, Kick generates four melee and four save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_charioteer",
        name="Charioteer",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Move", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="amazon_chimera",
        name="Chimera",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Flame",
                "description": "During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
        ],
    ),
    UnitModel(
        unit_id="amazon_darter",
        name="Darter",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
        ],
    ),
    UnitModel(
        unit_id="amazon_envoy",
        name="Envoy",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_harbinger",
        name="Harbinger",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="amazon_hydra",
        name="Hydra",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_javelineer",
        name="Javelineer",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_medusa",
        name="Medusa",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Stone",
                "description": "During a melee or missile attack, Stone does four damage to the defending army with no save possible.\n* During a dragon attack, Stone generates four missile results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Stone",
                "description": "During a melee or missile attack, Stone does four damage to the defending army with no save possible.\n* During a dragon attack, Stone generates four missile results.",
            },
        ],
    ),
    UnitModel(
        unit_id="amazon_nightmare",
        name="Nightmare",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Firewalking",
                "description": "During a maneuver roll, Firewalking generates four maneuver results.\n* During any non-maneuver roll, this unit may move itself and up to three health-worth of units in its army to any terrain.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly2",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Hoof", "description": "Counts as four movement points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Firebreath",
                "description": "During a melee attack, inflict four points of damage on the defending army with no save possible. Each unit killed makes a save roll. Those that do not generate a save result are buried.",
            },
            {
                "name": "Fly2",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_oracle",
        name="Oracle",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as five spell points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates three magic results.  During other non-maneuver rolls, Cantrip generates three magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
        ],
    ),
    UnitModel(
        unit_id="amazon_runner",
        name="Runner",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="amazon_seer",
        name="Seer",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_soldier",
        name="Soldier",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_spearer",
        name="Spearer",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
        ],
    ),
    UnitModel(
        unit_id="amazon_visionary",
        name="Visionary",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_war_chief",
        name="War Chief",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="amazon_war_driver",
        name="War Driver",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates three maneuver and three melee results.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates three maneuver and three melee results.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="amazon_warrior",
        name="Warrior",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["AMAZON"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_archer",
        name="Archer",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_bowman",
        name="Bowman",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_conjurer",
        name="Conjurer",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_coral_giant",
        name="Coral Giant",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_courier",
        name="Courier",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_eagle_knight",
        name="Eagle Knight",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates three maneuver or three save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates three maneuver or three save results.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_enchanter",
        name="Enchanter",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip' from the spell list.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_evoker",
        name="Evoker",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_fighter",
        name="Fighter",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_gryphon",
        name="Gryphon",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Ferry",
                "description": "During any non-maneuver roll, the Ferrying unit may move itself and up to four health-worth of units in its army to any terrain.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Ferry",
                "description": "During any non-maneuver roll, the Ferrying unit may move itself and up to four health-worth of units in its army to any terrain.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_guard",
        name="Guard",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_herald",
        name="Herald",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_horseman",
        name="Horseman",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Hoof", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Hoof", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_knight",
        name="Knight",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Hoof", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Hoof", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_leviathan",
        name="Leviathan",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Swallow",
                "description": "During a melee attack, target one unit in the defending army. Roll the target. If it does not roll its ID icon, it is killed and buried.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Tail",
                "description": "During a dragon or melee attack, Tail generates two melee results. Roll this unit again and apply the new result as well.",
            },
            {
                "name": "Fly2",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Wave",
                "description": "During a melee attack, the defending army subtracts X from their save results.\n* During a maneuver roll whilst marching, subtract X from each counter-maneuvering army's maneuver results. Wave does nothing if rolled when counter-maneuvering.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Hypnotic Glare",
                "description": "During a melee attack, when the defending army rolls for saves, all units that roll an ID result are Hypnotized and may not be rolled until the beginning of your next turn. Those ID results are not counted as saves.\n* The effect ends if the glaring unit leaves the terrain, is killed, or is rolled. The glaring unit may be excluded from any roll until the effect expires.\nNote: Hypnotic Glare works outside of the normal sequence of die roll resolution, applying it's effect immediately after the opponent's roll for saves is made, but before they resolve any SAIs",
            },
            {
                "name": "Fly2",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Tail",
                "description": "During a dragon or melee attack, Tail generates two melee results. Roll this unit again and apply the new result as well.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_protector",
        name="Protector",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_sharpshooter",
        name="Sharpshooter",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
        ],
    ),
    UnitModel(
        unit_id="coral_elf_sprite_swarm",
        name="Sprite Swarm",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_tako",
        name="Tako",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Entangle",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are killed.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Entangle",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are killed.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="coral_elf_trooper",
        name="Trooper",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["CORAL_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_androsphinx",
        name="Androsphinx",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Roar",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are immediately moved to their Reserve Area before the defending army rolls for saves.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Roar",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are immediately moved to their Reserve Area before the defending army rolls for saves.",
            },
        ],
    ),
    UnitModel(
        unit_id="dwarf_behemoth",
        name="Behemoth",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Stomp",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed and must make a save roll. Those that do not generate a save result are buried.\n* During a dragon attack, Stomp generates four melee results.",
            },
            {
                "name": "Bash",
                "description": "During a save roll against a melee attack, target one unit from the attacking army. The targeted unit takes damage equal to the melee results it generated.\n* The targeted unit must make a save roll against this damage. Bash also generates save results equal to the targeted unit's melee results.\n* During other save rolls, Bash generates four save results.\n* During a dragon attack choose an attacking dragon that has done damage. That dragon takes damage equal to the amount of damage it did.\n* Bash also generates save results equal to the damage the chosen dragon did.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Roar2",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are immediately moved to their Reserve Area before the defending army rolls for saves.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Charge",
                "description": "During a melee attack, the attacking army counts all Maneuver results as if they were Melee results.\n* Instead of making a regular save roll or a counter-attack, the defending army makes a combination save and melee roll.\n* The attacking army takes damage equal to these melee results. Only save results generated by spells may reduce this damage.\n* Charge has no effect during a counter-attack.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_crack_shot",
        name="Crack-Shot",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_crossbowman",
        name="Crossbowman",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_footman",
        name="Footman",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_gargoyle",
        name="Gargoyle",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Fly2",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {
                "name": "Fly2",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_lizard_rider",
        name="Lizard Rider",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Paw", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Paw", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_mammoth_rider",
        name="Mammoth Rider",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates three maneuver and three melee results.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates three maneuver and three melee results.",
            },
            {"name": "Save", "description": "Counts as three save points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_marksman",
        name="Marksman",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_patroller",
        name="Patroller",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_pony_rider",
        name="Pony Rider",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Hoof", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Hoof", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_roc",
        name="Roc",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Seize",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. Roll the targets. If they roll an ID result, they are immediately moved to their Reserve Area. Any that do not roll an ID are killed.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Seize",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. Roll the targets. If they roll an ID result, they are immediately moved to their Reserve Area. Any that do not roll an ID are killed.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
        ],
    ),
    UnitModel(
        unit_id="dwarf_sentry",
        name="Sentry",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_sergeant",
        name="Sergeant",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_skirmisher",
        name="Skirmisher",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="dwarf_thaumaturgist",
        name="Thaumaturgist",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_theurgist",
        name="Theurgist",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_umber_hulk",
        name="Umber Hulk",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Confuse",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army after they have rolled for saves.  Re-roll the targeted units, ignoring all previous results. Units are selected prior to resolving the save roll or any SAIs in the defending army.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Confuse",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army after they have rolled for saves.  Re-roll the targeted units, ignoring all previous results. Units are selected prior to resolving the save roll or any SAIs in the defending army.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="dwarf_warlord",
        name="Warlord",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="dwarf_wizard",
        name="Wizard",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["DWARF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.  During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
        ],
    ),
    UnitModel(
        unit_id="feral_antelope_folk",
        name="Antelope-Folk",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Hoof", "description": "Counts as one movement point."},
            {"name": "Hoof", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="feral_badger_folk",
        name="Badger-Folk",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_bear_folk",
        name="Bear-Folk",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Hug",
                "description": "During a melee attack, target one unit in the defending army. The target unit takes four points of damage with no save possible.\n* The targeted unit makes a melee roll. Melee results generated by this roll inflict damage on the Hugging unit with no save possible.\n* During a dragon attack, Hug generates four melee results.",
            },
            {"name": "Paw", "description": "Counts as four movement points."},
            {"name": "Paw", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_buffalo_folk",
        name="Buffalo-Folk",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {"name": "Hoof", "description": "Counts as three movement points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Hoof", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="feral_elephant_folk",
        name="Elephant-Folk",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Trumpet",
                "description": "During a dragon attack, melee attack or save roll, each Feral unit in this army doubles its melee and save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Trumpet",
                "description": "During a dragon attack, melee attack or save roll, each Feral unit in this army doubles its melee and save results.",
            },
        ],
    ),
    UnitModel(
        unit_id="feral_falcon_folk",
        name="Falcon-Folk",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="feral_fox_folk",
        name="Fox-Folk",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Paw", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Paw", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_hawk_folk",
        name="Hawk-Folk",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="feral_horse_folk",
        name="Horse-Folk",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Hoof", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Hoof", "description": "Counts as two movement points."},
            {"name": "Hoof", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="feral_hound_folk",
        name="Hound-Folk",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Paw", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Paw", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="feral_leopard_folk",
        name="Leopard-Folk",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Paw", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_lion_folk",
        name="Lion-Folk",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Paw", "description": "Counts as four movement points."},
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Roar",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are immediately moved to their Reserve Area before the defending army rolls for saves.",
            },
            {"name": "Paw", "description": "Counts as four movement points."},
            {
                "name": "Roar",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets are immediately moved to their Reserve Area before the defending army rolls for saves.",
            },
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_lynx_folk",
        name="Lynx-Folk",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Paw", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="feral_owl_folk",
        name="Owl-Folk",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Screech",
                "description": "During a melee attack, the defending army subtracts four save results against this melee action.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Seize",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. Roll the targets. If they roll an ID result, they are immediately moved to their Reserve Area. Any that do not roll an ID are killed.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
        ],
    ),
    UnitModel(
        unit_id="feral_rhino_folk",
        name="Rhino-Folk",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Gore",
                "description": "During a melee attack, target one unit in the defending army. The target takes two points of damage. If the unit is killed by Gore, it is then buried.\n* During a dragon attack, Gore generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Hoof", "description": "Counts as four movement points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Gore",
                "description": "During a melee attack, target one unit in the defending army. The target takes two points of damage. If the unit is killed by Gore, it is then buried.\n* During a dragon attack, Gore generates four melee results.",
            },
            {"name": "Hoof", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_tiger_folk",
        name="Tiger-Folk",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="feral_vulture_folk",
        name="Vulture-Folk",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="feral_weasel_folk",
        name="Weasel-Folk",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="feral_wolf_folk",
        name="Wolf-Folk",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates three melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates three maneuver results.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Paw", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="feral_wolverine_folk",
        name="Wolverine-Folk",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FERAL"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.  During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_adventurer",
        name="Adventurer",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Flaming Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Firewalkers may count this as one melee result. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_ashbringer",
        name="Ashbringer",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates three magic results.\n* During other non-maneuver rolls, Cantrip generates three magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_daybringer",
        name="Daybringer",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Flaming Shield",
                "description": "Counts as two save points. When at a terrain that contains red (fire), Firewalkers may count this as two melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_expeditioner",
        name="Expeditioner",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_explorer",
        name="Explorer",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {
                "name": "Flaming Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Firewalkers may count this as one melee result. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Move", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_firemaster",
        name="Firemaster",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as two save points. When at a terrain that contains red (fire), Firewalkers may count this as two melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_fireshadow",
        name="Fireshadow",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Create Fireminions",
                "description": "During any army roll, Create Fireminions generates four magic, maneuver, melee, missile or save results.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Create Fireminions",
                "description": "During any army roll, Create Fireminions generates four magic, maneuver, melee, missile or save results.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="firewalker_firestarter",
        name="Firestarter",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {
                "name": "Flaming Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Firewalkers may count this as one melee result. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_firestormer",
        name="Firestormer",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as two save points. When at a terrain that contains red (fire), Firewalkers may count this as two melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_genie",
        name="Genie",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Firecloud",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {
                "name": "Galeforce",
                "description": "During a melee or missile attack, or a magic action at a terrain, target an opposing army at any terrain. Until the beginning of your next turn, the target army subtracts four save and four maneuver results from all rolls.",
            },
            {
                "name": "Firewalking",
                "description": "During a maneuver roll, Firewalking generates four maneuver results.\n* During any non-maneuver roll, this unit may move itself and up to three health-worth of units in its army to any terrain.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_gorgon",
        name="Gorgon",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Flame",
                "description": "During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
            },
            {
                "name": "Flame",
                "description": "During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_guardian",
        name="Guardian",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {
                "name": "Flaming Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Firewalkers may count this as one melee result. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_nightsbane",
        name="Nightsbane",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as two save points. When at a terrain that contains red (fire), Firewalkers may count this as two melee results. Flaming Shields does not apply when making a counter-attack.",
            },
        ],
    ),
    UnitModel(
        unit_id="firewalker_phoenix",
        name="Phoenix",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Seize",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. Roll the targets. If they roll an ID result, they are immediately moved to their Reserve Area. Any that do not roll an ID are killed.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible. During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Rise From Ashes",
                "description": "During a save roll, Rise from the Ashes generates four save results. Whenever a unit with this SAI is killed or buried, roll the unit. If Rise from the Ashes is rolled, the unit is moved to your Reserve Area. If an effect both kills and buries this unit, it may roll once when killed and again when buried. If the first roll is successful, the unit is not buried.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {
                "name": "Seize",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. Roll the targets. If they roll an ID result, they are immediately moved to their Reserve Area. Any that do not roll an ID are killed.",
            },
            {
                "name": "Rise From Ashes",
                "description": "During a save roll, Rise from the Ashes generates four save results. Whenever a unit with this SAI is killed or buried, roll the unit. If Rise from the Ashes is rolled, the unit is moved to your Reserve Area. If an effect both kills and buries this unit, it may roll once when killed and again when buried. If the first roll is successful, the unit is not buried.",
            },
        ],
    ),
    UnitModel(
        unit_id="firewalker_salamander",
        name="Salamander",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as four save points. When at a terrain that contains red (fire), Firewalkers may count this as four melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_sentinel",
        name="Sentinel",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Flaming Shield",
                "description": "Counts as three save points. When at a terrain that contains red (fire), Firewalkers may count this as three melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_shadowchaser",
        name="ShadowChaser",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {
                "name": "Flaming Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Firewalkers may count this as one melee result. Flaming Shields does not apply when making a counter-attack.",
            },
        ],
    ),
    UnitModel(
        unit_id="firewalker_sunburst",
        name="Sunburst",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Move", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_sunflare",
        name="Sunflare",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="firewalker_watcher",
        name="Watcher",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FIREWALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Flaming Shield",
                "description": "Counts as two save points. When at a terrain that contains red (fire), Firewalkers may count this as two melee results. Flaming Shields does not apply when making a counter-attack.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_ambusher",
        name="Ambusher",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_cannibal",
        name="Cannibal",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Swallow",
                "description": "During a melee attack, target one unit in the defending army. Roll the target. If it does not roll its ID icon, it is killed and buried.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Stun",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll.\n* Those that do not generate a maneuver result are stunned and cannot be rolled until the beginning of your turn, unless they are the target of an individual-targeting effect which forces them to.\n* Stunned units that leave the terrain through any means are no longer stunned. Roll this unit again and apply the new result as well.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Net",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. Each targeted unit makes a maneuver roll.\n* Those that do not generate a maneuver result are netted and may not be rolled or leave the terrain they currently occupy until the beginning of your next turn.\n* Net does nothing during a missile attack targeting an opponent's Reserve Army from a Tower on it's eighth face.\n* When saving against an individual targeting effect, Net generates four save results.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Sleep",
                "description": "During a melee attack, target one unit in an opponent's army at this terrain. The target unit is asleep and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.",
            },
        ],
    ),
    UnitModel(
        unit_id="goblin_cutthroat",
        name="Cutthroat",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_deadeye",
        name="Deadeye",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
        ],
    ),
    UnitModel(
        unit_id="goblin_death_mage",
        name="Death Mage",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
        ],
    ),
    UnitModel(
        unit_id="goblin_death_naga",
        name="Death Naga",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.  Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.  Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_filcher",
        name="Filcher",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="goblin_harpies",
        name="Harpies",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Screech",
                "description": "During a melee attack, the defending army subtracts four save results against this melee action.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Screech",
                "description": "During a melee attack, the defending army subtracts four save results against this melee action.",
            },
        ],
    ),
    UnitModel(
        unit_id="goblin_hedge_wizard",
        name="Hedge Wizard",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_leopard_rider",
        name="Leopard Rider",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates three melee results. Roll this unit again and apply the new result as well.  During a maneuver roll, Rend generates three maneuver results.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates three melee results. Roll this unit again and apply the new result as well.  During a maneuver roll, Rend generates three maneuver results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_marauder",
        name="Marauder",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="goblin_mugger",
        name="Mugger",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="goblin_pelter",
        name="Pelter",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="goblin_shambler",
        name="Shambler",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_slingman",
        name="Slingman",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_thug",
        name="Thug",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_trickster",
        name="Trickster",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_troll",
        name="Troll",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Regenerate",
                "description": "During any non-maneuver roll, Regenerate generates four save results, OR, you may bring back up to four health-worth of units from your DUA to the army containing this unit.",
            },
            {
                "name": "Regenerate",
                "description": "During any non-maneuver roll, Regenerate generates four save results, OR, you may bring back up to four health-worth of units from your DUA to the army containing this unit.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="goblin_wardog_rider",
        name="Wardog Rider",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Paw", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Paw", "description": "Counts as one movement point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="goblin_wolf_rider",
        name="Wolf Rider",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["GOBLIN"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Paw", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Paw", "description": "Counts as three movement points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_adept",
        name="Adept",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_assassin",
        name="Assassin",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as five missile hit points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_beholder",
        name="Beholder",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Flame",
                "description": "During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Charm",
                "description": "During a melee attack, target up to four health-worth of units in the defending army; those units don't roll to save during this march.\n* Instead, the owner rolls these units and adds their results to the attacking army's results. Those units may take damage from the melee attack as normal.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Stone",
                "description": "During a melee or missile attack, Stone does four damage to the defending army with no save possible.\n* During a dragon attack, Stone generates four missile results.",
            },
            {
                "name": "Confuse",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army after they have rolled for saves.\n* Re-roll the targeted units, ignoring all previous results. Units are selected prior to resolving the save roll or any SAIs in the defending army.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Illusion",
                "description": "During a magic, melee or missile attack, target any of your armies. Until the beginning of your next turn, the target army cannot be targeted by any missile attacks or spells cast by opposing players.",
            },
        ],
    ),
    UnitModel(
        unit_id="lava_elf_bladesman",
        name="Bladesman",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_conqueror",
        name="Conqueror",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Melee", "description": "Counts as five melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="lava_elf_dead_shot",
        name="Dead-Shot",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_drider",
        name="Drider",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Web",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. The targets make a melee roll.\n* Those that do not generate a melee result are webbed and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.\n* Web does nothing during a missile action targeting an opponent's Reserve Army from a Tower on it's eighth-face.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Web",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. The targets make a melee roll.\n* Those that do not generate a melee result are webbed and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.\n* Web does nothing during a missile action targeting an opponent's Reserve Army from a Tower on it's eighth-face.",
            },
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_duelist",
        name="Duelist",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_fusilier",
        name="Fusilier",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_hell_hound",
        name="Hell Hound",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Flame",
                "description": "During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Flame",
                "description": "During a melee attack, target up to two health-worth of units in the defending army. The targets are killed and buried.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_infiltrator",
        name="Infiltrator",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as five melee hit points."},
            {"name": "Move", "description": "Counts as five movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
        ],
    ),
    UnitModel(
        unit_id="lava_elf_lurker_in_the_deep",
        name="Lurker in the Deep",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip' from the spell list.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Volley",
                "description": "During a save roll against a missile attack, Volley generates four save and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Volley generates four save results.\n* During a missile attack, Volley generates four missile results.\n* During a dragon attack, Volley generates four save and four missile results.",
            },
            {
                "name": "Cloak",
                "description": "During a save roll or dragon attack, add four save results to the army containing this unit until the beginning of your next turn.\n* During a magic action, Cloak generates four magic results.\n* During a roll for an individual-targeting effect, Cloak generates four magic, maneuver, melee, missile, or save results.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_necromancer",
        name="Necromancer",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Magic", "description": "Counts as five spell points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.  During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
        ],
    ),
    UnitModel(
        unit_id="lava_elf_rakshasa",
        name="Rakshasa",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Illusion",
                "description": "During a magic, melee or missile attack, target any of your armies. Until the beginning of your next turn, the target army cannot be targeted by any missile attacks or spells cast by opposing players.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Illusion",
                "description": "During a magic, melee or missile attack, target any of your armies. Until the beginning of your next turn, the target army cannot be targeted by any missile attacks or spells cast by opposing players.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_scorpion_knight",
        name="Scorpion Knight",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_scout",
        name="Scout",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_spider_rider",
        name="Spider Rider",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_spy",
        name="Spy",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_warlock",
        name="Warlock",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Magic", "description": "Counts as four spell points."},
        ],
    ),
    UnitModel(
        unit_id="lava_elf_wyvern_rider",
        name="Wyvern Rider",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["LAVA_ELF"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates five maneuver or five save results.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates one maneuver or one save result.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_darktree",
        name="Darktree",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_dryad",
        name="Dryad",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as three save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_eldar_dryad",
        name="Eldar Dryad",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as two spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip' from the spell list.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as three save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_hamadryad",
        name="Hamadryad",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_lady_nereid",
        name="Lady Nereid",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Paw", "description": "Counts as four movement points."},
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {"name": "Paw", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_naiad",
        name="Naiad",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Paw", "description": "Counts as three movement points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Paw", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as three save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_noble_willow",
        name="Noble Willow",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Wild Growth",
                "description": "During any non-maneuver roll, Wild Growth generates four save results or allows you to promote four health-worth of units in this army. Results may be split between saves and promotions in any way you choose. Any promotions happen all at once.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_nymph",
        name="Nymph",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Paw", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Paw", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_oak",
        name="Oak",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_oak_lord",
        name="Oak Lord",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts three points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates three melee results.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts three points of damage to the defending army with no save possible.  During a dragon attack, Smite generates three melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_oakling",
        name="Oakling",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_pine",
        name="Pine",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as three missile hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Save", "description": "Counts as three save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_pine_prince",
        name="Pine Prince",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {
                "name": "Volley",
                "description": "During a save roll against a missile attack, Volley generates four save and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Volley generates four save results.\n* During a missile attack, Volley generates four missile results.\n* During a dragon attack, Volley generates four save and four missile results.",
            },
            {"name": "Missile", "description": "Counts as two missile hit points."},
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_pineling",
        name="Pineling",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Missile", "description": "Counts as one missile hit point."},
            {"name": "Missile", "description": "Counts as two missile hit points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_redwood",
        name="Redwood",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Trample2",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Trample2",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_satyr",
        name="Satyr",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {"name": "Hoof", "description": "Counts as four movement points."},
            {
                "name": "Volley",
                "description": "During a save roll against a missile attack, Volley generates four save and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Volley generates four save results.\n* During a missile attack, Volley generates four missile results.\n* During a dragon attack, Volley generates four save and four missile results.",
            },
            {
                "name": "Sleep",
                "description": "During a melee attack, target one unit in an opponent's army at this terrain. The target unit is asleep and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.",
            },
            {"name": "Missile", "description": "Counts as four missile hit points."},
            {
                "name": "Confuse",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army after they have rolled for saves.\n* Re-roll the targeted units, ignoring all previous results. Units are selected prior to resolving the save roll or any SAIs in the defending army.",
            },
            {
                "name": "Volley",
                "description": "During a save roll against a missile attack, Volley generates four save and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Volley generates four save results.\n* During a missile attack, Volley generates four missile results.\n* During a dragon attack, Volley generates four save and four missile results.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Sleep",
                "description": "During a melee attack, target one unit in an opponent's army at this terrain. The target unit is asleep and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.",
            },
        ],
    ),
    UnitModel(
        unit_id="treefolk_strangle_vine",
        name="Strangle Vine",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Choke",
                "description": "During a melee attack, when the defending army rolls for saves, target up to four health-worth of units in the that army that rolled an ID result. The target units are killed. Their ID results are not counted towards the army's save results. Note: Choke works outside of the normal sequence of die roll resolution, applying it's effect immediately after the opponent's roll for saves is made, but before they resolve any SAIs",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Wild Growth",
                "description": "During any non-maneuver roll, Wild Growth generates four save results or allows you to promote four health-worth of units in this army. Results may be split between saves and promotions in any way you choose. Any promotions happen all at once.",
            },
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {
                "name": "Choke",
                "description": "During a melee attack, when the defending army rolls for saves, target up to four health-worth of units in the that army that rolled an ID result. The target units are killed. Their ID results are not counted towards the army's save results. Note: Choke works outside of the normal sequence of die roll resolution, applying it's effect immediately after the opponent's roll for saves is made, but before they resolve any SAIs",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
        ],
    ),
    UnitModel(
        unit_id="treefolk_unicorn",
        name="Unicorn",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {
                "name": "Teleport",
                "description": "During a maneuver roll, Teleport generates four maneuver results.\n* During any non-maneuver roll, this unit may move itself and up to three health-worth of units in its army to any terrain.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Counter",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Teleport",
                "description": "During a maneuver roll, Teleport generates four maneuver results.\n* During any non-maneuver roll, this unit may move itself and up to three health-worth of units in its army to any terrain.",
            },
        ],
    ),
    UnitModel(
        unit_id="treefolk_willow",
        name="Willow",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="treefolk_willowling",
        name="Willowling",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["TREEFOLK"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="undead_apparition",
        name="Apparition",
        unit_type="Heavy Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Magic", "description": "Counts as one spell point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="undead_carrion_crawler",
        name="Carrion Crawler",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Stun",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll.\\n* Those that do not generate a maneuver result are stunned and cannot be rolled until the beginning of your turn, unless they are the target of an individual-targeting effect which forces them to.\\n* Stunned units that leave the terrain through any means are no longer stunned. Roll this unit again and apply the new result as well.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Stun",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll.\\n* Those that do not generate a maneuver result are stunned and cannot be rolled until the beginning of your turn, unless they are the target of an individual-targeting effect which forces them to.\\n* Stunned units that leave the terrain through any means are no longer stunned. Roll this unit again and apply the new result as well.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="undead_death_knight",
        name="Death Knight",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Scare",
                "description": "During a melee attack, target up to three health-worth of units in the defending army. The targets make a save roll.\\n* Those that do not generate a save result are immediately moved to their Reserve Area before the defending army rolls for saves. Those that roll their ID icon are killed.",
            },
        ],
    ),
    UnitModel(
        unit_id="undead_dracolich",
        name="Dracolich",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {"name": "Magic", "description": "Counts as four spell points."},
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Magic", "description": "Counts as four spell points."},
        ],
    ),
    UnitModel(
        unit_id="undead_fenhound",
        name="Fenhound",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Paw", "description": "Counts as four movement points."},
            {"name": "Paw", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, it's army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="undead_ghast",
        name="Ghast",
        unit_type="Light Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Magic", "description": "Counts as two spell points."},
        ],
    ),
    UnitModel(
        unit_id="undead_ghost",
        name="Ghost",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Vanish",
                "description": "During a save roll, Vanish generates three save results. The unit may then move to any terrain or its Reserve Area. If the unit moves, the save results still apply to the army that the Vanishing unit left.",
            },
        ],
    ),
    UnitModel(
        unit_id="undead_ghoul",
        name="Ghoul",
        unit_type="Light Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Magic", "description": "Counts as one spell point."},
        ],
    ),
    UnitModel(
        unit_id="undead_heucuva",
        name="Heucuva",
        unit_type="Heavy Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Magic", "description": "Counts as two spell points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
        ],
    ),
    UnitModel(
        unit_id="undead_lich",
        name="Lich",
        unit_type="Heavy Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Magic", "description": "Counts as three spell points."},
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
        ],
    ),
    UnitModel(
        unit_id="undead_minor_death",
        name="Minor Death",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Slay",
                "description": "During a melee attack, target one unit in the defending army. Roll the target. If it does not roll its ID icon, it is killed.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Plague",
                "description": "During a melee attack, target one unit in the defending army. The target makes a save roll.\\n* If the target fails to generate a save result, it is killed and your opponent targets another unit with Plague in the same army.\\n* Continue to target units with Plague until a targeted unit generates a save result.",
            },
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Slay",
                "description": "During a melee attack, target one unit in the defending army. Roll the target. If it does not roll its ID icon, it is killed.",
            },
            {"name": "Move", "description": "Counts as four movement points."},
            {
                "name": "Plague",
                "description": "During a melee attack, target one unit in the defending army. The target makes a save roll.\\n* If the target fails to generate a save result, it is killed and your opponent targets another unit with Plague in the same army.\\n* Continue to target units with Plague until a targeted unit generates a save result.",
            },
        ],
    ),
    UnitModel(
        unit_id="undead_mummy",
        name="Mummy",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Wither",
                "description": "During a melee attack, target any opposing army at the same terrain. Until the beginning of your next turn, the targeted army subtracts three results from all rolls it makes.",
            },
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="undead_revenant",
        name="Revenant",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as two movement points."},
        ],
    ),
    UnitModel(
        unit_id="undead_skeletal_steed",
        name="Skeletal Steed",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {"name": "Hoof", "description": "Counts as four movement points."},
            {"name": "Save", "description": "Counts as four save points."},
            {"name": "Hoof", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Save", "description": "Counts as four save points."},
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {"name": "Hoof", "description": "Counts as four movement points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="undead_skeleton",
        name="Skeleton",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
        ],
    ),
    UnitModel(
        unit_id="undead_spectre",
        name="Spectre",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Move", "description": "Counts as three movement points."},
        ],
    ),
    UnitModel(
        unit_id="undead_vampire",
        name="Vampire",
        unit_type="Light Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {"name": "Magic", "description": "Counts as three spell points."},
            {"name": "Melee", "description": "Counts as four melee hit points."},
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
            {
                "name": "Convert",
                "description": "During a melee attack, target up to three health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed.\\n* The attacking player may return up to the amount of heath-worth killed this way from their DUA to the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="undead_wight",
        name="Wight",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as three save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Save", "description": "Counts as two save points."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
            {"name": "Melee", "description": "Counts as three melee hit points."},
        ],
    ),
    UnitModel(
        unit_id="undead_wraith",
        name="Wraith",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Move", "description": "Counts as two movement points."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Move", "description": "Counts as one movement point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
        ],
    ),
    UnitModel(
        unit_id="undead_zombie",
        name="Zombie",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["UNDEAD"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Save", "description": "Counts as one save point."},
            {"name": "Melee", "description": "Counts as one melee hit point."},
            {"name": "Melee", "description": "Counts as two melee hit points."},
        ],
    ),
    # FROSTWING UNITS
    UnitModel(
        unit_id="frostwing_advocate",
        name="Advocate",
        unit_type="Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates one maneuver or one save result.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_apprentice",
        name="Apprentice",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as two spell points. Can be used for Magic Negation.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates one maneuver or one save result.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as one spell point. Can be used for Magic Negation.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_assailer",
        name="Assailer",
        unit_type="Light Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Volley",
                "description": "During a save roll against a missile attack, Volley generates four save and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\n* During any other save roll, Volley generates four save results.\n* During a missile attack, Volley generates four missile results.\n* During a dragon attack, Volley generates four save and four missile results.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_assaulter",
        name="Assaulter",
        unit_type="Light Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates two maneuver or two save results.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_attacker",
        name="Attacker",
        unit_type="Light Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates one maneuver or one save result.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_bear_master",
        name="Bear Master",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Paw",
                "description": "Counts as three movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_cryohydra",
        name="Cryohydra",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Double Strike",
                "description": "During a melee attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Double Strike generates four melee results.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Frost Breath",
                "description": "During a melee or missile attack, target an opposing army at the same terrain. Until the beginning of your next turn, the target army halves all results they roll.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_defender",
        name="Defender",
        unit_type="Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates two maneuver or two save results.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_destroyer",
        name="Destroyer",
        unit_type="Heavy Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates one maneuver or one save result.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_devastator",
        name="Devastator",
        unit_type="Heavy Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates three maneuver or three save results.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_dispatcher",
        name="Dispatcher",
        unit_type="Heavy Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates two maneuver or two save results.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_frost_ogre",
        name="Frost Ogre",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Frost Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.\n* During a magic negation roll, Cantrip generates four anti-magic results.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as four spell points. Can be used for Magic Negation.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_hound_master",
        name="Hound Master",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Paw",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Paw",
                "description": "Counts as one movement point.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_magi",
        name="Magi",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Frost Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.\n* During a magic negation roll, Cantrip generates four anti-magic results.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as two spell points. Can be used for Magic Negation.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as four spell points. Can be used for Magic Negation.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_magus",
        name="Magus",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as three spell points. Can be used for Magic Negation.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates three maneuver or three save results.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as one spell point. Can be used for Magic Negation.",
            },
            {
                "name": "Frost Magic",
                "description": "Counts as two spell points. Can be used for Magic Negation.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_remorhaz",
        name="Remorhaz",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Swallow",
                "description": "During a melee attack, target one unit in the defending army. Roll the target. If it does not roll its ID icon, it is killed and buried.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Swallow",
                "description": "During a melee attack, target one unit in the defending army. Roll the target. If it does not roll its ID icon, it is killed and buried.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_vindicator",
        name="Vindicator",
        unit_type="Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Save",
                "description": "Counts as three save points.",
            },
            {
                "name": "Fly",
                "description": "During any roll, Fly generates four maneuver or four save results.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_wolf_master",
        name="Wolf Master",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Paw",
                "description": "Counts as three movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Paw",
                "description": "Counts as two movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_wolf_pack",
        name="Wolf Pack",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Howl",
                "description": "During a melee or missile attack, the defending army subtracts four save results.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Paw",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Paw",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Howl",
                "description": "During a melee or missile attack, the defending army subtracts four save results.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
        ],
    ),
    UnitModel(
        unit_id="frostwing_yeti",
        name="Yeti",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["FROSTWING"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
        ],
    ),
    # SCALDER UNITS
    UnitModel(
        unit_id="scalder_singeman",
        name="Singeman",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict one point of damage on the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_kindler",
        name="Kindler",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_dragonne_tender",
        name="Dragonne Tender",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict one point of damage on the attacking army.",
            },
            {
                "name": "Paw",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Paw",
                "description": "Counts as one movement point.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_glower",
        name="Glower",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_sparker",
        name="Sparker",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as 1 save point. When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict one point of damage on the attacking army.",
            },
            {
                "name": "Magic",
                "description": "Counts as one spell point.",
            },
            {
                "name": "Magic",
                "description": "Counts as two spell points.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Magic",
                "description": "Counts as one spell point.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_scorcher",
        name="Scorcher",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as two save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict two points of damage on the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_igniter",
        name="Igniter",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as three movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_dragonne_rider",
        name="Dragonne Rider",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as two save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict two points of damage on the attacking army.",
            },
            {
                "name": "Paw",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Paw",
                "description": "Counts as three movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_burner",
        name="Burner",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_smolderer",
        name="Smolderer",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as two save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict two points of damage on the attacking army.",
            },
            {
                "name": "Magic",
                "description": "Counts as one spell point.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Magic",
                "description": "Counts as three spell points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_searer",
        name="Searer",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as six melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as two save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict two points of damage on the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_charkin",
        name="Charkin",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Counter (scorching)",
                "description": "During a save roll against a melee attack, Counter generates four save results and inflicts four damage upon the attacking army. Only save results generated by spells may reduce this damage.\nNote: this damage is generated immediately, and is seperate from Scorching touch damage.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.\n* During any other save roll, Counter generates four save results.\n* During a melee attack, Counter generates four melee results.\n* During a dragon attack, Counter generates four save and four melee results.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as five melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as three movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_dragonne_knight",
        name="Dragonne Knight",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Scorching Wings",
                "description": "During any roll, Fly generates four maneuver or four save results.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as two save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict two points of damage on the attacking army.",
            },
            {
                "name": "Paw",
                "description": "Counts as six movement points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Paw",
                "description": "Counts as two movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_blazer",
        name="Blazer",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Flaming Arrow",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll. Those that do not generate a save result are killed.\n* Each unit killed must make another save roll. Those that do not generate a save result on this second roll are buried.\n* During a dragon attack, Flaming Arrow generates four missile results.",
            },
            {
                "name": "Move",
                "description": "Counts as three movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as six missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_inferno",
        name="Inferno",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Magic",
                "description": "Counts as six spell points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as two save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict two points of damage on the attacking army.",
            },
            {
                "name": "Magic",
                "description": "Counts as two spell points.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_ettercap",
        name="Ettercap",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as four save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as four save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_quickling",
        name="Quickling",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.\n* Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as four save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as four save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_unseelie_faerie",
        name="Unseelie Faerie",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as four save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Scorching Shield",
                "description": "Counts as four save points.  When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_web_birds",
        name="Web Birds",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Web",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. The targets make a melee roll.\n* Those that do not generate a melee result are webbed and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.\n* Web does nothing during a missile action targeting an opponents Reserve Army from a Tower on its eighth-face.",
            },
            {
                "name": "Scorching Wings",
                "description": "During any roll, Fly generates four maneuver or four save results.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
            },
            {
                "name": "Web",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army. The targets make a melee roll.\n* Those that do not generate a melee result are webbed and cannot be rolled or leave the terrain they currently occupy until the beginning of your next turn.\n* Web does nothing during a missile action targeting an opponents Reserve Army from a Tower on its eighth-face.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Scorching Wings",
                "description": "During any roll, Fly generates four maneuver or four save results.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
            },
        ],
    ),
    UnitModel(
        unit_id="scalder_will_o_wisps",
        name="Will o Wisps",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SCALDER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, its army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {
                "name": "Confuse",
                "description": "During a melee or missile attack, target up to four health-worth of units in the defending army after they have rolled for saves.\n* Re-roll the targeted units, ignoring all previous results. Units are selected prior to resolving the save roll or any SAIs in the defending army.",
            },
            {
                "name": "Scorching Wings",
                "description": "During any roll, Fly generates four maneuver or four save results.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
            },
            {
                "name": "Dispel Magic",
                "description": "Whenever any magic targets this unit, the army containing this unit and/or the terrain this unit occupies, you may roll this unit after all spells are announced but before any are resolved.\n* If the Dispel Magic icon is rolled, negate all unresolved magic that targets or effects this unit, its army or the terrain it occupies. Magic targeting other units, armies, or terrains is unaffected by this SAI.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Scorching Wings",
                "description": "During any roll, Fly generates four maneuver or four save results.\n* When at a terrain that contains red (fire), Scalders making a save roll against a melee action inflict four points of damage on the attacking army.\n* Only save results generated by spells may reduce this damage. Scorching Touch does not apply when saving against a counter-attack.",
            },
        ],
    ),
    # SWAMP_STALKER UNITS
    UnitModel(
        unit_id="swamp_stalker_warmonger",
        name="Warmonger",
        unit_type="Heavy Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_striker",
        name="Striker",
        unit_type="Light Melee",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_bog_runner",
        name="Bog Runner",
        unit_type="Cavalry",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
            {
                "name": "Move",
                "description": "Counts as one movement point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_sprayer",
        name="Sprayer",
        unit_type="Missile",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Missile",
                "description": "Counts as one missile hit point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_bog_adept",
        name="Bog Adept",
        unit_type="Magic",
        health=1,
        max_health=1,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as one point of whatever the owning army is rolling for.",
            },
            {
                "name": "Magic",
                "description": "Counts as two spell points.",
            },
            {
                "name": "Magic",
                "description": "Counts as one spell point.",
            },
            {
                "name": "Save",
                "description": "Counts as one save point.",
            },
            {
                "name": "Magic",
                "description": "Counts as one spell point.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_ravager",
        name="Ravager",
        unit_type="Heavy Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as one melee hit point.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_raider",
        name="Raider",
        unit_type="Light Melee",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as three melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as three movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_marsh_swimmer",
        name="Marsh Swimmer",
        unit_type="Cavalry",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_stormer",
        name="Stormer",
        unit_type="Missile",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_marsh_mage",
        name="Marsh Mage",
        unit_type="Magic",
        health=2,
        max_health=2,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as two points of whatever the owning army is rolling for.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Magic",
                "description": "Counts as two spell points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
            {
                "name": "Magic",
                "description": "Counts as two spell points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_annihilator",
        name="Annihilator",
        unit_type="Heavy Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Melee",
                "description": "Counts as five melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Save",
                "description": "Counts as three save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_invader",
        name="Invader",
        unit_type="Light Melee",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as three missile hit points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.\n* Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
            {
                "name": "Move",
                "description": "Counts as three movement points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_wave_rider",
        name="Wave Rider",
        unit_type="Cavalry",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Move",
                "description": "Counts as five movement points.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Coil",
                "description": "During a melee attack, target one unit in the defending army. The target takes four damage and makes a combination roll, counting save and melee results.\n* Any melee results that the target generates inflict damage on the Coiling unit with no save possible.\n* During a dragon attack, Coil generates four melee results.",
            },
            {
                "name": "Save",
                "description": "Counts as three save points.",
            },
            {
                "name": "Move",
                "description": "Counts as two movement points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_deluger",
        name="Deluger",
        unit_type="Missile",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Missile",
                "description": "Counts as five missile hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Bullseye",
                "description": "During a missile attack, target four health-worth of units in the defending army. The targets make a save roll.\n* Those that do not generate a save result are killed. Roll this unit again and apply the new result as well.\n* During a dragon attack, Bullseye generates four missile results.",
            },
            {
                "name": "Missile",
                "description": "Counts as two missile hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as three save points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_swamp_wizard",
        name="Swamp Wizard",
        unit_type="Magic",
        health=3,
        max_health=3,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as three points of whatever the owning army is rolling for.",
            },
            {
                "name": "Magic",
                "description": "Counts as five spell points.",
            },
            {
                "name": "Magic",
                "description": "Counts as three spell points.",
            },
            {
                "name": "Cantrip",
                "description": "During a magic action or magic negation roll, Cantrip generates four magic results.\n* During other non-maneuver rolls, Cantrip generates four magic results that allow you to cast spells marked as Cantrip from the spell list.",
            },
            {
                "name": "Save",
                "description": "Counts as two save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as two melee hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_crocosaur",
        name="Crocosaur",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Tail",
                "description": "During a dragon or melee attack, Tail generates two melee results. Roll this unit again and apply the new result as well.",
            },
            {
                "name": "Tail",
                "description": "During a dragon or melee attack, Tail generates two melee results. Roll this unit again and apply the new result as well.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Rend",
                "description": "During a melee or dragon attack, Rend generates four melee results. Roll this unit again and apply the new result as well.\n* During a maneuver roll, Rend generates four maneuver results.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_mudmen",
        name="Mudmen",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Smother",
                "description": "During a melee attack, target up to four health-worth of units in the defending army. The targets make a maneuver roll. Those that do not generate a maneuver result are killed.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_ormyrr",
        name="Ormyrr",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Magic",
                "description": "Counts as four spell points.",
            },
            {
                "name": "Coil",
                "description": "During a melee attack, target one unit in the defending army. The target takes four damage and makes a combination roll, counting save and melee results.\n* Any melee results that the target generates inflict damage on the Coiling unit with no save possible.\n* During a dragon attack, Coil generates four melee results.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Missile",
                "description": "Counts as four missile hit points.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_swamp_beast",
        name="Swamp Beast",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Surprise",
                "description": "During a melee attack, the defending army cannot counter-attack. The defending army may still make a save roll as normal. Surprise has no effect during a counter-attack.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Wave",
                "description": "During a melee attack, the defending army subtracts X from their save results.\n* During a maneuver roll whilst marching, subtract X from each counter-maneuvering armys maneuver results. Wave does nothing if rolled when counter-maneuvering.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.\n* Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
            {
                "name": "Wave",
                "description": "During a melee attack, the defending army subtracts X from their save results.\n* During a maneuver roll whilst marching, subtract X from each counter-maneuvering armys maneuver results. Wave does nothing if rolled when counter-maneuvering.",
            },
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.\n* Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
        ],
    ),
    UnitModel(
        unit_id="swamp_stalker_swamp_giant",
        name="Swamp Giant",
        unit_type="Monster",
        health=4,
        max_health=4,
        abilities={},
        species=SPECIES_DATA["SWAMP_STALKER"],
        faces=[
            {
                "name": "ID",
                "description": "Counts as four points of whatever the owning army is rolling for.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Poison",
                "description": "During a melee attack, target four health-worth of units in the defending army. Each targeted unit makes a save roll.\n* Those that do not generate a save result are killed and must make another save roll. Those that do not generate a save result on this second roll are buried.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
            {
                "name": "Melee",
                "description": "Counts as four melee hit points.",
            },
            {
                "name": "Move",
                "description": "Counts as four movement points.",
            },
            {
                "name": "Smite",
                "description": "During a melee attack, Smite inflicts four points of damage to the defending army with no save possible.\n* During a dragon attack, Smite generates four melee results.",
            },
            {
                "name": "Trample",
                "description": "During any roll, Trample generates four maneuver and four melee results.",
            },
            {
                "name": "Save",
                "description": "Counts as four save points.",
            },
        ],
    ),
]


# Helper functions for unit data access
def get_unit_by_id(unit_id: str):
    """Get a unit by its unit_id from UNIT_DATA."""
    for unit in UNIT_DATA:
        if hasattr(unit, "unit_id") and unit.unit_id == unit_id:
            return unit
    return None


def get_units_for_species(species_name: str) -> list:
    """Get all unit instances for a specific species from UNIT_DATA."""
    return [
        unit
        for unit in UNIT_DATA
        if hasattr(unit, "species_type")
        and unit.species_type.upper() == species_name.upper()
        or (hasattr(unit, "species") and unit.species and unit.species.name.upper() == species_name.upper())
    ]


def get_all_species() -> list:
    """Get a list of all species names from UNIT_DATA."""
    species_names = set()
    for unit in UNIT_DATA:
        if hasattr(unit, "species_type"):
            species_names.add(unit.species_type)
        elif hasattr(unit, "species"):
            if unit.species:
                species_names.add(unit.species.name)
    return list(species_names)


def get_units_by_class(unit_class_type: str) -> list:
    """Get all units of a specific class type from UNIT_DATA."""
    return [unit for unit in UNIT_DATA if hasattr(unit, "unit_type") and unit.unit_type == unit_class_type]


def validate_unit_data_integrity() -> bool:
    """Validate the integrity of all unit data. Returns True if all data is valid."""
    unit_ids = set()

    for unit in UNIT_DATA:
        # Check that it's a valid unit instance
        if not isinstance(unit, UnitModel):
            print(f"ERROR: Unit is not a valid Unit or UnitModel instance: {unit}")
            return False

        # Check for duplicate IDs
        unit_id = getattr(unit, "unit_id", None)
        if unit_id:
            if unit_id in unit_ids:
                print(f"ERROR: Duplicate unit unit_id: {unit_id}")
                return False
            unit_ids.add(unit_id)

        # Validate UnitModel instances
        if isinstance(unit, UnitModel):
            valid_unit_classes = [
                "Cavalry",
                "Heavy Magic",
                "Heavy Melee",
                "Heavy Missile",
                "Light Magic",
                "Light Melee",
                "Light Missile",
                "Magic",
                "Melee",
                "Missile",
                "Monster",
            ]
            valid_health_values = [1, 2, 3, 4]

            if not isinstance(unit.name, str) or not unit.name.strip():
                print(f"ERROR: Invalid name in {unit_id}")
                return False

            if hasattr(unit, "max_health") and unit.max_health not in valid_health_values:
                print(f"ERROR: Invalid max_health {unit.max_health} in {unit_id}")
                return False

            if hasattr(unit, "unit_type") and unit.unit_type not in valid_unit_classes:
                print(f"ERROR: Invalid unit_type '{unit.unit_type}' in {unit_id}")
                return False

    print(f"✓ All {len(unit_ids)} unit instances validated successfully")
    return True
