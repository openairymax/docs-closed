# 模块签名与污染位判据台账（V-16 / KM-01）

> 版本: 1.0.0
> 取证日期: 2026-11-02
> 证据级别: E2（内核源码推导，可逐行复算）；E1 实机取证待 285H 复核后补录
> 唯一事实源: `kernel/scripts/sign-file.c`、`kernel/kernel/module/signing.c`
> 判据实现: `ci/lib/modsig.py`（门禁 `ci/gates/module-signature.sh`）

---

## 1. 结论

KM-01 的原文是「镜像内全量 `.ko` 具 `.module_sig` 段且 `modinfo -F sig_id`
非空；`/proc/sys/kernel/tainted` 的 8192 位为 0；T6 kernel identity 实机转绿」。

**前两个分句的前提不成立。** 模块签名不是 ELF 段，而是追加在文件尾部的
`PKCS#7 + struct module_signature + 魔数`；`.module_sig` 段在真实模块里从未
存在过。以它判签的三处消费面全部恒为假，其中内核 spec 的 `%check` 会让
内核包**必然**构建失败，`run-smoke.sh` 的 T6 会让实机冒烟**必然**报未签名。

本版把判据改成与内核同源的三层：

| 层 | 判据 | 判什么 | 实现 |
|---|---|---|---|
| 打包 | 尾部 28 字节等于签名魔数 | 签名已追加（与 `module_sig_check()` 第一道检查一致） | kernel spec `%check`、`run-smoke.sh` T6 |
| 离线复核 | 魔数 + 12 字节结构自洽 + `sig_len` 不吞正文 | 签名块结构合法（与 `mod_check_sig()` 一致） | `ci/lib/modsig.py` |
| 运行期 | `tainted & 8192 == 0` | 内核真的验签通过，没有加载未签名模块 | `run-smoke.sh` T6、`ci/lib/modsig.py` |

三层合起来等价于「签名齐全且内核认可」。只做第一层会漏掉「签了但密钥不匹配」，
只做第三层会在 taint 由别的原因置位时误判，故三层都要。

---

## 2. 签名是追加的，不是段

### 2.1 写入侧

`scripts/sign-file.c` 把模块读入 `bd`，正文写完后写 PKCS#7 DER，再把
`sig_size`（仅 PKCS#7 长度）写进 12 字节信息块，最后写魔数：

- `scripts/sign-file.c:222` — `struct module_signature sig_info = { .id_type = PKEY_ID_PKCS7 };`
- `scripts/sign-file.c:398-401` — `sig_info.sig_len = htonl(sig_size)` 后依次写
  信息块与 `magic_number`
- `scripts/sign-file.c:77` — `magic_number[] = "~Module signature appended~\n"`

最终布局（PKCS#7 构型）：

```
[ 模块正文（已 strip） ][ PKCS#7 DER 签名 ][ struct module_signature 12B ][ 魔数 28B ]
```

`module_signature.h:23-32` 的注释列了「签名者名 / 密钥标识 / 签名数据 / 信息块」，
那是给 PGP 与 X.509 两种 legacy 构型留的位置；PKCS#7 构型把签名者与密钥标识
收进 PKCS#7 容器本身，信息块里 `signer_len` 与 `key_id_len` 恒为 0，所以尾部
**没有**任何可读的签名者标识块。

### 2.2 读取侧

`kernel/module/signing.c` 的读取顺序与写入侧严格对称：

- `signing.c:70-92` `module_sig_check()`：取末尾 `sizeof(MODULE_SIG_STRING) - 1`
  即 28 字节与魔数比较；不等则 `err = -ENODATA`（下文按 "unsigned module"
  处理）。相等则先截掉 28 字节，再调 `mod_verify_sig()`。
- `signing.c:43-67` `mod_verify_sig()`：从截断后的缓冲尾部拷出 12 字节
  `struct module_signature`，交 `mod_check_sig()` 自洽检查；通过后
  `modlen -= sig_len + sizeof(ms)`，以 `VERIFY_USE_SECONDARY_KEYRING` 调
  `verify_pkcs7_signature(mod, modlen, mod + modlen, sig_len, ...)`。
