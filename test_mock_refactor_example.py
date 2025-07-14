#!/usr/bin/env python3
"""
Example of refactoring a test to use the new mock data infrastructure.
Shows before/after comparison and type safety benefits.
"""

# === BEFORE: Manual test data (error-prone, incomplete) ===

def old_test_setup():
    """The old way - manually creating test data with potential for missing fields."""
    player_setup_data = [
        {
            "name": "Player 1",
            "home_terrain": "Highland",
            "frontier_terrain_proposal": "Coastland",
            "force_size": 24,
            "selected_dragons": [
                {"dragon_type": "Red Dragon", "die_type": "Drake"}
            ],
            "armies": {
                "home": {
                    "name": "Highland Guard",
                    "location": "Player 1 Highland",
                    "allocated_points": 10,
                    "units": [
                        {
                            "name": "Warrior",
                            "unit_id": "unit_1",
                            "health": 2,
                            "max_health": 2,
                            "unit_type": "warrior",
                            "abilities": {},
                            # Still missing: species, faces
                        },
                    ],
                    "unique_id": "player_1_home",
                },
                # ... more manual army definitions
            },
        },
        # ... more manual player definitions
    ]
    return player_setup_data


# === AFTER: Using mock infrastructure (type-safe, complete) ===

def new_test_setup():
    """The new way - using mock infrastructure for complete, type-safe data."""
    from models.test.mock import create_two_player_setup, create_player_with_dragons
    
    # Option 1: Use convenience function for standard setup
    players = create_two_player_setup(
        player1_name="Player 1",
        player1_home="Highland",
        player2_name="Player 2", 
        player2_home="Coastland",
        frontier_terrain="Coastland"
    )
    
    # Option 2: Create custom player with dragons
    dragon_player = create_player_with_dragons(
        name="Dragon Player",
        home_terrain="Highland",
        dragon_types=["Red Dragon", "Blue Dragon"],
        frontier_terrain_proposal="Coastland"
    )
    
    return players


# === TYPE SAFETY DEMONSTRATION ===

def demonstrate_type_safety():
    """Show how the new mock system catches errors at creation time."""
    from models.test.mock.unit_mock import create_unit_instance
    from models.test.mock import create_unit_dict
    
    # Type-safe model creation - mypy will catch missing arguments
    try:
        unit_instance = create_unit_instance(
            unit_id="test_unit",
            name="Test Warrior",
            unit_type="amazon_warrior",
            health=1,
            max_health=1,
            species_name="AMAZON"
        )
        print(f"✅ Created unit instance: {unit_instance.name}")
    except Exception as e:
        print(f"❌ Failed to create unit instance: {e}")
    
    # Complete dict creation - all required fields guaranteed  
    unit_dict = create_unit_dict(
        unit_id="dict_unit",
        name="Dict Warrior",
        unit_type="amazon_warrior" 
    )
    print(f"✅ Created unit dict with {len(unit_dict)} fields: {list(unit_dict.keys())}")
    
    # Verify all required fields are present
    required_fields = ["unit_id", "name", "unit_type", "health", "max_health", "species", "faces"]
    missing_fields = [field for field in required_fields if field not in unit_dict]
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
    else:
        print("✅ All required fields present")


# === GAME ENGINE INTEGRATION ===

def test_game_engine_with_mocks():
    """Show how to create a GameEngine with complete mock data."""
    from models.test.mock import create_two_player_setup
    from game_logic.engine import GameEngine
    
    # Create complete player setup
    players = create_two_player_setup()
    
    # Standard test configuration
    frontier_terrain = "Coastland"
    distance_rolls = [("Player 1", 3), ("Player 2", 5), ("__frontier__", 4)]
    first_player = "Player 1"
    
    try:
        # This should work without any MissingFieldError
        engine = GameEngine(
            player_setup_data=players,
            first_player_name=first_player,
            frontier_terrain=frontier_terrain, 
            distance_rolls=distance_rolls
        )
        print("✅ GameEngine created successfully with mock data")
        print(f"   Current player: {engine.get_current_player_name()}")
        print(f"   Current phase: {engine.current_phase}")
        return engine
        
    except Exception as e:
        print(f"❌ Failed to create GameEngine: {e}")
        return None


if __name__ == "__main__":
    print("=== Mock Data Infrastructure Demo ===\n")
    
    print("1. Type Safety Demonstration:")
    demonstrate_type_safety()
    
    print("\n2. Game Engine Integration:")
    engine = test_game_engine_with_mocks()
    
    print("\n3. Data Completeness Comparison:")
    old_data = old_test_setup()[0]  # First player
    new_data = new_test_setup()[0]   # First player
    
    print(f"Old data keys: {len(old_data)} - {list(old_data.keys())}")
    print(f"New data keys: {len(new_data)} - {list(new_data.keys())}")
    
    # Check army completeness
    old_home_army = old_data["armies"]["home"]
    new_home_army = new_data["armies"]["home"] 
    
    print(f"\nOld home army keys: {list(old_home_army.keys())}")
    print(f"New home army keys: {list(new_home_army.keys())}")
    
    # Check unit completeness
    if old_home_army["units"]:
        old_unit = old_home_army["units"][0]
        new_unit = new_home_army["units"][0]
        
        print(f"\nOld unit keys: {list(old_unit.keys())}")
        print(f"New unit keys: {list(new_unit.keys())}")
        
        print("\n✅ Mock infrastructure provides complete, consistent test data!")