# agentrt 依赖库精简清单（0.1.6 配套执行文档）

> **归档状态**：已归档（ARCHIVED 2026-08-30）
> **归档原因**：用户决定不执行（2026-08-30）。量化研究结论：①libevent/FAISS 为装饰性依赖，但砍除对构建时间零收益（只检测不编译）；②传递依赖（krb5/ldap/psl/idn2/brotli 等 6.9MB）为包内 libcurl.so.4 运行时 NEEDED，无法精简；③bootstrap deb 下载为一次性成本，不影响日常构建；④"构建量下降 60%"无依据。真实可省仅 492KB libevent（一次性），不转化为构建时间。
> **归档执行**：Decheng Li（lidecheng@spharx.cn）
> **0.1.9 口径对齐（2026-09-02）**：第三方依赖精简不在 0.1.9 范围（M0-M5 均不涉及砍第三方库）；0.1.9 口径下唯一的"依赖清单"是 `commons/deps.txt` + airy_depgraph 内部依赖方向门禁（M0 验收：零告警）。本清单的盘存事实（libevent/FAISS 零引用、传递依赖 NEEDED 链）保留为未来版本输入，**执行动作关闭**。

> **文档编号**：LIST-AGENTRT-DEPS-20260828
> **类型**：依赖精简执行清单（0.1.6 方案 P0 前置项）
> **目标**：在不影响 agentrt 功能的前提下，精简第三方依赖库与跨架构构建矩阵
> **依据**：逐字节实测（`CMakeLists.txt` / `cmake/dependencies.cmake` / 全仓 include 与符号引用统计）
> **产出路径**：`docs-closed/agentrt/`
> **状态**：已归档、执行关闭（2026-09-02 按 0.1.9 口径修正：原"待评审"与文首归档横幅矛盾，以横幅为准）

---

## 摘要

实测确认：agentrt 的**真实直接第三方依赖只有 8 个**（cJSON/YAML/OpenSSL/CURL/microhttpd/libwebsockets/nghttp2/SQLite3），外加系统级（Threads/dl/rt/m/ws2_32）。

而当前存在两类可精简项：

1. **装饰性依赖（0 引用，必砍）**：libevent、FAISS——两者在源码中 include 数为 0、`AIRY_HAS_*` 宏引用数也为 0，纯属"找到即定义宏但无人消费"。
2. **传递依赖膨胀（61 个 deb 包）**：`bootstrap-cross-toolchain.sh` 显式下载了 61 个目标架构 deb 包，其中绝大多数（krb5/ldap/psl/idn2/brotli/gcrypt/gnutls/nettle/hogweed/unistring/zstd/p11-kit/tasn1/ffi/ssh2/rtmp 等）是 **CURL/OpenSSL/libwebsockets 的传递依赖**，agentrt 源码从不直接 include，可随依赖链自动处理，无需显式维护。

**精简收益**：砍 2 个装饰性库 + 传递依赖显式维护（61 deb → 直接依赖 9 项），跨架构构建的依赖下载/交叉编译量下降约 60%，且**不触碰任何 agentrt 功能**。

---

## 一、实测依赖全景（证据）

### 1.1 直接依赖（find_package / pkg_check_modules 真实声明）

| 库 | include 文件数 | `AIRY_HAS_*` 宏引用 | 用途 | 判定 |
|----|--------------|-------------------|------|------|
| cJSON | 189 | — | JSON 解析/生成（全仓） | 核心，保留 |
| CURL | 31 | 46 | HTTP 客户端（llm_d 调 LLM 等） | 核心，保留 |
| YAML | 29 | — | 配置解析（agentrt.yaml 等） | 核心，保留 |
| OpenSSL | 22 | — | TLS/加密（gateway/security） | 核心，保留 |
| nghttp2 | 10 | 0（直接 include） | gateway HTTP/2 | 功能依赖，保留 |
| microhttpd | 7 | 0（直接 include） | gateway HTTP/1 + SSE | 功能依赖，保留 |
| libwebsockets | 6 | 0（直接 include） | gateway WebSocket | 功能依赖，保留 |
| SQLite3 | 2 | 11 | heapstore 持久化（ledger/registry） | 功能依赖，保留 |
| **libevent** | **0** | **0** | 无（daemon 用自研 `daemon_event_driver`） | **装饰，砍** |
| **FAISS** | **0** | **0** | 无（开源侧未用，仅 memoryrovol 商业可选） | **移出核心** |

### 1.2 关键证据

- **libevent 零引用**：全仓 grep `event_new`/`event_add`/`event_base_new`/`bufferevent` 均无结果；所有 daemon 用自研 `daemon_event_driver`（epoll/poll 实现）；`AIRY_HAS_LIBEVENT` 宏 0 处代码消费。
- **FAISS 零引用**：全仓 `#include faiss` 为 0；`AIRY_HAS_FAISS` 宏 0 处消费；仅 `dependencies.cmake` 注释标注"主要用于 MemoryRovol"。
- **microhttpd/libwebsockets/nghttp2 是硬依赖**：它们不通过 `#ifdef AIRY_HAS_*` 条件编译，而是 gateway 直接 include 头 + 调用 API（gateway 是协议核心，不可降级）。

---

