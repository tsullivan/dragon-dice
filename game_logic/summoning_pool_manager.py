"""
Summoning Pool Manager for Dragon Dice.

The Summoning Pool is where players' dragons are stored at the start of the game.
Dragons can be summoned from the pool to terrains, and when killed, they return to the pool.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from models.dragon_model import DragonModel


class SummoningPoolManager(QObject):
    """Manages the Summoning Pool for all players."""

    pool_updated = Signal(str)  # Emitted when a player's pool changes

    def __init__(self, parent=None):
        super().__init__(parent)
        # Player name -> List of DragonModel
        self._player_pools: Dict[str, List[DragonModel]] = {}

    def initialize_player_pool(self, player_name: str, initial_dragons: List[DragonModel]):
        """Initialize a player's summoning pool with their starting dragons."""
        if player_name not in self._player_pools:
            self._player_pools[player_name] = []

        self._player_pools[player_name] = initial_dragons.copy()
        print(f"SummoningPoolManager: Initialized {player_name}'s pool with {len(initial_dragons)} dragons")
        self.pool_updated.emit(player_name)

    def add_dragon_to_pool(self, player_name: str, dragon: DragonModel):
        """Add a dragon to a player's summoning pool (e.g., when dragon is killed)."""
        if player_name not in self._player_pools:
            self._player_pools[player_name] = []

        self._player_pools[player_name].append(dragon)
        print(f"SummoningPoolManager: Added {dragon.name} to {player_name}'s summoning pool")
        self.pool_updated.emit(player_name)

    def remove_dragon_from_pool(self, player_name: str, dragon_id: str) -> Optional[DragonModel]:
        """Remove a dragon from a player's summoning pool (e.g., when summoned)."""
        if player_name not in self._player_pools:
            return None

        pool = self._player_pools[player_name]
        for i, dragon in enumerate(pool):
            if dragon.get_id() == dragon_id or dragon.name == dragon_id:
                removed_dragon = pool.pop(i)
                print(f"SummoningPoolManager: Removed {removed_dragon.name} from {player_name}'s summoning pool")
                self.pool_updated.emit(player_name)
                return removed_dragon

        print(f"SummoningPoolManager: Dragon {dragon_id} not found in {player_name}'s pool")
        return None

    def get_player_pool(self, player_name: str) -> List[DragonModel]:
        """Get all dragons in a player's summoning pool."""
        return self._player_pools.get(player_name, []).copy()

    def get_available_dragons(self, player_name: str, dragon_type: Optional[str] = None) -> List[DragonModel]:
        """Get available dragons for summoning, optionally filtered by type."""
        pool = self.get_player_pool(player_name)

        if dragon_type:
            return [dragon for dragon in pool if dragon.dragon_type == dragon_type]

        return pool

    def has_dragons(self, player_name: str) -> bool:
        """Check if a player has any dragons in their summoning pool."""
        return len(self.get_player_pool(player_name)) > 0

    def get_dragon_count(self, player_name: str) -> int:
        """Get the number of dragons in a player's summoning pool."""
        return len(self.get_player_pool(player_name))

    def get_dragons_by_element(self, player_name: str, element: str) -> List[DragonModel]:
        """Get dragons in a player's pool that match a specific element."""
        pool = self.get_player_pool(player_name)
        return [dragon for dragon in pool if element in dragon.elements]

    def get_dragons_by_type(self, player_name: str, dragon_type: str) -> List[DragonModel]:
        """Get dragons in a player's pool that match a specific type."""
        pool = self.get_player_pool(player_name)
        return [dragon for dragon in pool if dragon.dragon_type == dragon_type]

    def get_dragonkin_by_element(self, player_name: str, element: str) -> List[DragonModel]:
        """Get dragonkin units in a player's pool that match a specific element."""
        pool = self.get_player_pool(player_name)
        # Filter for dragonkin (assuming they have "dragonkin" in their name or type)
        return [dragon for dragon in pool if "dragonkin" in dragon.name.lower() and element in dragon.elements]

    def get_pool_statistics(self, player_name: str) -> Dict[str, Any]:
        """Get statistics about a player's summoning pool."""
        pool = self.get_player_pool(player_name)

        stats = {
            "total_dragons": len(pool),
            "dragon_types": {},
            "elements": {},
            "health_total": 0,
        }

        for dragon in pool:
            # Count by type
            dragon_type = dragon.dragon_type
            stats["dragon_types"][dragon_type] = stats["dragon_types"].get(dragon_type, 0) + 1

            # Count by elements
            for element in dragon.elements:
                stats["elements"][element] = stats["elements"].get(element, 0) + 1

            # Total health
            stats["health_total"] += dragon.health

        return stats

    def get_all_pools_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get a summary of all players' summoning pools."""
        summary = {}
        for player_name in self._player_pools:
            summary[player_name] = self.get_pool_statistics(player_name)
        return summary

    def can_summon_dragon(self, player_name: str, dragon_id: str) -> bool:
        """Check if a player can summon a specific dragon."""
        pool = self.get_player_pool(player_name)
        return any(dragon.get_id() == dragon_id or dragon.name == dragon_id for dragon in pool)

    def find_dragon_in_pool(self, player_name: str, dragon_id: str) -> Optional[DragonModel]:
        """Find a specific dragon in a player's pool."""
        pool = self.get_player_pool(player_name)
        for dragon in pool:
            if dragon.get_id() == dragon_id or dragon.name == dragon_id:
                return dragon
        return None

    def clear_player_pool(self, player_name: str):
        """Clear all dragons from a player's summoning pool."""
        if player_name in self._player_pools:
            dragon_count = len(self._player_pools[player_name])
            self._player_pools[player_name] = []
            print(f"SummoningPoolManager: Cleared {dragon_count} dragons from {player_name}'s pool")
            self.pool_updated.emit(player_name)

    def get_all_players(self) -> List[str]:
        """Get list of all players with summoning pools."""
        return list(self._player_pools.keys())

    def transfer_dragon_between_pools(self, from_player: str, to_player: str, dragon_id: str) -> bool:
        """Transfer a dragon from one player's pool to another's (for special game effects)."""
        dragon = self.remove_dragon_from_pool(from_player, dragon_id)
        if dragon:
            self.add_dragon_to_pool(to_player, dragon)
            print(f"SummoningPoolManager: Transferred {dragon.name} from {from_player} to {to_player}")
            return True
        return False

    def get_pool_export_data(self, player_name: str) -> List[Dict[str, Any]]:
        """Export a player's pool data for saving/loading."""
        pool = self.get_player_pool(player_name)
        return [dragon.to_dict() for dragon in pool]

    def import_pool_data(self, player_name: str, pool_data: List[Dict[str, Any]]):
        """Import pool data for a player (for loading saved games)."""
        dragons = []
        for dragon_dict in pool_data:
            dragon = DragonModel.from_dict(dragon_dict)
            dragons.append(dragon)

        self.initialize_player_pool(player_name, dragons)
        print(f"SummoningPoolManager: Imported {len(dragons)} dragons for {player_name}")
