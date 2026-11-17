"""第 1 步：验证 DeepSeek API 是否打通，并确认能读到 token 用量。

运行前：
  pip install openai
  export DEEPSEEK_API_KEY=你的key
运行：
  python hello_api.py
验收：能看到模型回复 + 本次 token 用量。
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "回复一句话：你好"}],
    max_tokens=50,
)

print("模型回复：", resp.choices[0].message.content)
print("本次 token 用量：", resp.usage.total_tokens)
