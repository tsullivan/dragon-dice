#!/usr/bin/env python3
"""
Script to generate species cards HTML for all basic species with proper spell filtering.
Only includes spells for elements that each species actually possesses.
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.spell_model import ALL_SPELLS, SPELLS_BY_ELEMENT


def load_species_data():
    """Load species data from snapshot."""
    species_file = Path("models/test/snapshots/species_data.json")
    with open(species_file, "r") as f:
        return json.load(f)


def load_unit_data():
    """Load unit data from snapshot."""
    units_file = Path("models/test/snapshots/unit_data.json")
    with open(units_file, "r") as f:
        return json.load(f)


def get_css_class_name(species_name):
    """Convert species name to CSS class name."""
    # Handle special cases
    name_mapping = {
        "Amazon": "amazons",
        "Coral Elf": "coral-elves",
        "Dwarf": "dwarves",
        "Feral": "feral",
        "Firewalker": "firewalkers",
        "Frostwing": "frostwings",
        "Goblin": "goblins",
        "Lava Elf": "lava-elves",
        "Scalder": "scalders",
        "Swamp Stalker": "swamp-stalkers",
        "Treefolk": "treefolk",
        "Undead": "undead",
    }
    return name_mapping.get(species_name, species_name.lower().replace(" ", "-"))


def get_element_icon(element):
    """Get emoji icon for element."""
    element_icons = {
        "AIR": "🟦",
        "DEATH": "⬛",
        "EARTH": "🟨",
        "FIRE": "🟥",
        "WATER": "🟩",
        "IVORY": "🟫",
        "WHITE": "⬜",
    }
    return element_icons.get(element, "❓")


def get_spells_for_species(species_display_name, species_elements):
    """Get all spells available to a species, filtered by their elements."""
    available_spells = {}

    # Get species elements as a set for easy checking
    species_element_set = set(species_elements)
    
    # Special case: IVORY species (Amazons) can use "Any" spells from ALL elements
    is_ivory_species = "IVORY" in species_element_set

    # For each element, check if species has that element
    for element, spells in SPELLS_BY_ELEMENT.items():
        if element == "ELEMENTAL":
            # Elemental spells are available to all species
            available_spells[element] = []
            for spell in spells.values():
                if spell.species == "Any" or spell.species == species_display_name:
                    available_spells[element].append(spell)
        else:
            # For IVORY species: include "Any" spells from ALL elements
            # For other species: only include spells for elements they have
            if element in species_element_set or is_ivory_species:
                available_spells[element] = []
                for spell in spells.values():
                    # For IVORY species: only include "Any" spells from non-IVORY elements
                    # For other species: include "Any" spells + species-specific spells
                    if is_ivory_species and element not in species_element_set:
                        # IVORY species gets only "Any" spells from other elements
                        if spell.species == "Any":
                            available_spells[element].append(spell)
                    else:
                        # Normal logic: "Any" spells + species-specific spells
                        if spell.species == "Any" or spell.species == species_display_name:
                            available_spells[element].append(spell)

    return available_spells


def generate_spell_section(species_display_name, species_elements):
    """Generate the spells section HTML for a species."""
    spells = get_spells_for_species(species_display_name, species_elements)

    if not spells:
        return ""

    html = """
                <div class="section">
                    <div class="section-title">Spells</div>
                    <div class="spells-grid">"""

    # Add spell elements in a consistent order
    element_order = ["AIR", "DEATH", "EARTH", "FIRE", "WATER", "ELEMENTAL"]

    for element in element_order:
        if element in spells and spells[element]:
            element_class = element.lower()
            html += f"""
                        <div class="spell-element {element_class}">
                            <div class="spell-element-title">{element}</div>
                            <div class="spell-list">"""

            # Sort spells by cost, then by name
            sorted_spells = sorted(spells[element], key=lambda s: (s.cost, s.name))

            for spell in sorted_spells:
                indicators = []
                if spell.cantrip:
                    indicators.append('<span class="spell-tag cantrip">C</span>')
                if spell.reserves:
                    indicators.append('<span class="spell-tag reserves">R</span>')
                indicators.append(f'<span class="spell-cost">{spell.cost}</span>')

                indicators_html = "".join(indicators)
                html += f"""
                                <div class="spell-item"><span class="spell-name">{spell.name}</span><div class="spell-indicators">{indicators_html}</div></div>"""

            html += """
                            </div>
                        </div>"""

    html += """
                    </div>
                </div>"""

    return html


def organize_units_by_type(units, species_name):
    """Organize units by type for a specific species."""
    species_units = {}

    for unit_id, unit_data in units.items():
        if unit_data.get("species_name") == species_name:
            unit_type = unit_data.get("unit_type", "Unknown")
            health = unit_data.get("health", 1)
            name = unit_data.get("name", "Unknown")

            if unit_type not in species_units:
                species_units[unit_type] = []

            species_units[unit_type].append({"name": name, "health": health})

    # Sort units within each type by health
    for unit_type in species_units:
        species_units[unit_type].sort(key=lambda x: x["health"])

    return species_units


def generate_species_card(species_name, species_data, units_data):
    """Generate HTML for a single species card."""
    css_class = get_css_class_name(species_name)
    display_name = species_data["display_name"]

    # Generate element badges
    element_badges = ""
    for element_color in species_data["element_colors"]:
        icon = element_color[0]
        color_name = element_color[1].lower()
        element_badges += f'                    <div class="element-badge {color_name}">{icon}</div>\n'

    # Generate abilities
    abilities_html = ""
    for ability in species_data["abilities"]:
        name = ability["name"]
        description = ability["description"]
        # Use full description text without truncation
        abilities_html += f"""                        <div class="ability">
                            <span class="ability-name">{name}:</span> {description}
                        </div>
