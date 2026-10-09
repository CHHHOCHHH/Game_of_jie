"""
AI 对战测试脚本。

用法：
    python3 test_ai.py --p0 ai_king --p1 ai_random --games 100000 --seed 42

输出：
    每 1000 局打印 P0 胜、平、负的数量和胜率。
    结束时输出动作使用统计（从高到低排序）。
"""

import argparse
import random
import importlib
import sys
import unicodedata

from jie_core import (
    Player, GameState, SKILLS, check_game_over,
    resolve, end_of_round, pay, make_state,
)


# ==================== 显示工具 ====================
def display_width(s):
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
    return w


def pad_to(s, target):
    diff = target - display_width(s)
    return s + ' ' * diff if diff > 0 else s


def fmt_action(action):
    sid, n = action
    name = SKILLS[sid].name
    return f"{name}×{n}" if n > 1 else name


# ==================== AI 加载 ====================
def load_ai(module_name, **kwargs):
    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        print(f"错误：无法导入 {module_name}：{e}")
        sys.exit(1)
    if not hasattr(mod, "AI"):
        print(f"错误：{module_name} 中没有定义 AI 类")
        sys.exit(1)
    return mod.AI(**kwargs)


def sample_action(dist, rng):
    actions = list(dist.keys())
    probs = list(dist.values())
    total = sum(probs)
    if total <= 0:
        return actions[0]
    r = rng.random() * total
    acc = 0.0
    for a, p in zip(actions, probs):
        acc += p
        if r <= acc:
            return a
    return actions[-1]


# ==================== 模拟一局 ====================
def play_one_game(ai0, ai1, rng, action_counter, max_rounds=200):
    """
    模拟一局。返回 +1（P0 胜）、0（平）、-1（P1 胜）。
    action_counter: dict{(sid, n): count}，会在函数内被修改。
    """
    p0 = Player("P0")
    p1 = Player("P1")
    state = GameState([p0, p1])

    for _ in range(max_rounds):
        result = check_game_over(state)
        if result == "p0_win":
            return 1
        if result == "p1_win":
            return -1
        if result == "draw":
            return 0

        s0 = make_state(p0, p1)
        s1 = make_state(p1, p0)

        d0 = ai0.get_movement(s0)
        d1 = ai1.get_movement(s1)

        a0 = sample_action(d0, rng)
        a1 = sample_action(d1, rng)

        # 统计动作（多重攻击的不同 n 算作不同动作）
        action_counter[a0] = action_counter.get(a0, 0) + 1
        action_counter[a1] = action_counter.get(a1, 0) + 1

        moves = {0: a0, 1: a1}

        for i, (sid, n) in moves.items():
            p = state.players[i]
            sk = SKILLS[sid]
            pay(p, sk, n)

        resolve(state, moves)
        end_of_round(state)

    return 0


# ==================== 主流程 ====================
def main():
    parser = argparse.ArgumentParser(description="AI 对战测试")
    parser.add_argument("--p0", default="ai_king",
                        help="P0 的 AI 模块名（不带 .py）")
    parser.add_argument("--p1", default="ai_random",
                        help="P1 的 AI 模块名（不带 .py）")
    parser.add_argument("--games", type=int, default=100000,
                        help="总局数")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子（不指定则用系统时间）")
    parser.add_argument("--report-every", type=int, default=10000,
                        help="每多少局输出一次统计")
    parser.add_argument("--top-actions", type=int, default=0,
                        help="动作统计输出前 N 条（0 表示全部）")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    print(f"随机种子: {args.seed}")
    print(f"P0 = {args.p0}, P1 = {args.p1}, 总 {args.games} 局")
    print()

    ai0 = load_ai(args.p0, seed=rng.randint(0, 10**9))
    ai1 = load_ai(args.p1, seed=rng.randint(0, 10**9))

    counts = {-1: 0, 0: 0, 1: 0}
    action_counter = {}

    for i in range(args.games):
        r = play_one_game(ai0, ai1, rng, action_counter)
        counts[r] += 1

        if (i + 1) % args.report_every == 0:
            total = i + 1
            wins = counts[1]
            draws = counts[0]
            losses = counts[-1]
            print(f"[{total:>6} 局] "
                  f"P0胜={wins:>6} ({wins/total:6.2%})  "
                  f"平={draws:>6} ({draws/total:6.2%})  "
                  f"P0负={losses:>6} ({losses/total:6.2%})")

    # ============ 最终胜负 ============
    print()
    print(f"===== 最终结果（{args.games} 局）=====")
    total = args.games
    print(f"  P0 胜 (+1): {counts[1]:>8}  ({counts[1]/total:6.2%})")
    print(f"  平局  ( 0): {counts[0]:>8}  ({counts[0]/total:6.2%})")
    print(f"  P0 负 (-1): {counts[-1]:>8}  ({counts[-1]/total:6.2%})")
    ev = (counts[1] - counts[-1]) / total
    print(f"  期望收益: {ev:+.4f}")

    # ============ 动作使用统计 ============
    print()
    print(f"===== 动作使用统计（共 {args.games} 局）=====")
    items = sorted(action_counter.items(), key=lambda x: -x[1])
    total_actions = sum(action_counter.values())
    print(f"  总动作次数: {total_actions}  "
          f"（平均每局 {total_actions / args.games:.2f} 次）")
    print()

    shown = items if args.top_actions <= 0 else items[:args.top_actions]
    print(f"  {'动作':<14} {'总计':>8}   每局平均")
    print(f"  {'-'*14} {'-'*8}   {'-'*8}")
    for action, count in shown:
        label = fmt_action(action)
        avg = count / args.games
        print(f"  {pad_to(label, 14)}{count:>8}   {avg:.4f}")

    if args.top_actions > 0 and len(items) > args.top_actions:
        rest = len(items) - args.top_actions
        rest_count = sum(c for _, c in items[args.top_actions:])
        print(f"  ... 还有 {rest} 个动作，合计 {rest_count} 次 "
              f"({rest_count / args.games:.4f}/局)")


if __name__ == "__main__":
    main()