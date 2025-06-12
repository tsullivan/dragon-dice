from dataclasses import dataclass, field
from typing import List, Literal, TypedDict, Optional

# This is the new definition that was missing
class PlayerSetupData(TypedDict):
    """A dictionary representing the data collected for a single player during setup."""
    name: str
    home_terrain: str
    frontier_terrain: str

# Type definitions mirroring our TypeScript types
GamePhase = Literal['SETUP', 'GAMEPLAY']
SetupStep = Literal['DETERMINING_FRONTIER', 'AWAITING_DISTANCE_ROLLS', 'COMPLETE']
TurnPhase = Literal['FIRST_MARCH', 'SECOND_MARCH', 'RESERVES'] # etc.
MarchStep = Literal['DECIDE_MANEUVER', 'AWAITING_MANEUVER_INPUT', 'COMPLETE']

@dataclass
class Player:
    player_number: int
    name: str
    home_terrain: str
    proposed_frontier: str
    captured_terrains: int = 0

@dataclass
class Terrain:
    id: int
    owner_name: str
    type: str
    current_value: Optional[int] = None
    armies_present: List[str] = field(default_factory=list)


@dataclass
class GameState:
    players: List[Player] = field(default_factory=list)
    terrains: List[Terrain] = field(default_factory=list)
    frontier_terrain: Optional[Terrain] = None
    point_value: int = 0
    current_player_index: int = 0
    game_phase: GamePhase = 'SETUP'
    setup_step: SetupStep = 'DETERMINING_FRONTIER'
    current_turn_phase: TurnPhase = 'FIRST_MARCH'
    current_march_step: Optional[MarchStep] = None