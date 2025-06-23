# config/paths.py
from pathlib import Path

class ProjectPaths:
    """Centralized path management for the Dragon Dice project."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
    
    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"
    
    @property
    def unit_definitions_file(self) -> Path:
        return self.data_dir / "unit_definitions.json"
    
    @property
    def names_file(self) -> Path:
        return self.project_root / "names.txt"
    
    @property
    def test_visuals_dir(self) -> Path:
        return self.project_root / "test-visuals"
    
    @property
    def tests_dir(self) -> Path:
        return self.project_root / "tests"