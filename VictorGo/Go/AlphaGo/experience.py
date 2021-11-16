# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-21-4:42 下午
import numpy as np

class ExperienceBuffer:
    def __init__(self, states, actions, rewards):
        self.states = states
        self.actions = actions
        self.rewards = rewards

    def serialize(self, h5file):
        h5file.create_group('experience')
        h5file['experience'].create_dataset('states', data=self.states)
        h5file['experience'].create_dataset('actions', data=self.actions)
        h5file['rewards'].create_dataset('rewards', data=self.rewards)

def load_experience(h5file):
    return ExperienceBuffer(
        states=np.array(h5file['experience']['states']),
        actions=np.array(h5file['experience']['actions']),
        rewards=np.array(h5file['experience']['rewards'])
    )

class ExperienceCollector:
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.state_values = []
        self.current_episode_states = []
        self.current_episode_actions = []
        self.current_episode_estimated_values = []

    def begin_episode(self):
        self.current_episode_states = []
        self.current_episode_actions = []
        self.current_episode_estimated_values = []

    def record_decision(self, state, action, state_value):
        self.current_episode_states.append(state)
        self.current_episode_actions.append(action)
        self.current_episode_estimated_values(state_value)

    def complete_episode(self, reward):
        num_states = len(self.current_episode_states)
        self.states += self.current_episode_states
        self.actions += self.current_episode_actions
        self.rewards += [reward for i in range(num_states)]

        self.current_episode_states = []
        self.current_episode_actions = []

    def to_buffer(self):
        return ExperienceBuffer(
            states=np.array(self.states),
            actions=np.array(self.actions),
            rewards=np.array( self.rewards)
        )

def combine_experience(collectors):
    combined_states = np.concatenate([np.array(c.states) for c in collectors])
    combined_actions = np.concatenate([np.array(c.actions) for c in collectors])
    combined_rewards = np.concatenate([np.array(c.rewards) for c in collectors])

    return ExperienceBuffer(
        combined_states,
        combined_actions,
        combined_rewards,
    )
