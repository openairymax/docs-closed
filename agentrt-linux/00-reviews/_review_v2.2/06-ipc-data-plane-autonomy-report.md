# 06 — IPC 数据面自治缺陷报告

> **审计日期**：2026-07-16
> **审查范围**：07-ipc-fastpath.md 的状态机设计 + 03-capability-model.md 的 capability 设计
> **核心问题**：控制面离线时数据面能否自治？当前方案未覆盖此场景。

---

## 1. 问题起源

近 10 轮对话的用户第 9 条消息指出的核心问题：

> "airymax 的 IPC 设计里，控制面离线，数据面能否自治？"

---

## 2. 现状分析

### 2.1 07-ipc-fastpath.md 的覆盖

| 场景 | 覆盖状态 | 详情 |
|------|---------|------|
| fastpath 正常 SEND/RECV | 完整 | 8 状态 × 4 操作码 × 边界条件 |
| slowpath 回退 | 完整 | kfifo 满/跨 CPU/payload/加密 降级 |
| magic 校验失败 | 覆盖 | → ERROR, AIRY_EPROTO |
| **capability daemon 离线** | **未覆盖** | C-S9 失败 → ERROR，无离线降级 |
| **控制面恢复后 reconciliation** | **未覆盖** | 无恢复流程 |
| 背压机制 | 覆盖 | HI_WMARK 75% → 背压 |

### 2.2 C-S9（fastpath capability 检查）的设计空缺

fastpath 触发条件 C-S9：

> `airy_cap_check_fast()` 内联 capability 检查——fastpath 内联（OS-SEC-121）

当前设计：`airy_cap_check_fast()` 做位掩码比较，成功 → 继续，失败 → ERROR，返回 `AIRY_ECAPABILITY`。

**问题**：如果 capability daemon 离线（例如节点重启、守护进程崩溃），但 ring 已建立且 capability 已验证，C-S9 应该通过还是失败？

- 如果通过：数据面自治，但可能使用已过期的 capability
- 如果失败：数据面停顿，直到控制面恢复——违反"数据面自治"原则

**缺失的设计**：离线缓存校验机制。

### 2.3 03-capability-model.md 的覆盖

| 场景 | 覆盖状态 |
|------|---------|
| CNode 数据结构 | 完整（93 字节 airy_cnode） |
| MDB 派生链 | 完整（mint/mintcopy/derive/revoke） |
| 12 种 cap 类型 | 完整 |
| Token 生命周期 | 完整（创建/派生/撤销/过期） |
| **capability 离线校验** | **未覆盖** |
| **capability 缓存结构** | **未覆盖** |
| **控制面恢复 reconciliation** | **未覆盖** |

---

## 3. 缺失的设计

### 3.1 Capability 离线缓存校验

当下需要定义如下数据结构（存在于 ipc.h 的 reserved 字段或独立的 cap_cache.h）：

```c
/* Ring 建立时由控制面绑定，数据面只读 */
struct airy_ring_cap_cache {
    __u32 ring_id;       /* ring 标识符 */
    __u64 badge;         /* 权限掩码（在 ring 创建时绑定） */
    __u64 expires_ns;    /* 过期时间（0 = 永不过期，CLOCK_REALTIME） */
};
```

fastpath C-S9 的离线版本：

```c
static inline bool airy_cap_check_cached(
    const struct airy_ring_cap_cache *cache,
    uint64_t required_cap)
{
    /* expires_ns=0 表示永不过期 */
    if (cache->expires_ns != 0 &&
        get_realtime_ns() > cache->expires_ns)
        return false;
    return (cache->badge & required_cap) == required_cap;
}
```

**关键安全保障**：badge 是 ring 创建时由控制面通过完整性校验后绑定到 ring 的，用户态无法伪造。控制面离线不等于安全失效——已绑定的 badge 继续有效，直到过期。

### 3.2 控制面恢复 Reconciliation

控制面恢复后的五步 reconciliation：

```
步骤 1: 扫描所有活跃 ring → 收集 (ring_id, badge, agent_id) 列表
步骤 2: 对照 capability CNode 表 → 检查 badge 是否被撤销或权限变更
步骤 3: 对已撤销的 ring → 设置 RING_F_REVOKED 标志
步骤 4: 对权限变更的 ring → 更新 badge 缓存
步骤 5: 输出 reconciliation 报告 → debugfs + 事件通知
```

### 3.3 与 seL4 Endpoint 状态机的对照

| seL4 Endpoint | agentrt-linux 数据面自治 |
|--------------|----------------------|
| Endpoint 创建后，Send/Recv 不需要内核再干预 | Ring 创建后，send/recv 不需要控制面再参与 |
| Badge 在 Bind 时绑定，后续不可变 | Badge 在 ring 创建时由控制面绑定，数据面只读 |
| Capability 撤销通过 Revoke 递归 | Capability 撤销通过 reconciliation 在恢复时批量执行 |
| Badge 未过期则继续有效 | expires_ns 检查，永不过期=0 |

### 3.4 数据面自治三原则

| 原则 | 描述 | 对应的设计决策 |
|------|------|-------------|
| **Ring 生命周期与控制面解耦** | 创建/销毁由控制面，send/recv 由数据面 | 控制面离线不影响已建立的 ring |
| **Capability 离线缓存校验** | ring 创建时 badge 绑定，数据面只读检查 | 不需要在线询问 daemon 即可校验 |
| **控制面恢复 Reconciliation** | 恢复后批量检查所有 ring 的权限一致性 | 不与数据面操作竞争，安全无窗口期 |

### 3.5 fastpath 状态机扩展

需要在 [07-ipc-fastpath.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md) §2.3 状态转换表中增加控制面离线路径：

| 当前状态 | 事件 | 新状态 | 动作 |
|---------|------|--------|------|
| (新增) IDLE | SEND 且 C-S9 在线校验失败 | → ERROR | 返回 AIRY_ECAPABILITY |
| (新增) IDLE | SEND 且控制面离线 + C-S9c 缓存校验通过 | → FAST_SEND | 使用离线缓存校验 |
| (新增) IDLE | SEND 且控制面离线 + C-S9c 缓存校验失败 | → SLOW_SEND | 降级等待控制面恢复 |
| (新增) IDLE | RECV 且控制面离线 + C-S9c 缓存校验通过 | → FAST_RECV | 使用离线缓存校验 |

---

## 4. 建议

1. **编写 IPC 数据面自治设计文档**：三原则 + 离线校验 + Reconciliation
2. **扩展 ipc.h**：reserved[84] 中定义 ring_id (4B) + badge (8B) + expires_ns (8B)
3. **扩展 07-ipc-fastpath.md**：增加控制面离线状态转换
4. **扩展 03-capability-model.md**：增加离线缓存校验 + Reconciliation 流程
5. **实现 airy_cap_check_cached()**：内核态内联函数
6. **实现 airy_ring_reconcile()**：控制面恢复入口
7. **设计 debugfs 接口**：查看控制面在线状态 + ring 缓存状态
