# Use this file as a starting point for your algorithms.

import gym
from gym.envs.registration import register
from ray.rllib.algorithms.cql import CQLConfig

register(
    id='SokobanEnv-v0',
    entry_point='src.SokobanEnv:SokobanEnv',
    kwargs={"level_file": "puzzles/easy.txt"}
)

env = gym.make('SokobanEnv-v0')