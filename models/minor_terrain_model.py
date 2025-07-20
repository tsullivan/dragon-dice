from typing import Dict, List, Optional

from models.terrain_model import Terrain


class MinorTerrain(Terrain):
    """
    Represents a minor terrain die in the Dragon Dice game.
    Minor terrains are smaller terrain dice that can be placed on major terrains
    and provide additional effects to armies controlling them.
    """

    def __init__(
        self,
        name: str,
        eighth_face: str,
        faces: List[Dict[str, str]],
        elements: List[str],
    ):
        # Call parent constructor with is_advanced=False (minor terrains are never advanced)
        super().__init__(name, eighth_face, faces, elements, is_advanced=False)
        # Override terrain_type to be minor
        self.terrain_type = "minor"

    def get_terrain_base_name(self) -> str:
        """Get the base terrain type name from elements."""
        # Derive base name from elements for compatibility
        element_to_base_name = {
            ("AIR", "WATER"): "Coastland",
            ("DEATH",): "Deadland",
            ("FIRE", "WATER"): "Feyland",
            ("AIR", "EARTH"): "Flatland",
            ("EARTH", "FIRE"): "Highland",
            ("EARTH", "WATER"): "Swampland",
            ("AIR", "FIRE"): "Wasteland",
        }
        elements_tuple = tuple(sorted(self.elements))
        return element_to_base_name.get(elements_tuple, "Unknown")

    def __str__(self) -> str:
        return f"{self.name} (minor)"

    def __repr__(self) -> str:
        elements_str = (
            ", ".join(self.elements) if len(self.elements) > 1 else self.elements[0] if self.elements else "No elements"
        )
        return f"MinorTerrain(name='{self.name}', elements='{elements_str}', eighth_face='{self.eighth_face}')"


# Static minor terrain data - define all minor terrain instances
MINOR_TERRAIN_DATA = {
    "COASTLAND_BRIDGE": MinorTerrain(
        name="Coastland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_FOREST": MinorTerrain(
        name="Coastland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_KNOLL": MinorTerrain(
        name="Coastland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "COASTLAND_VILLAGE": MinorTerrain(
        name="Coastland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "WATER"],
    ),
    "DEADLAND_BRIDGE": MinorTerrain(
        name="Deadland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "DEADLAND_FOREST": MinorTerrain(
        name="Deadland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "DEADLAND_KNOLL": MinorTerrain(
        name="Deadland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "DEADLAND_VILLAGE": MinorTerrain(
        name="Deadland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["DEATH"],
    ),
    "FEYLAND_BRIDGE": MinorTerrain(
        name="Feyland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_FOREST": MinorTerrain(
        name="Feyland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_KNOLL": MinorTerrain(
        name="Feyland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FEYLAND_VILLAGE": MinorTerrain(
        name="Feyland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "FIRE"],
    ),
    "FLATLAND_BRIDGE": MinorTerrain(
        name="Flatland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_FOREST": MinorTerrain(
        name="Flatland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_KNOLL": MinorTerrain(
        name="Flatland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "FLATLAND_VILLAGE": MinorTerrain(
        name="Flatland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "EARTH"],
    ),
    "HIGHLAND_BRIDGE": MinorTerrain(
        name="Highland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_FOREST": MinorTerrain(
        name="Highland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_KNOLL": MinorTerrain(
        name="Highland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "HIGHLAND_VILLAGE": MinorTerrain(
        name="Highland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["FIRE", "EARTH"],
    ),
    "SWAMPLAND_BRIDGE": MinorTerrain(
        name="Swampland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_FOREST": MinorTerrain(
        name="Swampland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_KNOLL": MinorTerrain(
        name="Swampland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "SWAMPLAND_VILLAGE": MinorTerrain(
        name="Swampland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["WATER", "EARTH"],
    ),
    "WASTELAND_BRIDGE": MinorTerrain(
        name="Wasteland Bridge",
        eighth_face="Bridge",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Flood",
                "description": "The controlling army's maneuver results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_FOREST": MinorTerrain(
        name="Wasteland Forest",
        eighth_face="Forest",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Flanked",
                "description": "The controlling army's save results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_KNOLL": MinorTerrain(
        name="Wasteland Knoll",
        eighth_face="Knoll",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Landslide",
                "description": "The controlling army's missile results are halved. The minor terrain is buried at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
    "WASTELAND_VILLAGE": MinorTerrain(
        name="Wasteland Village",
        eighth_face="Village",
        faces=[
            {
                "name": "ID",
                "description": "Pick any action face on the minor terrain (magic, melee, or missile). Turn the die to the selected face.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Missile",
                "description": "The controlling army may conduct a Missile action or the action shown on the terrain.",
            },
            {
                "name": "Melee",
                "description": "The controlling army may conduct a Melee action or the action shown on the terrain.",
            },
            {
                "name": "Magic",
                "description": "The controlling army may conduct a Magic action or the action shown on the terrain.",
            },
            {
                "name": "Double Maneuvers",
                "description": "The controlling army doubles its ID results when rolling for maneuvers.",
            },
            {
                "name": "Double Saves",
                "description": "The controlling army doubles its ID results when rolling for saves.",
            },
            {
                "name": "Revolt",
                "description": "The controlling army's melee results are halved. The minor terrain is buried it at the beginning of the army's next march.",
            },
        ],
        elements=["AIR", "FIRE"],
    ),
}


# Helper functions for minor terrain access
def get_minor_terrain(terrain_name: str) -> Optional[MinorTerrain]:
    """Get a minor terrain by name."""
    terrain_key = terrain_name.upper()
    return MINOR_TERRAIN_DATA.get(terrain_key)


def get_all_minor_terrain_names() -> List[str]:
    """Get all minor terrain names."""
    return list(MINOR_TERRAIN_DATA.keys())


def get_all_minor_terrain_objects() -> List[MinorTerrain]:
    """Get all minor terrain objects."""
    return list(MINOR_TERRAIN_DATA.values())


def get_minor_terrains_by_element(element: str) -> List[MinorTerrain]:
    """Get all minor terrains that contain a specific element."""
    element = element.upper()
    return [terrain for terrain in MINOR_TERRAIN_DATA.values() if terrain.has_element(element)]


def get_minor_terrains_by_base_name(base_name: str) -> List[MinorTerrain]:
    """Get all minor terrains of a specific base terrain type."""
    return [
        terrain
        for terrain in MINOR_TERRAIN_DATA.values()
        if terrain.get_terrain_base_name().lower() == base_name.lower()
    ]


def get_minor_terrains_by_elements(elements: List[str]) -> List[MinorTerrain]:
    """Get all minor terrains that have the specified elements."""
    elements_set = {elem.upper() for elem in elements}
    return [terrain for terrain in MINOR_TERRAIN_DATA.values() if set(terrain.elements) == elements_set]


def get_minor_terrains_by_eighth_face(eighth_face: str) -> List[MinorTerrain]:
    """Get all minor terrains of a specific eighth_face."""
    return [terrain for terrain in MINOR_TERRAIN_DATA.values() if terrain.eighth_face.lower() == eighth_face.lower()]


def validate_minor_terrain_data() -> bool:
    """Validate all minor terrain data."""
    try:
        for terrain_name, terrain in MINOR_TERRAIN_DATA.items():
            if not isinstance(terrain, MinorTerrain):
                print(f"ERROR: {terrain_name} is not a MinorTerrain instance")
                return False

        print(f"✓ All {len(MINOR_TERRAIN_DATA)} minor terrains validated successfully")
        return True
    except Exception as e:
        print(f"ERROR: Minor terrain validation failed: {e}")
        return False
