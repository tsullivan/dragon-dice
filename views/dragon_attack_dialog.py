"""
Dragon Attack Dialog for Dragon Dice - handles the complete Dragon Attack Phase.

This dialog manages the 7-step Dragon Attack process:
1. Show dragons present at terrain
2. Determine dragon targets (dragon vs dragon vs army)
3. Roll attacking dragons
4. Resolve breath effects immediately
5. Army response (if being attacked)
6. Calculate damage and dragon deaths
7. Handle promotions and wing effects
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DragonDisplayWidget(QWidget):
    """Widget for displaying a single dragon's information."""

    def __init__(self, dragon_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.dragon_data = dragon_data
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dragon display UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Dragon frame
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 2px solid #666; border-radius: 5px; background-color: #f0f0f0; }")
        frame_layout = QVBoxLayout(frame)

        # Dragon name and owner
        name_label = QLabel(f"🐲 {self.dragon_data.get('name', 'Unknown Dragon')}")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f;")
        frame_layout.addWidget(name_label)

        owner_label = QLabel(f"Owner: {self.dragon_data.get('owner', 'Unknown')}")
        owner_label.setStyleSheet("font-size: 12px; color: #666;")
        frame_layout.addWidget(owner_label)

        # Dragon elements
        elements = self.dragon_data.get("elements", [])
        if elements:
            elements_text = " + ".join(elem.title() for elem in elements)
            elements_label = QLabel(f"Elements: {elements_text}")
            elements_label.setStyleSheet("font-size: 11px; color: #333;")
            frame_layout.addWidget(elements_label)

        # Dragon health
        health = self.dragon_data.get("health", 5)
        max_health = self.dragon_data.get("max_health", 5)
        health_label = QLabel(f"Health: {health}/{max_health}")
        health_label.setStyleSheet("font-size: 11px; color: #2e7d32;")
        frame_layout.addWidget(health_label)

        layout.addWidget(frame)


class DragonTargetingWidget(QWidget):
    """Widget for displaying dragon targeting information."""

    def __init__(self, targeting_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.targeting_info = targeting_info
        self._setup_ui()

    def _setup_ui(self):
        """Setup the targeting display UI."""
        layout = QVBoxLayout(self)

        # Targeting header
        header = QLabel("🎯 Dragon Targeting")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #d32f2f; margin-bottom: 10px;")
        layout.addWidget(header)

        # Targeting results
        for _dragon_id, target_info in self.targeting_info.items():
            target_frame = QFrame()
            target_frame.setFrameStyle(QFrame.Shape.Box)
            target_frame.setStyleSheet(
                "QFrame { border: 1px solid #ccc; border-radius: 3px; margin: 2px; padding: 5px; }"
            )

            target_layout = QVBoxLayout(target_frame)

            # Dragon name
            dragon_name = target_info.get("dragon_name", "Unknown Dragon")
            dragon_label = QLabel(f"🐲 {dragon_name}")
            dragon_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
            target_layout.addWidget(dragon_label)

            # Target description
            target_desc = target_info.get("target_description", "No target")
            target_label = QLabel(f"→ {target_desc}")
            target_label.setStyleSheet("color: #333; margin-left: 10px;")
            target_layout.addWidget(target_label)

            # Reason
            reason = target_info.get("reason", "")
            if reason:
                reason_label = QLabel(f"Reason: {reason}")
                reason_label.setStyleSheet("font-size: 10px; color: #666; margin-left: 10px;")
                target_layout.addWidget(reason_label)

            layout.addWidget(target_frame)


class DragonRollResultWidget(QWidget):
    """Widget for displaying dragon die roll results."""

    def __init__(self, dragon_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.dragon_data = dragon_data
        self._setup_ui()

    def _setup_ui(self):
        """Setup the roll result display UI."""
        layout = QVBoxLayout(self)

        # Dragon identifier
        dragon_name = self.dragon_data.get("dragon_name", "Unknown Dragon")
        header = QLabel(f"🎲 {dragon_name}")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f;")
        layout.addWidget(header)

        # Die result
        die_result = self.dragon_data.get("die_result", "Unknown")
        die_label = QLabel(f"Rolled: {die_result}")
        die_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #2e7d32;")
        layout.addWidget(die_label)

        # Damage dealt
        damage = self.dragon_data.get("damage_dealt", 0)
        if damage > 0:
            damage_label = QLabel(f"Damage: {damage} points")
            damage_label.setStyleSheet("font-size: 11px; color: #f57c00;")
            layout.addWidget(damage_label)

        # Special effects
        effects = self.dragon_data.get("special_effects", [])
        if effects:
            effects_label = QLabel("Effects:")
            effects_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #333;")
            layout.addWidget(effects_label)

            for effect in effects:
                effect_label = QLabel(f"• {effect}")
                effect_label.setStyleSheet("font-size: 10px; color: #666; margin-left: 10px;")
                layout.addWidget(effect_label)


class DragonAttackDialog(QDialog):
    """Dialog for handling Dragon Attack Phase interactions."""

    # Signals
    attack_completed = Signal(dict)  # Emits phase results
    attack_cancelled = Signal()
    army_response_needed = Signal(dict)  # Emits when army needs to respond
    promotion_selection_needed = Signal(dict)  # Emits when promotions are available

    def __init__(
        self,
        marching_player: str,
        terrain_name: str,
        dragons_present: List[Dict[str, Any]],
        marching_army: Dict[str, Any],
        parent=None,
    ):
        super().__init__(parent)
        self.marching_player = marching_player
        self.terrain_name = terrain_name
        self.dragons_present = dragons_present
        self.marching_army = marching_army

        # Attack state
        self.current_step = "show_dragons"  # show_dragons, targeting, rolling, breath_effects, army_response, damage_resolution, promotions
        self.targeting_results: Dict[str, Any] = {}
        self.dragon_roll_results: List[Dict[str, Any]] = []
        self.breath_effects: List[Dict[str, Any]] = []
        self.army_response_results: Dict[str, Any] = {}
        self.final_results: Dict[str, Any] = {}

        self.setWindowTitle(f"🐲 Dragon Attack at {terrain_name}")
        self.setModal(True)
        self.setMinimumSize(900, 700)

        self._setup_ui()
        self._update_step_display()

    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)

        # Step indicator
        self.step_label = QLabel()
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.step_label.font()
        font.setPointSize(18)
        font.setBold(True)
        self.step_label.setFont(font)
        self.step_label.setStyleSheet(
            "color: #d32f2f; margin: 10px; padding: 10px; background-color: #fafafa; border-radius: 5px;"
        )
        main_layout.addWidget(self.step_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(7)  # 7 steps in dragon attack
        self.progress_bar.setValue(1)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #d32f2f; }")
        main_layout.addWidget(self.progress_bar)

        # Main content area (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(self.scroll_area)

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)

        # Action buttons
        button_layout = QHBoxLayout()

        self.back_button = QPushButton("⬅️ Back")
        self.back_button.clicked.connect(self._go_back_step)
        self.back_button.setEnabled(False)
        button_layout.addWidget(self.back_button)

        button_layout.addStretch()

        self.next_button = QPushButton("Next Step ➡️")
        self.next_button.clicked.connect(self._go_next_step)
        button_layout.addWidget(self.next_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._cancel_attack)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Message area
        self.message_area = QTextEdit()
        self.message_area.setMaximumHeight(100)
        self.message_area.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc; border-radius: 3px;")
        self.message_area.setPlaceholderText("Dragon Attack messages will appear here...")
        main_layout.addWidget(self.message_area)

    def _update_step_display(self):
        """Update the UI for the current step."""
        self._clear_content()

        step_names = {
            "show_dragons": "Step 1: Dragons Present",
            "targeting": "Step 2: Dragon Targeting",
            "rolling": "Step 3: Dragon Rolls",
            "breath_effects": "Step 4: Breath Effects",
            "army_response": "Step 5: Army Response",
            "damage_resolution": "Step 6: Damage Resolution",
            "promotions": "Step 7: Promotions & Cleanup",
        }

        step_num = list(step_names.keys()).index(self.current_step) + 1
        self.step_label.setText(step_names.get(self.current_step, "Unknown Step"))
        self.progress_bar.setValue(step_num)

        # Update button states
        self.back_button.setEnabled(step_num > 1)

        if self.current_step == "show_dragons":
            self._show_dragons_step()
        elif self.current_step == "targeting":
            self._show_targeting_step()
        elif self.current_step == "rolling":
            self._show_rolling_step()
        elif self.current_step == "breath_effects":
            self._show_breath_effects_step()
        elif self.current_step == "army_response":
            self._show_army_response_step()
        elif self.current_step == "damage_resolution":
            self._show_damage_resolution_step()
        elif self.current_step == "promotions":
            self._show_promotions_step()

    def _clear_content(self):
        """Clear the content area."""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_dragons_step(self):
        """Show Step 1: Dragons Present at Terrain."""
        self._add_message(f"🐲 Dragon Attack Phase begins at {self.terrain_name}")
        self._add_message(f"Marching Player: {self.marching_player}")

        if not self.dragons_present:
            self._add_message("No dragons present at this terrain. Dragon Attack Phase will be skipped.")
            self.next_button.setText("Skip Phase")
            return

        self._add_message(f"Found {len(self.dragons_present)} dragon(s) at {self.terrain_name}")

        # Header
        header = QLabel(f"🐲 Dragons at {self.terrain_name}")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #d32f2f; margin-bottom: 10px;")
        self.content_layout.addWidget(header)

        # Dragons container
        dragons_container = QWidget()
        dragons_layout = QVBoxLayout(dragons_container)

        for dragon_data in self.dragons_present:
            dragon_widget = DragonDisplayWidget(dragon_data)
            dragons_layout.addWidget(dragon_widget)

        self.content_layout.addWidget(dragons_container)

        # Army info
        army_header = QLabel(f"⚔️ {self.marching_player}'s Army")
        army_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #2e7d32; margin-top: 20px; margin-bottom: 10px;"
        )
        self.content_layout.addWidget(army_header)

        army_info = QLabel(f"Army: {self.marching_army.get('name', 'Unknown Army')}")
        army_info.setStyleSheet("color: #333; margin-left: 10px;")
        self.content_layout.addWidget(army_info)

        units_count = len(self.marching_army.get("units", []))
        units_info = QLabel(f"Units: {units_count} units present")
        units_info.setStyleSheet("color: #333; margin-left: 10px;")
        self.content_layout.addWidget(units_info)

        self.next_button.setText("Determine Targets ➡️")

    def _show_targeting_step(self):
        """Show Step 2: Dragon Targeting Determination."""
        self._add_message("🎯 Determining dragon targets based on Dragon Dice targeting rules...")

        if not self.targeting_results:
            # Simulate targeting determination (in real implementation, this would come from DragonAttackManager)
            self.targeting_results = self._simulate_targeting()

        # Display targeting results
        targeting_widget = DragonTargetingWidget(self.targeting_results)
        self.content_layout.addWidget(targeting_widget)

        self.next_button.setText("Roll Dragons ➡️")

    def _show_rolling_step(self):
        """Show Step 3: Dragon Die Rolls."""
        self._add_message("🎲 Rolling dragon dice...")

        if not self.dragon_roll_results:
            # Simulate dragon rolls (in real implementation, this would come from DragonAttackManager)
            self.dragon_roll_results = self._simulate_dragon_rolls()

        # Header
        header = QLabel("🎲 Dragon Die Roll Results")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #d32f2f; margin-bottom: 10px;")
        self.content_layout.addWidget(header)

        # Roll results container
        rolls_container = QWidget()
        rolls_layout = QVBoxLayout(rolls_container)

        for roll_data in self.dragon_roll_results:
            roll_widget = DragonRollResultWidget(roll_data)
            rolls_layout.addWidget(roll_widget)

        self.content_layout.addWidget(rolls_container)

        self.next_button.setText("Process Breath Effects ➡️")

    def _show_breath_effects_step(self):
        """Show Step 4: Breath Effects Resolution."""
        self._add_message("💨 Processing dragon breath effects...")

        # Extract breath effects from roll results
        breath_effects = []
        for roll in self.dragon_roll_results:
            if roll.get("die_result") == "Dragon_Breath":
                breath_effects.extend(roll.get("breath_effects", []))

        if not breath_effects:
            self._add_message("No breath effects to resolve.")
            self.next_button.setText("Army Response ➡️")
            return

        # Header
        header = QLabel("💨 Dragon Breath Effects")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #d32f2f; margin-bottom: 10px;")
        self.content_layout.addWidget(header)

        # Breath effects display
        for effect in breath_effects:
            effect_frame = QFrame()
            effect_frame.setFrameStyle(QFrame.Shape.Box)
            effect_frame.setStyleSheet(
                "QFrame { border: 1px solid #f57c00; border-radius: 3px; margin: 2px; padding: 8px; background-color: #fff3e0; }"
            )

            effect_layout = QVBoxLayout(effect_frame)

            effect_name = QLabel(f"🔥 {effect.get('name', 'Unknown Effect')}")
            effect_name.setStyleSheet("font-weight: bold; color: #e65100;")
            effect_layout.addWidget(effect_name)

            effect_desc = QLabel(effect.get("effect", "No description"))
            effect_desc.setWordWrap(True)
            effect_desc.setStyleSheet("color: #333; margin-top: 5px;")
            effect_layout.addWidget(effect_desc)

            self.content_layout.addWidget(effect_frame)

        self.breath_effects = breath_effects
        self.next_button.setText("Army Response ➡️")

    def _show_army_response_step(self):
        """Show Step 5: Army Response (if army is being attacked)."""
        # Check if army is being attacked
        army_under_attack = any(roll.get("target_type") == "army" for roll in self.dragon_roll_results)

        if not army_under_attack:
            self._add_message("Army is not under direct attack. Skipping army response.")
            self.next_button.setText("Calculate Damage ➡️")
            return

        self._add_message(f"⚔️ {self.marching_player}'s army must respond to dragon attacks!")

        # Header
        header = QLabel(f"⚔️ {self.marching_player}'s Army Response")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #2e7d32; margin-bottom: 10px;")
        self.content_layout.addWidget(header)

        # Army response options
        response_info = QLabel(
            "Your army can make a combination roll counting melee, missile, and save results.\n"
            "Dragons need 5 points of damage to be killed (10 for White Dragons).\n"
            "Melee and missile results can kill dragons, but cannot be combined."
        )
        response_info.setWordWrap(True)
        response_info.setStyleSheet(
            "color: #333; margin-bottom: 15px; padding: 10px; background-color: #f5f5f5; border-radius: 3px;"
        )
        self.content_layout.addWidget(response_info)

        # Placeholder for army response (would integrate with actual combat system)
        response_placeholder = QLabel(
            "Army response handling would be integrated here with the existing combat system."
        )
        response_placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px; text-align: center;")
        self.content_layout.addWidget(response_placeholder)

        self.next_button.setText("Calculate Damage ➡️")

    def _show_damage_resolution_step(self):
        """Show Step 6: Damage Resolution."""
        self._add_message("⚖️ Calculating final damage and dragon deaths...")

        # Header
        header = QLabel("⚖️ Damage Resolution")
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #d32f2f; margin-bottom: 10px;")
        self.content_layout.addWidget(header)

        # Calculate totals
        total_damage = sum(roll.get("damage_dealt", 0) for roll in self.dragon_roll_results)
        dragons_killed = [
            roll
            for roll in self.dragon_roll_results
            if roll.get("target_type") == "dragon" and roll.get("damage_dealt", 0) >= 5
        ]

        # Damage summary
        damage_summary = QFrame()
        damage_summary.setFrameStyle(QFrame.Shape.Box)
        damage_summary.setStyleSheet(
            "QFrame { border: 2px solid #2e7d32; border-radius: 5px; padding: 10px; background-color: #e8f5e8; }"
        )

        summary_layout = QVBoxLayout(damage_summary)

        summary_title = QLabel("📊 Combat Summary")
        summary_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        summary_layout.addWidget(summary_title)

        damage_label = QLabel(f"Total damage dealt to army: {total_damage} points")
        damage_label.setStyleSheet("color: #333; margin-top: 5px;")
        summary_layout.addWidget(damage_label)

        if dragons_killed:
            killed_label = QLabel(f"Dragons killed: {len(dragons_killed)}")
            killed_label.setStyleSheet("color: #d32f2f; font-weight: bold; margin-top: 5px;")
            summary_layout.addWidget(killed_label)
        else:
            no_kills_label = QLabel("No dragons were killed")
            no_kills_label.setStyleSheet("color: #666; margin-top: 5px;")
            summary_layout.addWidget(no_kills_label)

        self.content_layout.addWidget(damage_summary)

        self.final_results = {
            "total_damage": total_damage,
            "dragons_killed": len(dragons_killed),
            "breath_effects": self.breath_effects,
        }

        if dragons_killed:
            self.next_button.setText("Check Promotions ➡️")
        else:
            self.next_button.setText("Complete Attack ➡️")

    def _show_promotions_step(self):
        """Show Step 7: Promotions and Cleanup."""
        dragons_killed = self.final_results.get("dragons_killed", 0)

        if dragons_killed > 0:
            self._add_message(f"🎉 Army killed {dragons_killed} dragon(s)! Checking for promotion opportunities...")

            # Header
            header = QLabel("🎉 Dragon Kill Promotions!")
            header.setStyleSheet("font-weight: bold; font-size: 16px; color: #2e7d32; margin-bottom: 10px;")
            self.content_layout.addWidget(header)

            promotion_info = QLabel(
                f"Congratulations! Your army successfully killed {dragons_killed} dragon(s).\n"
                "According to Dragon Dice rules, you may promote as many units as possible.\n"
                "The promotion system will be activated to handle your rewards."
            )
            promotion_info.setWordWrap(True)
            promotion_info.setStyleSheet(
                "color: #2e7d32; padding: 15px; background-color: #e8f5e8; border-radius: 5px; margin-bottom: 15px;"
            )
            self.content_layout.addWidget(promotion_info)
        else:
            self._add_message("No dragons were killed. No promotion opportunities available.")

            no_promotion_label = QLabel("No promotions available - no dragons were killed.")
            no_promotion_label.setStyleSheet("color: #666; padding: 15px; text-align: center;")
            self.content_layout.addWidget(no_promotion_label)

        # Wings cleanup
        wings_rolled = any(roll.get("wings_rolled", False) for roll in self.dragon_roll_results)
        if wings_rolled:
            wings_info = QLabel("🪽 Dragons that rolled wings have flown away and returned to their summoning pools.")
            wings_info.setStyleSheet(
                "color: #1976d2; padding: 10px; background-color: #e3f2fd; border-radius: 3px; margin-top: 10px;"
            )
            self.content_layout.addWidget(wings_info)

        self.next_button.setText("Complete Dragon Attack ✅")

    def _simulate_targeting(self) -> Dict[str, Any]:
        """Simulate dragon targeting for demonstration."""
        targeting = {}
        for i, dragon in enumerate(self.dragons_present):
            dragon_id = dragon.get("dragon_id", f"dragon_{i}")
            targeting[dragon_id] = {
                "dragon_name": dragon.get("name", "Unknown Dragon"),
                "target_description": f"{self.marching_player}'s army",
                "reason": "No other dragons to attack",
            }
        return targeting

    def _simulate_dragon_rolls(self) -> List[Dict[str, Any]]:
        """Simulate dragon die rolls for demonstration."""
        import random

        results = []
        dragon_faces = ["Jaws", "Dragon_Breath", "Claw_Front_Left", "Wing_Left", "Belly_Front", "Treasure"]

        for dragon in self.dragons_present:
            face = random.choice(dragon_faces)
            damage = {
                "Jaws": 12,
                "Dragon_Breath": 5,
                "Claw_Front_Left": 6,
                "Wing_Left": 5,
                "Belly_Front": 0,
                "Treasure": 0,
            }.get(face, 0)

            effects = []
            if face == "Jaws":
                effects.append("Jaws: 12 points of damage")
            elif face == "Dragon_Breath":
                effects.append("Breath: 5 units killed + elemental effect")
            elif "Claw" in face:
                effects.append("Claw: 6 points of damage")
            elif "Wing" in face:
                effects.append("Wing: 5 points of damage + dragon flies away")
            elif "Belly" in face:
                effects.append("Belly: Dragon vulnerable (no automatic saves)")
            elif face == "Treasure":
                effects.append("Treasure: Target army may promote one unit")

            results.append(
                {
                    "dragon_name": dragon.get("name", "Unknown Dragon"),
                    "die_result": face,
                    "damage_dealt": damage,
                    "special_effects": effects,
                    "target_type": "army",
                    "wings_rolled": "Wing" in face,
                    "treasure_rolled": face == "Treasure",
                    "breath_effects": [{"name": "Dragon Fire", "effect": "Roll killed units for burial saves"}]
                    if face == "Dragon_Breath"
                    else [],
                }
            )

        return results

    def _go_next_step(self):
        """Advance to the next step."""
        steps = [
            "show_dragons",
            "targeting",
            "rolling",
            "breath_effects",
            "army_response",
            "damage_resolution",
            "promotions",
        ]

        if self.current_step == "promotions":
            # Complete the attack
            self._complete_attack()
            return

        current_index = steps.index(self.current_step)
        if current_index < len(steps) - 1:
            self.current_step = steps[current_index + 1]
            self._update_step_display()

    def _go_back_step(self):
        """Go back to the previous step."""
        steps = [
            "show_dragons",
            "targeting",
            "rolling",
            "breath_effects",
            "army_response",
            "damage_resolution",
            "promotions",
        ]

        current_index = steps.index(self.current_step)
        if current_index > 0:
            self.current_step = steps[current_index - 1]
            self._update_step_display()

    def _complete_attack(self):
        """Complete the dragon attack and emit results."""
        self._add_message("✅ Dragon Attack Phase completed!")

        # Emit final results
        attack_results = {
            "terrain": self.terrain_name,
            "marching_player": self.marching_player,
            "dragons_present": len(self.dragons_present),
            "targeting_results": self.targeting_results,
            "roll_results": self.dragon_roll_results,
            "final_results": self.final_results,
            "breath_effects": self.breath_effects,
            "completed": True,
        }

        self.attack_completed.emit(attack_results)
        self.accept()

    def _cancel_attack(self):
        """Cancel the dragon attack."""
        self._add_message("❌ Dragon Attack cancelled by user")
        self.attack_cancelled.emit()
        self.reject()

    def _add_message(self, message: str):
        """Add a message to the message area."""
        current_text = self.message_area.toPlainText()
        if current_text:
            new_text = current_text + "\n" + message
        else:
            new_text = message
        self.message_area.setPlainText(new_text)

        # Scroll to bottom
        scrollbar = self.message_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_dragon_attack_results(self, results: Dict[str, Any]):
        """Set actual dragon attack results from the DragonAttackManager."""
        # This method would be called by the main gameplay view
        # to provide real data instead of simulation
        if "targeting_results" in results:
            self.targeting_results = results["targeting_results"]
        if "roll_results" in results:
            self.dragon_roll_results = results["roll_results"]
        if "breath_effects" in results:
            self.breath_effects = results["breath_effects"]

        # Refresh the current step display
        self._update_step_display()
