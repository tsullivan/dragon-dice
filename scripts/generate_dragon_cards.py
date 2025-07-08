#!/usr/bin/env python3
"""
Generate dragon reference cards HTML combining dragon types and forms with detailed face descriptions.
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dragon_model import DRAGON_FORM_DATA, DRAGON_TYPE_DATA
from models.die_face_model import DRAGON_DIE_FACES


def load_dragon_type_data():
    """Load dragon type data from snapshot."""
    dragon_type_file = Path("models/test/snapshots/dragon_type_data.json")
    with open(dragon_type_file, "r") as f:
        return json.load(f)


def load_dragon_form_data():
    """Load dragon form data from snapshot."""
    dragon_form_file = Path("models/test/snapshots/dragon_form_data.json")
    with open(dragon_form_file, "r") as f:
        return json.load(f)


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


def get_face_description(face_name):
    """Get the detailed description for a dragon die face."""
    face_data = DRAGON_DIE_FACES.get(face_name)
    if face_data:
        # Clean up the description for display
        description = face_data.description
        # Replace escape sequences
        description = description.replace("\\n", "<br>")
        description = description.replace("\\*", "*")
        return description
    return f"No description available for {face_name}"


def generate_dragon_types_section():
    """Generate the dragon types section HTML."""
    dragon_types = load_dragon_type_data()

    # Group dragons by type
    elemental_dragons = []
    hybrid_dragons = []
    special_dragons = []

    for dragon_key, dragon_data in dragon_types.items():
        dragon_type = dragon_data["dragon_type"]
        elements = dragon_data["elements"]
        health = dragon_data["health"]
        force_value = dragon_data["force_value"]
        display_name = dragon_data["display_name"]

        # Create element icons
        element_icons = "".join([get_element_icon(elem) for elem in elements])

        # Determine dragon name (remove element icons from display name)
        name_parts = display_name.split(" ", 1)
        if len(name_parts) > 1:
            dragon_name = name_parts[1]
        else:
            dragon_name = display_name

        dragon_item = {"icons": element_icons, "name": dragon_name, "health": health, "force": force_value}

        if dragon_type == "ELEMENTAL":
            elemental_dragons.append(dragon_item)
        elif dragon_type == "HYBRID":
            hybrid_dragons.append(dragon_item)
        else:  # IVORY, IVORY_HYBRID, WHITE
            special_dragons.append(dragon_item)

    # Sort each group
    elemental_dragons.sort(key=lambda x: x["name"])
    hybrid_dragons.sort(key=lambda x: x["name"])
    special_dragons.sort(key=lambda x: x["name"])

    html = ""

    # Generate elemental dragons
    html += """                    <div class="dragon-category">
                        <div class="category-title">Elemental Dragons</div>
                        <div class="dragon-list">
"""
    for dragon in elemental_dragons:
        html += f"""                            <div class="dragon-item">
                                <span class="dragon-icons">{dragon["icons"]}</span>
                                <span class="dragon-name">{dragon["name"]}</span>
                                <span class="health-badge">{dragon["health"]}</span>
                                <span class="force-badge">{dragon["force"]}</span>
                            </div>
"""
    html += """                        </div>
                    </div>

"""

    # Generate hybrid dragons
    html += """                    <div class="dragon-category">
                        <div class="category-title">Hybrid Dragons</div>
                        <div class="dragon-list">
"""
    for dragon in hybrid_dragons:
        html += f"""                            <div class="dragon-item">
                                <span class="dragon-icons">{dragon["icons"]}</span>
                                <span class="dragon-name">{dragon["name"]}</span>
                                <span class="health-badge">{dragon["health"]}</span>
                                <span class="force-badge">{dragon["force"]}</span>
                            </div>
"""
    html += """                        </div>
                    </div>

"""

    # Generate special dragons
    html += """                    <div class="dragon-category">
                        <div class="category-title">Special Dragons</div>
                        <div class="dragon-list">
"""
    for dragon in special_dragons:
        html += f"""                            <div class="dragon-item">
                                <span class="dragon-icons">{dragon["icons"]}</span>
                                <span class="dragon-name">{dragon["name"]}</span>
                                <span class="health-badge">{dragon["health"]}</span>
                                <span class="force-badge">{dragon["force"]}</span>
                            </div>
"""
    html += """                        </div>
                    </div>
