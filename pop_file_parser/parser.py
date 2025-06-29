"""
Парсер для pop файлов.
"""
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from .lexer import Token, Lexer

@dataclass
class ASTNode:
    """Базовый класс для узлов AST."""
    pass

@dataclass
class Mission(ASTNode):
    """Узел миссии."""
    waves: List['Wave'] = field(default_factory=list)
    templates: Optional[Dict[str, 'Template']] = None
    starting_currency: int = 400
    respawn_wave_time: int = 6
    fixed_respawn_wave_time: bool = False
    advanced: bool = False
    can_bots_attack_while_in_spawn_room: bool = False
    add_sentry_buster_when_damage_dealt_exceeds: Optional[int] = None
    add_sentry_buster_when_kill_count_exceeds: Optional[int] = None
    mission_objectives: List[Dict[str, Any]] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует миссию в формат Valve."""
        result = {
            "StartingCurrency": str(self.starting_currency),
            "RespawnWaveTime": str(self.respawn_wave_time),
            "CanBotsAttackWhileInSpawnRoom": "Yes" if self.can_bots_attack_while_in_spawn_room else "No"
        }
        
        if self.fixed_respawn_wave_time:
            result["FixedRespawnWaveTime"] = "Yes"
            
        if self.advanced:
            result["Advanced"] = "1"
            
        if self.add_sentry_buster_when_damage_dealt_exceeds is not None:
            result["AddSentryBusterWhenDamageDealtExceeds"] = str(self.add_sentry_buster_when_damage_dealt_exceeds)
            
        if self.add_sentry_buster_when_kill_count_exceeds is not None:
            result["AddSentryBusterWhenKillCountExceeds"] = str(self.add_sentry_buster_when_kill_count_exceeds)
            
        if self.mission_objectives:
            result["Mission"] = self.mission_objectives
            
        if self.custom_attributes:
            result["CustomAttributes"] = self.custom_attributes
            
        # Добавляем волны
        for wave in self.waves:
            if "Wave" not in result:
                result["Wave"] = []
            result["Wave"].append(wave.to_valve_format())
            
        return result

    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'Mission':
        """Создает миссию из формата Valve."""
        return cls(
            waves=[Wave.from_valve_format(wave) for wave in data.get("Wave", [])],
            templates=data.get("Templates"),
            starting_currency=int(data.get("StartingCurrency", 400)),
            respawn_wave_time=int(data.get("RespawnWaveTime", 6)),
            fixed_respawn_wave_time=data.get("FixedRespawnWaveTime", "").lower() in ["yes", "true", "1"],
            advanced=data.get("Advanced") == "1",
            can_bots_attack_while_in_spawn_room=data.get("CanBotsAttackWhileInSpawnRoom", "").lower() in ["yes", "true", "1"],
            add_sentry_buster_when_damage_dealt_exceeds=int(data["AddSentryBusterWhenDamageDealtExceeds"]) if "AddSentryBusterWhenDamageDealtExceeds" in data else None,
            add_sentry_buster_when_kill_count_exceeds=int(data["AddSentryBusterWhenKillCountExceeds"]) if "AddSentryBusterWhenKillCountExceeds" in data else None,
            mission_objectives=data.get("Mission", []),
            custom_attributes=data.get("CustomAttributes", {})
        )
        
@dataclass
class Wave(ASTNode):
    """Узел волны."""
    wave_spawns: List['WaveSpawn']
    tanks: List['Tank']
    description: Optional[str] = None
    total_count: Optional[int] = None
    total_currency: Optional[int] = None
    wait_for_all_spawned: Optional[str] = None
    wait_for_all_dead: Optional[str] = None
    start_output: Optional[Dict[str, str]] = None
    done_output: Optional[Dict[str, str]] = None

@dataclass
class Robot(ASTNode):
    """Узел робота."""
    name: str
    class_name: str
    attributes: Dict[str, Any]

@dataclass
class Template(ASTNode):
    """Узел шаблона."""
    name: str
    base: Optional[str]
    attributes: Dict[str, Any]

@dataclass
class WaveSpawn(ASTNode):
    """Узел спавна волны."""
    name: Optional[str] = None
    total_count: Optional[int] = None
    max_active: Optional[int] = None
    spawn_count: Optional[int] = None
    where: Union[str, List[str]] = field(default_factory=list)
    total_currency: Optional[int] = None
    wait_before_starting: Optional[int] = None
    wait_between_spawns: Optional[int] = None
    support: bool = False
    tf_bot: Optional[Robot] = None
    squad: List[Robot] = field(default_factory=list)
    random_choice: List[Dict[str, Robot]] = field(default_factory=list)
    wait_for_all_spawned: Optional[str] = None
    wait_for_all_dead: Optional[str] = None
    start_wave_output: Optional[Dict[str, str]] = None
    done_wave_output: Optional[Dict[str, str]] = None

@dataclass
class Tank(ASTNode):
    """Узел танка."""
    name: str = ""
    health: int = 0
    speed: int = 0
    skin: int = 0
    starting_path: str = ""
    on_killed_output: Optional[Dict[str, str]] = None
    on_bomb_dropped_output: Optional[Dict[str, str]] = None

class Parser:
    """Парсер для pop файлов."""
    
    def __init__(self):
        self.lexer = Lexer()
        self.current_token: Optional[Token] = None
        self.tokens: List[Token] = []
        self.pos = 0
        
    def error(self, message: str = "Invalid syntax") -> None:
        """Вызывает ошибку парсинга."""
        token = self.current_token
        raise Exception(
            f"Parsing error at line {token.line}, column {token.column}: {message}"
        )
        
    def eat(self, token_type: str) -> None:
        """Проверяет и переходит к следующему токену."""
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
        else:
            self.error(
                f"Expected {token_type}, got {self.current_token.type}"
            )
            
    def parse_string(self) -> str:
        """Парсит строковое значение."""
        token = self.current_token
        self.eat('STRING')
        return token.value
        
    def parse_number(self) -> Union[int, float]:
        """Парсит числовое значение."""
        token = self.current_token
        if token.type == 'INTEGER':
            self.eat('INTEGER')
            return token.value
        elif token.type == 'FLOAT':
            self.eat('FLOAT')
            return token.value
        else:
            self.error("Expected number")
            
    def parse_value(self) -> Any:
        """Парсит значение атрибута."""
        if self.current_token.type in ('INTEGER', 'FLOAT'):
            return self.parse_number()
        elif self.current_token.type == 'STRING':
            return self.parse_string()
        elif self.current_token.type == 'IDENTIFIER':
            value = self.current_token.value
            self.eat('IDENTIFIER')
            return value
        elif self.current_token.type == 'LBRACE':
            return self.parse_block()
        elif self.current_token.type == 'LBRACKET':
            return self.parse_array()
        else:
            self.error("Invalid value")
            
    def parse_array(self) -> List[Any]:
        """Парсит массив значений."""
        values = []
        self.eat('LBRACKET')
        
        while self.current_token.type != 'RBRACKET':
            values.append(self.parse_value())
            
        self.eat('RBRACKET')
        return values
        
    def parse_block(self) -> Dict[str, Any]:
        """Парсит блок атрибутов."""
        attributes = {}
        self.eat('LBRACE')
        
        while self.current_token.type != 'RBRACE':
            if self.current_token.type != 'IDENTIFIER':
                self.error("Expected identifier")
                
            key = self.current_token.value
            self.eat('IDENTIFIER')
            
            value = self.parse_value()
            attributes[key] = value
            
        self.eat('RBRACE')
        return attributes
        
    def parse_robot(self, data: Dict[str, Any]) -> Robot:
        """Парсит определение робота."""
        # Собираем все Item в список
        items = []
        if 'Item' in data:
            if isinstance(data['Item'], list):
                items.extend(data['Item'])
            else:
                items.append(data['Item'])
                
        # Собираем атрибуты
        attributes = []
        if 'Attributes' in data:
            if isinstance(data['Attributes'], list):
                attributes.extend(data['Attributes'])
            else:
                attributes.append(data['Attributes'])
                
        # Обрабатываем CharacterAttributes и ItemAttributes
        character_attributes = data.get('CharacterAttributes', {})
        item_attributes = data.get('ItemAttributes', {})
        
        # Базовые атрибуты по умолчанию
        name = data.get('Name', 'Unknown')
        class_name = data.get('Class')
        skill = data.get('Skill')
        health = int(data['Health']) if 'Health' in data else None
        scale = float(data.get('Scale', 1.0))
        
        # Остальные специальные атрибуты
        other_attributes = {
            key: value for key, value in data.items() 
            if key not in ['Name', 'Class', 'Health', 'Skill', 'Scale', 'Item', 
                          'Attributes', 'CharacterAttributes', 'ItemAttributes']
        }
        
        return Robot(
            name=name,
            class_name=class_name,
            health=health,
            skill=skill,
            scale=scale,
            items=items,
            attributes=other_attributes,
            character_attributes=character_attributes
        )
        
    def parse_wave(self) -> Wave:
        """Парсит определение волны."""
        attributes = self.parse_block()
        wave_spawns = []
        tanks = []
        
        # Парсим WaveSpawn
        if 'WaveSpawn' in attributes:
            spawn_data = attributes.pop('WaveSpawn')
            if isinstance(spawn_data, list):
                for spawn in spawn_data:
                    wave_spawns.append(self.parse_wave_spawn(spawn))
            else:
                wave_spawns.append(self.parse_wave_spawn(spawn_data))
                
        # Парсим Tank
        if 'Tank' in attributes:
            tank_data = attributes.pop('Tank')
            if isinstance(tank_data, list):
                for tank in tank_data:
                    tanks.append(self.parse_tank(tank))
            else:
                tanks.append(self.parse_tank(tank_data))
                
        return Wave(
            wave_spawns=wave_spawns,
            tanks=tanks,
            description=attributes.get('Description'),
            total_count=attributes.get('TotalCount'),
            total_currency=attributes.get('TotalCurrency'),
            wait_for_all_spawned=attributes.get('WaitForAllSpawned'),
            wait_for_all_dead=attributes.get('WaitForAllDead'),
            start_output=attributes.get('StartWaveOutput'),
            done_output=attributes.get('DoneOutput')
        )
        
    def parse_template(self) -> Template:
        """Парсит определение шаблона."""
        attributes = self.parse_block()
        
        if 'Name' not in attributes:
            self.error("Template missing Name")
            
        return Template(
            name=attributes.pop('Name'),
            base=attributes.pop('Base', None),
            attributes=attributes
        )
        
    def parse_mission(self) -> Mission:
        """Парсит определение миссии."""
        attributes = self.parse_block()
        
        waves = []
        if 'Wave' in attributes:
            wave_data = attributes.pop('Wave')
            if isinstance(wave_data, list):
                for wave in wave_data:
                    waves.append(self.parse_wave(wave))
            else:
                waves.append(self.parse_wave(wave_data))
                
        templates = {}
        if 'Templates' in attributes:
            templates_data = attributes.pop('Templates')
            if not isinstance(templates_data, dict):
                self.error("Templates must be an object")
            
            for template_name, template_data in templates_data.items():
                templates[template_name] = self.parse_template(template_data)
                
        # Парсим Mission objectives
        mission_objectives = []
        if 'Mission' in attributes:
            mission_data = attributes.pop('Mission')
            if isinstance(mission_data, list):
                mission_objectives.extend(mission_data)
            else:
                mission_objectives.append(mission_data)
                
        # Создаем объект Mission
        mission = Mission(
            name=attributes.get('Name'),
            map_name=attributes.get('Map'),
            is_advanced=attributes.get('Advanced') == '1',
            waves=waves,
            templates=templates if templates else None,
            starting_currency=int(attributes['StartingCurrency']) if 'StartingCurrency' in attributes else None,
            respawn_wave_time=int(attributes['RespawnWaveTime']) if 'RespawnWaveTime' in attributes else None,
            fixed_respawn_wave_time=int(attributes['FixedRespawnWaveTime']) if 'FixedRespawnWaveTime' in attributes else None,
            can_bots_attack_while_in_spawn_room=attributes.get('CanBotsAttackWhileInSpawnRoom') == 'Yes',
            add_sentry_buster_when_damage_dealt_exceeds=int(attributes['AddSentryBusterWhenDamageDealtExceeds']) if 'AddSentryBusterWhenDamageDealtExceeds' in attributes else None,
            add_sentry_buster_when_kill_count_exceeds=int(attributes['AddSentryBusterWhenKillCountExceeds']) if 'AddSentryBusterWhenKillCountExceeds' in attributes else None,
            mission_objectives=mission_objectives,
            event_popup_file=attributes.get('EventPopupFile'),
            custom_attributes={k: v for k, v in attributes.items() if k not in [
                'Name', 'Map', 'Advanced', 'Wave', 'Templates', 'Mission',
                'StartingCurrency', 'RespawnWaveTime', 'FixedRespawnWaveTime',
                'CanBotsAttackWhileInSpawnRoom', 'AddSentryBusterWhenDamageDealtExceeds',
                'AddSentryBusterWhenKillCountExceeds', 'EventPopupFile'
            ]}
        )
        
        return mission
        
    def parse_wave_spawn(self, data: Dict[str, Any]) -> WaveSpawn:
        """Парсит определение WaveSpawn."""
        tf_bot = None
        squad = []
        random_choice = []
        
        # Парсим TFBot
        if 'TFBot' in data:
            tf_bot = self.parse_robot(data['TFBot'])
            
        # Парсим Squad
        if 'Squad' in data:
            squad_data = data['Squad']
            if 'TFBot' in squad_data:
                if isinstance(squad_data['TFBot'], list):
                    for bot in squad_data['TFBot']:
                        squad.append(self.parse_robot(bot))
                else:
                    squad.append(self.parse_robot(squad_data['TFBot']))
                    
        # Парсим RandomChoice
        if 'RandomChoice' in data:
            for choice in data['RandomChoice']:
                if 'TFBot' in choice:
                    random_choice.append({
                        'TFBot': self.parse_robot(choice['TFBot'])
                    })
                    
        # Обрабатываем Where как список или строку
        where = data.get('Where', [])
        if isinstance(where, str):
            where = [where]
            
        return WaveSpawn(
            name=data.get('Name'),
            total_count=int(data['TotalCount']) if 'TotalCount' in data else None,
            max_active=int(data['MaxActive']) if 'MaxActive' in data else None,
            spawn_count=int(data['SpawnCount']) if 'SpawnCount' in data else None,
            where=where,
            total_currency=int(data['TotalCurrency']) if 'TotalCurrency' in data else None,
            wait_before_starting=int(data['WaitBeforeStarting']) if 'WaitBeforeStarting' in data else None,
            wait_between_spawns=int(data['WaitBetweenSpawns']) if 'WaitBetweenSpawns' in data else None,
            support=data.get('Support') == '1',
            tf_bot=tf_bot,
            squad=squad,
            random_choice=random_choice,
            wait_for_all_spawned=data.get('WaitForAllSpawned'),
            wait_for_all_dead=data.get('WaitForAllDead'),
            start_wave_output=data.get('StartWaveOutput'),
            done_wave_output=data.get('DoneWaveOutput')
        )
        
    def parse_tank(self, data: Dict[str, Any]) -> Tank:
        """Парсит определение Tank."""
        return Tank(
            name=data.get('Name', ''),
            health=int(data['Health']) if 'Health' in data else 0,
            speed=int(data['Speed']) if 'Speed' in data else 0,
            skin=int(data.get('Skin', 0)),
            starting_path=data.get('StartingPathTrackNode', ''),
            on_killed_output=data.get('OnKilledOutput'),
            on_bomb_dropped_output=data.get('OnBombDroppedOutput')
        )
        
    def parse(self, text: str) -> Mission:
        """Парсит текст pop файла."""
        self.tokens = self.lexer.tokenize(text)
        if not self.tokens:
            raise Exception("Empty input")
            
        self.pos = 0
        self.current_token = self.tokens[0]
        
        mission = self.parse_mission()
        
        if self.current_token.type != 'EOF':
            self.error("Expected end of file")
            
        return mission
