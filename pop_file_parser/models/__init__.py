"""
Модели для работы с MvM миссиями Team Fortress 2.
"""

from .robot import Robot
from .wave_spawn import WaveSpawn
from .tank import Tank
from .wave import Wave
from .tf_bot import TFBot

__all__ = [
    'Robot',
    'WaveSpawn',
    'Tank',
    'Wave',
    'TFBot'
]
