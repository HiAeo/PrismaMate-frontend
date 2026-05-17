# test_deepseek_api.py
# DeepSeek API 连通性验证脚本
# 验证 API Key、连通性、品牌提及提取、引用提取
#
# 使用方法：
# 1. 设置环境变量 DEEPSEEK_API_KEY
# 2. pip install openai requests
# 3. python test_deepseek_api.py

import os
import time
import json
import re
from datetime import datetime
from typing import Optional


# 品牌提及测试列表
TEST_BRANDS = [
    "华为", "阿里巴巴", "腾讯", "百度", "字节跳动",
    "OpenAI", "Google", "Microsoft", "Apple", "Meta"
]


def load_api_key() -> str:
    """从环境变量加载 API Key"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("❌ 环境变量 DEEPSEEK_API_KEY 未设置")
    return api_key


def call_deepseek_api(api_key: str, keyword: str, model: str = "deepseek-chat") -> dict:
    """调用 DeepSeek API"""
    import requests

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": keyword}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    elapsed = time.time() - start_time

    if response.status_code != 200:
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}",
            "elapsed": elapsed
        }

    result = response.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    return {
        "success": True,
        "content": content,
        "model": model,
        "elapsed": elapsed,
        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
    }


def extract_brand_mentions(text: str, brands: list) -> list:
    """从文本中精确匹配品牌名"""
    mentions = []
    for brand in brands:
        # 精确匹配整个词
        pattern = re.compile(rf'\b{re.escape(brand)}\b')
        matches = pattern.findall(text)
        if matches:
            # 获取匹配位置和上下文
            for match in matches:
                start = text.index(match)
                end = start + len(match)
                context_before = text[max(0, start-20):start]
                context_after = text[end:min(len(text), end+20)]
                mentions.append({
                    "brand": brand,
                    "context": f"...{context_before}{match}{context_after}..."
                })
    return mentions


def extract_citations(text: str) -> list:
    """提取文本中的 URL 引用"""
    # 匹配常见 URL 格式
    url_pattern = re.compile(
        r'https?://[^\s\)\]\}\'\"\<\>]+',
        re.IGNORECASE
    )
    urls = url_pattern.findall(text)

    # 去重并返回
    return list(set(urls))


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("DeepSeek API 连通性验证测试")
    print("=" * 60)

    results = {
        "test_date": datetime.now().isoformat(),
        "platform": "DeepSeek API",
        "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
        "tests": [],
        "summary": {}
    }

    # 测试 1: 加载 API Key
    print("\n[测试 1] 检查 API Key...")
    try:
        api_key = load_api_key()
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"  ✓ API Key 加载成功: {masked_key}")
        results["tests"].append({
            "name": "api_key_load",
            "status": "PASS",
            "detail": f"Key: {masked_key}"
        })
    except ValueError as e:
        print(f"  ✗ {e}")
        results["tests"].append({
            "name": "api_key_load",
            "status": "FAIL",
            "error": str(e)
        })
        results["summary"]["overall"] = "FAIL"
        save_and_exit(results)
        return

    # 测试 2: 基本 API 连通性
    print("\n[测试 2] API 连通性检查...")
    test_keyword = "请用一句话介绍人工智能"
    api_result = call_deepseek_api(api_key, test_keyword)
    if api_result["success"]:
        print(f"  ✓ API 调用成功")
        print(f"    - 响应时间: {api_result['elapsed']:.2f}s")
        print(f"    - Token 消耗: {api_result['tokens_used']}")
        print(f"    - 回答长度: {len(api_result['content'])} 字符")
        results["tests"].append({
            "name": "api_connectivity",
            "status": "PASS",
            "response_time": api_result["elapsed"],
            "tokens_used": api_result["tokens_used"]
        })
    else:
        print(f"  ✗ API 调用失败: {api_result['error']}")
        results["tests"].append({
            "name": "api_connectivity",
            "status": "FAIL",
            "error": api_result["error"]
        })
        results["summary"]["overall"] = "FAIL"
        save_and_exit(results)
        return

    # 测试 3: 品牌提及提取
    print("\n[测试 3] 品牌提及提取测试...")
    brand_test_keyword = "请介绍一下华为、阿里巴巴和腾讯这三家公司的业务"
    brand_result = call_deepseek_api(api_key, brand_test_keyword)
    if brand_result["success"]:
        mentions = extract_brand_mentions(brand_result["content"], TEST_BRANDS)
        unique_brands = list(set(m["brand"] for m in mentions))
        print(f"  ✓ 提取到 {len(mentions)} 处品牌提及")
        print(f"    - 涉及品牌: {', '.join(unique_brands) if unique_brands else '无'}")
        if mentions:
            print(f"    - 示例上下文: {mentions[0]['context'][:80]}...")
        results["tests"].append({
            "name": "brand_extraction",
            "status": "PASS" if mentions else "PARTIAL",
            "mentions_count": len(mentions),
            "brands_found": unique_brands,
            "response": brand_result["content"][:500] + "..."
        })
    else:
        print(f"  ✗ API 调用失败: {brand_result['error']}")
        results["tests"].append({
            "name": "brand_extraction",
            "status": "FAIL",
            "error": brand_result["error"]
        })

    # 测试 4: 引用提取
    print("\n[测试 4] 引用来源提取测试...")
    citation_keyword = "请介绍一下量子计算，并提供一个相关链接"
    citation_result = call_deepseek_api(api_key, citation_keyword)
    if citation_result["success"]:
        citations = extract_citations(citation_result["content"])
        print(f"  ✓ 提取到 {len(citations)} 个 URL 引用")
        if citations:
            for i, url in enumerate(citations[:3], 1):
                print(f"    - [{i}] {url[:80]}...")
        else:
            print(f"    - 未提取到 URL（可能是 AI 没有提供外部链接）")
        results["tests"].append({
            "name": "citation_extraction",
            "status": "PASS",
            "citations_count": len(citations),
            "citations": citations[:5]  # 最多保存5个
        })
    else:
        print(f"  ✗ API 调用失败: {citation_result['error']}")
        results["tests"].append({
            "name": "citation_extraction",
            "status": "FAIL",
            "error": citation_result["error"]
        })

    # 测试 5: 连续调用稳定性（3次）
    print("\n[测试 5] 连续调用稳定性测试（3次）...")
    stability_times = []
    for i in range(3):
        kw = f"第 {i+1} 次测试：什么是机器学习？"
        r = call_deepseek_api(api_key, kw)
        if r["success"]:
            stability_times.append(r["elapsed"])
            print(f"    第 {i+1} 次: {r['elapsed']:.2f}s - ✓")
        else:
            print(f"    第 {i+1} 次: FAIL - {r['error']}")
            stability_times.append(None)

    valid_times = [t for t in stability_times if t]
    if len(valid_times) == 3:
        avg_time = sum(valid_times) / len(valid_times)
        print(f"  ✓ 3 次调用全部成功，平均响应时间: {avg_time:.2f}s")
        results["tests"].append({
            "name": "stability_test",
            "status": "PASS",
            "times": stability_times,
            "avg_time": avg_time
        })
    else:
        print(f"  ⚠ {len(valid_times)}/3 次成功")
        results["tests"].append({
            "name": "stability_test",
            "status": "PARTIAL",
            "times": stability_times,
            "success_count": len(valid_times)
        })

    # 汇总
    all_pass = all(t["status"] in ["PASS"] for t in results["tests"])
    any_fail = any("FAIL" in t["status"] for t in results["tests"])
    results["summary"]["overall"] = "PASS" if all_pass else ("PARTIAL" if not any_fail else "FAIL")

    # 建议
    if results["summary"]["overall"] == "PASS":
        results["summary"]["recommendation"] = "DeepSeek API 完全可用，优先采用 API 模式实现适配器"
    elif results["summary"]["overall"] == "PARTIAL":
        results["summary"]["recommendation"] = "DeepSeek API 基本可用，但部分功能需优化"
    else:
        results["summary"]["recommendation"] = "DeepSeek API 存在问题，建议检查配置或联系支持"

    save_and_exit(results)


def save_and_exit(results: dict):
    """保存结果并退出"""
    # 保存报告
    report_path = "deepseek_api_test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 打印汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    for test in results["tests"]:
        status_icon = "✓" if test["status"] == "PASS" else ("⚠" if test["status"] == "PARTIAL" else "✗")
        print(f"  {status_icon} {test['name']}: {test['status']}")
    print(f"\n总体结论: {results['summary']['overall']}")
    print(f"建议: {results['summary']['recommendation']}")
    print(f"\n详细报告: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
