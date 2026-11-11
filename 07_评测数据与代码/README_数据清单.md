# Benchmark 代码与数据清单

> 更新：2026-11-02；git clone 仓库的 commit 为本地 `git rev-parse HEAD`，ACESEvals/ACES 为 codeload zip 快照，commit 来自 GitHub API。  
> 说明：代码下载不等于数据齐全；需要申请/大体量的条目见 `10_手工补充/材料缺口清单.md`。

## 1. Benchmark 代码快照

| Benchmark | 本地目录 | Commit | 大小 | License | 数据状态 |
|---|---|---|---|---|---|
| DefenderBench | `DefenderBench/` | `e431098e217ee6778f572df202785f1a705df167` | 498 MB | 代码：Microsoft Departing Intern License（需复核）；数据：上游许可未单独核对 | 代码 + `data_raw/`；CTI MCQ 2,500 题、phishing 20,137 texts / 15,756 webs；未按脚本预处理 |
| Cyber Defense Benchmark | `cyber_defense_benchmark/` | `e8b86d01ccefe338d455e61505ca285943635b27` | 22 MB | MIT | 含 `datasets/sample.zip`（约 11 MB，解压 `sample.json` 约 355,895,823 B）；完整数据需申请 |
| CyberGym | `CyberGym/` | `c6fe2027d39471375920b92cf1025e23a99ffda5` | 500 KB | Apache-2.0 | 仅代码；完整数据约 240 GB，未下载 |
| CAIBench | `CAIBench/` | `6dc79257777f5f1c9500b4d2319935d34a47412e` | 37 MB | MIT + 研究用途 proprietary 混合 | sparse checkout 含 `benchmarks` + `src/cai`；数据完整性/运行依赖未验证 |
| SecRL / ExCyTIn-Bench | `SecRL/` | `a1b234f7a846133f08b7b5e1614c5c63b96f3b5c` | 2.6 GB（含数据包） | MIT | 含 85 个问题/README 文件；`data_anonymized.tar.gz` 已下载并校验；未解压 |
| ACESEvals（推荐新 harness） | `ACESEvals/` | `2c76fbdea415d6fa6a87bbad846686fefd6ee9bb`（main zip） | 121 MB | MIT | 含 `cti_realm`、`cybench`、`excytin`（12 MB）、`eval_ranges`（80 MB）；`external/saber` 已补 `microsoft/ACES` 快照 `a9bdce1343fd1c331aafda3119cbf0d48f215382`（MIT）；未运行 `uv`/`inspect eval` |

### 1.1 DefenderBench 原始数据

- 位置：`DefenderBench/data_raw/`；这是手动下载的原始文件，不是 `defenderbench` 的 cache 目录。
- `cti-mcq.tsv`：`2,394,094` B（2,501 行，含表头，即 2,500 题），sha256 `11e0af8db2dae9706c6e79901d2390bcdf9746e8feccbd9ba10682df649bcc6a`；来源 `https://huggingface.co/datasets/AI4Sec/cti-bench`。
- `phishing-texts.json`：`52,079,789` B，20,137 条，sha256 `2479fdb94abb59332cc747f7b823a1651921b9828240c5dad0ffdba66ab02581`；来源 `https://huggingface.co/datasets/ealvaradob/phishing-dataset`。
- `phishing-webs.json`：`465,420,302` B，15,756 条，sha256 `cad05dd39b6384e1fe2f0880852004eeb1bed704394544e523decb193190f3f0`。
- 合计 `519,894,185` B（约 496 MiB）；`cti`/`phishing` 的预处理脚本尚未运行，需 `pandas`/`sklearn` 及仓库 cache 布局。

## 2. ExCyTIn-Bench 数据

- 数据源：`https://huggingface.co/datasets/anandmudgerikar/excytin-bench`
- 本地文件：`SecRL/secgym/database/data_anonymized.tar.gz`
- 压缩大小：`1,643,989,896` B
- SHA-256：`61ecd48685e4eb34cac226a0651fd6443174f6efaa628aea3b06aef2cb088720`
- 完整性：`gzip -t` 通过；sha256 与 Hugging Face 的 `x-linked-etag` 一致
- 解压后：约 `20.46 GB`
- 运行约束：解压 + Docker MySQL（8 个库约 10 GB；全集约 33 GB）；当前剩余磁盘约 27 GB，**未解压**
- 问题文件：`SecRL/secgym/questions/` 共 85 个文件（`o1/v0`、`o1/v1`、`o3/v0`、`o3/v1`、`opus5`）。README 中的旧路径 `o1/test` 已重组为 `o1/v1/test`；`o1/v0` 有账户邮箱合成 bug，建议用 `o1/v1`（已修正）或 `opus5`（1017 题，599 test / 418 train）。

## 3. 数据下载/解压命令

```bash
# CyberGym 全量（约 240 GB；确认磁盘后再执行）
# 参见 CyberGym/README.md 与 https://huggingface.co/datasets/sunblaze-ucb/cybergym

# Cyber Defense 完整数据：按 README 联系 research@simbian.ai

# ExCyTIn 解压（需约 20.5 GB 空闲；解压到 secgym/database/）
tar -xzf SecRL/secgym/database/data_anonymized.tar.gz -C SecRL/secgym/database/
```

## 4. 产品/行业代码快照

| 项目 | 本地目录 | Commit | 大小 | License 备注 |
|---|---|---|---|---|
| Agentic SOC Platform | `09_产品与行业资料/repos/agentic-soc-platform/` | `2da9bb33a62bcc73fbfac364b1051da069b457ee` | 9.9 MB | 根目录未发现 `LICENSE`；使用前需确认授权 |
| AlertINT Agent | `09_产品与行业资料/repos/alertint-agent/` | `f4c5bf1ae321e4818f8f638b50ee701d11705bd9` | 24 MB | FSL-1.1-ALv2（source-available，非 OSI 开源） |
| DeepSOC | `09_产品与行业资料/repos/deepsoc/` | `f7b47b5ed5a30a74b17ee2e93f55e16ff196f961` | 20 MB | MIT |

> 复用代码/图表/数据前先读对应 LICENSE；`README_数据清单.md` 只记录事实，不构成授权。
