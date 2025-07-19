# pop_file_parser

A compiler and editor for Team Fortress 2 Mann vs Machine .pop files.

## Features

### Core Features

- Reading and parsing Valve-format .pop files (original TF2 syntax)
- Validation of structure, syntax and TF2-specific parameters
- Full tank support with parameter configuration and event output
- Mission parameter support (Advanced, CanBotsAttackWhileInSpawnRoom etc.)
- Proper boolean value formatting (Yes/No instead of True/False)
- Edit robot parameters, waves, spawns, attributes, items
- Create new missions and templates
- Export to valid .pop format with mandatory quotes for all strings

### Supported Parameters

#### Mission Parameters
- StartingCurrency - initial currency
- RespawnWaveTime - respawn time
- FixedRespawnWaveTime - fixed respawn time (Yes/No)
- Advanced - advanced mode (1/0)
- CanBotsAttackWhileInSpawnRoom - can bots attack in spawn room (Yes/No)
- AddSentryBusterWhenDamageDealtExceeds - damage threshold for Sentry Buster spawn
- AddSentryBusterWhenKillCountExceeds - kill count threshold for Sentry Buster spawn

#### Tank Parameters
- Name - tank name
- Health - health points
- Speed - movement speed
- Skin - skin type (0-2)
- StartingPathTrackNode - initial path node
- OnKilledOutput - action on destruction
- OnBombDroppedOutput - action on bomb drop

#### Wave Parameters
- WaitWhenDone - delay after completion
- Checkpoint - save point (Yes/No)
- StartWaveOutput - action on wave start
- DoneOutput - action on completion
- InitWaveOutput - action on initialization

#### Spawn Parameters
- TotalCount - total count
- MaxActive - maximum active
- SpawnCount - count per spawn
- WaitBeforeStarting - delay before start
- WaitBetweenSpawns - delay between spawns
- Where - spawn point
- TotalCurrency - currency per wave
- Support - support enabled (Yes/No)
- RandomSpawn - random spawn (Yes/No)
- WaitForAllSpawned - wait for all spawned
- WaitForAllDead - wait for all dead

## New Features

#### Mission Support
- Create support missions (Spy, Sniper, SentryBuster etc.)
- Configure timing parameters (BeginAtWave, RunForThisManyWaves, CooldownTime)
- Control quantities (DesiredCount, MaxActive)
- Support for mission comments

Example:
```python
from pop_file_parser import PopFileCompiler, Mission, TFBot

compiler = PopFileCompiler()

# Create Spy mission
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

spy_mission.add_comments("Spies start appearing from wave 2")
compiler.add_mission(spy_mission)
```

#### Template Support
- Create named robot templates
- Reuse templates across different places
- Support for template comments
- Easy access through template manager

Example:
```python
# Create heavy robot template
heavy_bot = TFBot(
    name="Giant Heavy",
    class_name="HeavyWeapons",
    health=5000,
    scale=1.8,
    attributes=["MiniBoss"]
)

# Add template
compiler.add_template("GiantHeavy", heavy_bot, "Giant Heavy template")

# Use template in wave
template = compiler.get_template("GiantHeavy")
if template:
    wave.add_bot(template.bot)
```

#### Checkpoint and Output Blocks
- Support for save points (Checkpoint)
- StartWaveOutput - actions on wave start
- InitWaveOutput - actions on initialization
- DoneOutput - actions on completion

Example:
```python
wave = Wave()
wave.checkpoint = True  # Add save point
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

#### Block Comments
Support for comments in Wave, WaveSpawn, Mission, Template:

```python
wave = Wave()
wave.add_comments("Final wave with tank and giants")

spawn = WaveSpawn()
spawn.add_comments("Tank spawn with support")

mission = Mission(...)
mission.add_comments("Snipers for difficulty")

template = Template(...)
template.add_comments("Base template for engineers")
```

## Usage

```python
from pop_file_parser import PopFileCompiler, Tank, Wave, Squad, Robot

# Create new mission
compiler = PopFileCompiler()

# Add mission parameters
compiler.add_global_settings({
    "StartingCurrency": 400,
    "RespawnWaveTime": 6,
    "CanBotsAttackWhileInSpawnRoom": "No",
    "FixedRespawnWaveTime": "Yes"
})

# Create wave with tank
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

# Add wave
compiler.add_wave(wave)

# Export to file
compiler.export_to_file("mission.pop")
```

## API Documentation

See code documentation for full description of all classes and methods.

## License

MIT
