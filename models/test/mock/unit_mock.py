"""
Mock data helpers for UnitModel testing.
Provides type-safe mock data generation for tests.
"""

from typing import Dict, Any, List, Optional
from models.unit_model import UnitModel
from models.species_model import SPECIES_DATA
from models.die_face_model import DieFaceModel


def create_unit_dict(
    unit_id: str = "test_unit_1",
    name: str = "Test Unit",
    unit_type: str = "test_unit_type",
    health: int = 1,
    max_health: int = 1,
    species_name: str = "AMAZON",
    **extra_fields: Any,
) -> Dict[str, Any]:
    """
    Create a complete unit dictionary with all required fields.

    Args:
        unit_id: Unique identifier for the unit
        name: Display name of the unit
        unit_type: Type identifier for unit abilities/stats
        health: Current health points
        max_health: Maximum health points
        species_name: Species name (must exist in SPECIES_DATA)
        **extra_fields: Additional fields to include in the dict

    Returns:
        Complete unit dictionary that can be used with UnitModel.from_dict()
    """
    # Get the actual species model from SPECIES_DATA
    from models.species_model import SPECIES_DATA

    if species_name not in SPECIES_DATA:
        raise ValueError(f"Unknown species: {species_name}. Available: {list(SPECIES_DATA.keys())}")

    species_model = SPECIES_DATA[species_name]

    unit_dict = {
        "unit_id": unit_id,
        "name": name,
        "unit_type": unit_type,
        "health": health,
        "max_health": max_health,
        "species": species_model,  # Provide actual SpeciesModel instance
        "faces": [],  # Empty faces for basic mock
    }

    # Add any extra fields
    unit_dict.update(extra_fields)

    return unit_dict


def create_unit_with_faces(
    unit_id: str = "test_unit_1",
    name: str = "Test Unit",
    unit_type: str = "test_unit_type",
    health: int = 1,
    max_health: int = 1,
    species_name: str = "AMAZON",
    face_count: int = 6,
) -> Dict[str, Any]:
    """
    Create a unit dictionary with mock die faces.

    Args:
        face_count: Number of die faces to generate
        Other args: Same as create_unit_dict()

    Returns:
        Unit dictionary with mock die faces
    """
    # Create basic faces
    faces = []
    for i in range(face_count):
        face_dict = {
            "name": f"Face {i + 1}",
            "display_name": f"Test Face {i + 1}",
            "description": f"Mock face {i + 1} for testing",
            "face_type": "MELEE" if i % 2 == 0 else "SAVE",
            "base_value": 1,
            "abilities": [],
            "icon_path": f"test_face_{i + 1}.png",
        }
        faces.append(face_dict)

    return create_unit_dict(
        unit_id=unit_id,
        name=name,
        unit_type=unit_type,
        health=health,
        max_health=max_health,
        species_name=species_name,
        faces=faces,
    )


def create_minimal_unit_dict(unit_id: str = "minimal_unit") -> Dict[str, Any]:
    """
    Create a minimal but complete unit dictionary.
    Useful for tests that don't care about specific values.
    """
    return create_unit_dict(unit_id=unit_id)


def create_army_units_list(count: int = 3, base_name: str = "Unit") -> List[Dict[str, Any]]:
    """
    Create a list of unit dictionaries for army testing.

    Args:
        count: Number of units to create
        base_name: Base name for units (will be numbered)

    Returns:
        List of complete unit dictionaries
    """
    units = []
    for i in range(count):
        unit_dict = create_unit_dict(
            unit_id=f"{base_name.lower()}_{i + 1}",
            name=f"{base_name} {i + 1}",
            unit_type=f"{base_name.lower()}_type",
            health=1,
            max_health=1,
        )
        units.append(unit_dict)

    return units


# Type-safe unit creation (bypasses from_dict validation issues)
def create_unit_instance(
    unit_id: str = "test_unit_1",
    name: str = "Test Unit",
    unit_type: str = "test_unit_type",
    health: int = 1,
    max_health: int = 1,
    species_name: str = "AMAZON",
) -> UnitModel:
    """
    Create a UnitModel instance directly, bypassing dict parsing.
    This is type-safe and will catch missing arguments at creation time.
    """
    from models.species_model import SPECIES_DATA

    # Get species (this will fail fast if species doesn't exist)
    if species_name not in SPECIES_DATA:
        raise ValueError(f"Unknown species: {species_name}")

    species = SPECIES_DATA[species_name]

    # Create minimal faces
    faces = [
        DieFaceModel(
            name="Test Face",
            display_name="Test Face",
            description="Mock face for testing",
            face_type="MELEE",
            base_value=1,
            abilities=[],
            icon_path="test_face.png",
        )
    ]

    return UnitModel(
        unit_id=unit_id,
        name=name,
        unit_type=unit_type,
        health=health,
        max_health=max_health,
        species=species,
        faces=faces,
    )
