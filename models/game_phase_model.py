from typing import Dict, Any, List


class GamePhaseModel:
    """
    Model for game phase data with display name, order, and optional substeps.
    """

    def __init__(
        self,
        name: str,
        display_name: str,
        order: int,
        substeps: Dict[str, Dict[str, Any]] = None,
    ):
        self.name = name
        self.display_name = display_name
        self.order = order
        self.substeps = substeps or {}

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"GamePhaseModel(name='{self.name}', display_name='{self.display_name}', order={self.order})"

    def has_substeps(self) -> bool:
        """Check if this phase has substeps."""
        return len(self.substeps) > 0

    def get_ordered_substeps(self) -> List[tuple]:
        """Get substeps ordered by their ORDER field."""
        if not self.substeps:
            return []

        substep_items = []
        for key, value in self.substeps.items():
            order = value.get("ORDER", 999)
            substep_items.append((order, key, value))

        substep_items.sort(key=lambda x: x[0])
        return [(key, value) for _, key, value in substep_items]


# Game phase instances
GAME_PHASE_DATA = {
    "EXPIRE_EFFECTS": GamePhaseModel(
        name="EXPIRE_EFFECTS", display_name="Expire Effects", order=1
    ),
    "EIGHTH_FACE": GamePhaseModel(
        name="EIGHTH_FACE", display_name="Eighth Face", order=2
    ),
    "DRAGON_ATTACK": GamePhaseModel(
        name="DRAGON_ATTACK", display_name="Dragon Attack", order=3
    ),
    "SPECIES_ABILITIES": GamePhaseModel(
        name="SPECIES_ABILITIES", display_name="Species Abilities", order=4
    ),
    "FIRST_MARCH": GamePhaseModel(
        name="FIRST_MARCH",
        display_name="First March",
        order=5,
        substeps={
            "CHOOSE_ACTING_ARMY": {"DISPLAY_NAME": "Choose Acting Army", "ORDER": 1},
            "DECIDE_MANEUVER": {"DISPLAY_NAME": "Decide Maneuver", "ORDER": 2},
            "AWAITING_MANEUVER_INPUT": {
                "DISPLAY_NAME": "Awaiting Maneuver Input",
                "ORDER": 3,
            },
            "DECIDE_ACTION": {"DISPLAY_NAME": "Decide Action", "ORDER": 4},
            "SELECT_ACTION": {"DISPLAY_NAME": "Select Action", "ORDER": 5},
        },
    ),
    "SECOND_MARCH": GamePhaseModel(
        name="SECOND_MARCH",
        display_name="Second March",
        order=6,
        substeps={
            "CHOOSE_ACTING_ARMY": {"DISPLAY_NAME": "Choose Acting Army", "ORDER": 1},
            "DECIDE_MANEUVER": {"DISPLAY_NAME": "Decide Maneuver", "ORDER": 2},
            "AWAITING_MANEUVER_INPUT": {
                "DISPLAY_NAME": "Awaiting Maneuver Input",
                "ORDER": 3,
            },
            "DECIDE_ACTION": {"DISPLAY_NAME": "Decide Action", "ORDER": 4},
            "SELECT_ACTION": {"DISPLAY_NAME": "Select Action", "ORDER": 5},
        },
    ),
    "RESERVES": GamePhaseModel(name="RESERVES", display_name="Reserves", order=7),
}


# Helper functions
def get_game_phase(phase_name: str) -> GamePhaseModel:
    """Get a game phase by name."""
    phase_key = phase_name.upper()
    return GAME_PHASE_DATA.get(phase_key)


def get_all_game_phase_names() -> List[str]:
    """Get all game phase names."""
    return list(GAME_PHASE_DATA.keys())


def get_ordered_game_phases() -> List[GamePhaseModel]:
    """Get all game phases ordered by their order field."""
    phases = list(GAME_PHASE_DATA.values())
    phases.sort(key=lambda x: x.order)
    return phases


def get_turn_phases() -> List[str]:
    """Get turn phase names in order."""
    return [phase.name for phase in get_ordered_game_phases()]


def get_march_steps() -> List[str]:
    """Get march step names from FIRST_MARCH substeps."""
    first_march = GAME_PHASE_DATA.get("FIRST_MARCH")
    if not first_march or not first_march.substeps:
        return []

    ordered_substeps = first_march.get_ordered_substeps()
    return [step_name for step_name, _ in ordered_substeps]


def validate_game_phase_data() -> bool:
    """Validate all game phase data."""
    try:
        for phase_name, phase in GAME_PHASE_DATA.items():
            if not isinstance(phase, GamePhaseModel):
                print(f"ERROR: {phase_name} is not a GamePhaseModel instance")
                return False
            if phase.name != phase_name:
                print(f"ERROR: Game phase name mismatch: {phase.name} != {phase_name}")
                return False

            # Validate substeps if they exist
            for substep_key, substep_data in phase.substeps.items():
                if "DISPLAY_NAME" not in substep_data:
                    print(
                        f"ERROR: Missing DISPLAY_NAME in substep {substep_key} of phase {phase_name}"
                    )
                    return False
                if "ORDER" not in substep_data:
                    print(
                        f"ERROR: Missing ORDER in substep {substep_key} of phase {phase_name}"
                    )
                    return False

        print(f"✓ All {len(GAME_PHASE_DATA)} game phases validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Game phase validation failed: {e}")
        return False
