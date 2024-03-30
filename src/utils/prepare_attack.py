from src.game.configs import DifficultyConfigs
from src.characters.base import Character
from src.triggers.base import TriggerResponse
from src.utils.rolls import normal_roll
from src.game.configs import DifficultyConfigs
from src.game.game import Game, GameMode, Turn, NarrationType
from src.triggers.base import Trigger
from src.game.configs import DifficultyConfigs



def prepare_attack_action(
        game: Game, 
        trigger_id: str, 
        attacking: Character, 
        defending: Character, 
        attack_action: Trigger
    ):
    character_dex_mod = attacking.skills.get_modifier("DEXTERITY")
    _, weapon_name, _ = attacking.equipped_items.get_weapon_attack_stats()
    target_character_dex_mod = defending.skills.get_modifier("DEXTERITY")
    target_character_perc_mod = defending.skills.get_modifier("PERCEPTION")
    target_mod = max([target_character_dex_mod, target_character_perc_mod])
    dc = DifficultyConfigs.PREPARE_ATTACK_DC.value

    game.switch_game_mode(GameMode.COMBAT.value)

    if normal_roll(dc, character_dex_mod-target_mod):
        narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name}, {defending.name} is caught off guard!"

        game.add_to_player_narrator(
            text=narrative_message,
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        game.add_to_npc_narrator(
            text=narrative_message,
            text_tag=NarrationType.stage.value,
            characters=game.characters,
            ai_generate=True,
        )

        trigger = attack_action(character=attacking)
        trigger.prepare(character_to_attack=defending.name)

        return TriggerResponse(
            log_message=f"Trigger {trigger_id}: {attacking.name} attacks {defending.name}, {defending.name} is caught off guard!",
        )

    else:
        narrative_message = f"{defending.name} notices {attacking.name} is about to attack!"

        game.add_to_player_narrator(
            text=narrative_message,
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        game.add_to_npc_narrator(
            text=narrative_message,
            text_tag=NarrationType.stage.value,
            characters=game.characters,
            ai_generate=True,
        )

        if game.next_turn == Turn.GAME.value:
            game.next_turn = Turn.PLAYER.value
        else:
            game.next_turn = Turn.GAME.value

        return TriggerResponse(
            log_message=f"Trigger {trigger_id}: {defending.name} notices {attacking.name} is about to attack!",
        )