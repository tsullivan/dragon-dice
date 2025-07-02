# models/unit_model.py
from typing import Dict, Any, List, Optional


class UnitFace:
    """Represents a single face on a unit die."""

    # Face type constants for compatibility with legacy code
    ICON_MELEE = "MELEE"
    ICON_MISSILE = "MISSILE"
    ICON_MAGIC = "MAGIC"
    ICON_SAVE = "SAVE"
    ICON_ID = "ID"
    ICON_SAI = "SAI"
    ICON_MANEUVER = "MANEUVER"
    ICON_DRAGON_ATTACK_CLAW = "DRAGON_CLAW"
    ICON_DRAGON_ATTACK_BITE = "DRAGON_BITE"
    ICON_DRAGON_ATTACK_TAIL = "DRAGON_TAIL"
    ICON_DRAGON_BREATH = "DRAGON_BREATH"
    
    # SAI constants
    SAI_BULLSEYE = "BULLSEYE"
    SAI_DOUBLER = "DOUBLER"
    SAI_TRIPLER = "TRIPLER"
    SAI_RECRUIT = "RECRUIT"
    SAI_MAGIC_BOLT = "MAGIC_BOLT"

    # Face emoji and color mappings for display
    _FACE_INFO_MAP = {
        # Basic combat faces
        "Melee": {"emoji": "⚔️", "color": "#ffeeee"},  # Sword
        "Missile": {"emoji": "🏹", "color": "#eeeeff"},  # Bow and arrow
        "Magic": {"emoji": "✨", "color": "#ffffee"},  # Sparkles
        "Save": {"emoji": "🛡️", "color": "#eeffee"},  # Shield
        "ID": {"emoji": "🆔", "color": "#f0f0f0"},  # ID symbol
        "ID(kin)": {"emoji": "🆔", "color": "#f0f0f0"},  # ID symbol for dragonkin
        "Move": {"emoji": "👟", "color": "#fff0ee"},  # Running shoe
        # Dragon faces
        "Jaws": {"emoji": "🐉", "color": "#ffe0e0"},  # Dragon
        "Claw": {"emoji": "🦅", "color": "#e0e0ff"},  # Eagle (claws)
        "Belly": {"emoji": "🎯", "color": "#e0ffe0"},  # Target (vulnerable)
        "Tail": {"emoji": "🌪️", "color": "#ffffe0"},  # Tornado (tail whip)
        "Treasure": {"emoji": "💎", "color": "#ffe0ff"},  # Gem
        # Special combat abilities
        "Kick": {"emoji": "🦵", "color": "#ffeedd"},  # Leg (kick)
        "Trample": {"emoji": "🐘", "color": "#ddffdd"},  # Elephant (trample)
        "Trample2": {"emoji": "🐘", "color": "#ddffdd"},  # Elephant (trample)
        "Charge": {"emoji": "🏇", "color": "#fff0f0"},  # Horse racing (charge)
        "Gore": {"emoji": "🐂", "color": "#ffdddd"},  # Bull (gore)
        "Stomp": {"emoji": "🦶", "color": "#ffeecc"},  # Foot (stomp)
        "Bash": {"emoji": "🔨", "color": "#eeddff"},  # Hammer (bash)
        "Rend": {"emoji": "💥", "color": "#ffdddd"},  # Explosion (rend)
        "Smite": {"emoji": "⚡", "color": "#ffffdd"},  # Lightning (smite)
        # Ranged abilities
        "Bullseye": {"emoji": "🎯", "color": "#ddddff"},  # Target
        "Volley": {"emoji": "🏹", "color": "#ddffdd"},  # Multiple arrows
        "Net": {"emoji": "🕸️", "color": "#eeeeee"},  # Web/net
        # Magic abilities
        "Flame": {"emoji": "🔥", "color": "#ffdddd"},  # Fire
        "Firebreath": {"emoji": "🔥", "color": "#ffdddd"},  # Fire
        "Teleport": {"emoji": "🌀", "color": "#ddffff"},  # Swirl (teleport)
        "Fly": {"emoji": "🪶", "color": "#f0f0ff"},  # Feather (fly)
        "Fly2": {"emoji": "🪶", "color": "#f0f0ff"},  # Feather (fly)
        "Poison": {"emoji": "☠️", "color": "#ddffdd"},  # Skull (poison)
        "Sleep": {"emoji": "😴", "color": "#f0f0ff"},  # Sleeping face
        "Charm": {"emoji": "💫", "color": "#fff0ff"},  # Dizzy (charm)
        "Confuse": {"emoji": "😵", "color": "#fff0f0"},  # Confused face
        "Stun": {"emoji": "💫", "color": "#ffffdd"},  # Dizzy (stun)
        "Stone": {"emoji": "🗿", "color": "#dddddd"},  # Stone statue
        "Vanish": {"emoji": "👻", "color": "#f5f5f5"},  # Ghost (vanish)
        "Illusion": {"emoji": "🎭", "color": "#fff0ff"},  # Theater masks
        # Healing/support
        "Regenerate": {"emoji": "💚", "color": "#f0fff0"},  # Green heart (heal)
        "Convert": {"emoji": "🔄", "color": "#fff0f0"},  # Arrows (convert)
        "Rise From Ashes": {"emoji": "🔥", "color": "#ffddcc"},  # Phoenix rising
        "Flaming Shield": {"emoji": "🔥", "color": "#ffeecc"},  # Fire shield
        # Animal abilities
        "Paw": {"emoji": "🐾", "color": "#fff0ee"},  # Paw prints
        "Hoof": {"emoji": "🐴", "color": "#fff0ee"},  # Horse (hoof)
        "Roar": {"emoji": "🦁", "color": "#ffee00"},  # Lion (roar)
        "Roar2": {"emoji": "🦁", "color": "#ffee00"},  # Lion (roar)
        "Screech": {"emoji": "🦅", "color": "#eeeeff"},  # Eagle (screech)
        "Hug": {"emoji": "🤗", "color": "#fff0f0"},  # Hugging face
        "Scare": {"emoji": "😱", "color": "#ffeeee"},  # Scared face
        "Swallow": {"emoji": "🐍", "color": "#eeffee"},  # Snake (swallow)
        # Special dragon abilities
        "SFR (Dragonhunter)": {"emoji": "🗡️", "color": "#ffeeee"},  # Sword
        "SFR (Dragonzealot)": {"emoji": "⚔️", "color": "#ffeeee"},  # Crossed swords
        "TSR (Dragonmaster)": {"emoji": "🔮", "color": "#eeeeff"},  # Crystal ball
        # Dragonkin-specific abilities
        "SFR (Dragonkin Champion)": {"emoji": "🗡️", "color": "#ffeeee"},  # Sword (similar to Dragonhunter)
        "Dragonkin Breath (Champion)": {"emoji": "🐉", "color": "#ffe0e0"},  # Dragon breath
        "Dragonkin Breath (rare)": {"emoji": "🐉", "color": "#ffe0e0"},  # Dragon breath
        "Counter": {"emoji": "🔄", "color": "#fff0f0"},  # Counter-attack
        # Capture abilities
        "Seize": {"emoji": "🤗", "color": "#fff0f0"},  # Hugging face (capturing)
    }

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"UnitFace(name='{self.name}')"

    def get_emoji(self) -> str:
        """Get the emoji icon for this face type."""
        face_info = self._FACE_INFO_MAP.get(self.name, {"emoji": "❓"})
        return face_info["emoji"]

    def get_background_color(self) -> str:
        """Get the background color for this face type."""
        face_info = self._FACE_INFO_MAP.get(self.name, {"color": "#f0f0f0"})
        return face_info["color"]

    def get_display_text(self) -> str:
        """Get the display text with emoji and face name."""
        emoji = self.get_emoji()
        return f"{emoji}\n{self.name}"

    def get_tooltip(self) -> str:
        """Get the tooltip text with face name and description."""
        return f"{self.name}: {self.description}"

    def get_display_info(self) -> tuple[str, str, str]:
        """Get display information for this face.

        Returns:
            tuple: (display_text, background_color, tooltip)
        """
        return (
            self.get_display_text(),
            self.get_background_color(),
            self.get_tooltip(),
        )


