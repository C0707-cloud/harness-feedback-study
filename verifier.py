"""第 3 步（v2）：外部判分器（隐藏测试 + 错误过滤层）。

check() 用子进程跑隐藏测试，返回 (passed, detail)。
detail 只含「测试输入/期望/实际」，不含源码 —— 这就是错误过滤层。
"""
import subprocess

TESTS = [
    (1900, False), (2100, False), (2200, False), (2300, False),  # 世纪年非闰年
    (2000, True), (2400, True), (1600, True),                    # 世纪年闰年
    (2024, True), (2028, True), (1996, True),                    # 普通闰年
    (2023, False), (2025, False), (2026, False),                 # 普通平年
]

TEST_CODE = '''
import sys
try:
    import solution
except Exception as e:
    print(f"加载 solution 失败：{type(e).__name__}: {e}")
    raise SystemExit(1)
tests = __TESTS__
for year, expected in tests:
    try:
        got = solution.is_leap(year)
    except Exception as e:
        print(f"is_leap({year}) 抛异常：{type(e).__name__}: {e}")
        raise SystemExit(1)
    if got != expected:
        print(f"is_leap({year}) expected {expected}, got {got}")
        raise SystemExit(1)
print("PASS")
'''


def check():
    """运行隐藏测试，返回 (passed, detail)。detail 只含输入/期望/实际，不含源码。"""
    code = TEST_CODE.replace("__TESTS__", repr(TESTS))
    proc = subprocess.run(
        ["python", "-c", code],
        capture_output=True, text=True, timeout=30,
    )
    if proc.returncode == 0:
        return True, proc.stdout.strip()
    return False, proc.stdout.strip()


if __name__ == "__main__":
    passed, detail = check()
    print("通过" if passed else f"未通过：{detail}")
