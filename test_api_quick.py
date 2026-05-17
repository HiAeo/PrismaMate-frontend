# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

print("测试 API 连接...")

# 测试注册
import time
email = f"test_{int(time.time())}@example.com"
print(f"注册用户: {email}")

try:
    resp = requests.post(f"{API_BASE}/auth/register", json={
        "email": email,
        "username": f"user_{int(time.time())}",
        "password": "test123456"
    })
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text[:500]}")
except Exception as e:
    print(f"错误: {e}")
