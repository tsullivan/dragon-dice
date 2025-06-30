from typing import Dict, Any, List


class ActionModel:
    """
    Model for game action data with icon, display name, and substeps.
    """

    def __init__(
        self,
        name: str,
        icon: str,
        display_name: str,
        substeps: Dict[str, Dict[str, Any]] = None,
    ):
        self.name = name
        self.icon = icon
        self.display_name = display_name
        self.substeps = substeps or {}

    def __str__(self) -> str:
        return f"{self.icon} {self.display_name}"

    def __repr__(self) -> str:
        return f"ActionModel(name='{self.name}', icon='{self.icon}', display_name='{self.display_name}')"

    def has_substeps(self) -> bool:
        """Check if this action has substeps."""
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


# Action instances
ACTION_DATA = {
    "MELEE": ActionModel(
        name="MELEE",
        icon="⚔️",
        display_name="Melee",
        substeps={
            "AWAITING_ATTACKER_MELEE_ROLL": {
                "DISPLAY_NAME": "Awaiting Attacker Melee Roll",
                "ORDER": 1,
            },
            "AWAITING_DEFENDER_SAVES": {
                "DISPLAY_NAME": "Awaiting Defender Saves",
                "ORDER": 2,
            },
            "AWAITING_MELEE_COUNTER_ATTACK_ROLL": {
                "DISPLAY_NAME": "Awaiting Melee Counter Attack Roll",
                "ORDER": 3,
            },
        },
    ),
    "MISSILE": ActionModel(
        name="MISSILE",
        icon="🏹",
        display_name="Missile",
        substeps={
            "AWAITING_ATTACKER_MISSILE_ROLL": {
                "DISPLAY_NAME": "Awaiting Attacker Missile Roll",
                "ORDER": 1,
            },
            "AWAITING_DEFENDER_SAVES": {
                "DISPLAY_NAME": "Awaiting Defender Saves",
                "ORDER": 2,
            },
        },
    ),
    "MAGIC": ActionModel(
        name="MAGIC",
        icon="🔮",
        display_name="Magic",
        substeps={
            "AWAITING_MAGIC_ROLL": {"DISPLAY_NAME": "Awaiting Magic Roll", "ORDER": 1}
        },
    ),
    "SAVE": ActionModel(name="SAVE", icon="🛡️", display_name="Save"),
    "SAI": ActionModel(name="SAI", icon="💎", display_name="Special Action"),
    "MANEUVER": ActionModel(name="MANEUVER", icon="🏃", display_name="Maneuver"),
    "SKIP": ActionModel(name="SKIP", icon="⏭️", display_name="Skip"),
}


# Helper functions
def get_action(action_name: str) -> ActionModel:
    """Get an action by name."""
    action_key = action_name.upper()
    return ACTION_DATA.get(action_key)


def get_all_action_names() -> List[str]:
    """Get all action names."""
    return list(ACTION_DATA.keys())


def get_action_icon(action_type: str) -> str:
    """Get action icon. Raises KeyError if action type not found."""
    action_key = action_type.upper()
    if action_key not in ACTION_DATA:
        raise KeyError(
            f"Unknown action type: '{action_type}'. Valid action types: {
                list(ACTION_DATA.keys())}"
        )
    return ACTION_DATA[action_key].icon


def format_action_display(action_type: str) -> str:
    """Return 'icon display_name' format for display."""
    # Handle both "MELEE" and "Melee Action" formats
    if "Action" in action_type:
        base_action = action_type.replace(" Action", "").upper()
    else:
        base_action = action_type.upper()

    if base_action not in ACTION_DATA:
        raise KeyError(f"Unknown action type: '{base_action}'")

    action = ACTION_DATA[base_action]
    return f"{action.icon} {action.display_name}"


def validate_action_data() -> bool:
    """Validate all action data."""
    try:
        for action_name, action in ACTION_DATA.items():
            if not isinstance(action, ActionModel):
                print(f"ERROR: {action_name} is not an ActionModel instance")
                return False
            if action.name != action_name:
                print(f"ERROR: Action name mismatch: {action.name} != {action_name}")
                return False

            # Validate substeps if they exist
            for substep_key, substep_data in action.substeps.items():
                if "DISPLAY_NAME" not in substep_data:
                    print(
                        f"ERROR: Missing DISPLAY_NAME in substep {substep_key} of action {action_name}"
                    )
                    return False

        print(f"✓ All {len(ACTION_DATA)} actions validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Action validation failed: {e}")
        return False
