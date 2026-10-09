import pickle

with open("jie_V.pkl", "rb") as f:
    V = pickle.load(f)
with open("jie_pi.pkl", "rb") as f:
    pi = pickle.load(f)

print(f"V 条目数: {len(V)}")
print(f"pi 条目数: {len(pi)}")

# 1. V 值范围
vals = list(V.values())
print(f"\nV 范围: min={min(vals):.4f}, max={max(vals):.4f}")
print(f"V 均值: {sum(vals)/len(vals):.4f}")

# 2. 检查键结构
sample_key = next(iter(V))
print(f"\n示例键: {sample_key}（应为 6 个整数）")

# 3. 检查策略概率和
bad_probs = 0
for state, dist in pi.items():
    s = sum(dist.values())
    if abs(s - 1.0) > 1e-3:
        bad_probs += 1
        if bad_probs <= 3:
            print(f"概率和异常: {state} -> {s:.6f}")
print(f"\n概率和异常状态数: {bad_probs}")

# 4. 对称性检查：V(h0,pt0,tk0,h1,pt1,tk1) 应约等于 -V(h1,pt1,tk1,h0,pt0,tk0)
asym_count = 0
max_asym = 0
for state, v in V.items():
    h0, pt0, tk0, h1, pt1, tk1 = state
    mirror = (h1, pt1, tk1, h0, pt0, tk0)
    if mirror in V:
        diff = abs(v + V[mirror])
        max_asym = max(max_asym, diff)
        if diff > 0.05:
            asym_count += 1
print(f"\n对称性: 最大不对称={max_asym:.4f}, 不对称状态数={asym_count}")

# 5. 边界检查：双方 HP=2、点数=0、免单=0，V 应该接近 0
key = (4, 0, 0, 4, 0, 0)
if key in V:
    print(f"\n初始状态 V{(4,0,0,4,0,0)} = {V[key]:.4f}（应接近 0）")

# 6. 绝对优势：HP=2 vs HP=0.5、点数=20 vs 0
key = (4, 20, 2, 1, 0, 0)
if key in V:
    print(f"碾压状态 V{(4,20,2,1,0,0)} = {V[key]:.4f}（应接近 1.0）")

# 7. 抽样查看策略
print("\n=== 抽样状态 ===")
for key in [(4, 0, 0, 4, 0, 0), (2, 5, 1, 2, 5, 1), (1, 20, 0, 4, 0, 0)]:
    if key in pi:
        print(f"\n状态 {key}:")
        for action, p in sorted(pi[key].items(), key=lambda x: -x[1])[:5]:
            print(f"  动作 {action}: {p:.4f}")