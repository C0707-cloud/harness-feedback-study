"""第 3 步（v2）：题目定义 + 初始文件生成。"""
TASK_DESC = (
    "请实现一个函数 is_leap(year)，判断给定年份是否为闰年。"
    "闰年的判断规则是：年份能被 4 整除。"
)


def setup():
    """重置 solution.py 为初始（有 bug 的）状态。"""
    with open("solution.py", "w", encoding="utf-8") as f:
        f.write("def is_leap(year):\n    return year % 4 == 0\n")


if __name__ == "__main__":
    setup()
    print("已生成 solution.py")
