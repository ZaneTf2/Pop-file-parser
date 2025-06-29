"""
Пример создания экспертной MvM миссии с использованием pop_file_reader.
Демонстрирует создание сложных волн с уникальными механиками и все возможности парсера.

Особенности:
- Разнообразные типы роботов с уникальными способностями
- Сложные волны с интересными комбинациями и тактиками
- Продвинутые механики: uber-chains, boss-fight, special-squads
- Чистый, хорошо документированный и расширяемый код
- Полная поддержка всех параметров из формата Valve

Поддерживаемые параметры TFBot:
- ClassIcon: кастомные иконки для ботов
- MaxVisionRange: ограничение дальности видимости
- WeaponRestrictions: ограничения на использование оружия
- Action: специальные действия ботов
- TeleportWhere: точки телепортации
- UseCustomModel: кастомные модели
- Scale: масштаб модели
- Attributes/CharacterAttributes: все стандартные атрибуты

Поддерживаемые параметры WaveSpawn:
- WaitBeforeStarting: задержка перед началом спавна
- RandomSpawn: случайный выбор точки спавна
- Support: бесконечный спавн поддержки
- StartWaveOutput/DoneOutput: триггеры с Target/Action/Param
- WaitForAllSpawned/WaitForAllDead: последовательный спавн

Поддерживаемые корневые параметры:
- StartingCurrency: начальная валюта
- RobotLimit: лимит роботов
- AllowBotExtraSlots: дополнительные слоты
- RespawnWaveTime: время респавна
- FixedRespawnWaveTime: фиксированное время
- CanBotsAttackWhileInSpawnRoom: атака из спавна

Миссия требует от игроков:
- Эффективной командной работы
- Грамотного распределения ресурсов
- Умения противостоять различным тактикам противника
- Способности справляться с несколькими угрозами одновременно
"""
from pathlib import Path
from typing import Dict, List

from pop_file_parser.compiler import PopFileCompiler
from pop_file_parser.models.wave import Wave
from pop_file_parser.models.wave_spawn import WaveSpawn
from pop_file_parser.models.tf_bot import TFBot
from pop_file_parser.models.tank import Tank
from pop_file_parser.models.mission import Mission
from pop_file_parser.models.output_block import OutputBlock

