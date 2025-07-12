# models/unit_model.py
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from models.die_face_model import DieFaceModel
    from models.species_model import SpeciesModel


class UnitModel:
    def __init__(
        self,
        unit_id: str,
        name: str,
        unit_type: str,
        health: int,
        max_health: int,
        species: "SpeciesModel",
        faces: List["DieFaceModel"],
    ) -> None:
        self.unit_id = unit_id
        self.name = name
        self.unit_type = unit_type
        self.health = health
        self.max_health = max_health
        self.species = species
        self.faces = faces

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
            "species": self.species.to_dict() if self.species else None,
            "faces": [face.to_dict() for face in self.faces],
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

    def get_face_by_name(self, face_name: str) -> Optional["DieFaceModel"]:
        """Get a specific face by name."""
        for face in self.faces:
            if face.name == face_name:
                return face
        return None

    def get_face_by_index(self, index: int) -> Optional["DieFaceModel"]:
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

    def get_id(self) -> str:
        """Get the unit ID."""
        return self.unit_id

    @property
    def elements(self) -> List[str]:
        """Get the elements from the unit's species."""
        return self.species.elements if self.species else []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnitModel":
        from models.die_face_model import DieFaceModel
        from models.species_model import SpeciesModel

        # Handle species data
        species_data = data.get("species")
        if isinstance(species_data, dict):
            species = SpeciesModel.from_dict(species_data)
        elif species_data is not None:
            species = species_data  # Assume it's already a SpeciesModel instance
        else:
            # Create a default species if none provided
            species = SpeciesModel(
                name="Unknown",
                display_name="Unknown Species",
                elements=[],
                element_colors=[],
                description="Unknown species with no defined abilities or characteristics.",
            )

        # Handle faces data
        faces_data = data.get("faces", [])
        faces = []
        for face_data in faces_data:
            if isinstance(face_data, dict):
                faces.append(DieFaceModel.from_dict(face_data))
            else:
                faces.append(face_data)  # Assume it's already a DieFaceModel instance

        return cls(
            unit_id=data.get("unit_id", "unknown_id"),
            name=data.get("name", "Unknown Unit"),
            unit_type=data.get("unit_type", "unknown_type"),
            health=data.get("health", 0),
            max_health=data.get("max_health", 0),
            species=species,
            faces=faces,
        )

    @classmethod
    def from_unit_data(cls, unit_type_id: str, current_health: Optional[int] = None) -> "UnitModel":
        """Create a UnitModel instance from unit data definitions with validation."""
        from models.unit_data import get_unit_by_id

        # Get the existing unit instance
        unit_instance = get_unit_by_id(unit_type_id)
        if not unit_instance:
            raise ValueError(f"Unit type '{unit_type_id}' not found in unit data")

        # Create a new instance with custom health if specified
        health = current_health if current_health is not None else unit_instance.max_health

        # Validate health values
        if health < 0:
            raise ValueError(f"Current health cannot be negative: {health}")
        if health > unit_instance.max_health:
            raise ValueError(f"Current health ({health}) cannot exceed max health ({unit_instance.max_health})")

        return cls(
            unit_id=unit_instance.unit_id,
            name=unit_instance.name,
            unit_type=unit_instance.unit_type,
            health=health,
            max_health=unit_instance.max_health,
            species=unit_instance.species,
            faces=unit_instance.faces,
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
            raise ValueError(f"Invalid max_health: {max_health}. Must be integer between 1-4")

        # Validate unit_class_type
        unit_class = unit_data["unit_class_type"]
        if unit_class not in valid_unit_classes:
            raise ValueError(f"Invalid unit_class_type: '{unit_class}'. Must be one of: {valid_unit_classes}")

        # Validate species
        species = unit_data["species"]
        if not hasattr(species, "name"):
            raise ValueError("Invalid species reference in unit data")

    @classmethod
    def validate_all_unit_data(cls) -> Dict[str, Any]:
        """Validate all unit data and return a report of any issues."""
        from models.unit_data import UNIT_DATA

        validation_report: Dict[str, Any] = {
            "valid_units": 0,
            "invalid_units": [],
            "missing_ids": [],
            "duplicate_ids": [],
            "species_summary": {},
        }

        unit_ids_seen: Set[str] = set()
        species_counts: Dict[str, Dict[str, int]] = {}

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
                species_name = getattr(getattr(unit_instance, "species", None), "name", "Unknown")
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
