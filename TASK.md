# 任务书：报错回传故障的归因与单处修复

> 本文件是项目唯一行动依据。每完成一步，在底部「完成状态」勾选，防止跑偏。

## 一句话目标

证明「工具失败后只回 `Error: failed`」会让模型盲重试；把回传改成「stderr 关键行 + 退出码」后，同题同模型重跑，通过率 / 重试次数 / token 明显改善——且该变化只可能来自「信息回传」这一个零件。

## 已定参数（不可随意改动）

| 项 | 值 |
| --- | --- |
| 模型 | DeepSeek `deepseek-chat`，base_url `https://api.deepseek.com` |
| API key | 从环境变量 `DEEPSEEK_API_KEY` 读取，绝不硬编码 |
| 跑批次数 N | 10 |
| 轮次上限 | 8 轮（超限判 fail） |
| 隔离环境 | 本地 subprocess（先跑通方法，Docker/DSH 后续替换） |
| 指标 | 通过率、平均重试次数（= 直到 pass/超限的总轮数）、平均 token |

## 全局约定（最高优先级）

**只允许变一个东西**：`harness.py` 里的 `format_feedback` 函数。
其余全部锁死：模型、题目、环境、判分器、轮次上限、N。

## 分步任务

### 第 1 步：打通 API（约 30 分钟）
- 写 `hello_api.py`：用 key 调一次模型，打印回复 + `usage.total_tokens`。
- 验收：`python hello_api.py` 能看到回复和 token 数。
- 前置：`pip install openai`；`export DEEPSEEK_API_KEY=你的key`。

### 第 2 步：搭最小 harness（约 2 小时，全天最难）
写 `harness.py`，三个部件：
1. `run(command)`：subprocess 执行 shell 命令，返回 `(exit_code, stdout, stderr)`。
2. `format_feedback(exit_code, stdout, stderr, command, mode)` —— **唯一变量零件**：
   - `mode="truncated"`：成功回 stdout，失败只回 `Error: failed`。
   - `mode="full"`：回「命令 + 退出码 + stderr 关键行」。
3. `solve(task, mode)` 主循环：固定 system prompt（目标 + 两个工具：`bash` 执行命令、`write_file` 写文件；每次只输出一个 JSON）→ 调模型 → 执行 → verifier 判 pass → 未 pass 则 `format_feedback` 回喂 → 再调模型……最多 8 轮。加 `write_file` 是因为 Windows 下改文件不能用 `sed`/`cat` 等 bash 命令，用 Python 写文件保证跨平台。
- 验收：`python harness.py` 自测（不调模型），看到 truncated 回传 `Error: failed`、full 回传完整错误，改 `mode` 立刻变化。完整三环等 verifier 就位后（第 3 步）在第 4 步验证。

### 第 3 步：写题目 + 外部判分器（约 1 小时）
- 写 `task.py`：生成初始文件 `app.py`，内容为「`import nonexistent_pkg_xyz` 然后 `print("OK")`」。
- 写 `verifier.py`：subprocess 跑 `python app.py`，退出码 0 且 stdout 含 `OK` → pass，否则 fail + 原因。
- 为什么用这个题：包名独一无二注定不存在 → 环境无关、结果可控。截断版模型会疯狂 `pip install` 瞎烧轮次；完整版一眼看到 `ModuleNotFoundError` 转去改脚本。
- 验收：手动跑一次，verifier 正确判 fail；删掉 import 再跑，判 pass。

### 第 4 步：跑基线（坏版本，约 1.5 小时）
- 写 `run_batch.py`，固定 `mode="truncated"`，同题同模型跑 N=10 次，每次轨迹存 JSON。
- 轨迹字段：`run_id / mode / 每轮{round, model_output, command, exit_code, feedback_text, verifier_pass} / final{pass, total_rounds, total_tokens}`。
- 统计：通过率、平均重试次数、平均 token。
- 验收：拿到基线表 + 10 份轨迹，能指着一份轨迹说出「模型因只看到 failed 多试了 X 次」。

