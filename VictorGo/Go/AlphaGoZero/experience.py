# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-23-10:14 下午
import numpy as np

class AlphaGoZeroExperienceCollector:
    def __init__(self):
        self.states = []
        self.visit_number = []
        self.rewards = []
        self._current_episode_states = []
        self._current_episode_visit_number = []

    def begin_episode(self):
        self._current_episode_states = []
        self._current_episode_visit_number = []

    def record_decision(self, state, visit_number):
        self._current_episode_states.append(state)
        self._current_episode_visit_number.append(visit_number)

    def complete_episode(self, reward):
        num_states = len(self._current_episode_states)
        self.states += self._current_episode_states
        self.visit_number += self._current_episode_visit_number
        self.rewards += [reward for i in range(num_states)]

        self._current_episode_visit_number = []
        self._current_episode_states = []


class ExperienceBuffer:
    def __init__(self, states, visit_numbers, rewards):
        self.states = states
        self.visit_numbers = visit_numbers
        self.rewards = rewards

    def serialize(self, h5file):
        h5file.create_group('experience')
        h5file['experience'].create_dataset('states', data=self.states)
        h5file['experience'].create_dataset('visit_numbers', data=self.visit_numbers)
        h5file['experience'].create_dataset('rewards', data=self.rewards)


def load_experience(h5file):
    return ExperienceBuffer(
        states=np.array(h5file['experience']['states']),
        visit_numbers=np.array(h5file['experience']['visit_numbers']),
        rewards=np.array(h5file['experience']['rewards'])
    )


def combine_experience(collectors):
    combined_states = np.concatenate([np.array(c.states) for c in collectors])
    combined_visit_number = np.concatenate([np.array(c.visit_number) for c in collectors])
    combined_rewards = np.concatenate([np.array(c.rewards) for c in collectors])

    return ExperienceBuffer(combined_states, combined_visit_number, combined_rewards)
