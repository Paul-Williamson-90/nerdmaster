from src.game.configs import DifficultyConfigs
from src.characters.base import Character
from src.characters.skills.skills import SkillMap
from src.triggers.base import TriggerResponse
from src.utils.rolls import normal_roll
from src.game.configs import DifficultyConfigs
from src.game.terms import NarrationType

from typing import Tuple

def combat(game, trigger_id: str, attacking: Character, defending: Character):
    dc, modifier, weapon_name = get_combat_modifiers_and_dc(attacking, defending)
    return combat_resolutions(game, trigger_id, attacking, defending, dc, modifier, weapon_name)

def combat_resolutions(
        game, 
        trigger_id: str, 
        attacking: Character, 
        defending: Character, 
        dc: int, 
        modifier: int, 
        weapon_name: str
    ):
    if normal_roll(dc, modifier):
        narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and hits!\n"
        narrative_message += defending.health.take_damage(narrative_message) # TODO: Implement this on health

        game.add_to_player_narrator(
            text=narrative_message,
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        game.add_to_npc_narrator(
            text=narrative_message,
            characters=[char.name for char in game.characters],
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        return TriggerResponse(
            log_message=f"Activated {trigger_id}: {narrative_message}",
        )
    else:
        narrative_message = f"{attacking.name} attacks {defending.name} with their {weapon_name} and misses!"
        
        game.add_to_player_narrator(
            text=narrative_message,
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )

        game.add_to_npc_narrator(
            text=narrative_message,
            characters=[char.name for char in game.characters],
            text_tag=NarrationType.stage.value,
            ai_generate=True,
        )
        
        return TriggerResponse(
            log_message=f"Activated {trigger_id}: {narrative_message}",
        )


def get_combat_modifiers_and_dc(
        attacking: Character, 
        defending: Character
)->Tuple[int, int, str]:
    skill, weapon_name, weapon_modifier = attacking.equipped_items.get_weapon_attack_stats()
    attack_disadvantage = attacking.health.get_roll_modifier()
    attack = attacking.skills.get_modifier(skill) + weapon_modifier - attack_disadvantage

    defending_coverage = False # TODO: Implement this from character attributes defending.coverage

    defense = defending.skills.get_modifier(SkillMap.DEXTERITY.name) + (1 if defending_coverage else 0)
    defense += defending.health.get_roll_modifier()

    dc = DifficultyConfigs.ATTACK_DC.value
    modifier = attack-defense
    return dc, modifier, weapon_name
