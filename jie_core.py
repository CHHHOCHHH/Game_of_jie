"""
“结”游戏公共引擎：技能定义、结算规则、状态管理。
被 AI 模块和 test_ai.py 共用。
"""

from decimal import Decimal, getcontext
from dataclasses import dataclass, field
from typing import Optional

getcontext().prec = 28
ZERO = Decimal(0)
HALF = Decimal("0.5")

ATK, OP, DRAIN, NORM, COUNTER = "ATK", "OP", "DRAIN", "NORM", "COUNTER"
JIE = "JIE"

HP_MIN, HP_MAX = 1, 4
PT_MAX = 20
TK_MAX = 2


# ==================== 技能 ====================
@dataclass
class DefVariant:
    def_cost_lo: Optional[Decimal] = None
    def_cost_hi: Optional[Decimal] = None
    def_include_ticket: bool = False
    drain_tiers: tuple = ()


@dataclass
class Skill:
    id: int
    name: str
    stype: str
    cost_point: Decimal = ZERO
    cost_ticket: Decimal = ZERO
    dmg_per_hit: Decimal = ZERO
    multi: bool = False
    min_hits: int = 1
    def_skill_ids: frozenset = frozenset()
    is_rebound: bool = False
    is_absorb: bool = False
    is_pull: bool = False
    is_big: bool = False
    is_friction: bool = False
    is_unblockable: bool = False
    variants: dict = field(default_factory=dict)


SKILLS = {}


def _add(sid, name, stype, **kw):
    SKILLS[sid] = Skill(sid, name, stype, **kw)


# 攻击 1-8
_add(1, "啸波", ATK, cost_point=Decimal(1), dmg_per_hit=Decimal(1), multi=True)
_add(2, "电波", ATK, cost_point=Decimal(2), dmg_per_hit=Decimal(1), multi=True)
_add(3, "致命", ATK, cost_point=Decimal(3), dmg_per_hit=Decimal("1.5"), multi=True)
_add(4, "地波", ATK, cost_point=Decimal(4), dmg_per_hit=Decimal(2), multi=True)
_add(5, "片波", ATK, cost_point=Decimal(5), dmg_per_hit=Decimal("2.5"), multi=True)
_add(6, "派波", ATK, cost_point=Decimal(6), dmg_per_hit=Decimal(3), multi=True)
_add(7, "气波", ATK, cost_point=Decimal(7), dmg_per_hit=Decimal("3.5"), multi=True)
_add(8, "青龙波", ATK, cost_point=Decimal(8), dmg_per_hit=Decimal(4), multi=True)

# 运营
_add(9, "结", OP, cost_point=Decimal(-1))

# 防御
_add(10, "反弹", NORM, def_skill_ids=frozenset({1}), is_rebound=True)
_add(11, "小防", NORM, variants={JIE: DefVariant(Decimal(1), Decimal(2),True)})

# 攻击
_add(12, "金龙波", ATK, cost_point=Decimal(12), dmg_per_hit=Decimal(6), multi=True)

# 防御
_add(13, "大防", NORM, variants={JIE: DefVariant(Decimal(3), Decimal(5))})
_add(14, "免单", ATK, cost_ticket=Decimal(1), dmg_per_hit=Decimal("0.5"), multi=True)
_add(15, "吸", DRAIN, is_absorb=True,
     variants={JIE: DefVariant(Decimal(1), Decimal(5), True,
                               ((Decimal(1), Decimal(5), Decimal(1)),))})
_add(16, "大吸", DRAIN, cost_point=Decimal(1), is_absorb=True, is_big=True,
     variants={JIE: DefVariant(Decimal(1), Decimal(5), True,
                               ((Decimal(1), Decimal(5), Decimal(2)),))})
_add(17, "拉", COUNTER, is_pull=True)
_add(18, "大拉", COUNTER, cost_point=Decimal(1), is_pull=True, is_big=True)
_add(19, "摩擦", DRAIN, is_friction=True,
     variants={JIE: DefVariant(Decimal(1), Decimal(8), True,
                               ((Decimal(1), Decimal(5), Decimal(1)),))})
_add(20, "大摩", DRAIN, is_friction=True, is_big=True,
     variants={JIE: DefVariant(Decimal(1), None, True,
                               ((Decimal(1), Decimal(5), Decimal(2)),
                                (Decimal(6), Decimal(8), Decimal(1))))})
_add(21, "收", NORM, cost_point=Decimal(1),
     variants={JIE: DefVariant(Decimal(6), Decimal(7))})
