"""
Minor Terrain Manager for Dragon Dice.

Manages the placement of minor terrains on major terrains and their effects.
Minor terrains can be placed on major terrains to provide additional effects
to armies controlling them.
"""

from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal

from models.minor_terrain_model import MinorTerrain, get_minor_terrain
from utils import strict_get


class MinorTerrainPlacement:
    """Represents a minor terrain placed on a major terrain."""

    def __init__(self, minor_terrain: MinorTerrain, major_terrain_name: str, current_face_index: int = 0):
        self.minor_terrain = minor_terrain
        self.major_terrain_name = major_terrain_name
        self.current_face_index = current_face_index  # Which face is currently showing (0-7)
        self.controlling_player: Optional[str] = None
        self.needs_burial = False  # Set to True when negative eighth face is triggered

    def get_current_face(self):
        """Get the currently showing face of the minor terrain."""
        return self.minor_terrain.faces[self.current_face_index]

    def set_face(self, face_index: int):
        """Set the current face of the minor terrain."""
        if 0 <= face_index < len(self.minor_terrain.faces):
            self.current_face_index = face_index

    def get_face_name(self) -> str:
        """Get the name of the current face."""
        return self.get_current_face().name  # type: ignore[no-any-return]

    def get_face_description(self) -> str:
        """Get the description of the current face."""
        return self.get_current_face().description  # type: ignore[no-any-return]

    def is_negative_eighth_face(self) -> bool:
        """Check if the current face is a negative eighth face that causes burial."""
        face_name = self.get_face_name()
        return face_name in ["Flood", "Flanked", "Landslide", "Revolt"]

    def trigger_negative_effect(self):
        """Trigger the negative eighth face effect and mark for burial."""
        if self.is_negative_eighth_face():
            self.needs_burial = True

    def to_dict(self) -> Dict[str, Any]:
        """Export placement data for saving/loading."""
        return {
            "minor_terrain_name": self.minor_terrain.name,
            "terrain_base_name": self.minor_terrain.get_terrain_base_name(),
            "eighth_face": self.minor_terrain.eighth_face,
            "major_terrain_name": self.major_terrain_name,
            "current_face_index": self.current_face_index,
            "controlling_player": self.controlling_player,
            "needs_burial": self.needs_burial,
        }


