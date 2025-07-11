"""
Die face analysis logic for Dragon Dice units.

This module contains pure Python business logic for analyzing and counting
die faces from unit compositions, extracted from UI components for better
testability and reusability.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from typing import Counter as TypingCounter


@dataclass
class DieFaceCount:
    """Represents a count of specific die face types."""

    face_type: str
    count: int
    icon: str = ""

    def __post_init__(self):
        """Set icon after initialization."""
        if not self.icon:
            self.icon = DieFaceAnalyzer.get_icon_for_face_type(self.face_type)


class DieFaceAnalyzer:
    """
    Analyzes die faces from unit definitions and compositions.

    Handles counting, prioritization, and analysis of die face distributions
    across unit collections according to Dragon Dice rules.
    """

    # Priority order for displaying die faces (most important first)
    FACE_PRIORITY_ORDER = [
        "Melee",
        "Missile",
        "Magic",
        "Save",
        "Maneuver",
        "SAI",
    ]

    # Icon mappings for different face types
    FACE_ICONS = {
        "Melee": "⚔️",
        "Missile": "🏹",
        "Magic": "✨",
        "Save": "🛡️",
        "ID": "—",
        "SAI": "💎",
        "Maneuver": "🏃",
        "Claw": "🐉",
        "Jaws": "🦷",
        "Tail": "🐉",
        "Firebreath": "🔥",
    }

    def __init__(self, unit_roster=None):
        """
        Initialize analyzer.

        Args:
            unit_roster: Optional unit roster for looking up unit definitions
        """
        self.unit_roster = unit_roster

    def count_die_faces(self, units: List[Any]) -> Dict[str, int]:
        """
        Count all die faces from a list of units.

        Args:
            units: List of unit objects or dictionaries

        Returns:
            Dictionary mapping face types to counts
        """
        if not self.unit_roster or not units:
            return {}

        face_counts: TypingCounter[str] = Counter()

        for unit in units:
            unit_type = getattr(unit, "unit_type", unit.get("unit_type", ""))
            if not unit_type:
                continue

            unit_def = self.unit_roster.get_unit_definition(unit_type)
            if not unit_def:
                continue

            die_faces = unit_def.get("die_faces", {})

            # Count standard faces (face_1 through face_6)
            for face_key in [
                "face_1",
                "face_2",
                "face_3",
                "face_4",
                "face_5",
                "face_6",
            ]:
                face_type = die_faces.get(face_key)
                if face_type and face_type != "ID":  # Don't count ID faces
                    face_counts[face_type] += 1

            # Count eighth faces
            for face_key in ["eighth_face_1", "eighth_face_2"]:
                face_type = die_faces.get(face_key)
                if face_type and face_type != "ID":  # Don't count ID faces
                    face_counts[face_type] += 1

        return dict(face_counts)

    def get_sorted_face_counts(self, face_counts: Dict[str, int]) -> List[DieFaceCount]:
        """
        Sort face counts by priority and then by count.

        Args:
            face_counts: Dictionary of face type -> count

        Returns:
            List of DieFaceCount objects sorted by priority and count
        """
        sorted_faces = sorted(
            face_counts.items(),
            key=lambda x: (
                (self.FACE_PRIORITY_ORDER.index(x[0]) if x[0] in self.FACE_PRIORITY_ORDER else 999),
                -x[1],  # Negative for descending count order
            ),
        )

        return [DieFaceCount(face_type=face_type, count=count) for face_type, count in sorted_faces]

    def analyze_unit_die_faces(self, units: List[Any]) -> List[DieFaceCount]:
        """
        Analyze units and return sorted die face counts.

        Args:
            units: List of unit objects or dictionaries

        Returns:
            List of DieFaceCount objects sorted by priority
        """
        face_counts = self.count_die_faces(units)
        return self.get_sorted_face_counts(face_counts)

    def get_face_distribution_summary(self, units: List[Any]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of face distribution.

        Args:
            units: List of unit objects or dictionaries

        Returns:
            Dictionary with detailed face distribution analysis
        """
        face_counts = self.count_die_faces(units)
        sorted_faces = self.get_sorted_face_counts(face_counts)

        total_faces = sum(face_counts.values())

        summary = {
            "total_faces": total_faces,
            "unique_face_types": len(face_counts),
            "face_counts": face_counts,
            "sorted_faces": sorted_faces,
            "percentages": {},
            "most_common": None,
            "least_common": None,
        }

        # Calculate percentages
        if total_faces > 0:
            for face_type, count in face_counts.items():
                summary["percentages"][face_type] = round((count / total_faces) * 100, 1)  # type: ignore

        # Find most and least common
        if sorted_faces:
            summary["most_common"] = sorted_faces[0]  # First is highest priority/count
            summary["least_common"] = sorted_faces[-1]  # Last is lowest priority/count

        return summary

    def compare_army_compositions(self, army1_units: List[Any], army2_units: List[Any]) -> Dict[str, Any]:
        """
        Compare die face distributions between two army compositions.

        Args:
            army1_units: Units from first army
            army2_units: Units from second army

        Returns:
            Dictionary with comparison analysis
        """
        army1_faces = self.count_die_faces(army1_units)
        army2_faces = self.count_die_faces(army2_units)

        all_face_types = set(army1_faces.keys()) | set(army2_faces.keys())

        comparison = {
            "army1_total": sum(army1_faces.values()),
            "army2_total": sum(army2_faces.values()),
            "face_differences": {},
            "army1_advantages": [],
            "army2_advantages": [],
            "equal_faces": [],
        }

        for face_type in all_face_types:
            count1 = army1_faces.get(face_type, 0)
            count2 = army2_faces.get(face_type, 0)
            difference = count1 - count2

            comparison["face_differences"][face_type] = {  # type: ignore
                "army1_count": count1,
                "army2_count": count2,
                "difference": difference,
            }

            if difference > 0:
                comparison["army1_advantages"].append((face_type, difference))  # type: ignore
            elif difference < 0:
                comparison["army2_advantages"].append((face_type, abs(difference)))  # type: ignore
            else:
                comparison["equal_faces"].append(face_type)  # type: ignore

        return comparison

    def get_tactical_analysis(self, units: List[Any]) -> Dict[str, Any]:
        """
        Analyze units for tactical strengths and weaknesses.

        Args:
            units: List of unit objects or dictionaries

        Returns:
            Dictionary with tactical analysis
        """
        face_counts = self.count_die_faces(units)

        # Define tactical categories
        offensive_faces = [
            "Melee",
            "Missile",
            "Magic",
        ]
        defensive_faces = ["Save"]
        utility_faces = ["Maneuver", "SAI"]

        analysis: Dict[str, Any] = {
            "offensive_strength": sum(face_counts.get(face, 0) for face in offensive_faces),
            "defensive_strength": face_counts.get("Save", 0),
            "utility_strength": sum(face_counts.get(face, 0) for face in utility_faces),
            "total_combat_faces": sum(face_counts.get(face, 0) for face in offensive_faces + defensive_faces),
            "primary_strength": None,
            "weaknesses": [],
            "balanced": False,
        }

        # Determine primary strength
        strengths = [
            ("offensive", analysis["offensive_strength"]),
            ("defensive", analysis["defensive_strength"]),
            ("utility", analysis["utility_strength"]),
        ]

        strengths.sort(key=lambda x: x[1], reverse=True)
        analysis["primary_strength"] = strengths[0][0] if strengths and strengths[0][1] > 0 else None

        # Identify weaknesses (categories with very low counts)
        total_faces = sum(face_counts.values())
        if total_faces > 0:
            for category, count in strengths:
                if count / total_faces < 0.2:  # Less than 20% of faces
                    analysis["weaknesses"].append(category)

        # Check if army is balanced
        if len(analysis["weaknesses"]) == 0 and strengths[0][1] - strengths[-1][1] <= 2:
            analysis["balanced"] = True

        return analysis

    @staticmethod
    def get_icon_for_face_type(face_type: str) -> str:
        """
        Get emoji icon for a face type.

        Args:
            face_type: Face type constant

        Returns:
            Emoji icon string
        """
        return DieFaceAnalyzer.FACE_ICONS.get(face_type, "❓")

    def format_face_summary(self, face_counts: Dict[str, int], compact: bool = True) -> str:
        """
        Format face counts into a readable string.

        Args:
            face_counts: Dictionary of face type -> count
            compact: If True, use compact format with icons

        Returns:
            Formatted string representation
        """
        if not face_counts:
            return "No die faces"

        sorted_faces = self.get_sorted_face_counts(face_counts)

        if compact:
            # Compact format: ⚔️3 🏹2 🛡️1
            parts = []
            for face_count in sorted_faces:
                parts.append(f"{face_count.icon}{face_count.count}")
            return " ".join(parts)
        # Detailed format: Melee: 3, Missile: 2, Save: 1
        parts = []
        for face_count in sorted_faces:
            face_name = face_count.face_type.replace("_", " ").title()
            parts.append(f"{face_name}: {face_count.count}")
        return ", ".join(parts)


