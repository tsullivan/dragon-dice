# Dragon Dice E2E Testing Framework

This directory contains a comprehensive End-to-End (E2E) testing framework for the Dragon Dice application. The tests simulate real user interactions and validate complete workflows from UI to game logic.

## 📋 Test Categories

### 1. Complete Gameplay Flow Tests (`test_complete_gameplay_flow.py`)
- **Purpose**: Test the entire user journey from startup to action selection
- **Coverage**: Welcome screen → Player setup → Frontier selection → Distance rolls → Main gameplay
- **Key Features**:
  - Tests the specific infinite loop and unresponsive button issues
  - Validates all UI transitions work correctly
  - Ensures action buttons are responsive and functional
  - Verifies application can be closed normally

### 2. Comprehensive Game Flow Tests (`test_comprehensive_game_flows.py`) 🆕
- **Purpose**: Migrated and consolidated E2E tests using modern pytest framework
- **Coverage**: Game engine flows, UI integration, complete user journeys
- **Key Features**:
  - **TestGameEngineFlows**: Action flows, march phases, counter-maneuvers, phase transitions
  - **TestUIIntegrationFlows**: Button interactions, dialog integration, terrain/army interactions
  - **TestCompleteUserJourneys**: End-to-end user workflows from startup to gameplay
  - Unified pytest framework with better error handling and assertions

### 3. Visual Validation Tests (`test_visual_validation.py`)
- **Purpose**: Ensure UI elements render correctly and are visually accessible
- **Coverage**: Screen layouts, widget visibility, visual feedback
- **Key Features**:
  - Takes screenshots at key points for visual regression testing
  - Validates essential UI elements are present and visible
  - Tests error state visual feedback
  - Monitors UI responsiveness during transitions

### 4. Performance Validation Tests (`test_performance_validation.py`)
- **Purpose**: Test application performance and resource usage
- **Coverage**: Memory usage, response times, stability under load
- **Key Features**:
  - Memory leak detection
  - UI responsiveness measurement
  - Startup time validation
  - Infinite loop prevention verification
  - Stress testing scenarios

### 5. Legacy E2E Tests (`test_*_flows.py`) 📦
- **Purpose**: Original unittest-based E2E tests (preserved for compatibility)
- **Coverage**: Game engine logic, phase transitions, combat flows
- **Status**: Migrated to `test_comprehensive_game_flows.py`
- **Files**:
  - `test_first_march_flows.py` - First march phase testing
  - `test_action_flows.py` - Action selection and execution
  - `test_counter_maneuver_flows.py` - Counter-maneuver mechanics
  - `test_phase_transitions.py` - Game phase transitions
  - Others...

## 🚀 Running the Tests

### Quick Test (Essential Only)
```bash
# Run migrated comprehensive tests (recommended)
python test/e2e/run_comprehensive_e2e_tests.py --quick

# Run specific comprehensive test categories
pytest test/e2e/test_comprehensive_game_flows.py -v

# Run original complete gameplay flow
python test/e2e/test_complete_gameplay_flow.py
```

### Full Test Suite
```bash
# Run all modern E2E tests (recommended)
python test/e2e/run_comprehensive_e2e_tests.py

# Run specific categories
python test/e2e/run_comprehensive_e2e_tests.py --categories comprehensive visual performance

# Include legacy tests for comparison
python test/e2e/run_comprehensive_e2e_tests.py --categories comprehensive legacy

# Verbose output for debugging
python test/e2e/run_comprehensive_e2e_tests.py --verbose --no-capture
```

### Migrated Test Categories
```bash
# Game engine tests (migrated from multiple legacy files)
pytest test/e2e/test_comprehensive_game_flows.py::TestGameEngineFlows -v

# UI integration tests (migrated from UI test files)
pytest test/e2e/test_comprehensive_game_flows.py::TestUIIntegrationFlows -v

# Complete user journey tests (enhanced)
pytest test/e2e/test_comprehensive_game_flows.py::TestCompleteUserJourneys -v
```

### Individual Test Files
```bash
# Run specific test files
pytest test/e2e/test_complete_gameplay_flow.py -v
pytest test/e2e/test_visual_validation.py -v
pytest test/e2e/test_performance_validation.py -v
```

## 🛠️ Test Architecture

### Key Components

1. **Test Fixtures (`@pytest.fixture`)**
   - Automatic application setup and teardown
   - Shared test data and mocked game states
   - Qt application instance management

2. **Helper Methods**
   - Widget finding utilities (`_find_button_with_text`, `_find_combo_with_option`)
   - Navigation helpers (`_navigate_to_player_setup`, `_navigate_to_main_gameplay`)
   - Action simulation (`_add_basic_army_units`, `_test_action_buttons`)

3. **Assertions and Validations**
   - UI element presence and state validation
   - Performance threshold checking
   - Memory usage monitoring
   - Response time measurement

