#!/usr/bin/env python3
"""
Generate spell cards HTML from spell data snapshot.
"""

import json
from pathlib import Path


def load_spell_data():
    """Load spell data from snapshot."""
    spell_file = Path("models/test/snapshots/spell_data.json")
    with open(spell_file) as f:
        return json.load(f)


def get_element_class(element):
    """Get CSS class name for element."""
    element_classes = {
        "AIR": "air",
        "DEATH": "death",
        "EARTH": "earth",
        "FIRE": "fire",
        "WATER": "water",
        "ELEMENTAL": "elemental",
    }
    return element_classes.get(element, "elemental")


def get_element_display_name(element):
    """Get display name for element."""
    element_names = {
        "AIR": "Air Magic",
        "DEATH": "Death Magic",
        "EARTH": "Earth Magic",
        "FIRE": "Fire Magic",
        "WATER": "Water Magic",
        "ELEMENTAL": "Elemental Magic",
    }
    return element_names.get(element, element)


def generate_spell_card(spell_key, spell_data):  # noqa: ARG001
    """Generate HTML for a single spell card."""
    element_class = get_element_class(spell_data["element"])

    # Generate indicators
    indicators = []
    if spell_data["cantrip"]:
        indicators.append('<div class="spell-tag cantrip">CANTRIP</div>')
    if spell_data["reserves"]:
        indicators.append('<div class="spell-tag reserves">RESERVES</div>')
    indicators.append(f'<div class="spell-cost">{spell_data["cost"]}</div>')

    indicators_html = "".join(indicators)

    # Format species restriction (shorter version)
    species_text = spell_data["species"] if spell_data["species"] != "Any" else "All Species"

    card_html = f"""            <div class="spell-card {element_class}">
                <div class="card-header">
                    <div class="spell-name">{spell_data["name"]}</div>
                    <div class="spell-indicators">
                        {indicators_html}
                    </div>
                </div>
                <div class="card-content">
                    <div class="spell-species">{species_text}</div>
                    <div class="spell-description">{spell_data["effect"]}</div>
                </div>
            </div>
"""

    return card_html


def generate_complete_html():
    """Generate the complete spell cards HTML file."""
    spell_data = load_spell_data()

    # Read the base HTML template
    with open("assets/spell_cards_template.html") as f:
        template = f.read()

    # Group spells by element
    spells_by_element = {}
    for spell_key, spell_info in spell_data.items():
        element = spell_info["element"]
        if element not in spells_by_element:
            spells_by_element[element] = []
        spells_by_element[element].append((spell_key, spell_info))

    # Sort spells within each element by cost, then by name
    for element in spells_by_element:
        spells_by_element[element].sort(key=lambda x: (x[1]["cost"], x[1]["name"]))

    # Generate content with each element in its own section using two columns
    content_html = ""
    element_order = ["AIR", "DEATH", "EARTH", "FIRE", "WATER", "ELEMENTAL"]

    for element in element_order:
        if element in spells_by_element:
            element_class = get_element_class(element)
            element_display = get_element_display_name(element)

            content_html += f"""    <div class="element-section">
        <div class="element-title {element_class}">{element_display}</div>
        <div class="cards-container">
"""

            for spell_key, spell_info in spells_by_element[element]:
                content_html += generate_spell_card(spell_key, spell_info)

            content_html += """        </div>
    </div>
"""

    # Replace the placeholder comment with the generated content
    complete_html = template.replace("    <!-- This file will be populated by the generate script -->", content_html)

    return complete_html


def main():
    """Generate and save the complete spell cards HTML."""
    print("Generating spell cards from snapshot data...")

    spell_data = load_spell_data()
    print(f"Found {len(spell_data)} spells")

    # Count spells by element
    element_counts = {}
    for spell_info in spell_data.values():
        element = spell_info["element"]
        element_counts[element] = element_counts.get(element, 0) + 1

    print("Spells by element:")
    for element, count in sorted(element_counts.items()):
        print(f"  {element}: {count} spells")

    # Generate the complete HTML
    html_content = generate_complete_html()

    # Save to file
    with open("assets/spell_cards.html", "w") as f:
        f.write(html_content)

    print("\nGenerated complete spell cards HTML: assets/spell_cards.html")
    print(f"Total spells: {len(spell_data)}")


if __name__ == "__main__":
    main()