_add(22, "青龙收", NORM, cost_point=Decimal(1), def_skill_ids=frozenset({8}))
_add(23, "金龙收", NORM, cost_point=Decimal(1), def_skill_ids=frozenset({12}))
_add(24, "世界末日", ATK, cost_point=Decimal(20),
     dmg_per_hit=Decimal(10), multi=False, is_unblockable=True)


# ==================== 玩家 ====================
@dataclass
class Player:
    name: str
    hp: Decimal = Decimal(2)
    points: Decimal = Decimal(2)
    pending_points: Decimal = ZERO
    tickets: Decimal = Decimal(1)
    pending_tickets: Decimal = ZERO
    dead: bool = False


@dataclass
class GameState:
    players: list


# ==================== 工具 ====================
def single_cost(sk: Skill) -> Decimal:
    if sk.id == 14:
        return Decimal(1)
    return sk.cost_point


def normalize_n(sk: Skill, n: int) -> int:
    if n < sk.min_hits:
        return sk.min_hits
    return n


def can_pay(p: Player, sk: Skill, n: int) -> bool:
    if sk.cost_point > 0 and p.points < sk.cost_point * n:
        return False
    if sk.cost_ticket > 0 and p.tickets < sk.cost_ticket * n:
        return False
    return True


def legal_actions(pts, tks):
    """返回所有合法动作 (sid, n) 列表。"""
    pts = Decimal(pts)
    tks = Decimal(tks)
    actions = []
    for sid, sk in SKILLS.items():
        if sk.cost_point > 0:
            n_max = int(pts // sk.cost_point)
            if n_max < 1:
                continue
            if not sk.multi:
                n_max = 1
            for n in range(1, n_max + 1):
                actions.append((sid, n))
        elif sk.cost_point < 0:
            actions.append((sid, 1))
        elif sk.cost_ticket > 0:
            n_max = int(tks // sk.cost_ticket)
            if n_max < 1:
                continue
            if not sk.multi:
                n_max = 1
            for n in range(1, n_max + 1):
                actions.append((sid, n))
        else:
            actions.append((sid, 1))
    return actions


# ==================== 付费 ====================
def pay(p: Player, sk: Skill, n: int):
    if sk.cost_point < 0:
        p.pending_points += -sk.cost_point * n
    elif sk.cost_point > 0:
        p.points -= sk.cost_point * n
    if sk.cost_ticket > 0:
        p.tickets -= sk.cost_ticket * n


# ==================== 防御参数 ====================
def get_def_variant(def_sk: Skill) -> Optional[DefVariant]:
    if def_sk.variants:
        return def_sk.variants.get(JIE)
    return None


def def_valid(def_sk: Skill, atk_sk: Skill) -> bool:
    if atk_sk.is_unblockable:
        return False
    if def_sk.stype not in (NORM, DRAIN, COUNTER):
        return False
    if def_sk.stype == COUNTER:
        return False
    if atk_sk.id in def_sk.def_skill_ids:
        return True
    variant = get_def_variant(def_sk)
    if variant is None:
        return False
    if variant.def_cost_lo is None:
        return False
    sc = single_cost(atk_sk)
    if sc < variant.def_cost_lo:
        return False
    if variant.def_cost_hi is not None and sc > variant.def_cost_hi:
        return False
    if atk_sk.id == 14 and not variant.def_include_ticket:
        return False
    return True


def compute_drain(def_sk: Skill, atk_sk: Skill, n: int):
    if def_sk.stype != DRAIN:
        return ZERO, ZERO
    variant = get_def_variant(def_sk)
    if variant is None:
        return ZERO, ZERO
    if atk_sk.id == 14:
        total_tickets = Decimal(n)
        ratio = ZERO
        for lo, hi, r in variant.drain_tiers:
            if lo <= Decimal(1) <= hi:
                ratio = r
                break
        return ZERO, total_tickets * ratio
    sc = single_cost(atk_sk)
    ratio = ZERO
    for lo, hi, r in variant.drain_tiers:
        if lo <= sc <= hi:
            ratio = r
            break
    return sc * n * ratio, ZERO


# ==================== 结算 ====================
def resolve_atk_vs_atk(sk0: Skill, n0: int, sk1: Skill, n1: int):
    c0 = single_cost(sk0)
    c1 = single_cost(sk1)
    pairs = min(n0, n1)
    dmg0 = ZERO
    dmg1 = ZERO
    for _ in range(pairs):
        if c0 > c1:
            dmg1 += (c0 - c1) * HALF
        elif c1 > c0:
            dmg0 += (c1 - c0) * HALF
    if n0 > pairs:
        dmg1 += sk0.dmg_per_hit * (n0 - pairs)
    if n1 > pairs:
        dmg0 += sk1.dmg_per_hit * (n1 - pairs)
    return dmg0, dmg1


def resolve_atk_vs_def(atk_sk: Skill, n: int, def_sk: Skill):
    if def_valid(def_sk, atk_sk):
        if def_sk.is_rebound:
            return ZERO, atk_sk.dmg_per_hit * n, ZERO, ZERO
        pts, tix = compute_drain(def_sk, atk_sk, n)
        return ZERO, ZERO, pts, tix
    return atk_sk.dmg_per_hit * n, ZERO, ZERO, ZERO


def resolve_pulls(sk0: Skill, sk1: Skill):
    d0 = ZERO
    d1 = ZERO

    def pull_damage(pull_sk, absorb_sk):
        if pull_sk.is_big and absorb_sk.is_big:
            return Decimal(4)
        if pull_sk.is_big or absorb_sk.is_big:
            return Decimal(2)
        return Decimal(1)

    if sk0.is_pull and sk1.is_absorb:
        d1 += pull_damage(sk0, sk1)
    if sk1.is_pull and sk0.is_absorb:
        d0 += pull_damage(sk1, sk0)
    return d0, d1


def resolve(state: GameState, moves: dict):
    p0, p1 = state.players
    m0, m1 = moves.get(0), moves.get(1)
    if m0 is None or m1 is None:
        return

    sk0, n0 = SKILLS[m0[0]], m0[1]
    sk1, n1 = SKILLS[m1[0]], m1[1]

    dmg0 = ZERO
    dmg1 = ZERO
    pts0 = tix0 = ZERO
    pts1 = tix1 = ZERO

    pull_d0, pull_d1 = resolve_pulls(sk0, sk1)
    dmg0 += pull_d0
    dmg1 += pull_d1

    if sk0.stype == ATK and sk1.stype == ATK:
        a, b = resolve_atk_vs_atk(sk0, n0, sk1, n1)
        dmg0 += a
        dmg1 += b
    elif sk0.stype == ATK and sk1.stype in (NORM, DRAIN):
        dd, ad, pts, tix = resolve_atk_vs_def(sk0, n0, sk1)
        dmg1 += dd
        dmg0 += ad
        pts1 += pts
        tix1 += tix
    elif sk1.stype == ATK and sk0.stype in (NORM, DRAIN):
        dd, ad, pts, tix = resolve_atk_vs_def(sk1, n1, sk0)
        dmg0 += dd
        dmg1 += ad
        pts0 += pts
        tix0 += tix
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

    p0.hp -= dmg0
    p1.hp -= dmg1
    p0.pending_points += pts0
    p0.pending_tickets += tix0
    p1.pending_points += pts1
    p1.pending_tickets += tix1


def end_of_round(state: GameState, verbose: bool = False):
    for p in state.players:
        p.points += p.pending_points
        p.tickets += p.pending_tickets
        p.pending_points = ZERO
        p.pending_tickets = ZERO

    # 点数 / 免单封顶
    for p in state.players:
        if p.points > PT_MAX:
            if verbose:
                print(f"  ⚠ {p.name} 点数 {p.points} 超出上限 {PT_MAX}，已重置为 {PT_MAX}")
            p.points = Decimal(PT_MAX)
        if p.tickets > TK_MAX:
            if verbose:
                print(f"  ⚠ {p.name} 免单 {p.tickets} 超出上限 {TK_MAX}，已重置为 {TK_MAX}")
            p.tickets = Decimal(TK_MAX)

    # 死亡判定
    for p in state.players:
        if not p.dead and p.hp <= 0:
            p.dead = True


def check_game_over(state: GameState) -> Optional[str]:
    p0, p1 = state.players
    if p0.dead and p1.dead:
        return "draw"
    if p0.dead:
        return "p1_win"
    if p1.dead:
        return "p0_win"
    return None


def make_state(p: Player, opp: Player):
    """从 p 的视角构造六元组，用于查策略表。"""
    h = max(HP_MIN, min(HP_MAX, int(p.hp * 2)))
    h_opp = max(HP_MIN, min(HP_MAX, int(opp.hp * 2)))
    pt = max(0, min(PT_MAX, int(p.points)))
    pt_opp = max(0, min(PT_MAX, int(opp.points)))
    tk = max(0, min(TK_MAX, int(p.tickets)))
    tk_opp = max(0, min(TK_MAX, int(opp.tickets)))
    return (h, pt, tk, h_opp, pt_opp, tk_opp)