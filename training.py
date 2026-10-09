"""
“结”值迭代求解器 — 基于 jie_core 的简化版 + 多核并行 + 断点续训
"""

import numpy as np
from scipy.optimize import linprog
from itertools import product
from decimal import Decimal
import pickle
import time
import math
import os
from multiprocessing import Pool

# ============ 从 jie_core 导入公共引擎 ============
from jie_core import (
    SKILLS, Skill, DefVariant,
    ZERO, HALF, ATK, OP, DRAIN, NORM, COUNTER, JIE,
    HP_MIN, HP_MAX, PT_MAX, TK_MAX,
    single_cost, legal_actions, def_valid, compute_drain,
    resolve_atk_vs_atk, resolve_atk_vs_def,
)

# ============ 训练常量 ============
HP_HALVES = [1, 2, 3, 4]
TIME_PENALTY = 3e-5
CONVERGENCE_TOL = 1e-3
MAX_ITER = 200
TIME_LIMIT = 14400
NUM_WORKERS = 8 # CPU核数
CHUNK_SIZE = 1000
CHECKPOINT_PATH = "checkpoint.pkl"

MAX_RAW = 1.5 + PT_MAX * 0.2 + TK_MAX * 0.1

CURRENT_CONFIG = {
    'PT_MAX': PT_MAX,
    'TK_MAX': TK_MAX,
    'HP_HALVES': tuple(HP_HALVES),
    'TIME_PENALTY': TIME_PENALTY,
    'MAX_RAW': MAX_RAW,
    'SCHEMA_VERSION': 2,
}


# ============ 状态空间 ============
def all_states():
    for h0, h1, pt0, pt1, tk0, tk1 in product(
        HP_HALVES, HP_HALVES,
        range(PT_MAX + 1), range(PT_MAX + 1),
        range(TK_MAX + 1), range(TK_MAX + 1)
    ):
        yield (h0, pt0, tk0, h1, pt1, tk1)


# ============ 拉/大拉伤害（jie_core 未导出） ============
def pull_damage(pull_sk, absorb_sk):
    if pull_sk.is_big and absorb_sk.is_big:
        return Decimal(4)
    if pull_sk.is_big or absorb_sk.is_big:
        return Decimal(2)
    return Decimal(1)


# ============ 纯函数：计算效果 ============
def compute_effects(a0, a1):
    sid0, n0 = a0
    sid1, n1 = a1
    sk0 = SKILLS[sid0]
    sk1 = SKILLS[sid1]

    dmg0 = ZERO
    dmg1 = ZERO
    pt_d0 = pt_d1 = 0
    tk_d0 = tk_d1 = 0

    # 费用
    if sk0.cost_point > 0:
        pt_d0 -= int(sk0.cost_point) * n0
    elif sk0.cost_point < 0:
        pt_d0 += int(-sk0.cost_point) * n0
    if sk0.cost_ticket > 0:
        tk_d0 -= int(sk0.cost_ticket) * n0

    if sk1.cost_point > 0:
        pt_d1 -= int(sk1.cost_point) * n1
    elif sk1.cost_point < 0:
        pt_d1 += int(-sk1.cost_point) * n1
    if sk1.cost_ticket > 0:
        tk_d1 -= int(sk1.cost_ticket) * n1

    # 拉/大拉惩罚
    if sk0.is_pull and sk1.is_absorb:
        dmg1 += pull_damage(sk0, sk1)
    if sk1.is_pull and sk0.is_absorb:
        dmg0 += pull_damage(sk1, sk0)

    # 攻击结算
    if sk0.stype == ATK and sk1.stype == ATK:
        a, b = resolve_atk_vs_atk(sk0, n0, sk1, n1)
        dmg0 += a
        dmg1 += b
    elif sk0.stype == ATK and sk1.stype in (NORM, DRAIN, COUNTER):
        dd, ad, pts, tix = resolve_atk_vs_def(sk0, n0, sk1)
        dmg1 += dd
        dmg0 += ad
        pt_d1 += int(pts)
        tk_d1 += int(tix)
    elif sk1.stype == ATK and sk0.stype in (NORM, DRAIN, COUNTER):
        dd, ad, pts, tix = resolve_atk_vs_def(sk1, n1, sk0)
        dmg0 += dd
        dmg1 += ad
        pt_d0 += int(pts)
        tk_d0 += int(tix)
    elif sk0.stype == ATK and sk1.stype == OP:
        dmg1 += sk0.dmg_per_hit * n0
    elif sk1.stype == ATK and sk0.stype == OP:
        dmg0 += sk1.dmg_per_hit * n1

    # 摩擦/大摩自扣血
    if sk0.is_friction:
        if sk1.stype != ATK:
            dmg0 += Decimal("2.5") if sk0.is_big else Decimal("1.5")
    if sk1.is_friction:
        if sk0.stype != ATK:
            dmg1 += Decimal("2.5") if sk1.is_big else Decimal("1.5")

    return dmg0, dmg1, pt_d0, pt_d1, tk_d0, tk_d1


