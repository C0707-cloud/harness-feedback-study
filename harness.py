"""第 2 步（v2）：最小 harness（信息回传归因实验）。

唯一变量零件：format_feedback（行为由 MODE 控制）。
工具集：只保留 submit（提交代码）。每次提交后自动跑隐藏测试。
"""
import json
import os

from openai import OpenAI

MAX_ROUNDS = 8

# 本实验唯一变量：第 5 步把 "truncated" 改成 "full"，其余代码一律不动。
MODE = "full"

SYSTEM_PROMPT = """你是运行在 Windows 环境里的 Agent，目标由用户给出。
你每次只能提交一次代码，且只输出一个 JSON 对象，不要输出任何其他文字：
{"tool": "submit", "code": "完整的 Python 代码"}
提交后系统会自动运行验收测试并回传结果。"""


def submit(code):
    """把代码写入 solution.py。"""
    with open("solution.py", "w", encoding="utf-8") as f:
        f.write(code)


def format_feedback(passed, detail):
    """信息回传零件——本实验唯一变量，行为由 MODE 决定。"""
    if passed:
        return "通过。"
    if MODE == "truncated":
        return "Error: failed"
    return f"测试失败：{detail}"


def solve(task_desc, verifier=None, max_rounds=MAX_ROUNDS):
    """跑一次完整 Agent 循环，返回 (passed, total_rounds, total_tokens, trace)。"""
    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task_desc},
    ]
    total_tokens = 0
    trace = []
    for r in range(1, max_rounds + 1):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=2000,
        )
        total_tokens += resp.usage.total_tokens
        content = resp.choices[0].message.content
        try:
            action = json.loads(content)
        except json.JSONDecodeError:
            fb = "你上一轮没输出合法 JSON，请重新只输出一个 JSON 对象。"
            trace.append(
                {
                    "round": r,
                    "model_output": content,
                    "code": None,
                    "feedback_text": fb,
                    "verifier_pass": None,
                }
            )
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": fb})
            continue

        passed = False
        if action.get("tool") != "submit":
            fb = "未知工具，只能用 submit。"
            code = None
        else:
            code = action.get("code", "")
            submit(code)
            passed, detail = verifier() if verifier else (False, "no verifier")
            fb = format_feedback(passed, detail)

        trace.append(
            {
                "round": r,
                "model_output": content,
                "code": code,
                "feedback_text": fb,
                "verifier_pass": passed,
            }
        )

        if passed:
            return True, r, total_tokens, trace

        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": fb})
    return False, max_rounds, total_tokens, trace


if __name__ == "__main__":
    # 自测：不调模型，验证 verifier 判出 bug 失败 + format_feedback 截断
    from task import setup
    import verifier

    setup()
    passed, detail = verifier.check()
    print("初始 solution.py 判分:", passed, "| 详情:", detail)
    print("--- 当前 MODE 回传 ---")
    print(format_feedback(passed, detail))
