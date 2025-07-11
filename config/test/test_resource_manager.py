import json
import unittest
from unittest.mock import Mock, mock_open, patch

from config.paths import ProjectPaths
from config.resource_manager import ResourceManager


class TestResourceManager(unittest.TestCase):
    """Test the ResourceManager for loading application resources."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_paths = Mock(spec=ProjectPaths)
        self.mock_paths.names_file = "/test/path/names.txt"

        self.resource_manager = ResourceManager(self.mock_paths)

    def test_resource_manager_focuses_on_file_io(self):
        """Test that ResourceManager focuses on file I/O operations."""
        # ResourceManager should only handle file operations like load_names()
        # Unit definitions are now handled by AppDataModel
        assert hasattr(self.resource_manager, "load_names")
        assert not hasattr(self.resource_manager, "load_unit_definitions")

    def test_resource_manager_only_handles_files(self):
        """Test that ResourceManager only handles external file operations."""
        # ResourceManager methods should only deal with file I/O
        # Unit data processing is now handled by AppDataModel
        methods = [method for method in dir(self.resource_manager) if not method.startswith("_")]
        expected_methods = ["load_names"]  # Only file I/O methods
        file_io_methods = [method for method in methods if method.startswith("load_")]

        # Should only have file I/O related methods
        for method in file_io_methods:
            assert method in expected_methods, f"Unexpected method: {method}"

    def test_load_names_success(self):
        """Test successful loading of names file."""
        test_names_content = """[Player]
Alice
Bob
Charlie

[Army]
Iron Legion
Storm Guard
Fire Brigade
"""

        with patch("builtins.open", mock_open(read_data=test_names_content)):
            result = self.resource_manager.load_names()

            assert "Player" in result
            assert "Army" in result

            assert len(result["Player"]) == 3
            assert "Alice" in result["Player"]
            assert "Bob" in result["Player"]
            assert "Charlie" in result["Player"]

            assert len(result["Army"]) == 3
            assert "Iron Legion" in result["Army"]
            assert "Storm Guard" in result["Army"]
            assert "Fire Brigade" in result["Army"]

    def test_load_names_file_not_found(self):
        """Test handling of missing names file."""
        with patch("builtins.open", side_effect=FileNotFoundError()), patch("builtins.print") as mock_print:
            result = self.resource_manager.load_names()

            # Should return default names
            assert "Player" in result
            assert "Army" in result

            assert result["Player"] == ["Player 1", "Player 2", "Player 3", "Player 4"]
            assert result["Army"] == ["Army 1", "Army 2", "Army 3", "Army 4"]

            mock_print.assert_called()
            warning_call = mock_print.call_args[0][0]
            assert "not found" in warning_call

    def test_load_names_empty_categories(self):
        """Test handling of empty categories in names file."""
        test_names_content = """[Player]

[Army]
Single Army
"""

        with patch("builtins.open", mock_open(read_data=test_names_content)):  # noqa: SIM117
            with patch("builtins.print") as mock_print:
                result = self.resource_manager.load_names()

                # Player category should get default names
                assert result["Player"] == ["Player 1", "Player 2", "Player 3", "Player 4"]

                # Army category should have the provided name
                assert len(result["Army"]) == 1
                assert "Single Army" in result["Army"]

                mock_print.assert_called()

    def test_load_names_unknown_category(self):
        """Test handling of unknown categories in names file."""
        test_names_content = """[Player]
Alice

[UnknownCategory]
SomeValue

[Army]
Test Army
"""

        with patch("builtins.open", mock_open(read_data=test_names_content)):  # noqa: SIM117
            with patch("builtins.print") as mock_print:
                result = self.resource_manager.load_names()

                # Should only have known categories
                assert "Player" in result
                assert "Army" in result
                assert "UnknownCategory" not in result

                # Known categories should have correct data
                assert "Alice" in result["Player"]
                assert "Test Army" in result["Army"]

                # Should warn about unknown category
                mock_print.assert_called()

    def test_load_names_mixed_content(self):
        """Test loading names with mixed content and whitespace."""
        test_names_content = """
[Player]
Alice

Bob
  Charlie

[Army]

Iron Legion

Storm Guard

"""

        with patch("builtins.open", mock_open(read_data=test_names_content)):
            result = self.resource_manager.load_names()

            # Should handle whitespace and empty lines correctly
            assert len(result["Player"]) == 3
            assert "Alice" in result["Player"]
            assert "Bob" in result["Player"]
            assert "Charlie" in result["Player"]  # Stripped whitespace

            assert len(result["Army"]) == 2
            assert "Iron Legion" in result["Army"]
            assert "Storm Guard" in result["Army"]

    def test_default_paths_usage(self):
        """Test ResourceManager with default paths."""
        with patch("config.resource_manager.ProjectPaths") as mock_paths_class:
            mock_paths_instance = Mock()
            mock_paths_class.return_value = mock_paths_instance

            resource_manager = ResourceManager()

            # Should have created ProjectPaths instance
            mock_paths_class.assert_called_once()
            assert resource_manager.paths == mock_paths_instance

    def test_provided_paths_usage(self):
        """Test ResourceManager with provided paths."""
        custom_paths = Mock(spec=ProjectPaths)
        resource_manager = ResourceManager(custom_paths)

        assert resource_manager.paths == custom_paths

    def test_resource_manager_integration(self):
        """Test ResourceManager integration with file operations."""
        names_content = "[Player]\nAlice\n[Army]\nTest Army\n"

        with patch("builtins.open", mock_open(read_data=names_content)):
            names = self.resource_manager.load_names()

            # Names should load from mocked file
            assert "Alice" in names["Player"]
            assert "Test Army" in names["Army"]

            # ResourceManager should not handle unit definitions anymore
            assert not hasattr(self.resource_manager, "load_unit_definitions")


if __name__ == "__main__":
    unittest.main()