class MvMRobotBuilder:
    """Вспомогательный класс для создания предустановленных роботов."""
    
    @staticmethod
    def create_dragon_pyro() -> TFBot:
        """Создает Pyro с Dragon's Fury и усиленным огнем."""
        bot = TFBot()
        bot.name = "Dragon Pyro"
        bot.class_name = "Pyro"
        bot.skill = "Expert"
        bot.items = ["The Dragon's Fury", "The Burning Bandana"]
        bot.character_attributes = {
            "damage bonus": 1.25,
            "fire rate bonus": 0.8,
            "weapon burn time increased": 1.5
        }
        return bot
        
    @staticmethod
    def create_crits_demo() -> TFBot:
        """Создает Demo с гарантированными критами."""
        bot = TFBot()
        bot.name = "Crit Demo"
        bot.class_name = "Demoman"
        bot.skill = "Expert"
        bot.items = ["The Loch-n-Load"]
        bot.attributes = ["AlwaysCrit"]
        bot.character_attributes = {
            "faster reload rate": 0.8,
            "projectile speed increased": 1.2
        }
        return bot
        
    @staticmethod
    def create_kritzkrieg_medic() -> TFBot:
        """Создает Medic с Kritzkrieg."""
        bot = TFBot()
        bot.name = "Kritzkrieg Medic"
        bot.class_name = "Medic"
        bot.skill = "Expert"
        bot.items = ["The Kritzkrieg"]
        bot.attributes = ["SpawnWithFullCharge"]
        bot.character_attributes = {
            "heal rate bonus": 1.5,
            "uber duration bonus": 2
        }
        return bot

    @staticmethod
    def create_giant_boss_demo() -> TFBot:
        """Создает гигантского Demo-босса."""
        bot = TFBot()
        bot.name = "Giant Demoman Boss"
        bot.class_name = "Demoman"
        bot.health = 7500
        bot.skill = "Expert"
        bot.attributes = ["MiniBoss", "UseBossHealthBar", "HoldFireUntilFullReload"]
        bot.items = ["The Iron Bomber", "The Chargin' Targe"]
        bot.character_attributes = {
            "move speed bonus": 0.5,
            "damage bonus": 2.0,
            "faster reload rate": 0.6,
            "projectile spread angle penalty": 1,
            "charge recharge rate increased": 7,
            "charge impact damage increased": 1.5,
            "override footstep sound set": 4
        }
        return bot

    @staticmethod
    def create_crit_soldier_squad() -> List[TFBot]:
        """Создает отряд из Soldier с критами и Medic с kritzkrieg."""
        # Главный солдат
        soldier = TFBot()
        soldier.name = "Giant Crit Soldier"
        soldier.class_name = "Soldier"
        soldier.health = 4000
        soldier.skill = "Expert"
        soldier.attributes = ["MiniBoss", "HoldFireUntilFullReload", "AlwaysCrit"]
        soldier.items = ["The Original"]
        soldier.character_attributes = {
            "move speed bonus": 0.5,
            "faster reload rate": 0.6,
            "Projectile speed increased": 1.3,
            "override footstep sound set": 3
        }

        # Medic с криц-пушкой
        medic = TFBot()
        medic.name = "Kritzkrieg Medic"
        medic.class_name = "Medic"
        medic.skill = "Expert"
        medic.items = ["The Kritzkrieg"]
        medic.attributes = ["SpawnWithFullCharge"]
        medic.character_attributes = {
            "heal rate bonus": 1.5,
            "uber duration bonus": 2
        }

        return [soldier, medic]

    @staticmethod
    def create_tank(health: int = 25000, speed: int = 75) -> Tank:
        """
        Создает танк с заданными параметрами.
        
        Args:
            health: Здоровье танка
            speed: Скорость движения
        """
        tank = Tank()
        tank.name = "tankboss"
        tank.health = health
        tank.speed = speed
        return tank

    @staticmethod
    def create_sniper_bot() -> TFBot:
        """Создает снайпера с ограниченной дальностью видимости."""
        bot = TFBot()
        bot.name = "Limited Range Sniper"
        bot.class_name = "Sniper"
        bot.skill = "Expert"
        bot.class_icon = "sniper_bow"  # Новое поле ClassIcon
        bot.max_vision_range = 2000  # Новое поле MaxVisionRange
        bot.items = ["The Huntsman", "The Anger"]
        bot.character_attributes = {
            "damage bonus": 1.25
        }
        return bot

    @staticmethod
    def create_melee_heavy() -> TFBot:
        """Создает Heavy с ограничением на ближний бой."""
        bot = TFBot()
        bot.name = "Boxing Heavy"
        bot.class_name = "HeavyWeapons"
        bot.skill = "Expert"
        bot.class_icon = "heavy_fists"  # Новое поле ClassIcon
        bot.weapon_restrictions = "MeleeOnly"  # Новое поле WeaponRestrictions
        bot.items = ["The Killing Gloves of Boxing"]
        bot.action = "Mobber"  # Новое поле Action
        bot.character_attributes = {
            "move speed bonus": 1.3,
            "damage bonus": 1.5
        }
        return bot

    @staticmethod
    def create_teleporting_spy() -> TFBot:
        """Создает шпиона с телепортацией."""
        bot = TFBot()
        bot.name = "Teleporting Spy"
        bot.class_name = "Spy"
        bot.skill = "Expert"
        bot.class_icon = "spy_kunai"  # Новое поле ClassIcon
        bot.teleport_where = "spawnbot_flankers"  # Новое поле TeleportWhere
        bot.use_custom_model = "spy.mdl"  # Новое поле UseCustomModel
        bot.scale = 1.2  # Поле Scale
        bot.items = ["Conniver's Kunai"]
        bot.weapon_restrictions = "MeleeOnly"
        
        return bot

