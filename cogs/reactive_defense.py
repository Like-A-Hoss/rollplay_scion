import asyncio
import json
import re
import uuid
import traceback
import nextcord
from nextcord import Interaction

try:
    from ..utilities import dice as dice
    from .reactive_json import _read_state, _write_state, _set_status
    from .reactive_embeds import _get_state_embed
    from .player_attack_resolver import resolve_player_attack_state
    from ..settings import REACTIVE_DEFENSE_LOG_CHANNEL
except ImportError:
    import utilities.dice as dice
    from settings import REACTIVE_DEFENSE_LOG_CHANNEL
    from cogs.reactive_json import _read_state, _write_state, _set_status
    from cogs.reactive_embeds import _get_state_embed
    from cogs.player_attack_resolver import resolve_player_attack_state


_DEBUG_TASKS: set[asyncio.Task] = set()


def _safe_preview(value: str, limit: int = 120) -> str:
    text = str(value).replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


async def _debug_log(client: nextcord.Client, step: str, state_id: str | None = None, details: str | None = None):
    if not REACTIVE_DEFENSE_LOG_CHANNEL:
        return

    try:
        channel_id = int(REACTIVE_DEFENSE_LOG_CHANNEL)
    except (TypeError, ValueError):
        return

    channel = client.get_channel(channel_id)
    if channel is None:
        try:
            channel = await client.fetch_channel(channel_id)
        except Exception:
            return

    lines = [f"[reactive_defense] step={step}"]
    if state_id:
        lines.append(f"state_id={state_id}")
    if details:
        lines.append(f"details={_safe_preview(details, 900)}")

    try:
        await channel.send("\n".join(lines))
    except Exception:
        return


def _queue_debug_log(client: nextcord.Client, step: str, state_id: str | None = None, details: str | None = None):
    try:
        task = asyncio.create_task(_debug_log(client, step, state_id, details))
        _DEBUG_TASKS.add(task)
        task.add_done_callback(_DEBUG_TASKS.discard)
    except Exception:
        return


class HeroTypeSelect(nextcord.ui.Select):
    def __init__(self, state_id: str):
        options = [
            nextcord.SelectOption(label="Origin", value="Origin"),
            nextcord.SelectOption(label="Hero", value="Hero"),
            nextcord.SelectOption(label="Demigod", value="Demigod"),
            nextcord.SelectOption(label="God", value="God"),
            nextcord.SelectOption(label="God Feat of Strength", value="God Feat of Strength"),
        ]
        super().__init__(placeholder="Choose Hero Type", min_values=1, max_values=1, options=options, custom_id=f"hero_type_{state_id}")
        self.state_id = state_id

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        roll_info = data.get("roll_info", {})
        roll_info["hero_type"] = self.values[0]
        data["roll_info"] = roll_info
        _write_state(self.state_id, data)
        _queue_debug_log(interaction.client, "hero_type_selected", self.state_id, f"hero_type={self.values[0]}")
        await interaction.response.edit_message(embed=_get_state_embed(data, "Reflexive Defense Configuration"), view=ReflexiveConfigView(self.state_id))


class ScaleSelect(nextcord.ui.Select):
    def __init__(self, state_id: str):
        options = [nextcord.SelectOption(label=str(i), value=str(i)) for i in range(7)]
        super().__init__(placeholder="Choose Scale", min_values=1, max_values=1, options=options, custom_id=f"scale_{state_id}")
        self.state_id = state_id

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        roll_info = data.get("roll_info", {})
        roll_info["scale"] = int(self.values[0])
        data["roll_info"] = roll_info
        _write_state(self.state_id, data)
        _queue_debug_log(interaction.client, "scale_selected", self.state_id, f"scale={self.values[0]}")
        await interaction.response.edit_message(embed=_get_state_embed(data, "Reflexive Defense Configuration"), view=ReflexiveConfigView(self.state_id))


class ReflexiveRollModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Reflexive Defense Roll")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Dice pool (int)", placeholder="e.g. 3", required=True))
        self.add_item(nextcord.ui.TextInput(label="How many of those are divinity dice?"))
        self.add_item(nextcord.ui.TextInput(label="Enhancement (int)", placeholder="e.g. 0", required=True))
        self.add_item(nextcord.ui.TextInput(label="Scale (int)", placeholder="0-6", required=True))
        self.add_item(nextcord.ui.TextInput(label="Again (int)", placeholder="10", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        roll_info = data.get("roll_info", {})
        try:
            dice_pool = int(self.children[0].value)
        except Exception:
            await interaction.response.send_message("Invalid dice pool", ephemeral=True)
            return
        try:
            divinity_dice = int(self.children[1].value) if self.children[1].value else 0
        except Exception:
            divinity_dice = 0
        try:
            enhancement = int(self.children[2].value)
        except Exception:
            enhancement = 0
        try:
            scale = int(self.children[3].value) if self.children[3].value else 0
        except Exception:
            scale = 0
        try:
            again = int(self.children[4].value) if self.children[4].value else 10
        except Exception:
            again = 10

        hero_type = roll_info.get("hero_type", "Hero")
        if hero_type not in {"Demigod", "God", "God Feat of Scale", "God Feat of Strength"}:
            divinity_dice = 0
        divinity_dice = max(0, min(divinity_dice, dice_pool))
        mortal_dice_pool = max(0, dice_pool - divinity_dice)
        roll_info.update({"dice_pool": dice_pool, "enhancement": enhancement, "again": again, "hero_type": hero_type, "scale": scale})
        data["roll_info"] = roll_info

        if hero_type in {"Origin", "Hero"}:
            tn = 8
        elif hero_type in {"Demigod", "God"}:
            tn = 7
        else:
            tn = 6
        scion = dice.ScionDice(
            dice_pool=mortal_dice_pool,
            enhancement=enhancement,
            hero_type=hero_type,
            scale=scale,
            difficulty=0,
            divinity_dice=divinity_dice,
            tn=tn,
            again=again,
        )
        results = scion.roll()
        divine_results = scion.roll_divinity()
        exploded = scion.check_explode(results)
        divine_exploded = scion.check_explode(divine_results)
        exploded.extend(divine_exploded)
        successes = scion.count_successes(results, divine_results, exploded)
        botch = scion.check_botch(results, exploded, successes)
        catastrophic_success = scion.check_catastrophic_success(divine_results) if divinity_dice > 0 else False
        mortal_failure = scion.check_mortal_fail(divine_results) if divinity_dice > 0 else False

        data["defense_roll"] = {
            "dice_pool": mortal_dice_pool,
            "total_dice_pool": dice_pool,
            "divinity_dice": divinity_dice,
            "enhancement": enhancement,
            "hero_type": hero_type,
            "scale": scale,
            "again": again,
            "results": results,
            "divine_results": divine_results,
            "exploded": exploded,
            "successes": successes,
            "generated_successes": successes,
            "botch": botch,
            "divinity": divinity_dice > 0,
            "catastrophic_success": catastrophic_success,
            "mortal_failure": mortal_failure,
        }
        data["stunt_choice"] = None
        data["defense_spent"] = None
        data["final_defense"] = 1
        data["dive_for_cover"] = False
        data["roll_away_selected"] = False
        data["cover_type"] = data.get("cover_type")
        data["cover_hard_armor"] = int(data.get("cover_hard_armor", 0) or 0)
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_reflexive_stunt")
        _queue_debug_log(
            interaction.client,
            "reflexive_roll_complete",
            self.state_id,
            f"successes={successes}; botch={botch}; divinity_dice={divinity_dice}",
        )

        await interaction.response.edit_message(embed=_get_state_embed(data, "Configure Reflexive Stunts"), view=ReflexiveStuntView(self.state_id))


class DefenseSpendModal(nextcord.ui.Modal):
    def __init__(self, state_id: str, max_successes: int):
        super().__init__("Defense Stunt")
        self.state_id = state_id
        self.max_successes = max_successes
        self.add_item(nextcord.ui.TextInput(label=f"Successes to spend on Defense (0-{max_successes})", required=True))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        try:
            spend = int(self.children[0].value)
        except Exception:
            await interaction.response.send_message("Invalid number", ephemeral=True)
            return
        if spend < 0 or spend > self.max_successes:
            await interaction.response.send_message(f"Enter a value between 0 and {self.max_successes}", ephemeral=True)
            return

        data["stunt_choice"] = "defense"
        data["defense_spent"] = spend
        data["final_defense"] = 1 + spend
        _write_state(self.state_id, data)
        _queue_debug_log(interaction.client, "stunt_defense_selected", self.state_id, f"spend={spend}")

        await interaction.response.edit_message(
            embed=_get_state_embed(data, "Configure Reflexive Stunts"),
            view=ReflexiveStuntView(self.state_id),
        )


class CoverTypeSelect(nextcord.ui.Select):
    def __init__(self, state_id: str):
        options = [
            nextcord.SelectOption(label="Expendable", value="expendable"),
            nextcord.SelectOption(label="Light", value="light"),
            nextcord.SelectOption(label="Heavy", value="heavy"),
            nextcord.SelectOption(label="Full", value="full"),
        ]
        super().__init__(
            placeholder="Choose cover type (for Dive for Cover)",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"cover_type_{state_id}",
        )
        self.state_id = state_id

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        cover_type = self.values[0]
        cover_values = {"expendable": 1, "light": 4, "heavy": 10, "full": 10}

        data["cover_type"] = cover_type
        data["cover_hard_armor"] = cover_values[cover_type]
        _write_state(self.state_id, data)
        _queue_debug_log(interaction.client, "cover_type_selected", self.state_id, f"cover={cover_type}")

        await interaction.response.edit_message(
            embed=_get_state_embed(data, "Configure Reflexive Stunts"),
            view=ReflexiveStuntView(self.state_id),
        )


class DiveCoverModal(nextcord.ui.Modal):
    def __init__(self, state_id: str, max_successes: int):
        super().__init__("Dive for Cover")
        self.state_id = state_id
        self.max_successes = max_successes
        self.add_item(nextcord.ui.TextInput(label="Cover type (expendable/light/heavy/full)", required=True))
        self.add_item(nextcord.ui.TextInput(label=f"Successes to keep after cover (0-{max_successes - 1})", required=True))
        self.add_item(nextcord.ui.TextInput(label="Cover damage already taken (optional)", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        if data.get("attack", {}).get("attack_type", "Melee") != "Ranged":
            await interaction.response.send_message("Dive for cover is only available against ranged attacks.", ephemeral=True)
            return

        try:
            cover_type = self.children[0].value.strip().lower()
            if cover_type not in {"expendable", "light", "heavy", "full"}:
                raise ValueError
        except Exception:
            await interaction.response.send_message("Enter a valid cover type: expendable, light, heavy, or full.", ephemeral=True)
            return

        try:
            keep = int(self.children[1].value)
        except Exception:
            await interaction.response.send_message("Invalid defense amount", ephemeral=True)
            return

        if keep < 0 or keep > self.max_successes - 1:
            await interaction.response.send_message(f"Enter a defense amount between 0 and {max(0, self.max_successes - 1)}", ephemeral=True)
            return

        try:
            damage_taken = int(self.children[2].value) if self.children[2].value else 0
        except Exception:
            damage_taken = 0

        cover_values = {"expendable": 1, "light": 4, "heavy": 10, "full": 10}
        data["stunt_choice"] = "dive_for_cover"
        data["defense_spent"] = keep
        data["final_defense"] = 1 + keep
        data["cover_type"] = cover_type
        data["cover_hard_armor"] = cover_values[cover_type]
        data["cover_damage_taken"] = damage_taken
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")
        _queue_debug_log(interaction.client, "stunt_dive_cover_selected", self.state_id, f"cover={cover_type}; keep={keep}; damage_taken={damage_taken}")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class RollAwayModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Roll Away")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Type YES to confirm Roll Away", required=True))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        if self.children[0].value.strip().lower() != "yes":
            await interaction.response.send_message("Roll Away cancelled.", ephemeral=True)
            return

        data["stunt_choice"] = "roll_away"
        data["defense_spent"] = 0
        data["final_defense"] = 1
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")
        _queue_debug_log(interaction.client, "stunt_roll_away_selected", self.state_id)

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class ArmorModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Armor Values")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Soft armor (int)", required=False))
        self.add_item(nextcord.ui.TextInput(label="Hard armor (int)", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        try:
            soft = int(self.children[0].value) if self.children[0].value else 0
        except Exception:
            soft = 0
        try:
            hard = int(self.children[1].value) if self.children[1].value else 0
        except Exception:
            hard = 0

        data["armor"] = {"soft": soft, "hard": hard}
        _write_state(self.state_id, data)
        _set_status(self.state_id, "ready_to_resolve")
        _queue_debug_log(interaction.client, "armor_set", self.state_id, f"soft={soft}; hard={hard}")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Ready to Resolve Attack"), view=ArmorResolveView(self.state_id))


class FullDefenseModal(nextcord.ui.Modal):
    def __init__(self, state_id: str):
        super().__init__("Full Defense Details")
        self.state_id = state_id
        self.add_item(nextcord.ui.TextInput(label="Defense value (int)", required=True))
        self.add_item(nextcord.ui.TextInput(label="Defensive stunts taken", required=False))
        self.add_item(nextcord.ui.TextInput(label="Cover damage taken (optional)", required=False))

    async def callback(self, interaction: Interaction):
        data = _read_state(self.state_id)
        try:
            defense_value = int(self.children[0].value)
        except Exception:
            await interaction.response.send_message("Invalid defense value", ephemeral=True)
            return
        stunts = self.children[1].value or ""
        try:
            cover_damage = int(self.children[2].value) if self.children[2].value else 0
        except Exception:
            cover_damage = 0

        data["context"] = "full_defense"
        data["manual_defense"] = defense_value
        data["final_defense"] = defense_value
        data["manual_stunts"] = stunts
        data["cover_damage_taken"] = cover_damage
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")
        _queue_debug_log(interaction.client, "full_defense_details_set", self.state_id, f"defense={defense_value}; cover_damage={cover_damage}")

        await interaction.response.edit_message(embed=_get_state_embed(data, "Set Armor and Resolve"), view=ArmorResolveView(self.state_id))


class ReflexiveConfigView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id
        self.add_item(HeroTypeSelect(state_id))
        self.add_item(ScaleSelect(state_id))

    @nextcord.ui.button(label="Enter Roll Info", style=nextcord.ButtonStyle.primary)
    async def enter_roll_info(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(ReflexiveRollModal(self.state_id))


class ReflexiveStuntView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id
        data = _read_state(state_id)
        attack_type = data.get("attack", {}).get("attack_type", "Melee")
        if attack_type != "Ranged":
            self.remove_item(self.dive_for_cover)
        else:
            self.add_item(CoverTypeSelect(state_id))

    @nextcord.ui.button(label="Defense", style=nextcord.ButtonStyle.primary)
    async def defense(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        successes = data.get("defense_roll", {}).get("successes", 0)
        await interaction.response.send_modal(DefenseSpendModal(self.state_id, successes))

    @nextcord.ui.button(label="Dive for Cover", style=nextcord.ButtonStyle.secondary)
    async def dive_for_cover(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        if data.get("attack", {}).get("attack_type", "Melee") != "Ranged":
            await interaction.response.send_message("Dive for cover is only available against ranged attacks.", ephemeral=True)
            return
        successes = int(data.get("defense_roll", {}).get("successes", 0) or 0)
        if successes < 1:
            await interaction.response.send_message("You need at least 1 defense success to use Dive for Cover.", ephemeral=True)
            return

        if data.get("dive_for_cover"):
            await interaction.response.send_message("Dive for Cover is already selected.", ephemeral=True)
            return

        data["dive_for_cover"] = True
        data["stunt_choice"] = "dive_for_cover"
        data["defense_roll"]["successes"] = max(0, successes - 1)

        current_spend = int(data.get("defense_spent", 0) or 0)
        if current_spend > data["defense_roll"]["successes"]:
            current_spend = data["defense_roll"]["successes"]
            data["defense_spent"] = current_spend

        data["final_defense"] = 1 + current_spend
        _write_state(self.state_id, data)
        _queue_debug_log(interaction.client, "stunt_dive_cover_selected", self.state_id, "cost_applied=1_success")
        await interaction.response.edit_message(
            embed=_get_state_embed(data, "Configure Reflexive Stunts"),
            view=ReflexiveStuntView(self.state_id),
        )

    @nextcord.ui.button(label="Roll Away", style=nextcord.ButtonStyle.secondary)
    async def roll_away(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        selected = bool(data.get("roll_away_selected", False))
        data["roll_away_selected"] = not selected
        if data["roll_away_selected"]:
            data["stunt_choice"] = "roll_away"
        _write_state(self.state_id, data)
        _queue_debug_log(interaction.client, "stunt_roll_away_toggled", self.state_id, f"enabled={not selected}")
        await interaction.response.edit_message(
            embed=_get_state_embed(data, "Configure Reflexive Stunts"),
            view=ReflexiveStuntView(self.state_id),
        )

    @nextcord.ui.button(label="Continue", style=nextcord.ButtonStyle.success)
    async def continue_to_armor(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        defense_spent = int(data.get("defense_spent", 0) or 0)
        data["final_defense"] = 1 + defense_spent

        if data.get("roll_away_selected"):
            data["stunt_choice"] = "roll_away"
        elif data.get("dive_for_cover"):
            data["stunt_choice"] = "dive_for_cover"
        elif defense_spent > 0:
            data["stunt_choice"] = "defense"
        else:
            data["stunt_choice"] = None

        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_armor_values")
        _queue_debug_log(interaction.client, "stunt_continue_to_armor", self.state_id)
        await interaction.response.edit_message(
            embed=_get_state_embed(data, "Set Armor and Finalize Defense"),
            view=ArmorResolveView(self.state_id),
        )


class FullDefenseView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Enter Full Defense Details", style=nextcord.ButtonStyle.primary)
    async def enter_full_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(FullDefenseModal(self.state_id))


class ArmorResolveView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Set Armor", style=nextcord.ButtonStyle.primary)
    async def set_armor(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(ArmorModal(self.state_id))

    @nextcord.ui.button(label="Finalize Defense", style=nextcord.ButtonStyle.success)
    async def finalize_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        if not data:
            await interaction.response.edit_message(
                content="Defense state was not found. Ask the GM to rerun the attack.",
                embed=None,
                view=None,
            )
            _queue_debug_log(interaction.client, "defense_finalize_missing_state", self.state_id)
            return

        if data.get("context") != "full_defense":
            defense_roll = data.get("defense_roll", {})
            generated_successes = int(defense_roll.get("generated_successes", defense_roll.get("successes", 0)) or 0)
            defense_spent = int(data.get("defense_spent", 0) or 0)
            dive_cost = 1 if data.get("dive_for_cover") else 0
            total_spent = defense_spent + dive_cost

            if total_spent > generated_successes:
                await interaction.response.edit_message(
                    content=(
                        "You have spent more successes than you rolled. "
                        f"Rolled: {generated_successes}, Spent: {total_spent}. "
                        "Please adjust your stunt selections and try again."
                    ),
                    embed=_get_state_embed(data, "Configure Reflexive Stunts"),
                    view=ReflexiveStuntView(self.state_id),
                )
                _queue_debug_log(
                    interaction.client,
                    "defense_finalize_blocked_spend_overflow",
                    self.state_id,
                    f"generated={generated_successes}; spent={total_spent}",
                )
                return

        _set_status(self.state_id, "defense_ready")
        data = _read_state(self.state_id)
        _queue_debug_log(interaction.client, "defense_finalized", self.state_id)

        # Notify the original game channel so the GM/attacker has the state id for resolution.
        attack = data.get("attack", {})
        channel_id = attack.get("channel_id")
        if channel_id:
            channel = interaction.client.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await interaction.client.fetch_channel(channel_id)
                except Exception:
                    channel = None

            if channel:
                antagonist_name = data.get("antagonist_name", "Unknown")
                character_name = data.get("character_name", "Unknown")
                await channel.send(
                    "\n".join(
                        [
                            f"Attack ID: {self.state_id}",
                            f"For {antagonist_name} on {character_name}",
                        ]
                    )
                )

        await interaction.response.edit_message(
            content="Defense saved. Attempting auto-resolve now.",
            embed=_get_state_embed(data, "Defense Ready"),
            view=None,
        )

        ok, message = await resolve_player_attack_state(interaction.client, interaction, self.state_id)
        _queue_debug_log(interaction.client, "defense_auto_resolve_result", self.state_id, f"ok={ok}; message={message}")
        if ok:
            await interaction.followup.send("Auto-resolve completed and posted to the game channel.", ephemeral=True)
        else:
            await interaction.followup.send(
                f"Auto-resolve could not complete: {message} Use /attack_player_resolve with this attack ID: {self.state_id}",
                ephemeral=True,
            )


class DefenseChoiceView(nextcord.ui.View):
    def __init__(self, state_id: str):
        super().__init__(timeout=None)
        self.state_id = state_id

    @nextcord.ui.button(label="Reflexive Defense", style=nextcord.ButtonStyle.primary)
    async def reflexive_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        _set_status(self.state_id, "collecting_reflexive_info")
        _queue_debug_log(interaction.client, "defense_choice_reflexive", self.state_id)
        await interaction.response.edit_message(embed=_get_state_embed(_read_state(self.state_id), "Reflexive Defense Setup"), view=ReflexiveConfigView(self.state_id))

    @nextcord.ui.button(label="Full Defense", style=nextcord.ButtonStyle.secondary)
    async def full_defense(self, button: nextcord.ui.Button, interaction: Interaction):
        data = _read_state(self.state_id)
        data["context"] = "full_defense"
        _write_state(self.state_id, data)
        _set_status(self.state_id, "collecting_full_defense")
        _queue_debug_log(interaction.client, "defense_choice_full", self.state_id)
        await interaction.response.edit_message(embed=_get_state_embed(data, "Full Defense Setup"), view=FullDefenseView(self.state_id))


async def start_defense(
    interaction: Interaction,
    antagonist_name: str,
    character_name: str,
    player: nextcord.Member,
    attack_params: dict,
    attack_type: str,
    attack_cost: int,
):
    _queue_debug_log(
        interaction.client,
        "start_defense_begin",
        None,
        f"attacker={interaction.user.name}; target={player.display_name}; attack_type={attack_type}; attack_cost={attack_cost}",
    )

    attack_params["attack_type"] = attack_type

    state_id = str(uuid.uuid4())
    data = {
        "attacker": interaction.user.name,
        "antagonist_name": antagonist_name,
        "character_name": character_name,
        "player_id": player.id,
        "status": "awaiting_defense_choice",
        "context": None,
        "attack": {
            "attack_params": attack_params,
            "attack_type": attack_type,
            "attack_cost": attack_cost,
            "channel_id": interaction.channel.id if interaction.channel else None,
        },
    }
    _write_state(state_id, data)
    _queue_debug_log(interaction.client, "state_created", state_id)

    embed = nextcord.Embed(title="Defensive Reaction", color=0x1a1aff)
    embed.add_field(name="Attacker", value=interaction.user.name, inline=True)
    embed.add_field(name="Target", value=character_name, inline=True)
    embed.add_field(name="Attack Type", value=attack_type, inline=True)
    embed.add_field(name="Roll Away Cost", value=str(attack_cost), inline=True)
    embed.add_field(name="Instructions", value="Choose Reflexive Defense or Full Defense to begin.", inline=False)

    view = DefenseChoiceView(state_id)

    # Defer the interaction response to avoid Discord "interaction failed" timeout
    try:
        await interaction.response.defer(ephemeral=True)
        deferred = True
        _queue_debug_log(interaction.client, "interaction_deferred", state_id)
    except Exception:
        deferred = False
        _queue_debug_log(interaction.client, "interaction_defer_failed", state_id, traceback.format_exc())

    # Try to DM the player. If that fails (DMs closed), fall back to channel mention.
    sent_dm = False
    try:
        await player.send(embed=embed, view=view)
        sent_dm = True
        _queue_debug_log(interaction.client, "dm_sent", state_id, f"player_id={player.id}")
    except Exception:
        sent_dm = False
        _queue_debug_log(interaction.client, "dm_failed", state_id, traceback.format_exc())

    if sent_dm:
        msg = f"Sent defensive prompt to {player.display_name} via DM."
        if deferred:
            await interaction.followup.send(msg, ephemeral=True)
            _queue_debug_log(interaction.client, "followup_sent_dm_notice", state_id)
        else:
            try:
                await interaction.response.send_message(msg, ephemeral=True)
                _queue_debug_log(interaction.client, "response_sent_dm_notice", state_id)
            except Exception:
                _queue_debug_log(interaction.client, "response_failed_dm_notice", state_id, traceback.format_exc())
                pass
    else:
        # Fallback: post in the channel and mention the player
        channel = interaction.channel
        if channel is None and interaction.guild is not None:
            channel = interaction.guild.system_channel

        if channel:
            await channel.send(f"{player.mention}", embed=embed, view=view)
            msg = f"Could not DM {player.display_name}; posted prompt in channel."
            _queue_debug_log(interaction.client, "channel_fallback_posted", state_id, f"channel_id={channel.id}")
        else:
            msg = f"Could not deliver prompt to {player.display_name}."
            _queue_debug_log(interaction.client, "channel_fallback_missing", state_id)

        if deferred:
            await interaction.followup.send(msg, ephemeral=True)
            _queue_debug_log(interaction.client, "followup_sent_fallback_notice", state_id)
        else:
            try:
                await interaction.response.send_message(msg, ephemeral=True)
                _queue_debug_log(interaction.client, "response_sent_fallback_notice", state_id)
            except Exception:
                _queue_debug_log(interaction.client, "response_failed_fallback_notice", state_id, traceback.format_exc())
                pass

    return state_id