"""

    return html


def generate_dragon_forms_section():
    """Generate the dragon forms section HTML."""
    dragon_forms = load_dragon_form_data()

    html = ""

    for form_key, form_data in dragon_forms.items():
        display_name = form_data["display_name"]
        face_names = form_data["face_names"]

        html += f"""                    <div class="form-card">
                        <div class="form-title">{display_name} ({len(face_names)} faces)</div>
                        <div class="faces-list">
"""

        for face_name in face_names:
            # Get face description
            description = get_face_description(face_name)
            # Get display name (remove underscores and clean up)
            display_face_name = face_name.replace("_", " ")

            html += f"""                            <div class="face-item">
                                <div class="face-name">{display_face_name}</div>
                                <div class="face-description">{description}</div>
                            </div>
"""

        html += """                        </div>
                    </div>
"""

    return html


def generate_special_abilities_section():
    """Generate the special abilities section HTML."""
    return """                <div class="special-abilities">
                    <div class="special-title">Special Dragon Abilities</div>
                    <div class="special-item"><strong>Hybrid Dragons:</strong> Apply both elemental breath effects when breath result is rolled</div>
                    <div class="special-item"><strong>Ivory Hybrids:</strong> Apply elemental breath effect, affected by spells of their element or ivory</div>
                    <div class="special-item"><strong>White Dragons:</strong> Double damage from claws/jaws/tail/wing, double treasure results</div>
                </div>"""


def generate_summoning_rules_section():
    """Generate the summoning rules section HTML."""
    return """                <div class="summoning-rules">
                    <div class="rules-title">Dragon Summoning Rules</div>
                    
                    <div class="rule-item">
                        <span class="rule-category">Elemental Dragons:</span> Can be summoned from terrain or summoning pool using matching element magic
                    </div>
                    
                    <div class="rule-item">
                        <span class="rule-category">Hybrid Dragons:</span> Can be summoned from terrain using either element's magic
                    </div>
                    
                    <div class="rule-item">
                        <span class="rule-category">Ivory Dragons:</span> Can only be summoned from summoning pool using any single element magic
                    </div>
                    
                    <div class="rule-item">
                        <span class="rule-category">Ivory Hybrids:</span> Can be summoned from terrain using their element's magic or ivory effects
                    </div>
                    
                    <div class="rule-item">
                        <span class="rule-category">White Dragons:</span> Can only be summoned using "Summon White Dragon" spell (14 cost, any element combination)
                    </div>
                    
                    <div class="rule-item">
                        <span class="rule-category">Force Values:</span> Most dragons count as 1 force, White Dragons count as 2 force when assembling armies
                    </div>
                </div>"""


def generate_complete_html():
    """Generate the complete dragon cards HTML file."""

    # Generate sections
    dragon_types_html = generate_dragon_types_section()
    dragon_forms_html = generate_dragon_forms_section()
    special_abilities_html = generate_special_abilities_section()
    summoning_rules_html = generate_summoning_rules_section()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dragon Dice Dragon Reference Cards</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Roboto:wght@300;400;500&display=swap');
        
        body {{
            margin: 0;
            padding: 10mm;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            font-family: 'Roboto', sans-serif;
            min-height: 100vh;
        }}

        .page-container {{
            max-width: 100%;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 15px;
        }}

        .page-title {{
            text-align: center;
            font-family: 'Cinzel', serif;
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 20px;
            text-transform: uppercase;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        .sections-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .section {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            padding: 12px;
            border: 2px solid #3498db;
        }}

        .section-title {{
            font-family: 'Cinzel', serif;
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
            text-align: center;
            text-transform: uppercase;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }}

        .dragon-types-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 15px;
        }}

        .dragon-category {{
            background: rgba(52, 152, 219, 0.1);
            border-radius: 5px;
            padding: 6px;
            border: 1px solid #3498db;
        }}

        .category-title {{
            font-weight: 600;
            font-size: 10px;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 4px;
            text-transform: uppercase;
        }}

        .dragon-list {{
            font-size: 8px;
            line-height: 1.2;
        }}

        .dragon-item {{
            display: flex;
            align-items: center;
            margin-bottom: 2px;
            padding: 1px 2px;
            border-radius: 2px;
            background: rgba(255, 255, 255, 0.7);
        }}

        .dragon-icons {{
            margin-right: 3px;
            font-size: 7px;
        }}

        .dragon-name {{
            flex: 1;
            font-weight: 500;
        }}

        .health-badge {{
            background: #e74c3c;
            color: white;
            border-radius: 3px;
            padding: 0px 2px;
            font-size: 6px;
            font-weight: bold;
            min-width: 8px;
            text-align: center;
        }}

        .force-badge {{
            background: #9b59b6;
            color: white;
            border-radius: 3px;
            padding: 0px 2px;
            font-size: 6px;
            font-weight: bold;
            min-width: 8px;
            text-align: center;
            margin-left: 2px;
        }}

        .special-abilities {{
            background: rgba(230, 126, 34, 0.1);
            border: 1px solid #e67e22;
            border-radius: 5px;
            padding: 6px;
            margin-top: 8px;
        }}

        .special-title {{
            font-weight: 600;
            font-size: 9px;
            color: #e67e22;
            margin-bottom: 4px;
            text-transform: uppercase;
        }}

        .special-item {{
            font-size: 7px;
            line-height: 1.2;
            margin-bottom: 2px;
            color: #2c3e50;
        }}

        .forms-container {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
        }}

        .form-card {{
            background: rgba(46, 204, 113, 0.1);
            border: 1px solid #2ecc71;
            border-radius: 5px;
            padding: 8px;
        }}

        .form-title {{
            font-weight: 600;
            font-size: 12px;
            color: #27ae60;
            text-align: center;
            margin-bottom: 6px;
            text-transform: uppercase;
        }}

        .faces-list {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            font-size: 7px;
        }}

        .face-item {{
            background: rgba(255, 255, 255, 0.8);
            padding: 3px;
            border-radius: 3px;
            border: 1px solid #2ecc71;
        }}

        .face-name {{
            font-weight: 600;
            color: #27ae60;
            margin-bottom: 1px;
        }}

        .face-description {{
            color: #2c3e50;
            line-height: 1.3;
        }}

        .summoning-rules {{
            grid-column: 1 / -1;
            background: rgba(155, 89, 182, 0.1);
            border: 1px solid #9b59b6;
            border-radius: 5px;
            padding: 10px;
            margin-top: 15px;
        }}

        .rules-title {{
            font-weight: 600;
            font-size: 12px;
            color: #8e44ad;
            margin-bottom: 6px;
            text-transform: uppercase;
            text-align: center;
        }}

        .rule-item {{
            font-size: 8px;
            line-height: 1.3;
            margin-bottom: 4px;
            color: #2c3e50;
        }}

        .rule-category {{
            font-weight: 600;
            color: #8e44ad;
            text-transform: uppercase;
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white !important;
                padding: 5mm;
            }}

            .page-container {{
                background: white !important;
                box-shadow: none;
            }}

            .page-title {{
                font-size: 20px;
            }}

            .section-title {{
                font-size: 14px;
            }}

            .dragon-item, .face-item, .rule-item {{
                font-size: 7px;
            }}
        }}
    </style>
</head>
<body>
    <div class="page-container">
        <h1 class="page-title">Dragon Reference Cards</h1>
        
        <div class="sections-container">
            <!-- Dragon Types Section -->
            <div class="section">
                <div class="section-title">Dragon Types</div>
                
                <div class="dragon-types-grid">
{dragon_types_html}
                </div>

{special_abilities_html}
            </div>

            <!-- Dragon Forms Section -->
            <div class="section">
                <div class="section-title">Dragon Forms</div>
                
                <div class="forms-container">
{dragon_forms_html}
                </div>
            </div>
        </div>

{summoning_rules_html}
    </div>
</body>
</html>"""

    return html


def main():
    """Generate and save the complete dragon cards HTML."""
    print("Generating dragon reference cards...")

    # Load data for statistics
    dragon_types = load_dragon_type_data()
    dragon_forms = load_dragon_form_data()

    print(f"Found {len(dragon_types)} dragon types")
    print(f"Found {len(dragon_forms)} dragon forms")
    print(f"Available die faces: {len(DRAGON_DIE_FACES)}")

    # Generate the complete HTML
    html_content = generate_complete_html()

    # Save to file
    with open("assets/dragon_cards.html", "w") as f:
        f.write(html_content)

    print(f"\\nGenerated complete dragon reference cards: assets/dragon_cards.html")
    print(f"Total dragon types: {len(dragon_types)}")
    print(f"Total dragon forms: {len(dragon_forms)}")


if __name__ == "__main__":
    main()