# ============ 效果缓存 ============
EFFECT_CACHE = {}


def get_effects_and_actions(pt0, tk0, pt1, tk1):
    key = (pt0, tk0, pt1, tk1)
    if key in EFFECT_CACHE:
        return EFFECT_CACHE[key]
    actions0 = legal_actions(pt0, tk0)
    actions1 = legal_actions(pt1, tk1)
    effects = {}
    for a in actions0:
        for b in actions1:
            effects[(a, b)] = compute_effects(a, b)
    result = (actions0, actions1, effects)
    EFFECT_CACHE[key] = result
    return result


# ============ 矩阵博弈 ============
def solve_matrix_game(M):
    m, n = M.shape

    if m == 1:
        return float(M.min()), np.array([1.0])
    if n == 1:
        p0 = np.zeros(m)
        p0[np.argmax(M[:, 0])] = 1.0
        return float(M.max()), p0

    row_min = M.min(axis=1)
    best_row = int(np.argmax(row_min))
    if row_min[best_row] >= M.max() - 1e-9:
        p0 = np.zeros(m)
        p0[best_row] = 1.0
        return float(row_min[best_row]), p0

    col_max = M.max(axis=0)
    best_col = int(np.argmin(col_max))
    if col_max[best_col] <= M.min() + 1e-9:
        best_row_for_col = int(np.argmax(M[:, best_col]))
        p0 = np.zeros(m)
        p0[best_row_for_col] = 1.0
        return float(M[best_row_for_col, best_col]), p0

    c = np.zeros(m + 1)
    c[-1] = -1.0
    A_ub = np.zeros((n, m + 1))
    for j in range(n):
        A_ub[j, :m] = -M[:, j]
        A_ub[j, m] = 1.0
    b_ub = np.zeros(n)
    A_eq = np.zeros((1, m + 1))
    A_eq[0, :m] = 1.0
    b_eq = np.array([1.0])
    bounds = [(0, None)] * m + [(None, None)]

    try:
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                         bounds=bounds, method='highs')
    except Exception:
        return float(M.mean()), np.ones(m) / m
    if not result.success:
        return float(M.mean()), np.ones(m) / m

    v = result.x[m]
    p0 = np.maximum(result.x[:m], 0)
    s = p0.sum()
    if s > 0:
        p0 /= s
    else:
        p0 = np.ones(m) / m
    return float(v), p0


# ============ 初始价值 ============
def heuristic(state):
    h0, pt0, tk0, h1, pt1, tk1 = state
    raw = (h0 * 0.5 + pt0 * 0.2 + tk0 * 0.1) - (h1 * 0.5 + pt1 * 0.2 + tk1 * 0.1)
    return math.tanh(raw / 5.7)