def create_wave_one(currency: int = 600) -> Wave:
    """
    Создает первую волну с демонстрацией новых возможностей WaveSpawn:
    - WaitBeforeStarting: задержка спавна
    - RandomSpawn: случайные точки появления
    - Улучшенные Output блоки
    - Последовательный спавн через WaitForAllSpawned
    
    Args:
        currency: Количество денег за волну
    """
    wave = Wave()
    wave.add_comment("Демонстрация новых возможностей WaveSpawn")
    wave.checkpoint = True
    
    # Scout Rush с новыми параметрами
    scouts = WaveSpawn()
    scouts.add_comment("Быстрые скауты с рандомным спавном")
    scouts.name = "Scout Rush"
    scouts.where = "spawnbot"
    scouts.total_count = 24
    scouts.max_active = 8
    scouts.spawn_count = 4
    scouts.total_currency = currency // 3
    scouts.wait_before_starting = 5  # Новый параметр
    scouts.random_spawn = True  # Новый параметр
    
    scout = TFBot()
    scout.class_name = "Scout"
    scout.skill = "Hard"
    scout.items = ["Force-A-Nature", "Pretty Boy's Pocket Pistol"]
    scout.item_attributes = {
        "ItemName": "Force-A-Nature",
        "damage bonus": 1.2,
        "faster reload rate": 0.85
    }
    scouts.squad.append(scout)
    wave.wave_spawns.append(scouts)
    
    # Dragon Pyros
    pyros = WaveSpawn()
    pyros.add_comment("Dragon Squad - элитные пиро с усиленным огнём")
    pyros.name = "Dragon Squad"
    pyros.where = "spawnbot"
    pyros.total_count = 15
    pyros.max_active = 5
    pyros.spawn_count = 3
    pyros.total_currency = currency // 3
    pyros.wait_for_all_spawned = "Scout Rush"
    
    pyros.squad.append(MvMRobotBuilder.create_dragon_pyro())
    wave.wave_spawns.append(pyros)
    
    # Support Soldiers
    soldiers = WaveSpawn()
    soldiers.name = "Buff Support"
    soldiers.where = "spawnbot"
    soldiers.total_count = 12
    soldiers.max_active = 4
    soldiers.spawn_count = 2
    soldiers.total_currency = currency // 3
    soldiers.support = True
    
    soldiers.squad.append(MvMRobotBuilder.create_crit_soldier_squad())
    wave.wave_spawns.append(soldiers)
    
    return wave

def create_wave_two(currency: int = 800) -> Wave:
    """
    Создает вторую волну с демонстрацией всех новых возможностей TFBot.
    
    Особенности Squad-блоков:
    1. Sniper Squad:
        * ClassIcon: кастомные иконки для снайперов
        * MaxVisionRange: ограничение дальности обзора
        * WeaponRestrictions: только определенное оружие
    
    2. Melee Squad:
        * Action: специальное поведение ботов (Mobber)
        * ClassIcon: кастомные иконки для мили ботов
        * WeaponRestrictions: только ближний бой
    
    3. Spy Squad:
        * TeleportWhere: телепортация в особые точки
        * UseCustomModel: кастомные модели
        * Scale: измененный размер модели
    
    4. Boss Squad:
        * Все стандартные атрибуты и новые возможности
        * Улучшенные Output блоки с параметрами
        * Продвинутая логика появления
    
    Args:
        currency: Количество денег за волну
    """
    wave = Wave()
    wave.add_comment("Демонстрация всех новых возможностей TFBot")

    # Sniper Squad с MaxVisionRange
    sniper_spawn = WaveSpawn()
    sniper_spawn.name = "Sniper Squad"
    sniper_spawn.where = "spawnbot_mission_sniper"
    sniper_spawn.total_count = 3
    sniper_spawn.max_active = 3
    sniper_spawn.spawn_count = 3
    sniper_spawn.total_currency = currency // 4
    sniper_spawn.wait_before_starting = 0
    sniper_spawn.squad.append(MvMRobotBuilder.create_sniper_bot())

    # Melee Squad с Action и WeaponRestrictions
    melee_spawn = WaveSpawn()
    melee_spawn.name = "Melee Squad"
    melee_spawn.where = "spawnbot"
    melee_spawn.total_count = 12
    melee_spawn.max_active = 4
    melee_spawn.spawn_count = 4
    melee_spawn.total_currency = currency // 4
    melee_spawn.wait_before_starting = 10
    melee_spawn.random_spawn = True
    melee_spawn.squad.append(MvMRobotBuilder.create_melee_heavy())

    # Spy Squad с TeleportWhere и UseCustomModel
    spy_spawn = WaveSpawn()
    spy_spawn.name = "Spy Squad"
    spy_spawn.where = "spawnbot_mission_spy"
    spy_spawn.total_count = 6
    spy_spawn.max_active = 2
    spy_spawn.spawn_count = 2
    spy_spawn.total_currency = currency // 4
    spy_spawn.wait_for_all_dead = "Melee Squad"
    spy_spawn.squad.append(MvMRobotBuilder.create_teleporting_spy())

    # Boss Squad с улучшенными атрибутами
    boss_spawn = WaveSpawn()
    boss_spawn.name = "Boss Squad"
    boss_spawn.where = "spawnbot"
    boss_spawn.total_count = 1
    boss_spawn.max_active = 1
    boss_spawn.spawn_count = 1
    boss_spawn.total_currency = currency // 4
    boss_spawn.wait_for_all_dead = "Spy Squad"
    
    # Создаем босса с использованием всех новых возможностей
    boss = TFBot()
    boss.name = "Ultimate Boss"
    boss.class_name = "HeavyWeapons"
    boss.health = 10000
    boss.skill = "Expert"
    boss.class_icon = "heavy_deflector_giant"
    boss.weapon_restrictions = "PrimaryOnly"
    boss.action = "Mobber"
    boss.scale = 1.8
    boss.items = ["Deflector", "The Team Captain"]
    boss.attributes = {"MiniBoss", "UseBossHealthBar", "AlwaysCrit"}
    boss.character_attributes = {
        "move speed bonus": 0.5,
        "damage bonus": 2.0,
        "override footstep sound set": 4
    }
    boss_spawn.squad.append(boss)

    # Добавляем все спавны в волну
    wave.wave_spawns.extend([
        sniper_spawn,
        melee_spawn,
        spy_spawn,
        boss_spawn
    ])
    
    return wave

