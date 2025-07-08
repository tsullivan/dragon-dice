# Dragon Dice Model Data Snapshots

This directory contains JSON snapshot files that define all model data for the Dragon Dice companion application.

## Files

- **species_data.json** - All species definitions with elements, abilities, and display information
- **spell_data.json** - All spells with costs, effects, restrictions, and element associations  
- **dragon_form_data.json** - Dragon die forms (Drake, Wyrm) with face definitions
- **dragon_type_data.json** - Dragon types (Elemental, Hybrid, Ivory, etc.) with rules and properties
- **terrain_data.json** - All terrain dice with faces, elements, and special abilities
- **unit_data.json** - All unit data with species, health, faces, and classifications

## Purpose

These snapshots serve two main purposes:

1. **Reference Documentation** - Provide a complete, structured definition of all game elements in JSON format
2. **Change Detection** - Ensure model data doesn't change unexpectedly through automated testing

## Testing

The snapshot tests (`test_model_snapshots.py`) automatically:
- Generate fresh snapshots from the current model data
- Compare against existing snapshots to detect changes
- Fail if model data has changed without updating snapshots

### Running Snapshot Tests

```bash
# Run all snapshot tests
python -m pytest test/test_model_snapshots.py -v

# Run a specific snapshot test
python -m pytest test/test_model_snapshots.py::TestModelSnapshots::test_species_snapshot -v

# Generate fresh snapshots (delete existing files first)
rm test/snapshots/*.json
python -m pytest test/test_model_snapshots.py::TestModelSnapshots::test_generate_all_snapshots -v
```

### Updating Snapshots

If model data changes intentionally:

1. Delete the relevant snapshot file(s) in this directory
2. Re-run the snapshot tests to generate fresh snapshots
3. Review the new snapshot files to confirm changes are correct
4. Commit the updated snapshot files

## Statistics

Current model data counts:
- **Species**: 40 (including subspecies and dragon variants)
- **Spells**: 47 (across all elements and types)
- **Dragon Forms**: 2 (Drake, Wyrm)
- **Dragon Types**: 28 (Elemental, Hybrid, Ivory, White variants)
- **Terrains**: 48 (major terrain dice with different subtypes)
- **Units**: 240 (all unit variations across species)

Total entries: ~400+ game elements defined