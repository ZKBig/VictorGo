# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-21-2:29 下午
from Go.encoders.alphaGo import AlphaGoEncoder
from Go.AlphaGo.self_game_simulation import experience_simulator
from Go.agent.cloning_predict_agent import load_predict_model
from Go.agent.policy_gradient_agent import PolicyAgent
from Go.agent.action_value_agent import ValueAgent
from Go.AlphaGo.Policy_Value_model import policy_value_model
from Go.AlphaGo.experience import load_experience
import h5py

encoder = AlphaGoEncoder()

player = load_predict_model(h5file=h5py.File("alphago_policy.h5"))
opponent = load_predict_model(h5file=h5py.File("alphago_policy.h5"))

player = PolicyAgent(player.model, encoder)
opponent = PolicyAgent(opponent.model, encoder)

experience = experience_simulator(1000, player, opponent)

player.train(experience)

with h5py.File("alphago_policy.h5", "w") as agent_out:
    player.serialize(agent_out)

with h5py.File("alphago_experience.h5", "w") as experience_out:
    experience.serialize(experience_out)

input_shape = (encoder.num_planes, 19, 19)
state_value_network = policy_value_model(input_shape=input_shape, is_policy_net=False)
state_value = ValueAgent(state_value_network, encoder)

experience = load_experience(h5py.File('alphago_experience.h5', 'r'))
state_value.train(experience)

with h5py.File('alphago_state_value.h5', 'w') as alphago_state_value:
    state_value.serialize(alphago_state_value)









