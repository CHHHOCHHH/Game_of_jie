"""
贪心查表 AI：读取 jie_pi.pkl，永远选择概率最高的招式（argmax）。
与 ai_smart 的区别：ai_smart 按概率分布随机采样，ai_best 直接取最大值。
"""

import pickle
import os
from jie_core import legal_actions


POLICY_PATH = "jie_pi.pkl"


class AI:
    def __init__(self, policy_path=None, seed=None):
        # seed 参数为了接口统一，本 AI 是确定性的，不使用
        self.seed = seed
        path = policy_path or POLICY_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到策略表 {path}")
        with open(path, "rb") as f:
            self.pi = pickle.load(f)

    def get_movement(self, state):
        dist = self.pi.get(state, None)
        if dist is None or not dist:
            # 未知状态，用合法动作均匀分布兜底
            my_h, my_pt, my_tk, _, _, _ = state
            actions = legal_actions(my_pt, my_tk)
            if not actions:
                return {(9, 1): 1.0}
            p = 1.0 / len(actions)
            return {a: p for a in actions}

        # 取概率最高的动作
        best_action = max(dist.items(), key=lambda x: x[1])[0]
        return {best_action: 1.0}