# ============ Checkpoint ============
def save_checkpoint(V_arr, iteration, config, path=CHECKPOINT_PATH):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump({
            'V_arr': V_arr,
            'iteration': iteration,
            'config': config,
            'timestamp': time.time(),
            'schema_version': 2,
        }, f, protocol=4)
    os.replace(tmp, path)


def load_checkpoint(path=CHECKPOINT_PATH):
    with open(path, "rb") as f:
        return pickle.load(f)


def ask_resume(ckpt):
    print("检测到 checkpoint：")
    print(f"  已迭代 {ckpt['iteration']} 轮")
    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ckpt['timestamp']))
    print(f"  保存时间 {ts}")
    while True:
        ans = input("继续 (c) / 从头开始 (n) / 退出 (q)？ [c]: ").strip().lower()
        if ans in ('', 'c'):
            return True
        if ans == 'n':
            return False
        if ans == 'q':
            return None


# ============ 多进程 ============
_STATES = None
_STATE_TO_IDX = None


def _init_worker(states, state_to_idx):
    global _STATES, _STATE_TO_IDX
    _STATES = states
    _STATE_TO_IDX = state_to_idx


def _process_chunk(args):
    chunk_indices, V_array = args
    results = []
    local_max_delta = 0.0

    for idx in chunk_indices:
        state = _STATES[idx]
        h0, pt0, tk0, h1, pt1, tk1 = state
        actions0, actions1, effects = get_effects_and_actions(pt0, tk0, pt1, tk1)

        if not actions0 or not actions1:
            results.append((idx, 0.0, {}))
            continue

        m, n = len(actions0), len(actions1)
        M = np.zeros((m, n))

        for i, a in enumerate(actions0):
            for j, b in enumerate(actions1):
                dmg0, dmg1, dpt0, dpt1, dtk0, dtk1 = effects[(a, b)]
                new_hp0 = Decimal(h0) * HALF - dmg0
                new_hp1 = Decimal(h1) * HALF - dmg1

                if new_hp0 <= 0 and new_hp1 <= 0:
                    M[i, j] = 0.0
                    continue
                if new_hp0 <= 0:
                    M[i, j] = -1.0
                    continue
                if new_hp1 <= 0:
                    M[i, j] = 1.0
                    continue

                nh0 = max(1, min(4, int(new_hp0 * 2)))
                nh1 = max(1, min(4, int(new_hp1 * 2)))
                npt0 = max(0, min(PT_MAX, pt0 + dpt0))
                npt1 = max(0, min(PT_MAX, pt1 + dpt1))
                ntk0 = max(0, min(TK_MAX, tk0 + dtk0))
                ntk1 = max(0, min(TK_MAX, tk1 + dtk1))
                s_next = (nh0, npt0, ntk0, nh1, npt1, ntk1)
                next_idx = _STATE_TO_IDX[s_next]
                M[i, j] = V_array[next_idx] - TIME_PENALTY

        v, p0 = solve_matrix_game(M)
        d = abs(v - V_array[idx])
        if d > local_max_delta:
            local_max_delta = d

        pi_entry = {actions0[k]: float(p0[k]) for k in range(m) if p0[k] > 1e-6}
        results.append((idx, v, pi_entry))

    return chunk_indices[0], local_max_delta, results


