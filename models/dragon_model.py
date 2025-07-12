import uuid
from typing import Any, Dict, List, Optional

from models.die_face_model import DRAGON_DIE_FACES, DieFaceModel
from models.element_model import ELEMENT_DATA


class DragonModel:
    """
    Represents an individual dragon instance in the game.
    Each dragon has a unique ID, name, form (Drake/Wyrm), type, elements, health, and owner.
    """

    def __init__(
        self,
        name: str,
        dragon_form: str,  # "DRAKE" or "WYRM"
        dragon_type: str,  # Dragon type key like "FIRE_ELEMENTAL"
        elements: List[str],  # Element keys like ["FIRE"] or ["WATER", "AIR"]
        owner: str,
        health: Optional[int] = None,
    ):
        self.unique_id = str(uuid.uuid4())
        self.name = name
        self.dragon_form = dragon_form.upper()  # DRAKE or WYRM
        self.dragon_type = dragon_type.upper()
        self.elements = [element.upper() for element in elements]
        self.owner = owner

        # Set health based on dragon type, defaulting to 5 (10 for White Dragons)
        if health is not None:
            self.health = health
        else:
            self.health = 10 if dragon_type.upper() == "WHITE" else 5

        self.max_health = self.health  # Track original health
        self._validate()

    def _validate(self):
        """Validate dragon instance data."""
        if not self.name:
            raise ValueError("Dragon must have a name")

        if self.dragon_form not in ["DRAKE", "WYRM"]:
            raise ValueError(f"Invalid dragon form: {self.dragon_form}. Must be DRAKE or WYRM")

        if not self.elements:
            raise ValueError("Dragon must have at least one element")

        if self.health <= 0:
            raise ValueError("Dragon health must be positive")

        if not self.owner:
            raise ValueError("Dragon must have an owner")

    def get_id(self) -> str:
        """Get the unique ID of this dragon."""
        return self.unique_id

    def get_form_data(self) -> Optional["Dragon"]:
        """Get the dragon form data (faces, etc.)."""
        return DRAGON_FORM_DATA.get(self.dragon_form)

    def get_type_data(self) -> Optional["DragonTypeModel"]:
        """Get the dragon type data (rules, display info, etc.)."""
        return DRAGON_TYPE_DATA.get(self.dragon_type)

    def get_display_name(self) -> str:
        """Get the full display name of this dragon."""
        type_data = self.get_type_data()
        if type_data:
            return f"{self.name} ({type_data.get_display_name()} {self.dragon_form.title()})"
        return f"{self.name} ({self.dragon_type} {self.dragon_form.title()})"

    def is_alive(self) -> bool:
        """Check if the dragon is alive."""
        return self.health > 0

    def is_dead(self) -> bool:
        """Check if the dragon is dead."""
        return self.health <= 0

    def take_damage(self, damage: int) -> int:
        """Apply damage to the dragon and return actual damage taken."""
        if damage <= 0:
            return 0

        actual_damage = min(damage, self.health)
        self.health -= actual_damage
        print(f"DragonModel: {self.name} took {actual_damage} damage (health: {self.health}/{self.max_health})")
        return actual_damage

    def heal(self, amount: int) -> int:
        """Heal the dragon and return actual healing done."""
        if amount <= 0:
            return 0

        max_healing = self.max_health - self.health
        actual_healing = min(amount, max_healing)
        self.health += actual_healing
        print(f"DragonModel: {self.name} healed {actual_healing} (health: {self.health}/{self.max_health})")
        return actual_healing

    def reset_health(self):
        """Reset dragon to full health."""
        self.health = self.max_health

    def has_element(self, element: str) -> bool:
        """Check if the dragon has a specific element."""
        return element.upper() in self.elements

    def has_any_element(self, elements: List[str]) -> bool:
        """Check if the dragon has any of the specified elements."""
        return any(self.has_element(element) for element in elements)

    def has_all_elements(self, elements: List[str]) -> bool:
        """Check if the dragon has all of the specified elements."""
        return all(self.has_element(element) for element in elements)

    def is_white_dragon(self) -> bool:
        """Check if this is a White Dragon."""
        return self.dragon_type == "WHITE"

    def is_hybrid_dragon(self) -> bool:
        """Check if this is a Hybrid Dragon."""
        type_data = self.get_type_data()
        return type_data is not None and type_data.dragon_type in [DragonTypeModel.HYBRID, DragonTypeModel.IVORY_HYBRID]

    def is_ivory_dragon(self) -> bool:
        """Check if this is an Ivory Dragon."""
        type_data = self.get_type_data()
        return type_data is not None and type_data.dragon_type in [DragonTypeModel.IVORY, DragonTypeModel.IVORY_HYBRID]

    def can_be_summoned_from_terrain(self) -> bool:
        """Check if this dragon can be summoned from terrain (not just summoning pool)."""
        type_data = self.get_type_data()
        return type_data is not None and type_data.can_summon_from_terrain()

    def get_force_value(self) -> int:
        """Get how many dragons this counts as for force assembly."""
        type_data = self.get_type_data()
        return type_data.get_force_value() if type_data else 1

    def has_doubled_damage(self) -> bool:
        """Check if this dragon has doubled damage."""
        type_data = self.get_type_data()
        return type_data is not None and type_data.has_doubled_damage()

    def has_doubled_treasure(self) -> bool:
        """Check if this dragon has doubled treasure results."""
        type_data = self.get_type_data()
        return type_data is not None and type_data.has_doubled_treasure()

    def to_dict(self) -> Dict[str, Any]:
        """Convert dragon to dictionary for serialization."""
        return {
            "unique_id": self.unique_id,
            "name": self.name,
            "dragon_form": self.dragon_form,
            "dragon_type": self.dragon_type,
            "elements": self.elements,
            "owner": self.owner,
            "health": self.health,
            "max_health": self.max_health,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DragonModel":
        """Create dragon from dictionary data."""
        dragon = cls(
            name=data["name"],
            dragon_form=data["dragon_form"],
            dragon_type=data["dragon_type"],
            elements=data["elements"],
            owner=data["owner"],
            health=data["health"],
        )
        dragon.max_health = data.get("max_health", dragon.health)
        return dragon

    def copy(self) -> "DragonModel":
        """Create a copy of this dragon with a new unique ID."""
        return DragonModel(
            name=self.name,
            dragon_form=self.dragon_form,
            dragon_type=self.dragon_type,
            elements=self.elements.copy(),
            owner=self.owner,
            health=self.health,
        )

    def __str__(self) -> str:
        return self.get_display_name()

    def __repr__(self) -> str:
        return f"DragonModel(name='{self.name}', type='{self.dragon_type}', form='{self.dragon_form}', owner='{self.owner}', health={self.health})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, DragonModel):
            return False
        return self.unique_id == other.unique_id

    def __hash__(self) -> int:
        return hash(self.unique_id)


class Dragon:
    """
    Represents a dragon die type in the Dragon Dice game.
    Each dragon has a display name and 12 faces with their effects.
    """

    def __init__(self, display_name: str, face_names: List[str]):
        self.display_name = display_name
        self.name = display_name.upper()  # Normalized name for keys
        self.faces = [DRAGON_DIE_FACES[face_name] for face_name in face_names]

        self._validate()

    def _validate(self):
        """Validate dragon data."""
        if len(self.faces) != 12:
            raise ValueError(f"Dragon must have exactly 12 faces, got {len(self.faces)}")

        if not self.display_name:
            raise ValueError("Dragon must have a display name")

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"Dragon(display_name='{self.display_name}', faces={len(self.faces)})"

    def get_face_names(self) -> List[str]:
        """Get all face names for this dragon."""
        return [face.name for face in self.faces]

    def get_face_by_name(self, face_name: str) -> Optional[DieFaceModel]:
        """Get a specific face by name."""
        for face in self.faces:
            if face.name == face_name:
                return face
        return None

    def get_face_by_index(self, index: int) -> Optional[DieFaceModel]:
        """Get a face by its index (0-11)."""
        if 0 <= index < len(self.faces):
            return self.faces[index]
        return None


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
    Model for different dragon types with their rules and display formatting.
    Supports Elemental, Hybrid, Ivory, Ivory Hybrid, and White dragons.
    """

    # Dragon type constants
    ELEMENTAL = "ELEMENTAL"
    HYBRID = "HYBRID"
    IVORY = "IVORY"
    IVORY_HYBRID = "IVORY_HYBRID"
    WHITE = "WHITE"

    def __init__(
        self,
        name: str,
        dragon_type: str,
        elements: List[str],
        is_white: bool = False,
    ):
        self.name = name
        self.dragon_type = dragon_type
        self.elements = elements  # List of element keys like ["FIRE"] or ["WATER", "AIR"]
        self.is_white = is_white

        self._validate()

    def _validate(self):
        """Validate dragon type data."""
        valid_types = [self.ELEMENTAL, self.HYBRID, self.IVORY, self.IVORY_HYBRID, self.WHITE]
        if self.dragon_type not in valid_types:
            raise ValueError(f"Invalid dragon type: {self.dragon_type}. Must be one of {valid_types}")

        if self.dragon_type == self.HYBRID and len(self.elements) != 2:
            raise ValueError("Hybrid dragons must have exactly 2 elements")

        if self.dragon_type == self.IVORY_HYBRID and len(self.elements) != 1:
            raise ValueError("Ivory Hybrid dragons must have exactly 1 element")

        if self.dragon_type in [self.ELEMENTAL, self.IVORY, self.WHITE] and len(self.elements) != 1:
            raise ValueError(f"{self.dragon_type} dragons must have exactly 1 element")

        # Validate elements exist
        for element in self.elements:
            if element not in ELEMENT_DATA:
                raise ValueError(f"Invalid element: {element}")

    def get_element_icons(self) -> List[str]:
        """Get the element icons for this dragon."""
        return [ELEMENT_DATA[element].icon for element in self.elements]

    def get_display_name(self) -> str:
        """Get the formatted display name for this dragon type."""
        element_icons = self.get_element_icons()

        if self.dragon_type == self.ELEMENTAL:
            # "{black_icon} Death Elemental"
            base_name = f"{ELEMENT_DATA[self.elements[0]].display_name} Elemental"
            if self.is_white:
                base_name = f"White {base_name}"
            return f"{''.join(element_icons)} {base_name}"

        if self.dragon_type == self.HYBRID:
            # "{green_icon}{blue_icon} Water/Air Hybrid"
            element_names = [ELEMENT_DATA[elem].display_name for elem in self.elements]
            base_name = f"{'/'.join(element_names)} Hybrid"
            return f"{''.join(element_icons)} {base_name}"

        if self.dragon_type == self.IVORY:
            # Same as Elemental but Ivory rules
            base_name = f"{ELEMENT_DATA[self.elements[0]].display_name} Elemental"
            return f"{''.join(element_icons)} {base_name}"

        if self.dragon_type == self.IVORY_HYBRID:
            # Ivory Hybrid: element + ivory
            element_name = ELEMENT_DATA[self.elements[0]].display_name
            base_name = f"Ivory/{element_name} Hybrid Dragon"
            return f"🟫{''.join(element_icons)} {base_name}"

        if self.dragon_type == self.WHITE:
            # White Dragon
            return f"{''.join(element_icons)} White Dragon"

        return self.name  # Fallback

    def get_description(self) -> str:
        """Get the detailed description for this dragon type."""
        if self.dragon_type == self.ELEMENTAL:
            return "The standard dragon is an Elemental Dragon. It is made up of one of the five elements."

        if self.dragon_type == self.HYBRID:
            return (
                "Hybrid Dragons are composed of two elements.\n"
                "When a breath result is rolled, apply both elemental breath effects.\n"
                "Hybrid Dragons are affected by any spell or effect that can affect either of its elements."
            )

        if self.dragon_type == self.IVORY:
            return (
                "Ivory Dragons may be summoned by using any one single element of magic or by any effect of a single element (such as a Dragon's Lair or Dragon Staff).\n"
                "Ivory Dragons may only be summoned from the Summoning Pool. They may not be summoned from another terrain."
            )

        if self.dragon_type == self.IVORY_HYBRID:
            return (
                "Ivory Hybrid Dragons are composed of one element and ivory.\n"
                "When a breath result is rolled, apply the elemental breath effect.\n"
                "Ivory Hybrid Dragons are affected by any spell or effect that can affect its element or ivory.\n"
                "Ivory Hybrid Dragons can only be summoned from a terrain by magic or an effect that matches their element."
            )

        if self.dragon_type == self.WHITE:
            return (
                "White Dragons have ten health instead of five.\n"
                "All damage inflicted from a White Dragon's claws, jaws, tail and wing results are doubled.\n"
                "In addition, treasure results are also doubled, allowing two units to be promoted instead of one.\n"
                "White Dragons count as two normal dragons when assembling forces.\n"
                "White Dragons can only be summoned by the Summon White Dragon spell."
            )

        return "Unknown dragon type."

    def get_health(self) -> int:
        """Get the health of this dragon type."""
        if self.dragon_type == self.WHITE:
            return 10
        return 5

    def get_force_value(self) -> int:
        """Get how many dragons this counts as for force assembly."""
        if self.dragon_type == self.WHITE:
            return 2
        return 1

    def has_doubled_damage(self) -> bool:
        """Check if this dragon type has doubled damage."""
        return self.dragon_type == self.WHITE

    def has_doubled_treasure(self) -> bool:
        """Check if this dragon type has doubled treasure results."""
        return self.dragon_type == self.WHITE

    def can_summon_from_terrain(self) -> bool:
        """Check if this dragon can be summoned from terrain (not just summoning pool)."""
        return self.dragon_type not in [self.IVORY]

    def __str__(self) -> str:
        return self.get_display_name()

    def __repr__(self) -> str:
        return f"DragonTypeModel(name='{self.name}', type='{self.dragon_type}', elements={self.elements})"


# Static dragon die data - define dragon instances based on JSON structure
DRAGON_FORM_DATA = {
    "DRAKE": Dragon(
        display_name="Drake",
        face_names=[
            "Jaws",
            "Dragon_Breath",
            "Claw_Front_Left",
            "Claw_Front_Right",
            "Wing_Left",
            "Wing_Right",
            "Belly_Front",
            "Belly_Rear",
            "Claw_Rear_Left",
            "Claw_Rear_Right",
            "Tail_Front",
            "Tail_Tip",
        ],
    ),
    "WYRM": Dragon(
        display_name="Wyrm",
        face_names=[
            "Jaws",
            "Dragon_Breath",
            "Claw_Front_Left",
            "Claw_Front_Right",
            "Belly_Front",
            "Belly_Rear",
            "Claw_Rear_Left",
            "Claw_Rear_Right",
            "Tail_Front",
            "Tail_Middle",
            "Tail_Tip",
            "Treasure",
        ],
    ),
}

# Complete dragon type definitions - all possible dragon types from the game
DRAGON_TYPE_DATA = {
    # Elemental Dragons (single element)
    "EARTH_ELEMENTAL": DragonTypeModel(
        name="Earth Elemental Dragon", dragon_type=DragonTypeModel.ELEMENTAL, elements=["EARTH"]
    ),
    "FIRE_ELEMENTAL": DragonTypeModel(
        name="Fire Elemental Dragon", dragon_type=DragonTypeModel.ELEMENTAL, elements=["FIRE"]
    ),
    "WATER_ELEMENTAL": DragonTypeModel(
        name="Water Elemental Dragon", dragon_type=DragonTypeModel.ELEMENTAL, elements=["WATER"]
    ),
    "AIR_ELEMENTAL": DragonTypeModel(
        name="Air Elemental Dragon", dragon_type=DragonTypeModel.ELEMENTAL, elements=["AIR"]
    ),
    "DEATH_ELEMENTAL": DragonTypeModel(
        name="Death Elemental Dragon", dragon_type=DragonTypeModel.ELEMENTAL, elements=["DEATH"]
    ),
    # Hybrid Dragons (two elements) - all combinations
    "DEATH_AIR_HYBRID": DragonTypeModel(
        name="Death/Air Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["DEATH", "AIR"]
    ),
    "DEATH_WATER_HYBRID": DragonTypeModel(
        name="Death/Water Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["DEATH", "WATER"]
    ),
    "DEATH_EARTH_HYBRID": DragonTypeModel(
        name="Death/Earth Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["DEATH", "EARTH"]
    ),
    "AIR_DEATH_HYBRID": DragonTypeModel(
        name="Air/Death Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["AIR", "DEATH"]
    ),
    "AIR_WATER_HYBRID": DragonTypeModel(
        name="Air/Water Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["AIR", "WATER"]
    ),
    "AIR_EARTH_HYBRID": DragonTypeModel(
        name="Air/Earth Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["AIR", "EARTH"]
    ),
    "WATER_DEATH_HYBRID": DragonTypeModel(
        name="Water/Death Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["WATER", "DEATH"]
    ),
    "WATER_AIR_HYBRID": DragonTypeModel(
        name="Water/Air Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["WATER", "AIR"]
    ),
    "WATER_EARTH_HYBRID": DragonTypeModel(
        name="Water/Earth Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["WATER", "EARTH"]
    ),
    "FIRE_DEATH_HYBRID": DragonTypeModel(
        name="Fire/Death Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["FIRE", "DEATH"]
    ),
    "FIRE_AIR_HYBRID": DragonTypeModel(
        name="Fire/Air Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["FIRE", "AIR"]
    ),
    "FIRE_WATER_HYBRID": DragonTypeModel(
        name="Fire/Water Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["FIRE", "WATER"]
    ),
    "FIRE_EARTH_HYBRID": DragonTypeModel(
        name="Fire/Earth Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["FIRE", "EARTH"]
    ),
    "EARTH_DEATH_HYBRID": DragonTypeModel(
        name="Earth/Death Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["EARTH", "DEATH"]
    ),
    "EARTH_AIR_HYBRID": DragonTypeModel(
        name="Earth/Air Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["EARTH", "AIR"]
    ),
    "EARTH_WATER_HYBRID": DragonTypeModel(
        name="Earth/Water Hybrid Dragon", dragon_type=DragonTypeModel.HYBRID, elements=["EARTH", "WATER"]
    ),
    # Ivory Dragons
    "IVORY": DragonTypeModel(name="Ivory Dragon", dragon_type=DragonTypeModel.IVORY, elements=["IVORY"]),
    # Ivory Hybrid Dragons (element + ivory)
    "IVORY_DEATH_HYBRID": DragonTypeModel(
        name="Ivory/Death Hybrid Dragon", dragon_type=DragonTypeModel.IVORY_HYBRID, elements=["DEATH"]
    ),
    "IVORY_AIR_HYBRID": DragonTypeModel(
        name="Ivory/Air Hybrid Dragon", dragon_type=DragonTypeModel.IVORY_HYBRID, elements=["AIR"]
    ),
    "IVORY_WATER_HYBRID": DragonTypeModel(
        name="Ivory/Water Hybrid Dragon", dragon_type=DragonTypeModel.IVORY_HYBRID, elements=["WATER"]
    ),
    "IVORY_FIRE_HYBRID": DragonTypeModel(
        name="Ivory/Fire Hybrid Dragon", dragon_type=DragonTypeModel.IVORY_HYBRID, elements=["FIRE"]
    ),
    "IVORY_EARTH_HYBRID": DragonTypeModel(
        name="Ivory/Earth Hybrid Dragon", dragon_type=DragonTypeModel.IVORY_HYBRID, elements=["EARTH"]
    ),
    # White Dragons
    "WHITE": DragonTypeModel(name="White Dragon", dragon_type=DragonTypeModel.WHITE, elements=["WHITE"], is_white=True),
}


# Helper functions for dragons
def get_dragon(dragon_name: str) -> Optional[Dragon]:
    """Get a dragon die by name (DRAKE or WYRM)."""
    dragon_key = dragon_name.upper()
    return DRAGON_FORM_DATA.get(dragon_key)


def get_all_dragon_names() -> List[str]:
    """Get all dragon die names."""
    return list(DRAGON_FORM_DATA.keys())


def get_all_dragons() -> List[Dragon]:
    """Get all dragon die objects."""
    return list(DRAGON_FORM_DATA.values())


def get_available_dragon_forms() -> List[str]:
    """Get available dragon die forms (Drake, Wyrm)."""
    return [dragon.display_name for dragon in DRAGON_FORM_DATA.values()]


def get_available_dragon_types() -> List[str]:
    """Get available dragon type names."""
    return list(DRAGON_TYPE_DATA.keys())


def get_dragon_type(dragon_type_name: str) -> Optional[DragonTypeModel]:
    """Get a dragon type by name."""
    dragon_type_key = dragon_type_name.upper()
    return DRAGON_TYPE_DATA.get(dragon_type_key)


def get_all_dragon_type_names() -> List[str]:
    """Get all dragon type names."""
    return list(DRAGON_TYPE_DATA.keys())


def get_all_dragon_types() -> List[DragonTypeModel]:
    """Get all dragon type objects."""
    return list(DRAGON_TYPE_DATA.values())


def create_dragon_type(name: str, dragon_type: str, elements: List[str], is_white: bool = False) -> DragonTypeModel:
    """Create a new dragon type instance."""
    return DragonTypeModel(name=name, dragon_type=dragon_type, elements=elements, is_white=is_white)


def get_elemental_dragon_types() -> List[DragonTypeModel]:
    """Get all elemental dragon types."""
    return [dt for dt in DRAGON_TYPE_DATA.values() if dt.dragon_type == DragonTypeModel.ELEMENTAL]


def get_hybrid_dragon_types() -> List[DragonTypeModel]:
    """Get all hybrid dragon types."""
    return [dt for dt in DRAGON_TYPE_DATA.values() if dt.dragon_type == DragonTypeModel.HYBRID]


def get_ivory_dragon_types() -> List[DragonTypeModel]:
    """Get all ivory dragon types."""
    return [dt for dt in DRAGON_TYPE_DATA.values() if dt.dragon_type == DragonTypeModel.IVORY]


def get_white_dragon_types() -> List[DragonTypeModel]:
    """Get all white dragon types."""
    return [dt for dt in DRAGON_TYPE_DATA.values() if dt.dragon_type == DragonTypeModel.WHITE]


def validate_dragon_data() -> bool:
    """Validate all dragon data."""
    try:
        # Validate dragon dice
        for dragon_name, dragon in DRAGON_FORM_DATA.items():
            if not isinstance(dragon, Dragon):
                print(f"ERROR: {dragon_name} is not a Dragon instance")
                return False
            if dragon.name != dragon_name:
                print(f"ERROR: Dragon name mismatch: {dragon.name} != {dragon_name}")
                return False
            if len(dragon.faces) != 12:
                print(f"ERROR: Dragon {dragon_name} has {len(dragon.faces)} faces, expected 12")
                return False

        # Validate dragon types
        for dragon_type_name, dragon_type in DRAGON_TYPE_DATA.items():
            if not isinstance(dragon_type, DragonTypeModel):
                print(f"ERROR: {dragon_type_name} is not a DragonTypeModel instance")
                return False

            # Validate display name generation
            try:
                display_name = dragon_type.get_display_name()
                if not display_name:
                    print(f"ERROR: Dragon type {dragon_type_name} has empty display name")
                    return False
            except Exception as e:
                print(f"ERROR: Dragon type {dragon_type_name} failed display name generation: {e}")
                return False

            # Validate description
            try:
                description = dragon_type.get_description()
                if not description:
                    print(f"ERROR: Dragon type {dragon_type_name} has empty description")
                    return False
            except Exception as e:
                print(f"ERROR: Dragon type {dragon_type_name} failed description generation: {e}")
                return False

        print("✓ All dragon data validated successfully")
        print(f"  - {len(DRAGON_FORM_DATA)} dragon forms")
        print(f"  - {len(DRAGON_TYPE_DATA)} dragon types")
        return True
    except Exception as e:
        print(f"ERROR: Dragon data validation failed: {e}")
        return False


def calculate_required_dragons(force_size_points: int) -> int:
    """Calculate required dragons based on force size points.

    Official rules: 1 dragon per 24 points (or part thereof)
    Examples: 15 pts = 1 dragon, 24 pts = 1 dragon, 30 pts = 2 dragons, 60 pts = 3 dragons
    """
    import math

    POINTS_PER_DRAGON = 24  # noqa: N806
    return math.ceil(force_size_points / POINTS_PER_DRAGON)