class UnitModel:
    def __init__(
        self,
        unit_id: str,
        name: str,
        unit_type: str,
        health: int,
        max_health: int,
        abilities: Dict[str, Any],
        species: Optional[Any] = None,
        faces: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.unit_id = unit_id
        self.name = name
        self.unit_type = unit_type
        self.health = health
        self.max_health = max_health
        self.abilities = abilities
        self.species = species
        self.faces = [
            UnitFace(face["name"], face["description"]) for face in (faces or [])
        ]

    def __repr__(self):
        species_name = self.species.name if self.species else "Unknown"
        return f"UnitModel(id={self.unit_id}, name='{self.name}', species='{species_name}', type='{self.unit_type}', hp={self.health}/{self.max_health})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "name": self.name,
            "unit_type": self.unit_type,
            "health": self.health,
            "max_health": self.max_health,
            "abilities": self.abilities,
            "species": self.species,
            "faces": [
                {"name": face.name, "description": face.description}
                for face in self.faces
            ],
        }

    def get_species_name(self) -> str:
        """Get the species name for this unit."""
        return self.species.name if self.species else "Unknown"

    def get_species(self):
        """Get the SpeciesModel for this unit."""
        return self.species

    def get_face_names(self) -> List[str]:
        """Get all face names for this unit."""
        return [face.name for face in self.faces]

    def get_face_by_name(self, face_name: str) -> Optional["UnitFace"]:
        """Get a specific face by name."""
        for face in self.faces:
            if face.name == face_name:
                return face
        return None

    def get_face_by_index(self, index: int) -> Optional["UnitFace"]:
        """Get a face by its index."""
        if 0 <= index < len(self.faces):
            return self.faces[index]
        return None

    def is_monster(self) -> bool:
        """Check if this is a monster unit (10 faces)."""
        return len(self.faces) == 10

    def is_regular_unit(self) -> bool:
        """Check if this is a regular unit (6 faces)."""
        return len(self.faces) == 6

    def get_die_faces(self) -> List[str]:
        """Get the die face names for this unit."""
        return self.get_face_names()

    @property
    def die_faces(self) -> List[str]:
        """Get the die face names for this unit (compatibility property)."""
        return self.get_face_names()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnitModel":
        return cls(
            unit_id=data.get("unit_id", "unknown_id"),
            name=data.get("name", "Unknown Unit"),
            unit_type=data.get("unit_type", "unknown_type"),
            health=data.get("health", 0),
            max_health=data.get("max_health", 0),
            abilities=data.get("abilities", {}),
            faces=data.get("faces", []),
        )

    @classmethod
    def from_unit_data(
        cls, unit_type_id: str, current_health: int = None
    ) -> "UnitModel":
        """Create a UnitModel instance from unit data definitions with validation."""
        from models.unit_data import get_unit_by_id

        # Get the existing unit instance
        unit_instance = get_unit_by_id(unit_type_id)
        if not unit_instance:
            raise ValueError(f"Unit type '{unit_type_id}' not found in unit data")

        # Create a new instance with custom health if specified
        health = (
            current_health if current_health is not None else unit_instance.max_health
        )

        # Validate health values
        if health < 0:
            raise ValueError(f"Current health cannot be negative: {health}")
        if health > unit_instance.max_health:
            raise ValueError(
                f"Current health ({health}) cannot exceed max health ({unit_instance.max_health})"
            )

        return cls(
            unit_id=unit_instance.unit_id,
            name=unit_instance.name,
            unit_type=unit_instance.unit_type,
            health=health,
            max_health=unit_instance.max_health,
            abilities=unit_instance.abilities.copy(),
            species=unit_instance.species,
            faces=[
                {"name": face.name, "description": face.description}
                for face in unit_instance.faces
            ],
        )

    @staticmethod
    def _validate_unit_data(unit_data: Dict[str, Any]) -> None:
        """Validate that unit data meets required criteria."""
        required_fields = [
            "type_id",
            "display_name",
            "max_health",
            "unit_class_type",
            "species",
        ]
        valid_unit_classes = [
            "Heavy Melee",
            "Light Melee",
            "Cavalry",
            "Missile",
            "Magic",
            "Monster",
        ]

        # Check required fields
        for field in required_fields:
            if field not in unit_data:
                raise ValueError(f"Missing required field '{field}' in unit data")
            if field != "species" and not unit_data[field]:
                raise ValueError(f"Field '{field}' cannot be empty")

        # Validate type_id format
        type_id = unit_data["type_id"]
        if not isinstance(type_id, str) or len(type_id) < 3:
            raise ValueError(f"Invalid type_id format: '{type_id}'")

        # Validate display_name
        display_name = unit_data["display_name"]
        if not isinstance(display_name, str) or len(display_name.strip()) == 0:
            raise ValueError(f"Invalid display_name: '{display_name}'")

        # Validate max_health
        max_health = unit_data["max_health"]
        if not isinstance(max_health, int) or max_health < 1 or max_health > 4:
            raise ValueError(
                f"Invalid max_health: {max_health}. Must be integer between 1-4"
            )

        # Validate unit_class_type
        unit_class = unit_data["unit_class_type"]
        if unit_class not in valid_unit_classes:
            raise ValueError(
                f"Invalid unit_class_type: '{unit_class}'. Must be one of: {valid_unit_classes}"
            )

        # Validate species
        species = unit_data["species"]
        if not hasattr(species, "name"):
            raise ValueError(f"Invalid species reference in unit data")

    @classmethod
    def validate_all_unit_data(cls) -> Dict[str, list]:
        """Validate all unit data and return a report of any issues."""
        from models.unit_data import UNIT_DATA

        validation_report = {
            "valid_units": 0,
            "invalid_units": [],
            "missing_ids": [],
            "duplicate_ids": [],
            "species_summary": {},
        }

        unit_ids_seen = set()
        species_counts = {}

        for unit_instance in UNIT_DATA:
            try:
                # Check for duplicate IDs
                unit_id = unit_instance.unit_id
                if unit_id in unit_ids_seen:
                    validation_report["duplicate_ids"].append(unit_id)
                else:
                    unit_ids_seen.add(unit_id)

                # Validate unit instance
                if not isinstance(unit_instance, UnitModel):
                    raise ValueError(f"Not a UnitModel instance: {type(unit_instance)}")

                # Basic validation
                if not unit_instance.unit_id or not unit_instance.name:
                    raise ValueError("Missing required fields")

                if not hasattr(unit_instance.species, "name"):
                    raise ValueError("Invalid species reference")

                validation_report["valid_units"] += 1

                # Count by species
                species_name = unit_instance.species.name
                if species_name not in species_counts:
                    species_counts[species_name] = {"valid": 0, "invalid": 0}
                species_counts[species_name]["valid"] += 1

            except Exception as e:
                species_name = getattr(
                    getattr(unit_instance, "species", None), "name", "Unknown"
                )
                validation_report["invalid_units"].append(
                    {
                        "species": species_name,
                        "unit_id": getattr(unit_instance, "unit_id", "Unknown"),
                        "error": str(e),
                    }
                )

                if species_name not in species_counts:
                    species_counts[species_name] = {"valid": 0, "invalid": 0}
                species_counts[species_name]["invalid"] += 1

        # Add totals to species summary
        for species_name, counts in species_counts.items():
            validation_report["species_summary"][species_name] = {
                "valid": counts["valid"],
                "invalid": counts["invalid"],
                "total": counts["valid"] + counts["invalid"],
            }

        return validation_report