def create_wave_three(currency: int = 1000) -> Wave:
    """
    Создает третью волну: Giant Demo Boss + Double Tank + Support.
    Тактика: Несколько серьезных угроз одновременно требуют разделения команды.
    
    Args:
        currency: Количество денег за волну
    """
    wave = Wave()
    
    # Giant Demo Boss
    boss_spawn = WaveSpawn()
    boss_spawn.name = "Demo Boss"
    boss_spawn.where = "spawnbot"
    boss_spawn.total_count = 1
    boss_spawn.total_currency = currency // 3
    
    boss_spawn.squad.append(MvMRobotBuilder.create_giant_boss_demo())
    wave.wave_spawns.append(boss_spawn)
    
    # Double Tank
    tank1_spawn = WaveSpawn()
    tank1_spawn.name = "Tank Alpha"
    tank1_spawn.where = "tankpath_1"
    tank1_spawn.total_count = 1
    tank1_spawn.total_currency = currency // 6
    tank1_spawn.squad.append(MvMRobotBuilder.create_tank(20000, 85))
    wave.wave_spawns.append(tank1_spawn)
    
    tank2_spawn = WaveSpawn()
    tank2_spawn.name = "Tank Beta"
    tank2_spawn.where = "tankpath_2"
    tank2_spawn.total_count = 1
    tank2_spawn.total_currency = currency // 6
    tank2_spawn.wait_for_all_spawned = "Tank Alpha"
    tank2_spawn.squad.append(MvMRobotBuilder.create_tank(20000, 85))
    wave.wave_spawns.append(tank2_spawn)
    
    # Support Mix
    support_spawn = WaveSpawn()
    support_spawn.name = "Mixed Support"
    support_spawn.where = "spawnbot"
    support_spawn.total_count = 20
    support_spawn.max_active = 6
    support_spawn.spawn_count = 3
    support_spawn.total_currency = currency // 3
    support_spawn.support = True
    
    # Добавляем смесь поддержки
    support_spawn.squad.extend([
        MvMRobotBuilder.create_dragon_pyro(),
        MvMRobotBuilder.create_crits_demo()
    ])
    wave.wave_spawns.append(support_spawn)
    
    return wave

def create_templates() -> Dict[str, TFBot]:
    """Создает набор пользовательских шаблонов роботов."""
    return {
        "T_TFBot_Medic_Shield": TFBot(
            name="Shield Medic",
            class_name="Medic",
            health=2000,
            skill="Expert",
            attributes={"ProjectileShield", "SpawnWithFullCharge"},
            character_attributes={
                "heal rate bonus": 2.0,
                "uber duration bonus": 2.0,
                "generate rage on heal": 2.0,
                "increase buff duration": 1.5
            },
            items=["The Quick-Fix"]
        ),
        "T_TFBot_Giant_Heavyweapons_Brass": TFBot(
            name="Giant Brass Heavy",
            class_name="HeavyWeapons",
            health=5000,
            skill="Expert",
            attributes={"MiniBoss"},
            character_attributes={
                "move speed bonus": 0.5,
                "damage bonus": 1.5,
                "fire rate bonus": 0.8,
                "projectile spread angle penalty": 1,
                "override footstep sound set": 4
            },
            items=["The Brass Beast", "The Team Captain"]
        )
    }

