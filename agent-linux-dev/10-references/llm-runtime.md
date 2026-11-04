# 本地大模型运行环境台账（K-20 / K-21）

> 版本: 1.0.0
> 取证日期: 2026-11-04
> 证据级别: E2（打包面与判定分支由门禁逐条复算）；E1 目标机推理待加权重复验后补录
> 唯一事实源: 清单 `/var/lib/airy-llm/manifest.json` 与 `state/status.json`
> 判据实现: `ci/gates/model-manifest.sh`、`ci/gates/llm-offline.sh`、`ci/gates/llm-accel.sh`
> 登记册: docs-linux `140-application-development/06-agent-deployment.md`

---

## 1. 结论

K-20 要求「大模型运行环境预置，装机即可用，不依赖联网」；K-21 要求「模型资产
以摘要绑定，不符即硬失败」。

0.0.3 的镜像里 preset 钉着 `airy-llm.service`，配方却没有交付该单元与它要的
包：装机后单元因为找不到可执行文件而进入 failed，模型状态从任何服务视图都
看不出来。更隐蔽的是「模型目录存在」被当成「模型可用」——权重半份、摘要不符、
引擎路径不存在，三种状态在目录列表里都是几个文件。

本版把运行环境拆成三层，各有唯一事实源：

| 层 | 事实源 | 结论 |
|---|---|---|
| 交付面 | 装机镜像内的入口、包、单元、preset | 缺任一项则装机后不可用，由门禁在构建期判死 |
| 资产面 | `/var/lib/airy-llm/manifest.json` 记录的 sha256 | 缺件、尺寸或摘要不符即硬失败，不写入任何目标文件 |
| 运行面 | `state/status.json` 与 `ConditionPathExists` | 无清单则单元不启动，状态查询退 4 而不是报 ok |

## 2. 镜像内交付面

| 物件 | 路径 | 门禁断言 |
|---|---|---|
| 入口 | `/usr/bin/airy-model` | `model-manifest.sh` |
| 包 | `%{python3_sitelib}/airyllm` | `model-manifest.sh`（`source-bundle`、归档名、`%files`） |
| 单元 | `/usr/lib/systemd/system/airy-llm.service` | `model-manifest.sh`（`StateDirectory=airy-llm`、`ConditionPathExists`） |
| preset | `disable airy-llm.service` | `model-manifest.sh` |
| 数据根 | `/var/lib/airy-llm` | 单元 `StateDirectory`，装机即建 |

单元默认 disabled 是刻意的：没有清单的机器上拉起一个必然失败的推理服务，只会
把「没装模型」伪装成「服务故障」。装了资产之后由 `boot-set` 清单启用，启用位
与其它单元共用同一份清单，不另写一份。

## 3. 引擎与权重不进 RPM

权重以 GB 计，不随系统包发布；推理引擎由清单给绝对路径。两者都由安装介质或
离线资产包提供，经 `airy-model install` 收进运行根：同尺寸同摘要则跳过，已损坏
的副本被源文件替换，每件资产经临时文件原子落位，清单最后落位作为提交点。

这条边界让镜像保持可复现：同一份镜像在带模型与不带模型的机器上字节一致，
模型的有无只由清单表达，不由镜像内容表达。

## 4. 为什么没有独立的 `distro/comps/airyllm.xml`

施工图的产出物栏把 `distro/comps/airyllm.xml` 列为 K-20 的交付件。本版没有
新建该文件，理由是构建链只有一份包组声明：

- `distro/scripts/build-desktop.sh` 用 `createrepo_c --groupfile` 建库，只收
  一个文件；
- `distro/scripts/lib/closure.sh` 与 `ci/gates/fw-closure.sh` 的 `COMPS` 常量
  指向 `distro/comps/airymaxos-comps.xml`，闭包与种子校验都只读这一份；
- `ks_spec.py` 校验 kickstart 点名的包是否被 comps 覆盖，同样只收一个入参。

再建一份不被任何环节读取的 comps，就是一条「看起来声明了、实际不生效」的
死声明——比不声明更容易误导：它会让后来的人以为改那份文件能改变镜像内容。

实际交付面也不缺包组：`airymaxos-system` 已含 `airyllm` 包与 `airy-model` 入口，
kickstart 按包名直接安装，不经包组。因此 K-20 的「预置」由单元与包显式交付，
不引入第二份包组声明。若将来出现独立 RPM 形态的推理引擎，正确的做法是把该
包组并入 `airymaxos-comps.xml`，仍然保持单一 comps。

## 5. 判定与降级

- 清单缺失 → 单元不启动，`airy-model status` 退 4（absent），与「加载失败」分开。
- 摘要不符或文件大小不符 → 退 1（failed），错误字段给出 `sha256` / `size`，
  不回落到上一个版本。
- 加速后端不可用 → 退回 CPU 路径并在报告里写明 `backend=cpu`，不静默降级。
- 单元被强制拉起而没有资产 → 由运行层的摘要校验判失败，不让它冒充就绪。

## 6. 取证命令

```
ci/gates/model-manifest.sh            # 交付面：入口、包、单元、preset
ci/gates/llm-offline.sh               # 离线：代码与单元里没有运行期网络请求
ci/gates/llm-accel.sh                 # 加速：后端探测与降级路径
airy-model status --json              # 运行面：state / backend / reason / digest
```

## 7. 验收记录

| 项 | 结论 | 级别 |
|---|---|---|
| 交付面四项齐全 | 通过（`model-manifest.sh`） | E2 |
| 离线约束 | 通过（`llm-offline.sh`） | E2 |
| 后端降级不静默 | 通过（`llm-accel.sh`） | E2 |
| 目标机首次推理（含加速） | 待复验 | E1 待补 |
