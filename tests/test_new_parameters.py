"""
Тесты для новых параметров в моделях MvM миссии.
"""
import pytest
from pop_file_reader.models.mission_info import MissionInfo
from pop_file_reader.models.mission import Mission
from pop_file_reader.models.tf_bot import TFBot
from pop_file_reader.models.wave_spawn import WaveSpawn

def test_tf_bot_new_fields():
    """Тест новых полей TFBot."""
    bot = TFBot(
        class_icon="sniper_bow",
        max_vision_range=800,
        weapon_restrictions="SecondaryOnly",
        action="Mobber",
        teleport_where="spawnbot",
        use_custom_model="models/player/demo.mdl"
    )
    
    valve_format = bot.to_valve_format()
    assert valve_format["ClassIcon"] == "sniper_bow"
    assert valve_format["MaxVisionRange"] == 800
    assert valve_format["WeaponRestrictions"] == "SecondaryOnly"
    assert valve_format["Action"] == "Mobber"
    assert valve_format["TeleportWhere"] == "spawnbot"
    assert valve_format["UseCustomModel"] == "models/player/demo.mdl"
    
    new_bot = TFBot.from_valve_format(valve_format)
    assert new_bot.class_icon == "sniper_bow"
    assert new_bot.max_vision_range == 800
    assert new_bot.weapon_restrictions == "SecondaryOnly"
    assert new_bot.action == "Mobber"
    assert new_bot.teleport_where == "spawnbot"
    assert new_bot.use_custom_model == "models/player/demo.mdl"

def test_wave_spawn_new_fields():
    """Тест новых полей WaveSpawn."""
    spawn = WaveSpawn(
        wait_before_starting=10,
        random_spawn=True,
        start_wave_output={
            "Target": "wave_start_relay",
            "Action": "Trigger",
            "Param": "Some param"
        }
    )
    
    valve_format = spawn.to_valve_format()
    assert valve_format["WaitBeforeStarting"] == 10
    assert valve_format["RandomSpawn"] == 1
    assert valve_format["StartWaveOutput"]["Target"] == "wave_start_relay"
    assert valve_format["StartWaveOutput"]["Action"] == "Trigger"
    assert valve_format["StartWaveOutput"]["Param"] == "Some param"
    
    new_spawn = WaveSpawn.from_valve_format(valve_format)
    assert new_spawn.wait_before_starting == 10
    assert new_spawn.random_spawn is True
    assert new_spawn.start_wave_output["Target"] == "wave_start_relay"

def test_mission_info():
    """Тест корневых параметров миссии."""
    info = MissionInfo(
        starting_currency=400,
        robot_limit=45,
        allow_bot_extra_slots=True,
        respawn_wave_time=3,
        fixed_respawn_wave_time=True,
        can_bots_attack_in_spawn=False
    )
    
    valve_format = info.to_valve_format()
    assert valve_format["RobotLimit"] == 45
    assert valve_format["AllowBotExtraSlots"] == 1
    assert valve_format["RespawnWaveTime"] == 3
    assert valve_format["FixedRespawnWaveTime"] == "Yes"
    assert valve_format["CanBotsAttackWhileInSpawnRoom"] == "no"
    
    new_info = MissionInfo.from_valve_format(valve_format)
    assert new_info.robot_limit == 45
    assert new_info.allow_bot_extra_slots is True
    assert new_info.respawn_wave_time == 3
    assert new_info.fixed_respawn_wave_time is True
    assert new_info.can_bots_attack_in_spawn is False