- `signing.c:119-124` 未开 `CONFIG_MODULE_SIG_FORCE` 时不拒绝加载，只调
  `security_locked_down(LOCKDOWN_MODULE_SIGNATURE)`。
- `kernel/module/main.c:2053-2058`：`!mod->sig_ok` 时
  `add_taint_module(mod, TAINT_UNSIGNED_MODULE, LOCKDEP_STILL_OK)`。

`TAINT_UNSIGNED_MODULE` 在 `kernel/panic.c:484` 对应字母 `E`，位序号 13，
即 `/proc/sys/kernel/tainted` 的 **8192**。

### 2.3 结构自洽的三条硬约束

`kernel/module_signature.c:21-46` 的 `mod_check_sig()` 是唯一权威判据，
`ci/lib/modsig.py` 逐条对齐：

1. `sig_len < file_len - 12`：签名段不能吞掉模块正文，否则 `-EBADMSG`；
2. `id_type == PKEY_ID_PKCS7(2)`：否则 `-ENOPKG`（"not signed with expected
   PKCS#7 message"）；
3. `algo / hash / signer_len / key_id_len / __pad[3]` 全为 0：否则 `-EBADMSG`。

第 3 条意味着：在 PKCS#7 构型下，任何非零的 `signer_len` 或 `key_id_len`
都是非法签名块，不是「更完整的签名」。校验器对 `id_type=1`（X.509 legacy）
只要求两个长度非零，对其它 `id_type` 直接判非法，与内核语义一致。

### 2.4 可信钥匙环

`arch/x86/configs/openeuler_defconfig` 的相关项：

| 配置 | 值 | 行 |
|---|---|---|
| `CONFIG_MODULE_SIG` | `y` | 978 |
| `CONFIG_MODULE_SIG_ALL` | `y` | 980 |
| `CONFIG_MODULE_SIG_HASH` | `"sha256"` | 987 |
| `CONFIG_MODULE_SIG_FORCE` | 未开 | 979 |
| `CONFIG_MODULE_SIG_KEY` | `"certs/signing_key.pem"` | 9037 |
| `CONFIG_MODULE_SIG_KEY_TYPE_RSA` | `y` | 9038 |
| `CONFIG_SYSTEM_TRUSTED_KEYS` | `""` | 9041 |

密钥与信任链：

- `certs/Makefile:43-63`：当 `CONFIG_MODULE_SIG_KEY` 为 `certs/signing_key.pem`
  且文件不存在时，用 `openssl req -new -nodes -x509` 现场生成（RSA 或
  secp384r1，取决于 `CONFIG_MODULE_SIG_KEY_TYPE_ECDSA`）。
- `certs/Makefile:66`：`system_certificates.o` 依赖 `signing_key.x509`。
- `certs/system_certificates.S:12`：把 `certs/signing_key.x509` 以 `.incbin`
  编进 `system_certificate_list` 的 `__module_cert_start/end` 区间。
- `certs/system_keyring.c:286-294`：开 `CONFIG_MODULE_SIG` 时整段证书列表
  （含 `signing_key.x509`）装入 `builtin_trusted_keys`；二级钥匙环链接到
  builtin（`system_keyring.c:253`），故 `VERIFY_USE_SECONDARY_KEYRING` 能
  解析到它。

`CONFIG_SYSTEM_TRUSTED_KEYS=""` 不影响这条链：该宏只追加额外的 CA，签名
证书是独立编入的。`load_module_cert()`（`system_keyring.c:265-274`）只在
`CONFIG_IMA_APPRAISE_MODSIG` 下启用，不是模块加载验签路径。

### 2.5 安装期签名时机

`scripts/Makefile.modinst:99-121`：`modules_install` 规则是
`cmd_install → cmd_strip → cmd_sign`，`cmd_sign` 为

```
scripts/sign-file $(CONFIG_MODULE_SIG_HASH) "$(sig-key)" certs/signing_key.x509 $@
```