class UnitDieFaceExtractor:
    """Utility class for extracting die face data from various unit sources."""

    @staticmethod
    def extract_from_unit_definition(unit_def: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract die faces from a unit definition dictionary.

        Args:
            unit_def: Unit definition dictionary

        Returns:
            Dictionary mapping face positions to face types
        """
        die_faces = unit_def.get("die_faces", {})

        # Ensure we have all standard face positions
        face_positions = ["face_1", "face_2", "face_3", "face_4", "face_5", "face_6"]
        eighth_positions = ["eighth_face_1", "eighth_face_2"]

        extracted_faces = {}

        for position in face_positions + eighth_positions:
            face_type = die_faces.get(position)
            if face_type:
                extracted_faces[position] = face_type

        return extracted_faces

    @staticmethod
    def validate_face_structure(die_faces: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate that die face structure is correct.

        Args:
            die_faces: Dictionary of face position -> face type

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for required face positions
        required_positions = [
            "face_1",
            "face_2",
            "face_3",
            "face_4",
            "face_5",
            "face_6",
        ]

        for position in required_positions:
            if position not in die_faces:
                errors.append(f"Missing required face position: {position}")

        # Check for valid face types
        valid_face_types = [
            "Melee",
            "Missile",
            "Magic",
            "Save",
            "ID",
            "SAI",
            "Maneuver",
        ]

        for position, face_type in die_faces.items():
            if face_type not in valid_face_types:
                errors.append(f"Invalid face type '{face_type}' at position {position}")

        return len(errors) == 0, errors
