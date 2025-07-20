# Dragon Dice Companion Application

A digital companion app for the physical tabletop game Dragon Dice®. Built with Python and PySide6, this application helps manage game state, track turns and phases, and guide players through rules without replacing the physical components.

See @README.md for setup and running instructions.
See the Markdown files in the @assets folder for complete Dragon Dice game rules.

## Architecture Overview

The application follows a **signal-driven architecture** with clear domain separation:

### Core Domains

```
dragon-dice/
├── game_logic/              # Core game rules and mechanics
│   ├── game_orchestrator.py # Main game coordinator (replaces old engine.py)
│   ├── core_engine.py       # Business logic delegation
│   ├── action_resolver.py   # Combat and action resolution
│   └── spell_resolver.py    # Magic system
├── controllers/             # UI controllers and services
│   ├── phase_controllers/   # Focused phase management
│   │   ├── turn_flow_controller.py     # Master phase coordinator
│   │   ├── march_phase_controller.py   # First/Second March phases
│   │   ├── automatic_phase_controller.py # Expire Effects, Eighth Face, Dragon Attacks
│   │   ├── species_abilities_controller.py # Species-specific abilities
│   │   └── reserves_phase_controller.py    # Reserve deployment
│   ├── army_data_service.py # Army data formatting for UI
│   └── combat_service.py    # Combat analysis for UI
├── models/                  # Data models and state management
│   ├── game_state/         # Game state managers
│   │   ├── game_state_manager.py # Primary game state
│   │   ├── dua_manager.py        # Dead Unit Area
│   │   ├── bua_manager.py        # Buried Unit Area
│   │   └── reserves_manager.py   # Reserve units
│   ├── effect_state/       # Effect and spell state
│   └── unit_model.py       # Unit definitions
└── views/                  # Qt UI components
    └── main_gameplay_view.py
```

### Signal Flow Architecture

The application uses Qt signals/slots for loose coupling:

1. **UI Events** → Controllers → Game Logic
2. **Game State Changes** → Signals → UI Updates  
3. **Phase Transitions** → TurnFlowController → Specialized Phase Controllers

### Key Architectural Principles

- **Fail-Fast**: Use `strict_get()` instead of `.get()` to catch missing data early
- **Signal-Driven**: Qt signals/slots for component communication
- **Domain Separation**: Clear boundaries between UI, controllers, and game logic
- **Phase Controllers**: Focused controllers for each game phase group

## Contributing Guidelines for LLMs

### Core Development Rules

1. **Always use strict field access**: Use `strict_get()`, `strict_get_optional()`, and `strict_get_with_fallback()` from `utils.field_access` instead of dict `.get()` methods
2. **Prefer breaking changes over legacy compatibility**: Don't add backwards compatibility or fallback code
3. **Use focused phase controllers**: Don't modify the old `engine_old.py` - work with the new phase controller architecture
4. **Follow signal patterns**: Connect through proper signal/slot mechanisms, don't call methods directly across domains

### Code Quality Requirements

Run these commands before any commit:
```bash
python scripts/format_code.py        # Auto-fix formatting
python scripts/run_linter.py         # Check code quality  
python scripts/run_typecheck.py      # Verify type annotations
```

**Type Annotations**: Required for all function parameters and return values
**Line Length**: 120 characters maximum
**Import Organization**: First-party modules separated, alphabetically sorted

### Common Tasks and Patterns

#### Adding New Game Features

1. **Identify the domain**: Game logic goes in `game_logic/`, UI data formatting in `controllers/`
2. **Use appropriate phase controller**: Add to existing phase controllers or create new ones
3. **Follow signal patterns**: Emit signals for state changes, connect via slots
4. **Add to GameOrchestrator**: Register new managers/controllers in `_initialize_managers()`

#### Fixing Phase Flow Issues

1. **Work with TurnFlowController**: Don't bypass the phase controller architecture
2. **Check signal connections**: Look for missing or double signal connections
3. **Use phase controller signals**: Each controller has completion signals like `march_phase_completed`
4. **Avoid direct method calls**: Use signal emission instead of calling `advance_phase()` directly

#### Working with Game State

```python
# ✅ Correct: Use strict field access
player_data = strict_get(game_state, "players")
army_units = strict_get_optional(army_data, "units", [])

# ❌ Incorrect: Lenient access
player_data = game_state.get("players", {})  # Don't do this
```

#### Adding UI Controllers

1. **Inherit from QObject**: Use Qt's signal/slot system
2. **Connect to GameOrchestrator**: Get data through proper channels
3. **Format data for UI**: Transform game data into UI-friendly formats
4. **Emit status signals**: Keep UI informed of state changes

#### Testing Complex Game Flows

For issues deep in gameplay flow, create focused tests that simulate game state rather than clicking through the entire UI:

```python
# Create specific game state for testing
test_state = {
    "players": {"Player1": {"armies": {...}}},
    "terrains": {...}
}
orchestrator = GameOrchestrator(test_state, ...)
# Test specific functionality
```

### Architecture-Specific Guidelines

#### GameOrchestrator vs Phase Controllers

- **GameOrchestrator**: High-level coordination, manager initialization, UI signal emission
- **Phase Controllers**: Specific phase logic, user interaction patterns, phase completion

#### When to Use Each Domain

- **game_logic/**: Core rules, dice resolution, spell effects, combat calculations
- **controllers/**: Data formatting for UI, user input processing, UI state management  
- **models/**: Data structures, state management, validation
- **views/**: Qt widgets, UI layout, user interaction

#### Signal Connection Patterns

```python
# ✅ Correct: Connect through controller
self.phase_controller.phase_completed.connect(self.handle_phase_completion)

# ❌ Incorrect: Direct method calls across domains
self.game_orchestrator.advance_phase()  # Don't call directly
```

### Testing Strategy

- **Unit Tests**: Individual components in `*/test/` directories
- **Integration Tests**: Cross-component interactions in `test/e2e/`
- **Visual Tests**: UI screenshot regression testing
- **Focused State Tests**: Complex game state scenarios without full UI interaction

### Common Pitfalls to Avoid

1. **Don't modify engine_old.py**: This is legacy code, use the new architecture
2. **Don't create circular imports**: Keep domain boundaries clear
3. **Don't skip type annotations**: All public methods need proper typing
4. **Don't use lenient field access**: Always use strict_get() functions
5. **Don't bypass phase controllers**: Work within the established phase flow

### Git Workflow

The project uses git hooks for quality control:
- **Pre-commit hooks**: Run type checking and linting automatically
- **Commit message format**: Clear, descriptive commit messages with scope
- **Use `--no-verify` sparingly**: Only for emergency fixes or work-in-progress

This architecture provides a stable foundation for implementing Dragon Dice rules while maintaining clear separation of concerns and testability.
