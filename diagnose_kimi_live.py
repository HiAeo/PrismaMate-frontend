#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kimi API 诊断脚本 - 在线诊断
直接调用 Kimi API，获取原始响应格式，诊断适配器问题
"""
import os
import sys
import json
import traceback

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "prismamate-backend"))

# 设置 PYTHONPATH
os.environ.setdefault("PYTHONPATH", os.path.join(os.path.dirname(__file__), "prismamate-backend"))

print("=" * 60)
print("Kimi API 在线诊断")
print("=" * 60)

# ============================================================
# 步骤1: 读取 API Key
# ============================================================
print("\n[步骤1] 读取 API Key...")
api_key_path = os.path.join(os.path.dirname(__file__), "API KEY.txt")
if os.path.exists(api_key_path):
    with open(api_key_path, "r", encoding="utf-8") as f:
        content = f.read()
        for line in content.split("\n"):
            line_lower = line.lower()
            if "kimi" in line_lower and "api" in line_lower:
                # 跳过注释行
                if line.strip().startswith("#"):
                    continue
                # 尝试找到冒号或等号后的 key
                for sep in [":", "：", "="]:
                    if sep in line:
                        parts = line.split(sep, 1)
                        if len(parts) == 2:
                            potential_key = parts[1].strip().strip('"').strip("'")
                            if potential_key.startswith("sk-"):
                                os.environ["KIMI_API_KEY"] = potential_key
                                print(f"  [OK] 找到 Kimi API Key: {potential_key[:10]}...{potential_key[-4:]}")
                                break
                break
else:
    print("  [ERROR] API KEY.txt 不存在")
    sys.exit(1)

if not os.environ.get("KIMI_API_KEY"):
    print("  [ERROR] 未找到 KIMI_API_KEY")
    sys.exit(1)

# ============================================================
# 步骤2: 直接调用 Kimi API
# ============================================================
print("\n[步骤2] 直接调用 Kimi API...")
import requests

url = "https://api.moonshot.cn/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['KIMI_API_KEY']}"
}
payload = {
    "model": "moonshot-v1-8k",
    "messages": [{"role": "user", "content": "你好，请回复 OK"}],
    "temperature": 0.3
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"  HTTP 状态码: {response.status_code}")
    print(f"  响应头: {dict(response.headers)}")
    
    raw_json = response.json()
    print(f"\n[步骤2a] 原始 JSON 响应 (完整):")
    print(json.dumps(raw_json, ensure_ascii=False, indent=2))
    
    # 提取 content
    print(f"\n[步骤2b] 提取 choices[0].message.content:")
    try:
        content = raw_json["choices"][0]["message"]["content"]
        print(f"  内容: {content}")
    except (KeyError, IndexError, TypeError) as e:
        print(f"  ✗ 提取失败: {e}")
        print(f"  choices 类型: {type(raw_json.get('choices'))}")
        print(f"  choices 值: {raw_json.get('choices')}")
    
    api_success = response.status_code == 200
    
except Exception as e:
    print(f"  ✗ API 调用失败: {e}")
    traceback.print_exc()
    api_success = False

# ============================================================
# 步骤3: 调用 KimiAdapter.search()
# ============================================================
print("\n" + "=" * 60)
print("[步骤3] 调用 KimiAdapter.search()...")

if api_success:
    try:
        from app.adapters.kimi_adapter import KimiAdapter
        
        print("  导入 KimiAdapter 成功")
        adapter = KimiAdapter()
        print(f"  adapter 对象创建成功: {adapter}")
        
        # 调用 search
        print("\n  调用 adapter.search(keyword='测试')...")
        result = adapter.search(keyword="测试品牌检测")
        
        print(f"\n[步骤3a] 适配器返回结果 (完整):")
        print(f"  类型: {type(result)}")
        print(f"  内容: {json.dumps(result, ensure_ascii=False, indent=4)}")
        
        # 检查 result 的结构
        print(f"\n[步骤3b] 检查 result 结构:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {type(value).__name__} = {repr(value)[:200]}")
        
    except Exception as e:
        print(f"\n  ✗ KimiAdapter 调用失败!")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {e}")
        print(f"\n  完整堆栈:")
        traceback.print_exc()
else:
    print("  ⚠ 跳过适配器测试（API 调用失败）")

# ============================================================
# 步骤4: 检查适配器内部结构
# ============================================================
print("\n" + "=" * 60)
print("[步骤4] 检查 KimiAdapter 内部结构...")

try:
    from app.adapters.kimi_adapter import KimiAdapter
    
    adapter = KimiAdapter()
    
    # 检查 _api_search 方法
    print("\n  检查 _api_search 方法源码...")
    import inspect
    api_search_source = inspect.getsource(adapter._api_search)
    
    # 查找可能的问题
    print("\n  查找潜在的 'for ... in' 模式:")
    for i, line in enumerate(api_search_source.split("\n"), 1):
        if "for " in line and " in " in line:
            print(f"    行 {i}: {line.strip()}")
    
    # 查找可能的 Field 引用
    print("\n  查找 Field 引用:")
    for i, line in enumerate(api_search_source.split("\n"), 1):
        if "Field" in line:
            print(f"    行 {i}: {line.strip()}")
            
except Exception as e:
    print(f"  ✗ 检查失败: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
