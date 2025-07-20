"""
Type-safe model creation for testing.
Creates actual model instances with full type checking, bypassing dict-based creation.
"""

from typing import List, Optional

from models.army_model import ArmyModel
from models.die_face_model import DieFaceModel
from models.species_model import SPECIES_DATA
from models.unit_model import UnitModel


def create_test_die_face(
    name: str = "Test Face",
    display_name: Optional[str] = None,
    description: str = "Test die face for unit testing",
    face_type: str = "MELEE",
    base_value: int = 1,
) -> DieFaceModel:
    """
    Create a typed DieFaceModel instance for testing.

    All parameters are typed and mypy will catch missing required arguments.
    """
    return DieFaceModel(
        name=name, display_name=display_name, description=description, face_type=face_type, base_value=base_value
    )


def create_test_unit(
    unit_id: str,
    name: str,
    unit_type: str,
    health: int = 1,
    max_health: Optional[int] = None,
    species_key: str = "AMAZON",
    face_count: int = 1,
) -> UnitModel:
    """
    Create a typed UnitModel instance for testing.

    Args:
        unit_id: Unique identifier (REQUIRED - mypy will catch if missing)
        name: Unit display name (REQUIRED - mypy will catch if missing)
        unit_type: Unit type identifier (REQUIRED - mypy will catch if missing)
        health: Current health points
        max_health: Maximum health (defaults to health if not specified)
        species_key: Key for species in SPECIES_DATA
        face_count: Number of die faces to create

    Returns:
        Fully typed UnitModel instance

    Raises:
        ValueError: If species_key not found in SPECIES_DATA
        TypeError: If required arguments are missing (caught by mypy)
    """
    if max_health is None:
        max_health = health

    # Validate species exists (fail-fast)
    if species_key not in SPECIES_DATA:
        available_species = list(SPECIES_DATA.keys())
        raise ValueError(f"Unknown species key: {species_key}. Available: {available_species}")

    species = SPECIES_DATA[species_key]

    # Create die faces
    faces = []
    for i in range(face_count):
        face = create_test_die_face(
            name=f"{name} Face {i + 1}", face_type="MELEE" if i % 2 == 0 else "SAVE", base_value=1
        )
        faces.append(face)

    # This is fully type-checked - mypy will catch missing/wrong types
    return UnitModel(
        unit_id=unit_id,
        name=name,
        unit_type=unit_type,
        health=health,
        max_health=max_health,
        species=species,
        faces=faces,
    )


def create_test_army(
    name: str, army_type: str, location: str, max_points: int = 20, units: Optional[List[UnitModel]] = None
) -> ArmyModel:
    """
    Create a typed ArmyModel instance for testing.

    Args:
        name: Army display name (REQUIRED)
        army_type: Type of army (home, campaign, horde)
        location: Army location (REQUIRED)
        max_points: Maximum points the army can have
        units: List of UnitModel instances (optional, creates default if None)

    Returns:
        Fully typed ArmyModel instance
    """
    if units is None:
        # Create default test units
        units = [
            create_test_unit(
                unit_id=f"{name.lower().replace(' ', '_')}_unit_1", name=f"{name} Warrior", unit_type="test_warrior"
            ),
            create_test_unit(
                unit_id=f"{name.lower().replace(' ', '_')}_unit_2", name=f"{name} Archer", unit_type="test_archer"
            ),
        ]

    # Create army with ArmyModel constructor signature
    army = ArmyModel(name=name, army_type=army_type, location=location, max_points=max_points)

    # Add units after creation
    for unit in units:
        army.add_unit(unit)

    return army


# Convenience functions for common test scenarios


def create_home_army_typed(player_name: str, terrain_name: str, unit_count: int = 2) -> ArmyModel:
    """Create a typed home army for testing."""
    unique_id = f"{player_name.lower().replace(' ', '_')}_home"

    units = []
    for i in range(unit_count):
        unit = create_test_unit(
            unit_id=f"{unique_id}_unit_{i + 1}",
            name=f"{terrain_name} Defender {i + 1}",
            unit_type="home_defender",
            health=2,
            max_health=2,
        )
        units.append(unit)

    return create_test_army(
        unique_id=unique_id,
        name=f"{terrain_name} Guard",
        location=f"{player_name} {terrain_name}",
        allocated_points=10,
        units=units,
    )


def create_campaign_army_typed(player_name: str, frontier_terrain: str, unit_count: int = 3) -> ArmyModel:
    """Create a typed campaign army for testing."""
    unique_id = f"{player_name.lower().replace(' ', '_')}_campaign"

    units = []
    for i in range(unit_count):
        unit = create_test_unit(
            unit_id=f"{unique_id}_unit_{i + 1}",
            name=f"Campaign {['Soldier', 'Scout', 'Captain'][i % 3]} {i + 1}",
            unit_type=f"campaign_{['soldier', 'scout', 'captain'][i % 3]}",
            health=1,
            max_health=1,
        )
        units.append(unit)

    return create_test_army(
        unique_id=unique_id,
        name=f"{player_name} Expeditionary Force",
        location=frontier_terrain,
        allocated_points=10,
        units=units,
    )


def create_minimal_typed_unit(unit_id: str = "minimal_unit") -> UnitModel:
    """Create a minimal but complete typed unit for simple tests."""
    return create_test_unit(unit_id=unit_id, name="Minimal Test Unit", unit_type="test_minimal")