### Example Test Structure
```python
class TestCompleteGameplayFlow:
    @pytest.fixture(autouse=True)
    def setup_application(self, qtbot):
        """Set up the application for testing."""
        self.qtbot = qtbot
        self.main_window = MainWindow()
        self.qtbot.addWidget(self.main_window)
        self.main_window.show()
        yield
        self.main_window.close()
    
    def test_complete_two_player_game_flow(self, qtbot):
        """Test a complete two-player game from start to action selection."""
        self._test_welcome_screen_setup()
        self._test_player_setup_flow() 
        self._test_frontier_selection()
        self._test_distance_rolls()
        self._test_main_gameplay_action_selection()
```

## 🎯 Testing Strategy

### 1. **User Journey Testing**
- Simulates real user interactions with realistic data
- Tests complete workflows, not just individual components
- Validates that fixes for specific issues (like infinite loops) work in practice

### 2. **Regression Prevention**
- Tests are designed to catch regressions in previously fixed issues
- Visual regression testing through screenshots
- Performance regression detection through metrics

### 3. **Integration Validation**
- Tests interactions between UI components and game logic
- Validates signal/slot connections work correctly
- Ensures data flows properly through the application layers

### 4. **Error Recovery Testing**
- Tests how the application handles malformed data
- Validates error states provide appropriate feedback
- Ensures the application remains stable under error conditions

## 📊 Test Reporting

### Console Output
- Real-time progress with emoji indicators
- Performance metrics (timing, memory usage)
- Clear pass/fail status for each test phase

### Screenshots (Visual Tests)
- Automatic screenshot capture at key points
- Stored in `test/e2e/screenshots/` directory
- Useful for debugging UI issues and visual regressions

### Performance Metrics
- Memory usage tracking
- Response time measurements
- Resource leak detection
- Startup time validation

## 🔧 Configuration and Customization

### Environment Variables
- `E2E_SAVE_SCREENSHOTS=1` - Enable screenshot capture
- Add custom variables as needed for test configuration

### Test Timeouts
```python
# Configurable in E2ETestConfig class
STARTUP_TIMEOUT = 10
NAVIGATION_TIMEOUT = 5
ACTION_TIMEOUT = 3
```

### Performance Thresholds
```python
MAX_STARTUP_TIME = 5.0
MAX_MEMORY_GROWTH_MB = 100
MAX_RESPONSE_TIME_MS = 50
```

## 🐛 Debugging Failed Tests

### 1. **Visual Debugging**
```bash
# Run with visual output and no capture
python test/e2e/run_comprehensive_e2e_tests.py --verbose --no-capture --no-screenshots
```

### 2. **Individual Test Debugging**
```bash
# Run a single test with full output
pytest test/e2e/test_complete_gameplay_flow.py::TestCompleteGameplayFlow::test_complete_two_player_game_flow -v -s
```


## 📋 Best Practices for E2E Tests

### 1. **Test Independence**
- Each test should be able to run independently
- Use fixtures for setup/teardown to ensure clean state
- Don't rely on the order of test execution

### 2. **Realistic Data**
- Use realistic player names, army configurations, terrain selections
- Test with data that represents actual user scenarios
- Include edge cases and boundary conditions

### 3. **Clear Assertions**
- Use descriptive assertion messages
- Test both positive and negative conditions
- Validate both functional and visual aspects

### 4. **Performance Awareness**
- Keep test execution time reasonable
- Use timeouts to prevent hanging tests
- Monitor resource usage during tests

### 5. **Maintainability**
- Use helper methods to reduce code duplication
- Keep tests focused on specific scenarios
- Document complex test logic with comments

## 🚦 CI/CD Integration

### Running in Automated Environments
```bash
# Headless mode for CI (requires virtual display)
xvfb-run -a python test/e2e/run_comprehensive_e2e_tests.py --quick

# Or with pytest directly
xvfb-run -a pytest test/e2e/test_comprehensive_game_flows.py --tb=short
```

### Exit Codes
- `0` - All tests passed
- `1` - Test failures or errors
- Use in CI pipelines to gate deployments

## 📝 Adding New E2E Tests

### 1. **Create Test File**
```python
# test/e2e/test_new_feature.py
import pytest
from test.e2e.test_comprehensive_game_flows import TestCompleteUserJourneys

class TestNewFeature(TestCompleteUserJourneys):
    def test_new_feature_flow(self, qtbot):
        # Test implementation
        pass
```

### 2. **Update Test Runner**
Add new test categories to `run_comprehensive_e2e_tests.py` if needed.

### 3. **Follow Patterns**
- Use existing helper methods when possible
- Follow the established naming conventions
- Include both positive and negative test cases

This comprehensive E2E testing framework ensures that the Dragon Dice application works correctly from the user's perspective and helps prevent regressions in critical functionality like the action button responsiveness and infinite loop issues that were previously encountered.