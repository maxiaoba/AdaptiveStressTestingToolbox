"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""
from Cartpole.cartpole import CartPoleEnv
from garage.misc.overrides import overrides
from garage.core import Serializable
import numpy as np
import gym

class CartPoleNdEnv(CartPoleEnv, Serializable):
    def __init__(self, nd, *args, **kwargs):
        self.nd = nd
        Serializable.quick_init(self, locals())
        super(CartPoleNdEnv, self).__init__(*args, **kwargs)

    @property
    def ast_action_space(self):
        high = np.array([self.wind_force_mag for i in range(self.nd)])
        return gym.spaces.Box(-high,high)

    def ast_step(self, action, ast_action):
        if self.use_seed:
            np.random.seed(ast_action)
            ast_action = self.ast_action_space.sample()
        ast_action = np.mean(ast_action)
        use_seed = self.use_seed
        self.use_seed = False
        results = super(CartPoleNdEnv, self).ast_step(action, ast_action)
        self.use_seed = use_seed
        return results