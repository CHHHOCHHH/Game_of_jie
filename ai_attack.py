"""
进攻 AI：有 2 费以上就出啸波×2，否则出结。
"""

from jie_core import SKILLS, legal_actions


class AI:
    def __init__(self, seed=None):
        # seed 参数为了接口统一，本 AI 是确定性的，不使用
        self.seed = seed

    def get_movement(self, state):
        my_h, my_pt, my_tk, op_h, op_pt, op_tk = state
        
        # 有 2 点及以上，出啸波×2
        if my_pt >= 2 and (1, 2) in legal_actions(my_pt, my_tk):
            return {(1, 2): 1.0}

        # 否则出结
        if (9, 1) in legal_actions(my_pt, my_tk):
            return {(9, 1): 1.0}

        # 兜底：如果连结都出不了（理论上不会发生），返回第一个合法动作
        actions = legal_actions(my_pt, my_tk)
        if actions:
            return {actions[0]: 1.0}
        return {(9, 1): 1.0}