且 `ifndef CONFIG_MODULE_SIG_ALL` 时 `cmd_sign := :`。本项目
`CONFIG_MODULE_SIG_ALL=y`，所以**安装进 `%{buildroot}` 的每个 `.ko` 都已签**，
`%install` 不需要、也不应该再补签。

---

## 3. 三处假判定与其根因

| 位置 | 原判据 | 后果 | 处置 |
|---|---|---|---|
| `distro/specs/kernel/airymaxos-kernel.spec` `%install` | 抽样一个 `.ko`，`readelf -S` 找 `.module_sig` 段，找不到就再签一次 | 判据恒假，在已签模块上再叠加一份 PKCS#7，尾部结构被破坏 | 整段删除（0.0.3-7 引入，0.0.4-2 移除） |
| 同 spec `%check` | 全量 `readelf -S` 找 `.module_sig` | 恒假 ⇒ 内核包**必然**构建失败 | 改为尾部 28 字节魔数全量比对 |
| `distro/ci/run-smoke.sh` T6 | 抽查一个模块的 `.module_sig` 段；taint 文件缺失时当 0 放行 | 实机**必然**报未签名；taint 缺失被静默放过 | 改为全量尾部比对 + taint 严格判定（缺失/非整数即失败） |

根因是同一个：把「签名」理解成 ELF 段。三处各自修补会留下三套口径，
所以统一收敛到「尾部结构」这一个事实，再按判定代价分层（见 §1 表）。

附属缺陷：`distro/tools/tests/test_run_smoke.py` 的夹具原先不写 taint 文件，
恰好被旧代码「缺失当 0」放行，使回归无法发现该分支。修判据时同时给夹具补
`write_taint(0)`，并新增「1/2 未签名」「taint 不可读」两个负例。

---

## 4. 判据分层与消费面

| 消费面 | 判定内容 | 退出码 |
|---|---|---|
| kernel spec `%check`（仅 `CONFIG_MODULE_SIG_ALL=y` 时） | `find … -name '*.ko'` 全量，尾部 28 字节等于魔数；`total > 0` 且 `unsigned == 0` | 构建失败 |
| `run-smoke.sh` T6 | 同上，外加 `tainted` 可读、十进制、`& 8192 == 0` | T6 失败 |
| `ci/gates/module-signature.sh` | 结构层（§2.3 三条）+ 污染位；`--kind struct\|taint\|all`、`--kernel REL`、`--taint FILE` | `0` 通过 / `1` 不通过 / `5` 证据不可用 |
| `ci/tests/test_module_signature.sh` | 负例驱动：28 条断言，逐条破坏单一前提 | `0` / `1` |

分层理由：打包与冒烟只需回答「签名在不在」，用 Bash 尾部比对即可，零依赖、
在内核包内也能跑；结构自洽需要读 12 字节并做大小端解释，放 Python 校验器，
由门禁在镜像树上跑。两处判据同源（都来自 `module_sig_check()` /
`mod_check_sig()`），不是两套标准。

退出码 `5` 是刻意的：缺 `usr/lib/modules`、空模块树、`tainted` 不可读、
遇到压缩模块，都属于「证据不可用」，不能当通过，也不能当不合格——后者会
把取证环境问题误报成产品缺陷。

---

## 5. 与 KM-01 原文的偏差

| 原文 | 实际 | 处置 |
|---|---|---|
| `.ko` 具 `.module_sig` 段 | 不存在该段；签名追加在文件尾部 | 判据改为尾部魔数 + 结构自洽 |
| `modinfo -F sig_id` 非空 | `sig_id` 的数据来源是尾部的签名者标识块；PKCS#7 构型下 `signer_len=key_id_len=0`，该块为空 | 不作为判据；改用结构自洽 + 运行期 taint |
| `tainted` 8192 位为 0 | 成立，且与 `module_sig_check()` 的失败分支一一对应 | 保留，作为唯一能证明「内核认可」的判据 |

偏差需要回写方案：KM-01 的验收口径以本台账为准，V-16 的完成判据为
「`ci/ci.sh module-signature --root <镜像根>` 退 0」加「285H 实机 T6 转绿」。