### 第 5 步：单处修复 + 复验（约 1 小时）
- **只改 `format_feedback`**（`truncated` → `full`），其余一个字符不动。
- 用同一个 `run_batch.py`、同样 N=10、同题同模型重跑。
- 验收：确认 diff 里只有 `format_feedback` 变了。

### 第 6 步：对比结论（约 1 小时）
- 写 `report.md`：前后对比表（通过率 / 平均重试 / 平均 token）。
- 结论三句话：是不是 harness 的锅 → 是「信息回传」零件 → 证据多硬。
- 证据等级：通过率差用 Wilson 区间或 bootstrap，token/重试用均值差（可配 bootstrap）；若区间含 0，老实写「证据不够」。

## 文件清单

| 文件 | 作用 |
| --- | --- |
| `hello_api.py` | 验证 API 通不通 |
| `harness.py` | 最小执行层（含唯一变量零件） |
| `task.py` | 题目 + 初始文件生成 |
| `verifier.py` | 外部判分 |
| `run_batch.py` | 跑批 + 轨迹采集 |
| `report.md` | 对比表 + 归因结论 |

## 时间账（约 8 小时）

第1步 0.5h → 第2步 2h → 第3步 1h → 第4步 1.5h → 第5步 1h → 第6步 1h，留 1h 缓冲。

## 完成状态

- [x] 第 1 步：打通 API
- [x] 第 2 步：搭最小 harness
- [x] 第 3 步：写题目 + 外部判分器
- [ ] 第 4 步：跑基线（坏版本，N=10）
- [ ] 第 5 步：单处修复 + 复验（好版本，N=10）
- [ ] 第 6 步：对比结论 report.md

---

## 升级方案 v2（2026-11-17 起，v1 暂停于第 4 步）

**为什么升级**：v1 题目无区分度（坏版本 10/10）。根因：模型通过「读文件」旁路绕过「信息回传」截断。

**升级核心**：堵死所有旁路，让「失败回传」成为唯一诊断通道。

**改动方向**：
1. 题目：改为「修复 solution.py，通过隐藏验收测试」（题面给不完整的功能描述，边界只藏在测试里）。
2. 工具集：砍掉通用 bash 和读文件，改为 `submit`（提交补丁）+ `check`（运行验收）。
3. 新增「错误过滤层」：删掉报错里的源码片段 / 敏感信息 / 真实路径，模型只收结构化结果。
4. 唯一变量不变：`format_feedback`（truncated → 只回 `Error: failed`；full → 回过滤后的关键错误）。

**信息流（已修正）**：
模型提交补丁 → 诊断服务运行隐藏测试 → 错误过滤 → 模型收到结构化结果 → 再提交……（循环）

**题目定稿（用户主导）**：
- 题面：请实现 `is_leap(year)`，判断闰年；规则是「年份能被 4 整除」（故意漏掉 100/400 例外）。
- 初始 `solution.py`：`def is_leap(year): return year % 4 == 0`（buggy 版本）。
- 隐藏测试（13 个年份 + 预期）：1900/2100/2200/2300→False；2000/2400/1600→True；2024/2028/1996→True；2023/2025/2026→False。

**工具设计**：只保留 `submit`（提交代码）；每次提交后 harness 自动跑隐藏测试并回传结果。verifier 返回的失败详情只含「测试输入/期望/实际」（不含源码）＝错误过滤层。

**探针结果（2026-11-17）**：题面连发 3 次，模型 3 次都写 `year % 4 == 0` → 踩坑，v2 成立。

**v2 进度**：
- [x] 第 2 步：搭 harness（submit 工具）
- [x] 第 3 步：出题（is_leap + 隐藏测试 13 例）
- [x] 第 4 步：跑基线 truncated（7/10，3 次失败；轨迹证实「截断导致瞎猜」）
- [x] 第 5 步：单处修复（MODE → full）+ 复验（10/10，2.0 轮，364 token）
- [x] 第 6 步：对比结论（report.md）
