# Harness 报错回传故障的归因与单处修复

一个最小化的 Agent 评测实验：证明「执行层把报错截断成 `Error: failed`」会让 Agent 盲重试、浪费 token，并通过对单零件的修复把它修好。

## 做了什么

- 自建最小 Harness（模型 → 提交代码 → 隐藏测试 → 回传结果），模拟实验室「报错被截断」的故障。
- 黑盒验收：模型读不到源码和测试，失败回传是唯一诊断通道。
- 控制变量：只改「信息回传」一个零件（diff 仅一行 `MODE`），同题同模型复测。

## 核心结论

1. 是 Harness 的锅，不是模型、不是题目。
2. 是「信息回传」零件（`format_feedback`）的锅——它把真实报错截断成 `Error: failed`，模型失去唯一线索只能穷举。
3. 证据等级：token（1268→364，−71%）与重试（4.4→2.0 轮）为硬证据（置信区间不重叠）；通过率（7/10→10/10）N=10 太小，仅观察。

## 结果

| 指标 | truncated | full |
|---|---|---|
| 通过率 | 7/10 | 10/10 |
| 平均重试 | 4.4 轮 | 2.0 轮 |
| 平均 token | 1268 | 364 |

## 怎么跑

```bash
pip install openai
export DEEPSEEK_API_KEY=你的key      # Windows cmd: set DEEPSEEK_API_KEY=你的key
python hello_api.py                  # 第 1 步：验证 API
python harness.py                    # 第 2 步：自测 harness
python run_batch.py                  # 第 4/5 步：跑批（MODE 在 harness.py 顶部改）
```

## 文件结构

- `harness.py`：最小执行层（唯一变量 `format_feedback`）
- `task.py`：题目（is_leap + 题面故意漏规则）
- `verifier.py`：隐藏测试 + 错误过滤层
- `run_batch.py`：跑批 + 轨迹采集
- `report.md`：完整报告（结论 + 置信区间 + 局限）
- `TASK.md`：任务书　`LOG.md`：项目日志