"""

    # Get units for this species
    species_units = organize_units_by_type(units_data, species_name)

    # Generate units grid (excluding monsters)
    units_html = ""
    # Standard unit types in preferred order (excluding Monster)
    unit_type_order = ["Heavy Melee", "Light Melee", "Cavalry", "Missile", "Magic", "Heavy Magic", "Light Magic"]

    # Add units in order
    displayed_types = set()
    for unit_type in unit_type_order:
        if unit_type in species_units:
            units_html += f"""                        <div class="unit-category">
                            <div class="unit-type">{unit_type}</div>
"""
            for unit in species_units[unit_type]:
                units_html += f'                            <div class="unit-item"><span class="unit-name">{unit["name"]}</span><span class="health-badge">{unit["health"]}</span></div>\n'
            units_html += "                        </div>\n"
            displayed_types.add(unit_type)

    # Add any remaining unit types not in the standard order (excluding Monster)
    for unit_type in sorted(species_units.keys()):
        if unit_type not in displayed_types and unit_type != "Monster":
            units_html += f"""                        <div class="unit-category">
                            <div class="unit-type">{unit_type}</div>
"""
            for unit in species_units[unit_type]:
                units_html += f'                            <div class="unit-item"><span class="unit-name">{unit["name"]}</span><span class="health-badge">{unit["health"]}</span></div>\n'
            units_html += "                        </div>\n"

    # Generate monsters
    monsters = [unit for unit in species_units.get("Monster", []) if unit["health"] == 4]
    monsters_html = ""
    for monster in monsters:
        monsters_html += f'                        <div class="monster-item"><span class="monster-name">{monster["name"]}</span><span class="health-badge">{monster["health"]}</span></div>\n'

    # Generate spell section with proper filtering
    spells_section = generate_spell_section(display_name, species_data["elements"])

    card_html = f"""        <!-- {display_name} -->
        <div class="species-card {css_class}">
            <div class="card-header">
                <h2 class="species-name">{display_name.upper()}</h2>
                <div class="elements">
{element_badges.rstrip()}
                </div>
            </div>
            <div class="card-content">
                <div class="section">
                    <div class="section-title">Species Abilities</div>
                    <div class="abilities-list">
{abilities_html.rstrip()}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">Units</div>
                    <div class="units-grid">
{units_html.rstrip()}
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Monsters</div>
                    <div class="monsters-grid">
{monsters_html.rstrip()}
                    </div>
                </div>
{spells_section}
            </div>
        </div>

"""

    return card_html


def generate_complete_html(cards_html):
    """Generate complete HTML with CSS and structure."""
    # Read CSS from existing file
    try:
        with open("assets/species_cards.html", "r") as f:
            existing_content = f.read()

        # Extract CSS section
        css_start = existing_content.find("<style>")
        css_end = existing_content.find("</style>") + 8
        css_section = existing_content[css_start:css_end]

    except FileNotFoundError:
        # Fallback basic CSS if file not found
        css_section = """<style>
        /* Basic styles would go here */
        </style>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dragon Dice Species Reference Cards</title>
    {css_section}
</head>
<body>
    <h1 class="header-title">DRAGON DICE SPECIES REFERENCE</h1>
    
    <div class="cards-container">
{cards_html}
    </div>
</body>
</html>"""

    return html


def main():
    """Generate species cards for all basic species with spell filtering."""
    species_data = load_species_data()
    units_data = load_unit_data()

    # Get only basic species (not subspecies or dragon types)
    basic_species = [
        "AMAZON",
        "CORAL_ELF",
        "DWARF",
        "FERAL",
        "FIREWALKER",
        "FROSTWING",
        "GOBLIN",
        "LAVA_ELF",
        "SCALDER",
        "SWAMP_STALKER",
        "TREEFOLK",
        "UNDEAD",
    ]

    # Test spell filtering for all species
    print("Testing spell filtering for all species...")
    for species_key in basic_species:
        if species_key in species_data:
            species_info = species_data[species_key]
            display_name = species_info["display_name"]
            elements = species_info["elements"]
            spells = get_spells_for_species(display_name, elements)
            spell_count = sum(len(spell_list) for spell_list in spells.values())
            element_names = ", ".join(elements)
            print(f"{display_name} ({element_names}): {spell_count} spells across {len(spells)} elements")
            for element, spell_list in spells.items():
                if spell_list:
                    print(f"  {element}: {len(spell_list)} spells")

    # Generate cards
    cards_html = ""
    for species_key in basic_species:
        if species_key in species_data:
            species_info = species_data[species_key]
            species_name = species_info["name"]
            card_html = generate_species_card(species_name, species_info, units_data)
            cards_html += card_html

    # Generate complete HTML
    complete_html = generate_complete_html(cards_html)

    # Save to file
    output_file = "species_cards_output.html"
    with open(output_file, "w") as f:
        f.write(complete_html)

    print(f"\nGenerated complete species cards HTML: {output_file}")
    print(f"Total species: {len(basic_species)}")


if __name__ == "__main__":
    main()
