# deepseek_feasibility_test.py
# DeepSeek 平台可行性测试脚本
# 独立运行，不依赖项目框架
#
# 使用方法：
# 1. pip install playwright
# 2. python -m playwright install chromium
# 3. python deepseek_feasibility_test.py

import asyncio
import json
from datetime import datetime

from playwright.async_api import async_playwright


# 选择器配置（多级备选方案，按优先级排序）
INPUT_SELECTORS = [
    "div._24fad49 textarea",
    "[class*='_24fad49'] textarea",
    "textarea",
]

SUBMIT_SELECTORS = [
    "div.ds-icon svg",
    "[class*='ec4f5d61'] svg",
    "[class*='bf38813a'] svg",
    "button[type='submit']",
    "svg",
]

RESPONSE_SELECTORS = [
    "[data-testid='assistant-message']",
    ".ds-markdown",
    "[class*='ds-message']",
    "div.ds-message",
]


async def find_working_selector(page, selectors: list, action: str = "wait", timeout: int = 5000):
    """遍历选择器列表，返回第一个成功的选择器"""
    for selector in selectors:
        try:
            if action == "wait":
                await page.wait_for_selector(selector, timeout=timeout)
            elif action == "click":
                await page.click(selector, timeout=timeout)
            print(f"    [OK] {selector}")
            return selector
        except Exception as e:
            print(f"    [FAIL] {selector}")
            continue
    return None


async def test_deepseek():
    """DeepSeek 平台可行性测试脚本"""

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for i in range(5):
            start_time = datetime.now()
            used_selectors = {}

            try:
                print(f"\n--- 第 {i+1}/5 次测试 ---")

                # 打开 DeepSeek
                print("[1] 打开 DeepSeek...")
                await page.goto("https://chat.deepseek.com", timeout=30000)

                # 查找输入框
                print("[2] 查找输入框...")
                input_selector = await find_working_selector(page, INPUT_SELECTORS, "wait")
                if not input_selector:
                    raise Exception(f"输入框选择器全部失效")
                used_selectors["input"] = input_selector

                # 输入关键词
                print(f"[3] 输入关键词...")
                await page.fill(selector=input_selector, value="人工智能发展趋势")

                # 查找发送按钮
                print("[4] 查找发送按钮...")
                submit_selector = await find_working_selector(page, SUBMIT_SELECTORS, "click")
                if not submit_selector:
                    raise Exception(f"发送按钮选择器全部失效")
                used_selectors["submit"] = submit_selector

                # 等待回答
                print("[5] 等待 AI 回答...")
                response_selector = await find_working_selector(page, RESPONSE_SELECTORS, "wait", timeout=120000)
                if not response_selector:
                    raise Exception(f"响应选择器全部失效")
                used_selectors["response"] = response_selector

                # 获取回答内容
                response_text = await page.text_content(selector=response_selector)
                elapsed = (datetime.now() - start_time).total_seconds()

                # 检查是否包含引用
                has_citations = bool(response_text and ("http" in response_text or "[1]" in response_text))

                results.append({
                    "attempt": i + 1,
                    "status": "success",
                    "response_time": round(elapsed, 2),
                    "has_citations": has_citations,
                    "response_length": len(response_text) if response_text else 0,
                    "selectors_used": used_selectors,
                    "error": None,
                    "error_type": None
                })

                print(f"[OK] 第 {i+1} 次成功: {elapsed:.1f}s, 引用: {has_citations}")

            except Exception as e:
                elapsed = (datetime.now() - start_time).total_seconds()
                error_msg = str(e)

                # 分类错误类型
                error_type = "unknown"
                if "timeout" in error_msg.lower():
                    error_type = "timeout"
                elif "captcha" in error_msg.lower():
                    error_type = "captcha"
                elif "失效" in error_msg:
                    error_type = "selector_not_found"
                elif "not found" in error_msg.lower():
                    error_type = "selector_not_found"

                results.append({
                    "attempt": i + 1,
                    "status": "failed",
                    "response_time": round(elapsed, 2),
                    "has_citations": False,
                    "response_length": 0,
                    "selectors_used": used_selectors,
                    "error": error_msg,
                    "error_type": error_type
                })

                print(f"[FAIL] 第 {i+1} 次失败 [{error_type}]: {error_msg}")

            # 随机延迟
            if i < 4:
                delay = 5.0
                print(f"[6] 等待 {delay:.1f}s...")
                await asyncio.sleep(delay)

        await browser.close()

    # 生成报告
    success_count = sum(1 for r in results if r["status"] == "success")
    failure_count = sum(1 for r in results if r["status"] == "failed")
    captcha_count = sum(1 for r in results if r.get("error_type") == "captcha")
    timeout_count = sum(1 for r in results if r.get("error_type") == "timeout")
    selector_fail_count = sum(1 for r in results if r.get("error_type") == "selector_not_found")

    report = {
        "test_date": datetime.now().isoformat(),
        "platform": "DeepSeek",
        "platform_url": "https://chat.deepseek.com",
        "test_keyword": "人工智能发展趋势",
        "total_attempts": 5,
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": f"{success_count / 5 * 100:.0f}%",
        "selectors_config": {
            "input": INPUT_SELECTORS,
            "submit": SUBMIT_SELECTORS,
            "response": RESPONSE_SELECTORS,
        },
        "error_summary": {
            "captcha_count": captcha_count,
            "timeout_count": timeout_count,
            "selector_failures": selector_fail_count,
        },
        "results": results,
        "recommendation": "",
        "conclusion": ""
    }

    # 根据结果给出建议
    if success_count == 5:
        report["conclusion"] = "PASS"
        report["recommendation"] = "Playwright 路径可行，按原计划推进"
    elif success_count >= 3:
        report["conclusion"] = "CONDITIONAL_PASS"
        report["recommendation"] = "建议优先评估官方 API 方案的可用性和结果一致性，考虑混合方案"
    else:
        report["conclusion"] = "FAIL"
        report["recommendation"] = "强烈建议优先使用官方 API，Playwright 作为备选方案"

    # 保存报告
    report_path = "deepseek_feasibility_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 打印摘要
    print("\n" + "=" * 60)
    print("DeepSeek 可行性测试报告")
    print("=" * 60)
    print(f"测试时间: {report['test_date']}")
    print(f"总尝试: {report['total_attempts']}, 成功: {success_count}, 失败: {failure_count}")
    print(f"成功率: {report['success_rate']}")
    print(f"\n错误分布:")
    print(f"  - 验证码: {captcha_count}")
    print(f"  - 超时: {timeout_count}")
    print(f"  - 选择器失效: {selector_fail_count}")
    print(f"\n结论: {report['conclusion']}")
    print(f"建议: {report['recommendation']}")
    print(f"\n详细报告: {report_path}")
    print("=" * 60)

    return report


if __name__ == "__main__":
    asyncio.run(test_deepseek())
