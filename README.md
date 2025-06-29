# pop_file_parser

Компилятор и редактор файлов формата .pop для Team Fortress 2 Mann vs Machine.

## Возможности

### Основные функции

- Чтение и парсинг .pop файлов Valve-формата (оригинальный синтаксис TF2)
- Валидация структуры, синтаксиса и специфичных для TF2 параметров
- Полная поддержка танков (Tank) с настройкой параметров и вывода событий
- Поддержка Mission параметров (Advanced, CanBotsAttackWhileInSpawnRoom и др.)
- Правильное форматирование булевых значений (Yes/No вместо True/False)
- Редактирование параметров роботов, волн, спавнов, атрибутов, предметов
- Создание новых миссий и шаблонов (templates)
- Экспорт в валидный .pop формат с обязательными кавычками для всех строк

### Поддерживаемые параметры

#### Параметры миссии
- StartingCurrency - начальная валюта
- RespawnWaveTime - время возрождения
- FixedRespawnWaveTime - фиксированное время возрождения (Yes/No)
- Advanced - продвинутый режим (1/0)
- CanBotsAttackWhileInSpawnRoom - могут ли боты атаковать в спавне (Yes/No)
- AddSentryBusterWhenDamageDealtExceeds - порог урона для спавна Sentry Buster
- AddSentryBusterWhenKillCountExceeds - порог убийств для спавна Sentry Buster

#### Параметры танка
- Name - имя танка
- Health - здоровье
- Speed - скорость
- Skin - скин (0-2)
- StartingPathTrackNode - начальная точка пути
- OnKilledOutput - действие при уничтожении
- OnBombDroppedOutput - действие при сбросе бомбы

#### Параметры волны
- WaitWhenDone - задержка после завершения
- Checkpoint - точка сохранения (Yes/No)
- StartWaveOutput - действие при старте волны
- DoneOutput - действие при завершении
- InitWaveOutput - действие при инициализации

#### Параметры спавна
- TotalCount - общее количество
- MaxActive - максимум активных
- SpawnCount - количество за спавн
- WaitBeforeStarting - задержка перед стартом
- WaitBetweenSpawns - задержка между спавнами
- Where - точка спавна
- TotalCurrency - валюта за волну
- Support - поддержка (Yes/No)
- RandomSpawn - случайный спавн (Yes/No)
- WaitForAllSpawned - ждать спавна всех
- WaitForAllDead - ждать смерти всех

## Новые возможности

#### Поддержка миссий (Mission)
- Создание миссий поддержки (Spy, Sniper, SentryBuster и др.)
- Настройка временных параметров (BeginAtWave, RunForThisManyWaves, CooldownTime)
- Управление количеством (DesiredCount, MaxActive)
- Поддержка комментариев к миссиям

Пример:
```python
from pop_file_parser import PopFileCompiler, Mission, TFBot

compiler = PopFileCompiler()

# Создаем миссию Spy
spy_bot = TFBot(
    name="Spy",
    class_name="Spy"
)

spy_mission = Mission(
    objective="Spy",
    where="spawnbot",
    begin_at_wave=2,
    run_for_waves=3,
    cooldown_time=30,
    initial_cooldown=15,
    desired_count=2,
    tf_bot=spy_bot
)

spy_mission.add_comments("Шпионы начинают появляться со второй волны")
compiler.add_mission(spy_mission)
```

#### Поддержка шаблонов (Templates)
- Создание именованных шаблонов роботов
- Переиспользование шаблонов в разных местах
- Поддержка комментариев к шаблонам
- Удобный доступ через менеджер шаблонов

Пример:
```python
# Создаем шаблон тяжелого робота
heavy_bot = TFBot(
    name="Giant Heavy",
    class_name="HeavyWeapons",
    health=5000,
    scale=1.8,
    attributes=["MiniBoss"]
)

# Добавляем шаблон
compiler.add_template("GiantHeavy", heavy_bot, "Шаблон гигантского пулеметчика")

# Используем шаблон в волне
template = compiler.get_template("GiantHeavy")
if template:
    wave.add_bot(template.bot)
```

#### Checkpoint и Output блоки
- Поддержка точек сохранения (Checkpoint)
- StartWaveOutput - действия при старте волны
- InitWaveOutput - действия при инициализации
- DoneOutput - действия при завершении

Пример:
```python
wave = Wave()
wave.checkpoint = True  # Добавляем точку сохранения
wave.start_wave_output = {
    "Target": "wave_start_relay",
    "Action": "Trigger"
}
wave.done_output = {
    "Target": "wave_finished_relay",
    "Action": "Trigger"
}

compiler.add_wave(wave)
```

#### Комментарии к блокам
Поддержка комментариев для Wave, WaveSpawn, Mission, Template:

```python
wave = Wave()
wave.add_comments("Финальная волна с танком и гигантами")

spawn = WaveSpawn()
spawn.add_comments("Спавн танка с поддержкой")

mission = Mission(...)
mission.add_comments("Снайперы для усложнения")

template = Template(...)
template.add_comments("Базовый шаблон для инженеров")
```

## Установка

```bash
pip install pop-file-reader
```

## Использование

```python
from pop_file_parser import PopFileCompiler, Tank, Wave, Squad, Robot

# Создаем новую миссию
compiler = PopFileCompiler()

# Добавляем параметры миссии
compiler.add_global_settings({
    "StartingCurrency": 400,
    "RespawnWaveTime": 6,
    "CanBotsAttackWhileInSpawnRoom": "No",
    "FixedRespawnWaveTime": "Yes"
})

# Создаем волну с танком
wave = Wave(
    wave_spawns=[
        Squad(
            name="Tank Squad",
            total_count=1,
            max_active=1,
            spawn_count=1,
            where="tankpath",
            total_currency=100,
            squad=[
                Tank(
                    name="Tank",
                    health=20000,
                    speed=75,
                    starting_path_track_node="tank_path_1",
                    on_killed_output={
                        "Target": "tank_killed_relay",
                        "Action": "Trigger"
                    }
                )
            ]
        )
    ]
)

# Добавляем волну
compiler.add_wave(wave)

# Экспортируем в файл
compiler.export_to_file("mission.pop")
```

## Документация API

См. документацию в коде для полного описания всех классов и методов.

## Лицензия

MIT
