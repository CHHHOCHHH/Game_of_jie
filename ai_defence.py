"""
保守 AI：50% 防御、30% 结、20% 攻击。
"""

import random
from jie_core import SKILLS, legal_actions, ATK, NORM, DRAIN, COUNTER


DEFENCE_TYPES = {NORM, DRAIN, COUNTER}


class AI:
    def __init__(self, seed=None):
        # 使用独立的 Random 实例，避免全局 random 的干扰
        self.rng = random.Random(seed)

    def get_movement(self, state):
        my_h, my_pt, my_tk, _, _, _ = state
        actions = legal_actions(my_pt, my_tk)
        if not actions:
            return {(9, 1): 1.0}

        defence_actions = [a for a in actions if SKILLS[a[0]].stype in DEFENCE_TYPES]
        attack_actions = [a for a in actions if SKILLS[a[0]].stype == ATK]
        jie_action = (9, 1) if (9, 1) in actions else None

        dist = {}

        # 50% 防御
        if defence_actions:
            p_each = 0.5 / len(defence_actions)
            for a in defence_actions:
                dist[a] = dist.get(a, 0) + p_each
        elif jie_action:
            dist[jie_action] = dist.get(jie_action, 0) + 0.5

        # 30% 结
        if jie_action:
            dist[jie_action] = dist.get(jie_action, 0) + 0.3
        elif attack_actions:
            p_each = 0.3 / len(attack_actions)
            for a in attack_actions:
                dist[a] = dist.get(a, 0) + p_each

        # 20% 攻击
        if attack_actions:
            p_each = 0.2 / len(attack_actions)
            for a in attack_actions:
                dist[a] = dist.get(a, 0) + p_each
        elif jie_action:
            dist[jie_action] = dist.get(jie_action, 0) + 0.2

        # 归一化
        total = sum(dist.values())
        if total > 0:
            dist = {a: p / total for a, p in dist.items()}
        else:
            dist = {(9, 1): 1.0}
        return dist