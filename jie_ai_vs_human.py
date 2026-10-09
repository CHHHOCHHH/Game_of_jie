"""
“结”——拍手游戏结系简化版 1v1 程序（策略表 AI 版）

基于 jie_core.py，仅保留人机对战相关逻辑。
P1 从训练好的策略表 jie_pi.pkl 中按概率分布选择动作。
每轮显示双方视角的概率分布和最优招式。
输入 -1 可以手动设置双方状态为任意六元组。
"""

import pickle
import random
import time
import unicodedata
from decimal import Decimal

from jie_core import (
    SKILLS, Player, GameState,
    ZERO, HALF, PT_MAX, TK_MAX, HP_MIN, HP_MAX,
    check_game_over, resolve, end_of_round, pay,
    make_state, normalize_n, can_pay,
)


# ==================== 显示工具 ====================
FULLWIDTH_SPACE = '\u3000'
TARGET_WIDTH = 18

GAME_OVER_TEXT = {
    "draw": "平局",
    "p0_win": "P0 胜",
    "p1_win": "P1 胜",
}


def display_width(s):
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
    return w


def pad_name(name, target_width=TARGET_WIDTH):
    W = display_width(name)
    diff = target_width - W
    if diff <= 0:
        return name
    n_full = 3 if W < 4 else (2 if W < 8 else 1)
    n_full = min(n_full, diff // 2)
    n_half = diff - 2 * n_full
    return name + FULLWIDTH_SPACE * n_full + ' ' * n_half


def action_str(action):
    sid, n = action
    name = SKILLS[sid].name
    return f"{name}×{n}" if n > 1 else name


def print_dist(title, dist, top_n=6):
    items = sorted(dist.items(), key=lambda x: -x[1])[:top_n]
    print(f"    {title}:")
    for action, p in items:
        padded = pad_name(action_str(action))
        bar = "█" * int(p * 50)
        print(f"      {padded}{p:.4f}  {bar}")


def display_state(p0, p1):
    print(f"  P0: HP={p0.hp:.1f} 点数={p0.points} 免单={p0.tickets}")
    print(f"  P1: HP={p1.hp:.1f} 点数={p1.points} 免单={p1.tickets}")


def display_distributions(p0, p1, pi):
    s0 = make_state(p0, p1)
    print(f"\n  [P0 视角] 状态={s0}")
    v = V.get(s0, 0.0)
    p_win = (1 + v) / 2
    print(f"  当前 P0 近似胜率: {p_win:.1%}")
    d0 = pi.get(s0, {(9, 1): 1.0})
    print_dist("P0 应出的招式（概率分布）", d0)
    best0 = max(d0.items(), key=lambda x: x[1])
    print(f"    → 最优: {action_str(best0[0])} ({best0[1]:.4f})")

    s1 = make_state(p1, p0)
    d1 = pi.get(s1, {(9, 1): 1.0})
    v = V.get(s1, 0.0)
    p_win = (1 + v) / 2
    print(f"\n  [P1 视角] 状态={s1}（P1 作为第一玩家）")
    print(f"  当前 P1 近似胜率: {p_win:.1%}")
    print_dist("P1 应出的招式（概率分布）", d1)
    best1 = max(d1.items(), key=lambda x: x[1])
    print(f"    → 最优: {action_str(best1[0])} ({best1[1]:.4f})")


# ==================== 策略表 ====================
PI = {}
V = {}

def load_policy(path="jie_pi.pkl"):
    global PI
    with open(path, "rb") as f:
        PI = pickle.load(f)
    print(f"已加载策略表: {path}，共 {len(PI)} 个状态")
    
def load_V(path="jie_V.pkl"):
    global V
    with open(path,"rb") as f:
        V = pickle.load(f)
    print(f"已加载胜率表: {path}，共 {len(V)} 个状态")


def query_dist(state):
    return PI.get(state, {(9, 1): 1.0})


def sample_from_dist(dist):
    actions = list(dist.keys())
    probs = list(dist.values())
    total = sum(probs)
    r = random.random() * total
    acc = 0.0
    for a, p in zip(actions, probs):
        acc += p
        if r <= acc:
            return a
    return actions[-1]


def ai_choose_table(p, opp):
    return sample_from_dist(query_dist(make_state(p, opp)))


# ==================== 人类输入 ====================
RESET_SIGNAL = "RESET"


def human_input(p):
    while True:
        raw = input(f"{p.name} 请输入 技能编号[ 发数]（例：1 2；-1 重置状态）: ").strip()
        if not raw:
            continue
        if raw == "-1":
            return RESET_SIGNAL
        parts = raw.split()
        try:
            sid = int(parts[0])
        except ValueError:
            print("  技能编号必须是整数")
            continue
        if sid not in SKILLS:
            print(f"  无效编号 {sid}")
            continue
        sk = SKILLS[sid]
        n = 1
        if len(parts) >= 2:
            try:
                n = int(parts[1])
            except ValueError:
                print("  发数必须是整数")
                continue
        n = normalize_n(sk, n)
        if not can_pay(p, sk, n):
            print(f"  资源不足，无法出 {sk.name}×{n}；"
                  f"当前 点数={p.points} 免单={p.tickets}")
            continue
        return (sid, n)


def handle_reset(p0, p1) -> bool:
    raw = input("请输入六元组 (h0,pt0,tk0,h1,pt1,tk1)，如 (4,2,1,4,2,1): ").strip()
    try:
        clean = raw.strip("() ")
        nums = [int(x.strip()) for x in clean.split(",")]
        if len(nums) != 6:
            print(f"  错误：需要 6 个整数，收到 {len(nums)} 个")
            return False
        h0, pt0, tk0, h1, pt1, tk1 = nums

        if not (1 <= h0 <= 4 and 1 <= h1 <= 4):
            print("  HP 半值必须在 1-4 之间（对应 0.5-2.0）")
            return False
        if not (0 <= pt0 <= PT_MAX and 0 <= pt1 <= PT_MAX):
            print(f"  点数必须在 0-{PT_MAX} 之间")
            return False
        if not (0 <= tk0 <= TK_MAX and 0 <= tk1 <= TK_MAX):
            print(f"  免单必须在 0-{TK_MAX} 之间")
            return False

        for p, (h, pt, tk) in zip([p0, p1],
                                  [(h0, pt0, tk0), (h1, pt1, tk1)]):
            p.hp = Decimal(h) * HALF
            p.points = Decimal(pt)
            p.tickets = Decimal(tk)
            p.pending_points = ZERO
            p.pending_tickets = ZERO
            p.dead = False

        print("  ✓ 状态已重置")
        return True
    except Exception as e:
        print(f"  解析错误：{e}")
        return False


# ==================== 单回合 ====================
def play_round(state, in0, in1, verbose=False):
    if check_game_over(state):
        return {}, None

    moves = {}
    for i, inp in ((0, in0), (1, in1)):
        p = state.players[i]
        if p.dead:
            moves[i] = None
            continue
        sid, n = inp if inp else (9, 1)
        sk = SKILLS[sid]
        n = normalize_n(sk, n)
        if not can_pay(p, sk, n):
            sid, n = 9, 1
            sk = SKILLS[sid]
        moves[i] = (sid, n)
        pay(p, sk, n)

    resolve(state, moves)
    end_of_round(state, verbose=verbose)
    return moves, moves


# ==================== 技能表 ====================
def print_skill_table():
    print("\n=== 技能编号表（全结系）===")
    rows = [
        (1,  "啸波", "1×n 费用，1×n 伤害，多重"),
        (2,  "电波", "2×n 费用，1×n 伤害，多重"),
        (3,  "致命", "3×n 费用，1.5×n 伤害，多重"),
        (4,  "地波", "4×n 费用，2×n 伤害，多重"),
        (5,  "片波", "5×n 费用，2.5×n 伤害，多重"),
        (6,  "派波", "6×n 费用，3×n 伤害，多重"),
        (7,  "气波", "7×n 费用，3.5×n 伤害，多重"),
        (8,  "青龙波", "8×n 费用，4×n 伤害，多重"),
        (9,  "结", "−1 费，获得 1 点数"),
        (10, "反弹", "0 费，普通防御，反弹啸波"),
        (11, "小防", "0 费，普通防御 1-2 费结系攻击"),
        (12, "金龙波", "12×n 费用，6×n 伤害，多重"),
        (13, "大防", "0 费，普通防御 3-5 费结系攻击"),
        (14, "免单", "1x×n，消耗免单，0.5×n 伤害，多重"),
        (15, "吸", "0 费，吸 1-5 费结系攻击+免单，1 倍"),
        (16, "大吸", "1 费，吸 1-5 费结系攻击+免单，2 倍"),
        (17, "拉", "0 费，反制防御，与吸/大吸同轮触发惩罚"),
        (18, "大拉", "1 费，反制防御，与吸/大吸同轮触发更重惩罚"),
        (19, "摩擦", "0 费，吸 1-8 费结系攻击+免单"),
        (20, "大摩", "0 费，吸所有结系攻击"),
        (21, "收", "1 费，普通防御 6-7 费结系攻击"),
        (22, "青龙收", "1 费，普通防御 青龙波"),
        (23, "金龙收", "1 费，普通防御 金龙波"),
        (24, "世界末日", "20 费，10 伤害，单发，不可防御"),
    ]
    for sid, name, desc in rows:
        print(f"  {sid:>2}  {name:<6}  {desc}")
    print()


# ==================== 主循环 ====================
def main():
    random.seed(time.time())

    print("=== 结：拍手游戏结系简化版 1v1（策略表 AI 版） ===")
    print("P0 是人类，P1 是策略表 AI。")
    print("输入 -1 可以重置状态。")
    print()

    try:
        load_policy("jie_pi.pkl")
    except FileNotFoundError:
        print("错误：找不到 jie_pi.pkl")
        return
    try:
        load_V("jie_V.pkl")
    except FileNotFoundError:
        print("错误：找不到 jie_V.pkl")
        return
    
    print_skill_table()

    p0 = Player("P0")
    p1 = Player("P1")
    state = GameState([p0, p1])

    r = 0
    max_rounds = 200
    while r < max_rounds:
        result = check_game_over(state)
        if result:
            print(f"\n结果: {GAME_OVER_TEXT[result]}")
            return

        r += 1
        print(f"\n{'='*50}")
        print(f"===== 第 {r} 轮 =====")
        print(f"{'='*50}")

        # 状态 + 人类输入（支持重置后重新显示）
        while True:
            display_state(p0, p1)
            inp0 = human_input(p0)
            if inp0 == RESET_SIGNAL:
                handle_reset(p0, p1)
                continue
            break

        display_distributions(p0, p1, PI)

        # AI 决策
        inp1 = ai_choose_table(p1, p0)

        hp0_before = p0.hp
        hp1_before = p1.hp

        moves, _ = play_round(state, inp0, inp1, verbose=True)

        def fmt(m):
            return "—" if m is None else action_str(m)

        print(f"\n  ---- 结算 ----")
        parts = [f"P0={fmt(moves.get(0))}", f"P1={fmt(moves.get(1))}"]
        if hp0_before - p0.hp > 0:
            parts.append(f"P0 HP-{hp0_before - p0.hp}")
        if hp1_before - p1.hp > 0:
            parts.append(f"P1 HP-{hp1_before - p1.hp}")
        print("  " + "  ".join(parts))

        print("\n  ---- 本轮结束 ----")
        for p in state.players:
            status = "存活" if not p.dead else "死亡"
            print(f"  {p.name}: HP={p.hp:.1f} 点数={p.points} 免单={p.tickets} {status}")

        if not check_game_over(state):
            input("\n按 Enter 进入下一轮...")

    print("达到最大轮次")


if __name__ == "__main__":
    main()