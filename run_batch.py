"""第 4 步（v2）：跑批脚本。固定变量跑 N 次，采集轨迹存 JSON。"""
import json

import harness
from task import TASK_DESC, setup
from verifier import check

N = 10
OUT = f"results_v2_{harness.MODE}.json"


def main():
    results = []
    for i in range(1, N + 1):
        setup()  # 每次重置 solution.py 到初始 bug 状态
        passed, rounds, tokens, trace = harness.solve(TASK_DESC, verifier=check)
        results.append(
            {
                "run_id": i,
                "mode": harness.MODE,
                "passed": passed,
                "total_rounds": rounds,
                "total_tokens": tokens,
                "trace": trace,
            }
        )
        print(f"run {i}/{N}: passed={passed}, rounds={rounds}, tokens={tokens}")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    n_pass = sum(1 for r in results if r["passed"])
    avg_rounds = sum(r["total_rounds"] for r in results) / N
    avg_tokens = sum(r["total_tokens"] for r in results) / N
    print(f"\n汇总：通过率 {n_pass}/{N}，平均重试 {avg_rounds:.1f} 轮，平均 token {avg_tokens:.0f}")
    print(f"轨迹已存：{OUT}")


if __name__ == "__main__":
    main()
