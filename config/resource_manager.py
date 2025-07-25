# config/resource_manager.py
from typing import Dict, List, Optional

from config.paths import ProjectPaths


class ResourceManager:
    """Manages external application resources like files and names."""

    def __init__(self, paths: Optional[ProjectPaths] = None):
        self.paths = paths or ProjectPaths()

    def load_names(self) -> Dict[str, List[str]]:
        """Load names from the names.txt file."""
        names_by_category: Dict[str, List[str]] = {"Player": [], "Army": []}
        current_category = None

        try:
            with open(self.paths.names_file) as f:
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
                            print(f"Warning: Unknown category '{category}' in names.txt.")
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