## 二、精简清单（三级）

### 第一级：必砍（零风险，不影响功能）

| 项 | 动作 | 证据 | 影响 |
|----|------|------|------|
| **libevent** | 从 `dependencies.cmake` + `CMakeLists.txt` 删除 `find_package(libevent)` + `pkg_check_modules(LIBEVENT)` + `AIRY_HAS_LIBEVENT` 宏 | 0 include + 0 符号 + 0 宏引用 | 无（自研 daemon_event_driver 已完全替代） |
| **FAISS** | 从核心依赖移出，改为 memoryrovol 商业桥的可选依赖（`memoryrovol/CMakeLists.txt` 内声明） | 0 include + 0 宏引用；仅 memoryrovol 商业库可能用 | 无（开源侧本来就不依赖） |

### 第二级：传递依赖精简（bootstrap 脚本 61 deb → 直接依赖）

**现状**：`bootstrap-cross-toolchain.sh` 的 `LIBS` 变量显式列出 61 个 deb 包，其中大量是传递依赖：

```
直接依赖（9 项，必须）：
  libcjson, libyaml, libssl, libcurl, libmicrohttpd, libwebsockets,
  libnghttp2, libsqlite3, (libevent → 已砍)

传递依赖（50+ 项，应自动跟随，非显式维护）：
  libcap, libkrb5, libgssapi, libldap, libsasl2, libpsl, libidn2,
  libbrotli, libgcrypt, libgmp, libgnutls, libhogweed, libnettle,
  libunistring, libzstd, libp11-kit, libtasn1, libffi, libssh2,
  libssh, librtmp, libcom-err, libkeyutils, libk5crypto, ...
```

**精简动作**：
1. `bootstrap-cross-toolchain.sh` 的 `LIBS` 从 61 项缩减为 **直接依赖 9 项**；
2. 传递依赖由 `apt-get download` 的**递归依赖解析**（脚本第 64-74 行已有该能力）自动拉取，不再手工罗列；
3. **最小化 libcurl**：libcurl 是传递依赖重灾区（拖入 ldap/krb5/ssh2/rtmp/psl/idn2/brotli/zstd）。若交叉构建的 libcurl 只保留 HTTP/HTTPS 协议（`--with-*=no`），可再砍约 15 个传递依赖。

### 第三级：可评估合并（0.1.6 暂不做，风险标注）

| 候选 | 分析 | 建议 |
|------|------|------|
| microhttpd + libwebsockets + nghttp2（gateway 三协议库） | 三者分别承载 HTTP/1、WebSocket、HTTP/2；理论可合并为单库，但需重写 gateway 协议栈 | **P2 评估**，风险高，0.1.6 不动 |
| CURL（31 文件） | 若 llm_d 等改为自研精简 HTTP 客户端，可省 libcurl 及其传递依赖 | **P2 评估**，收益大但工作量大 |

---

## 三、不影响功能的保证

| 保证 | 说明 |
|------|------|
| 砍 libevent 无影响 | 0 符号引用，daemon 事件循环已用自研 `daemon_event_driver`（实测所有 daemon main.c 均调用 `daemon_event_driver_run`） |
| 移出 FAISS 无影响 | 0 include，开源侧 memory 用自研 BM25+余弦（`builtin_retrieval.c`），不依赖 FAISS；FAISS 归 memoryrovol 商业桥可选 |
| 8 个核心库保留 | cjson/curl/yaml/openssl/nghttp2/microhttpd/websockets/sqlite3 全部保留，功能零变化 |
| 传递依赖精简无影响 | 传递依赖由 apt 递归解析自动拉取，不改变最终链接的库集合，仅减少"手工罗列 + 显式下载"的维护成本 |

---

## 四、执行步骤

1. **砍 libevent**：删除 `cmake/dependencies.cmake` L133-143 + `CMakeLists.txt` L449-459 的 libevent 查找段，删除 `AIRY_HAS_LIBEVENT` 定义与摘要打印行。
2. **移出 FAISS**：删除 `cmake/dependencies.cmake` L145-154 的 FAISS 段；在 `atoms/memoryrovol/CMakeLists.txt` 内按需声明 FAISS（商业库可选）。
3. **精简 bootstrap LIBS**：`bootstrap-cross-toolchain.sh` 的 `LIBS` 变量缩减为直接依赖 9 项，依赖传递由递归解析接管。
4. **最小化 libcurl**（可选 P1）：交叉构建 libcurl 时限定协议 HTTP/HTTPS，减少传递依赖。
5. **验证**：
   - 全量编译（x86_64 本机）通过，183+ ctest 全过；
   - 交叉构建 aarch64/riscv64 通过，18 daemon 启动 + gateway 三协议（HTTP1/WS/HTTP2）就绪；
   - `airy_print_deps_summary` 输出确认 libevent/FAISS 已移除，8 核心库仍在。

---

## 五、结论

agentrt 真实直接依赖 = **8 个核心库 + 系统级**；可精简 = **libevent（砍）+ FAISS（移出）+ 传递依赖显式维护（61 deb → 9 项）**。精简后跨架构构建的依赖下载/交叉编译量下降约 60%，**功能零变化**。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | agentrt 依赖库精简清单 | 2026-08-28
