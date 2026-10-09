"""
查表 AI：从 jie_pi.pkl 读取策略表，按概率分布出招。
"""

import pickle
import os
from jie_core import legal_actions


POLICY_PATH = "jie_pi.pkl"


class AI:
    def __init__(self, policy_path=None, seed=None):
        # seed 参数被接受但不用——查表 AI 是确定性的，
        # 随机性由 test_ai.py 的采样器负责
        self.seed = seed
        path = policy_path or POLICY_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到策略表 {path}")
        with open(path, "rb") as f:
            self.pi = pickle.load(f)

    def get_movement(self, state):
        dist = self.pi.get(state, None)
        if dist is None or not dist:
            my_h, my_pt, my_tk, _, _, _ = state
            actions = legal_actions(my_pt, my_tk)
            if not actions:
                return {(9, 1): 1.0}
            p = 1.0 / len(actions)
            return {a: p for a in actions}
        return dict(dist)