class MinorTerrainManager(QObject):
    """Manages minor terrain placements on major terrains."""

    placement_updated = Signal(str)  # Emitted when placement changes at a terrain
    minor_terrain_buried = Signal(str, str)  # Emitted when minor terrain is buried (terrain_name, minor_terrain_name)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Major terrain name -> List of MinorTerrainPlacement
        self._terrain_placements: Dict[str, List[MinorTerrainPlacement]] = {}

    def place_minor_terrain(
        self, minor_terrain: MinorTerrain, major_terrain_name: str, controlling_player: str
    ) -> bool:
        """Place a minor terrain on a major terrain."""
        if major_terrain_name not in self._terrain_placements:
            self._terrain_placements[major_terrain_name] = []

        placement = MinorTerrainPlacement(minor_terrain, major_terrain_name)
        placement.controlling_player = controlling_player

        self._terrain_placements[major_terrain_name].append(placement)
        print(
            f"MinorTerrainManager: Placed {minor_terrain.name} on {major_terrain_name} controlled by {controlling_player}"
        )
        self.placement_updated.emit(major_terrain_name)
        return True

    def remove_minor_terrain(self, major_terrain_name: str, minor_terrain_name: str) -> Optional[MinorTerrainPlacement]:
        """Remove a minor terrain from a major terrain."""
        if major_terrain_name not in self._terrain_placements:
            return None

        placements = self._terrain_placements[major_terrain_name]
        for i, placement in enumerate(placements):
            if placement.minor_terrain.name == minor_terrain_name:
                removed_placement = placements.pop(i)
                print(f"MinorTerrainManager: Removed {minor_terrain_name} from {major_terrain_name}")
                self.placement_updated.emit(major_terrain_name)
                return removed_placement

        return None

    def get_minor_terrains_at_terrain(self, major_terrain_name: str) -> List[MinorTerrainPlacement]:
        """Get all minor terrain placements at a major terrain."""
        return self._terrain_placements.get(major_terrain_name, []).copy()

    def get_controlled_minor_terrains(self, major_terrain_name: str, player_name: str) -> List[MinorTerrainPlacement]:
        """Get minor terrains at a major terrain controlled by a specific player."""
        placements = self.get_minor_terrains_at_terrain(major_terrain_name)
        return [p for p in placements if p.controlling_player == player_name]

    def has_minor_terrains_at_terrain(self, major_terrain_name: str) -> bool:
        """Check if any minor terrains are placed at a major terrain."""
        return len(self.get_minor_terrains_at_terrain(major_terrain_name)) > 0

    def set_minor_terrain_face(self, major_terrain_name: str, minor_terrain_name: str, face_index: int) -> bool:
        """Set the face of a specific minor terrain."""
        placements = self.get_minor_terrains_at_terrain(major_terrain_name)
        for placement in placements:
            if placement.minor_terrain.name == minor_terrain_name:
                placement.set_face(face_index)
                print(
                    f"MinorTerrainManager: Set {minor_terrain_name} to face {face_index} ({placement.get_face_name()})"
                )

                # Check if this triggers a negative effect
                if placement.is_negative_eighth_face():
                    placement.trigger_negative_effect()
                    print(f"MinorTerrainManager: {minor_terrain_name} triggered negative effect, marked for burial")

                self.placement_updated.emit(major_terrain_name)
                return True
        return False

    def get_minor_terrain_effects(self, major_terrain_name: str, player_name: str) -> List[Dict[str, Any]]:
        """Get the effects of minor terrains controlled by a player at a terrain."""
        controlled_placements = self.get_controlled_minor_terrains(major_terrain_name, player_name)
        effects = []

        for placement in controlled_placements:
            current_face = placement.get_current_face()
            effect_data = {
                "minor_terrain_name": placement.minor_terrain.name,
                "face_name": current_face.name,
                "face_description": current_face.description,
                "effect_type": self._categorize_effect(current_face.name),
                "needs_burial": placement.needs_burial,
            }
            effects.append(effect_data)

        return effects

    def _categorize_effect(self, face_name: str) -> str:
        """Categorize the type of effect based on face name."""
        if face_name == "ID":
            return "choice"
        if face_name in ["Magic", "Melee", "Missile"]:
            return "action"
        if face_name in ["Double Saves", "Double Maneuvers"]:
            return "enhancement"
        if face_name in ["Flood", "Flanked", "Landslide", "Revolt"]:
            return "negative"
        return "unknown"

    def process_burial_requirements(self, major_terrain_name: str) -> List[Tuple[str, MinorTerrainPlacement]]:
        """Get minor terrains that need to be buried and remove them."""
        if major_terrain_name not in self._terrain_placements:
            return []

        placements = self._terrain_placements[major_terrain_name]
        to_bury = []

        # Find placements that need burial
        for _i, placement in enumerate(placements):
            if placement.needs_burial:
                to_bury.append((placement.minor_terrain.name, placement))

        # Remove them from terrain
        for terrain_name, placement in to_bury:
            self.remove_minor_terrain(major_terrain_name, terrain_name)
            self.minor_terrain_buried.emit(major_terrain_name, terrain_name)

        return to_bury

    def clear_terrain_placements(self, major_terrain_name: str):
        """Clear all minor terrain placements from a major terrain."""
        if major_terrain_name in self._terrain_placements:
            count = len(self._terrain_placements[major_terrain_name])
            self._terrain_placements[major_terrain_name] = []
            print(f"MinorTerrainManager: Cleared {count} minor terrain placements from {major_terrain_name}")
            self.placement_updated.emit(major_terrain_name)

    def get_all_placements(self) -> Dict[str, List[MinorTerrainPlacement]]:
        """Get all minor terrain placements across all terrains."""
        return self._terrain_placements.copy()

    def get_placement_statistics(self) -> Dict[str, Any]:
        """Get statistics about minor terrain placements."""
        stats = {
            "total_placements": 0,
            "terrains_with_minor_terrains": 0,
            "placements_by_base_name": {},
            "placements_by_eighth_face": {},
            "placements_needing_burial": 0,
        }

        for _terrain_name, placements in self._terrain_placements.items():
            if placements:
                stats["terrains_with_minor_terrains"] += 1

                for placement in placements:
                    stats["total_placements"] += 1

                    # Count by base terrain name
                    base_name = placement.minor_terrain.get_terrain_base_name()
                    if base_name not in stats["placements_by_base_name"]:
                        stats["placements_by_base_name"][base_name] = 0
                    stats["placements_by_base_name"][base_name] += 1

                    # Count by eighth face
                    eighth_face = placement.minor_terrain.eighth_face
                    if eighth_face not in stats["placements_by_eighth_face"]:
                        stats["placements_by_eighth_face"][eighth_face] = 0
                    stats["placements_by_eighth_face"][eighth_face] += 1

                    # Count burial requirements
                    if placement.needs_burial:
                        stats["placements_needing_burial"] += 1

        return stats

    def export_placement_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all placement data for saving/loading."""
        export_data = {}
        for terrain_name, placements in self._terrain_placements.items():
            export_data[terrain_name] = [placement.to_dict() for placement in placements]
        return export_data

    def import_placement_data(self, placement_data: Dict[str, List[Dict[str, Any]]]):
        """Import placement data for loading saved games."""
        self._terrain_placements = {}

        for terrain_name, placement_list in placement_data.items():
            self._terrain_placements[terrain_name] = []

            for placement_dict in placement_list:
                # Reconstruct MinorTerrain from data using base name and eighth face
                terrain_base_name = strict_get(placement_dict, "terrain_base_name").upper()
                eighth_face = strict_get(placement_dict, "eighth_face").upper()
                terrain_key = f"{terrain_base_name}_{eighth_face}"

                # Fallback for old save format
                if not terrain_base_name and "minor_terrain_color" in placement_dict:
                    terrain_key = f"{placement_dict['minor_terrain_color'].upper()}_{placement_dict['minor_terrain_eighth_face'].upper()}"

                minor_terrain = get_minor_terrain(terrain_key)

                if minor_terrain:
                    placement = MinorTerrainPlacement(
                        minor_terrain, placement_dict["major_terrain_name"], placement_dict["current_face_index"]
                    )
                    placement.controlling_player = placement_dict.get("controlling_player")
                    placement.needs_burial = placement_dict.get("needs_burial", False)

                    self._terrain_placements[terrain_name].append(placement)

        print(f"MinorTerrainManager: Imported placement data for {len(self._terrain_placements)} terrains")