# ============ 主循环 ============
def value_iteration(max_iter=MAX_ITER, tol=CONVERGENCE_TOL,
                    time_limit=TIME_LIMIT,
                    save_path="jie_V.pkl", pi_path="jie_pi.pkl",
                    num_workers=NUM_WORKERS, chunk_size=CHUNK_SIZE,
                    checkpoint_path=CHECKPOINT_PATH,
                    resume=None):
    states = list(all_states())
    state_to_idx = {s: i for i, s in enumerate(states)}
    N = len(states)

    print(f"状态总数: {N}")
    print(f"时间惩罚: {TIME_PENALTY}")
    print(f"更新方式: Jacobi + {num_workers} 进程并行")
    print()

    start_iter = 0
    V_arr = None

    if os.path.exists(checkpoint_path) and resume is not False:
        try:
            ckpt = load_checkpoint(checkpoint_path)
            same_config = (ckpt.get('config') == CURRENT_CONFIG
                           and ckpt.get('V_arr') is not None
                           and ckpt['V_arr'].shape == (N,))
            if not same_config:
                print("checkpoint 与当前配置不匹配，将从头开始")
                resume = False
            else:
                if resume is None:
                    ans = ask_resume(ckpt)
                    if ans is None:
                        print("已退出")
                        return None, None
                    resume = ans
                if resume:
                    V_arr = ckpt['V_arr']
                    start_iter = ckpt['iteration']
                    print(f"从第 {start_iter} 轮继续")
        except Exception as e:
            print(f"读取 checkpoint 失败：{e}，将从头开始")
            resume = False

    if V_arr is None:
        V_arr = np.array([heuristic(s) for s in states], dtype=np.float64)
        start_iter = 0
        print("从头开始训练")

    pi = {}
    chunks = [list(range(i, min(i + chunk_size, N)))
              for i in range(0, N, chunk_size)]
    print(f"分块数: {len(chunks)}")
    print()

    start = time.time()
    current_iter = start_iter
    converged = False

    try:
        with Pool(num_workers, initializer=_init_worker,
                  initargs=(states, state_to_idx)) as pool:
            for it in range(start_iter, max_iter):
                current_iter = it + 1
                new_V_arr = V_arr.copy()
                new_pi = {}
                max_delta = 0.0
                finished = 0

                args = [(c, V_arr) for c in chunks]
                for chunk_start, chunk_delta, chunk_results in pool.imap_unordered(
                        _process_chunk, args):
                    for idx, v, pi_entry in chunk_results:
                        new_V_arr[idx] = v
                        if pi_entry:
                            new_pi[states[idx]] = pi_entry
                    if chunk_delta > max_delta:
                        max_delta = chunk_delta
                    finished += 1
                    elapsed = time.time() - start
                    print(f"  iter {it+1}, 块 {finished}/{len(chunks)}, "
                          f"起始状态 {chunk_start:>6d}, "
                          f"局部 delta={chunk_delta:.8f}, 已用 {elapsed:.1f}s")

                V_arr = new_V_arr
                pi = new_pi

                elapsed = time.time() - start
                print(f"迭代 {it+1} 完成, delta={max_delta:.8f}, 已用 {elapsed:.1f}s")

                save_checkpoint(V_arr, current_iter, CURRENT_CONFIG, checkpoint_path)
                print(f"  [checkpoint] 已保存")

                if max_delta < tol:
                    print(f"在第 {it+1} 次迭代收敛")
                    converged = True
                    break
                if elapsed > time_limit:
                    print(f"达到时间限制 {time_limit}s，停止迭代")
                    break

    except KeyboardInterrupt:
        print("\n\n用户中断，正在保存...")
        save_checkpoint(V_arr, current_iter, CURRENT_CONFIG, checkpoint_path)
        V = {s: float(V_arr[i]) for i, s in enumerate(states)}
        with open(save_path, "wb") as f:
            pickle.dump(V, f)
        with open(pi_path, "wb") as f:
            pickle.dump(pi, f)
        print(f"checkpoint + V + pi 已保存（第 {current_iter} 轮）")
        raise

    V = {s: float(V_arr[i]) for i, s in enumerate(states)}
    with open(save_path, "wb") as f:
        pickle.dump(V, f)
    with open(pi_path, "wb") as f:
        pickle.dump(pi, f)
    print(f"已保存 V 到 {save_path}，策略到 {pi_path}")

    if converged and os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
        print(f"已删除 checkpoint（训练完成）")
    elif not converged:
        print(f"checkpoint 保留（未收敛，可继续）")

    return V, pi


if __name__ == "__main__":
    import multiprocessing as mp
    try:
        mp.set_start_method('fork', force=True)
    except RuntimeError:
        pass
    value_iteration()