---

## 6. 已知边界

### 6.1 同 NEVRA 两次构建不可逐字节复现

`CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"` 且仓库不带该文件时，
`certs/Makefile:47-53` 每次构建用 `openssl req` 现场生成一对新密钥。
密钥不同 ⇒ `signing_key.x509` 不同 ⇒ `system_certificate_list` 不同 ⇒
`vmlinuz` 与全部 `.ko` 的尾部 PKCS#7 不同 ⇒ 同一 NEVRA 的两次构建
**sha256 必然不同**。

这与方案 §1.1 判据②（内核 NEVRA 两次构建 sha256 相同）直接冲突。本版
不伪装可复现：判据②对内核包按「镜像内自洽」解释——同一次构建产出的
`vmlinuz` 与模块由同一份 `signing_key.x509` 签署，且该证书编在同一份
`vmlinuz` 里。彻底解决需要把签名密钥外置为构建输入（固定私钥 + 吊销策略），
属于密钥管理议题，不在本版范围，登记为已知边界。

影响面仅限可复现性审计，不影响运行：每台机器上「内核内编的证书」与
「模块尾部的签名」始终配对。

### 6.2 压缩模块不可离线判定

`openeuler_defconfig` 为 `CONFIG_MODULE_COMPRESS_NONE=y`，本版镜像里全是
未压缩 `.ko`，尾部比对成立。若将来开启压缩，签名在压缩**之前**写入
（`Makefile.modinst` 的 `cmd_sign` 先于压缩规则），魔数被封进压缩流，
读文件尾部只会得到压缩帧。

校验器对此的处理是**退 5 并提示解压**，而不是把「读不到魔数」误报成
「未签名」：误报为不合格会让排障朝错误方向走。开关压缩时需同步让门禁
在解压后的树上跑。

### 6.3 `%check` 的判据比门禁弱一层

spec 的 `%check` 只做尾部魔数（Bash、无 Python 依赖，保证内核包自身可构建）；
结构自洽与 taint 由门禁在镜像树上补。这是有意的能力分层，不是遗漏：
构建期拿不到运行期 taint，而结构自洽在内核包内做需要引入 Python 依赖，
收益不抵成本。

---

## 7. 285H 实机取证步骤

在 285H 上装好 0.0.4 镜像、以产品内核启动后，按序执行（全部只读）：

1. `uname -r` 应为 `6.6.157-alk`（`-alk` 来自 `CONFIG_LOCALVERSION`）。
2. `grep -E '^CONFIG_MODULE_SIG(_ALL|_FORCE)?=' /boot/config-$(uname -r)`
   应得 `y`、`y`、未开。
3. `cat /proc/sys/kernel/tainted`；`$(( $(cat …) & 8192 ))` 应为 0。
   若为 8192 或含该位，读 `dmesg | grep -i 'module verification failed'`
   定位是哪个模块。
4. 全量尾部比对：
   `find /usr/lib/modules/$(uname -r) -name '*.ko' -exec sh -c '…tail -c 28…' _ {} +`
   或直接跑门禁（见 5）。
5. 门禁离线复核：
   `ci/ci.sh module-signature --root /` —— 结构层 + 污染位一次判完。
6. 桌面会话内跑 `run-smoke.sh`，T6 必须 PASS。
7. 把第 1–6 步的实际输出（`tainted` 值、模块总数、T6 行）回填本节，
   证据级别由 E2 升为 E1。

---

## 8. 维护约定

- 判据只允许改一处：`ci/lib/modsig.py`。spec 与 `run-smoke.sh` 的 Bash
  比对只允许保留「尾部魔数」这一条最弱判据，不得复制结构解析。
- 内核升级后先复核 `struct module_signature` 的字段序与
  `mod_check_sig()` 的约束，再动校验器；`include/linux/module_signature.h`
  与 `kernel/module_signature.c` 是本台账的事实源。
- 修改本文件时同步检查三处消费面是否仍与 §4 的表一致。

---

> **文档结束** | AgentRT 开源维护团队
