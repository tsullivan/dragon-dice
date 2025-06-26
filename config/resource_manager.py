# config/resource_manager.py
from pathlib import Path
from typing import Dict, List, Optional
import json

from config.paths import ProjectPaths


class ResourceManager:
    """Manages application resources like data files and names."""

    def __init__(self, paths: Optional[ProjectPaths] = None):
        self.paths = paths or ProjectPaths()

    def load_unit_definitions(self) -> Dict[str, List[Dict]]:
        """Load unit definitions from JSON file."""
        try:
            with open(self.paths.unit_definitions_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            error_msg = (
                f"Unit definitions file not found at {self.paths.unit_definitions_file}"
            )
            print(f"ERROR: {error_msg}")
            # Could show dialog here if we have a parent widget
            return {}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in unit definitions file: {e}"
            print(f"ERROR: {error_msg}")
            # Could show dialog here if we have a parent widget
            return {}

    def load_names(self) -> Dict[str, List[str]]:
        """Load names from the names.txt file."""
        names_by_category = {"Player": [], "Army": []}
        current_category = None

        try:
            with open(self.paths.names_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("[") and line.endswith("]"):
                        category = line[1:-1]
                        if category in names_by_category:
                            current_category = category
                        else:
                            current_category = None
                            print(
                                f"Warning: Unknown category '{category}' in names.txt."
                            )
                    elif current_category:
                        names_by_category[current_category].append(line)

            # Validate that we have names for both categories
            for category, names in names_by_category.items():
                if not names:
                    print(f"Warning: No {category} names found in names.txt")
                    # Add default names
                    if category == "Player":
                        names_by_category[category] = [
                            "Player 1",
                            "Player 2",
                            "Player 3",
                            "Player 4",
                        ]
                    elif category == "Army":
                        names_by_category[category] = [
                            "Army 1",
                            "Army 2",
                            "Army 3",
                            "Army 4",
                        ]

            return names_by_category

        except FileNotFoundError:
            print(f"Warning: names.txt not found at {self.paths.names_file}")
            # Return default names
            return {
                "Player": ["Player 1", "Player 2", "Player 3", "Player 4"],
                "Army": ["Army 1", "Army 2", "Army 3", "Army 4"],
            }