def create_mission() -> None:
    """
    Создает и сохраняет полную экспертную MvM миссию.
    
    Миссия состоит из трех сложных волн с уникальными механиками:
    1. Scout Rush + Dragon Pyros - быстрая атака и большой урон
    2. Tank + Crits Squad - разделение внимания и критический урон
    3. Giant Demo Boss + Double Tank - финальное испытание

    Support-миссии:
    - Sentry Buster: стандартный контроль турелей
    - Spy Support: 4 шпиона каждые 20 секунд после 3й волны
    - Sniper Support: 2 снайпера каждые 30 секунд на 4й волне
    """
    compiler = PopFileCompiler()
    
    # Добавляем базовые файлы с роботами
    compiler.base_files = [
        "robot_giant.pop",
        "robot_standard.pop",
        "robot_gatebot.pop"
    ]

    # Добавляем поддержку - Sentry Buster
    compiler.add_mission(Mission(
        objective="DestroySentries",
        initial_cooldown=30,
        where="spawnbot_mission_sentrybuster",
        begin_at_wave=1,
        run_for_waves=3,
        cooldown_time=30,
        tf_bot=TFBot(template="T_TFBot_SentryBuster")
    ))

    # Поддержка - Spy после 3й волны
    compiler.add_mission(Mission(
        objective="Spy",
        initial_cooldown=20,
        where="spawnbot_mission_spy",
        begin_at_wave=3,
        run_for_waves=1,
        cooldown_time=20,
        desired_count=4,
        tf_bot=TFBot(class_name="Spy", skill="Expert")
    ))

    # Поддержка - Sniper на 4й волне
    compiler.add_mission(Mission(
        objective="Sniper",
        initial_cooldown=30,
        where="spawnbot_mission_sniper",
        begin_at_wave=4,
        run_for_waves=1,
        cooldown_time=30,
        desired_count=2,
        tf_bot=TFBot(class_name="Sniper", skill="Expert", name="Elite Sniper", items=["The Hitman's Heatmaker"])
    ))
    
    # Детальные настройки миссии с демонстрацией всех новых параметров
    mission_settings = {
        # Основные параметры
        "StartingCurrency": 1200,  # Начальная валюта
        "RobotLimit": 45,  # Увеличенный лимит роботов
        "AllowBotExtraSlots": True,  # Разрешаем дополнительные слоты
        "RespawnWaveTime": 3,  # Уменьшенное время респавна
        "FixedRespawnWaveTime": True,  # Фиксированное время респавна
        "CanBotsAttackWhileInSpawnRoom": False,  # Запрет атаки из спавна
        
        # Стандартные параметры
        "AddSentryBusterWhenDamageDealtExceeds": 3000,
        "Advanced": 1
    }
    compiler.add_global_settings(mission_settings)
    
    # Создаем волны с демонстрацией различных возможностей
    
    # Волна 1: Демонстрация новых параметров WaveSpawn
    wave_one = create_wave_one(600)
    wave_one.checkpoint = True  # Сохранение после первой волны
    # Демонстрация улучшенного Output блока с Target/Action
    wave_one.start_wave_output = OutputBlock(
        name="StartWaveOutput",
        target="wave_start_relay",
        action="Trigger"
    )
    wave_one.done_output = OutputBlock(
        name="DoneOutput",
        target="wave_finished_relay",
        action="Trigger"
    )
    
    # Основной output
    wave_one.add_custom_output(
        name="WaveInitOutput",
        target="wave_init_relay",
        action="Trigger"
    )

    # Parameters как отдельный блок
    wave_one.add_custom_output(
        name="Parameters",
        custom_settings="""
        delay 1.0
        repeat 3
        """
    )
    
    compiler.add_wave(wave_one)

    wave_two = create_wave_two(800)
    wave_two.checkpoint = True  # Сохранение после второй волны
    wave_two.start_wave_output = OutputBlock(
        name="StartWaveOutput",
        target="wave_start_relay",
        action="Trigger"
    )
    wave_two.done_output = OutputBlock(
        name="DoneOutput",
        target="wave_finished_relay",
        action="Trigger"
    )
    wave_two.init_wave_output = OutputBlock(  # Особая инициализация второй волны
        name="InitWaveOutput",
        target="second_wave_init_relay",
        action="Trigger"
    )
    compiler.add_wave(wave_two)

    wave_three = create_wave_three(1000)
    wave_three.checkpoint = True  # Сохранение после финальной волны
    wave_three.start_wave_output = OutputBlock(
        name="StartWaveOutput",
        target="wave_start_relay",
        action="Trigger"
    )
    wave_three.done_output = OutputBlock(
        name="DoneOutput",
        target="mission_finished_relay",  # Особое событие для финальной волны
        action="Trigger"
    )
    compiler.add_wave(wave_three)
    
    # Сохраняем миссию в файл
    output_path = Path("expert_mission.pop")
    compiler.export_to_file(output_path)
    print(f"Expert mission successfully exported to {output_path.absolute()}")

if __name__ == "__main__":
    create_mission()
