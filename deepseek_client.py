import requests
import json
import time
from config import DEEPSEEK_API_KEY

def chat(messages, max_tokens=2000, temperature=0.3, retries=3):
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    
    for attempt in range(retries):
        try:
            resp = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=90)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                print(f"DeepSeek API error {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"DeepSeek API attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    return None