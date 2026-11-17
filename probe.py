"""探针：验证模型看到 v2 题面后，第一版会不会踩闰年的坑。"""
import os
from openai import OpenAI

TASK = (
    "请实现一个函数 is_leap(year)，判断给定年份是否为闰年。"
    "闰年的判断规则是：年份能被 4 整除。"
    "请只输出 Python 代码，不要解释。"
)

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

for i in range(1, 4):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": TASK}],
        max_tokens=500,
    )
    print(f"--- 第 {i} 次 ---")
    print(resp.choices[0].message.content)
    print()
