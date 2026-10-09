"""
随机 AI：在合法动作里均匀随机。
"""

from jie_core import legal_actions


class AI:
    def __init__(self, seed=None):
        # seed 参数被接受但不用——随机性由 test_ai.py 的采样器负责
        self.seed = seed

    def get_movement(self, state):
        my_h, my_pt, my_tk, _, _, _ = state
        actions = legal_actions(my_pt, my_tk)
        if not actions:
            return {(9, 1): 1.0}
        p = 1.0 / len(actions)
        return {a: p for a in actions}