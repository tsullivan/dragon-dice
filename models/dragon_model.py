from typing import Dict, List
from models.element_model import ELEMENT_ICONS


class DragonAttackModel:
    """
    Model for dragon attack types.
    """

    def __init__(self, name: str, icon: str, display_name: str):
        self.name = name
        self.icon = icon
        self.display_name = display_name

    def __str__(self) -> str:
        return f"{self.icon} {self.display_name}"

    def __repr__(self) -> str:
        return f"DragonAttackModel(name='{self.name}', icon='{self.icon}', display_name='{self.display_name}')"


class DragonTypeModel:
    """
    Model for dragon types with element associations.
    """

    def __init__(self, name: str, display_name: str, element: str):
        self.name = name
        self.display_name = display_name
        self.element = element

        # Validate element
        if element not in [icon for icon, _ in ELEMENT_ICONS.values()]:
            raise ValueError(f"Invalid element icon: {element}")

    def __str__(self) -> str:
        return f"{self.element} {self.display_name}"

    def __repr__(self) -> str:
        return f"DragonTypeModel(name='{self.name}', display_name='{self.display_name}', element='{self.element}')"


class DragonDieTypeModel:
    """
    Model for dragon die types.
    """

    def __init__(self, name: str, display_name: str, description: str):
        self.name = name
        self.display_name = display_name
        self.description = description

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"DragonDieTypeModel(name='{self.name}', display_name='{self.display_name}')"


# Dragon attack instances
DRAGON_ATTACKS = {
    "CLAW": DragonAttackModel(name="CLAW", icon="🗺️", display_name="Claw Attack"),
    "BITE": DragonAttackModel(name="BITE", icon="🦷", display_name="Bite Attack"),
    "TAIL": DragonAttackModel(name="TAIL", icon="🐉", display_name="Tail Attack"),
    "BREATH": DragonAttackModel(name="BREATH", icon="🔥", display_name="Breath Attack"),
}

# Dragon type instances
DRAGON_TYPES = {
    "RED": DragonTypeModel(
        name="RED", display_name="Red Dragon", element=ELEMENT_ICONS["FIRE"][0]
    ),
    "BLUE": DragonTypeModel(
        name="BLUE", display_name="Blue Dragon", element=ELEMENT_ICONS["AIR"][0]
    ),
    "GREEN": DragonTypeModel(
        name="GREEN", display_name="Green Dragon", element=ELEMENT_ICONS["WATER"][0]
    ),
    "BLACK": DragonTypeModel(
        name="BLACK", display_name="Black Dragon", element=ELEMENT_ICONS["DEATH"][0]
    ),
    "GOLD": DragonTypeModel(
        name="GOLD", display_name="Gold Dragon", element=ELEMENT_ICONS["EARTH"][0]
    ),
    "UNDEAD": DragonTypeModel(
        name="UNDEAD", display_name="Undead Dragon", element=ELEMENT_ICONS["DEATH"][0]
    ),
    "SWAMP": DragonTypeModel(
        name="SWAMP", display_name="Swamp Dragon", element=ELEMENT_ICONS["WATER"][0]
    ),
    "IVORY": DragonTypeModel(
        name="IVORY", display_name="Ivory Dragon", element=ELEMENT_ICONS["IVORY"][0]
    ),
}

# Dragon die type instances
DRAGON_DIE_TYPES = {
    "DRAKE": DragonDieTypeModel(
        name="DRAKE", display_name="Drake", description="Standard dragon die"
    ),
    "WYRM": DragonDieTypeModel(
        name="WYRM", display_name="Wyrm", description="Advanced dragon die"
    ),
}

# Combined dragon data structure
DRAGON_DATA = {
    "ATTACKS": DRAGON_ATTACKS,
    "TYPES": DRAGON_TYPES,
    "DIE_TYPES": DRAGON_DIE_TYPES,
}


# Helper functions
def get_dragon_attack(attack_name: str) -> DragonAttackModel:
    """Get a dragon attack by name."""
    attack_key = attack_name.upper()
    return DRAGON_ATTACKS.get(attack_key)


def get_dragon_type(type_name: str) -> DragonTypeModel:
    """Get a dragon type by name."""
    type_key = type_name.upper()
    return DRAGON_TYPES.get(type_key)


def get_dragon_die_type(die_type_name: str) -> DragonDieTypeModel:
    """Get a dragon die type by name."""
    die_type_key = die_type_name.upper()
    return DRAGON_DIE_TYPES.get(die_type_key)


def get_all_dragon_attack_names() -> List[str]:
    """Get all dragon attack names."""
    return list(DRAGON_ATTACKS.keys())


def get_all_dragon_type_names() -> List[str]:
    """Get all dragon type names."""
    return list(DRAGON_TYPES.keys())


def get_all_dragon_die_type_names() -> List[str]:
    """Get all dragon die type names."""
    return list(DRAGON_DIE_TYPES.keys())


def get_available_dragon_types() -> List[str]:
    """Get available dragon type display names."""
    return [dragon_type.display_name for dragon_type in DRAGON_TYPES.values()]


def get_available_dragon_die_types() -> List[str]:
    """Get available dragon die type display names."""
    return [die_type.display_name for die_type in DRAGON_DIE_TYPES.values()]


def validate_dragon_data() -> bool:
    """Validate all dragon data."""
    try:
        # Validate dragon attacks
        for attack_name, attack in DRAGON_ATTACKS.items():
            if not isinstance(attack, DragonAttackModel):
                print(f"ERROR: {attack_name} is not a DragonAttackModel instance")
                return False
            if attack.name != attack_name:
                print(
                    f"ERROR: Dragon attack name mismatch: {attack.name} != {attack_name}"
                )
                return False

        # Validate dragon types
        for type_name, dragon_type in DRAGON_TYPES.items():
            if not isinstance(dragon_type, DragonTypeModel):
                print(f"ERROR: {type_name} is not a DragonTypeModel instance")
                return False
            if dragon_type.name != type_name:
                print(
                    f"ERROR: Dragon type name mismatch: {dragon_type.name} != {type_name}"
                )
                return False

        # Validate dragon die types
        for die_type_name, die_type in DRAGON_DIE_TYPES.items():
            if not isinstance(die_type, DragonDieTypeModel):
                print(f"ERROR: {die_type_name} is not a DragonDieTypeModel instance")
                return False
            if die_type.name != die_type_name:
                print(
                    f"ERROR: Dragon die type name mismatch: {die_type.name} != {die_type_name}"
                )
                return False

        print(f"✓ All dragon data validated successfully")
        print(f"  - {len(DRAGON_ATTACKS)} dragon attacks")
        print(f"  - {len(DRAGON_TYPES)} dragon types")
        print(f"  - {len(DRAGON_DIE_TYPES)} dragon die types")
        return True
    except Exception as e:
        print(f"ERROR: Dragon data validation failed: {e}")
        return False
