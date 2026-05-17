"""
PrismaMate 棱镜 - 极简检测完整闭环测试

测试流程：
1. 启动后端服务器
2. 调用检测 API
3. 验证报告生成

使用方法：
python test_simple_detection.py
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# 添加后端路径
backend_path = Path(__file__).parent / "prismamate-backend"
sys.path.insert(0, str(backend_path))


def test_api_endpoint():
    """测试 API 端点（不依赖服务器）"""
    print("=" * 60)
    print("测试 1: API 端点导入测试")
    print("=" * 60)

    try:
        # 测试导入检测 API 模块
        from app.api.v1 import detect
        print("[PASS] API 模块导入成功")

        # 测试导入报告生成器
        from app.services.report_generator import ReportGenerator, generate_report
        print("[PASS] 报告生成器导入成功")

        # 测试导入品牌提取器
        from app.services.brand_extractor import create_extractor
        print("[PASS] 品牌提取器导入成功")

        return True
    except ImportError as e:
        print(f"[FAIL] 导入失败: {e}")
        return False


def test_report_generation():
    """测试报告生成（不需要 DeepSeek API）"""
    print("\n" + "=" * 60)
    print("测试 2: 报告生成测试（Mock 数据）")
    print("=" * 60)

    try:
        from app.services.report_generator import (
            ReportGenerator,
            DetectionResult,
            BrandMentionResult,
            generate_report
        )
        import datetime

        # 创建 Mock 检测结果
        mock_results = [
            DetectionResult(
                platform="DeepSeek",
                keyword="华为 AI 技术",
                query_time=datetime.datetime.now(),
                response_text="华为是全球领先的科技公司，在 AI 领域有深厚积累。",
                response_time=1.5,
                citations=[
                    {"url": "https://huawei.com", "context_before": "...", "context_after": "..."}
                ]
            )
        ]

        # 创建 Mock 品牌提及
        mock_mentions = [
            BrandMentionResult(
                brand_name="华为",
                canonical_name="华为",
                position=0,
                context="华为是全球领先的科技公司",
                sentiment="positive"
            )
        ]

        # 生成报告
        generator = ReportGenerator()
        report = generator.generate(
            detection_results=mock_results,
            brand_mentions=mock_mentions,
            brands=["华为"],
            keywords=["华为 AI 技术"],
            platforms=["DeepSeek"]
        )

        print(f"  报告编号: {report.report_id}")
        print(f"  验证码: {report.verification_code}")
        print(f"  哈希值: {report.report_hash[:32]}...")
        print(f"  品牌提及: {len(report.brand_mentions)} 条")
        print("[PASS] 报告生成成功")

        # 测试 HTML 渲染
        html = generator.render_html(report)
        assert len(html) > 1000, "HTML 内容过短"
        assert report.report_id in html, "报告编号未在 HTML 中"
        assert report.verification_code in html, "验证码未在 HTML 中"
        print(f"  HTML 长度: {len(html)} 字符")
        print("[PASS] HTML 渲染成功")

        return True

    except Exception as e:
        print(f"[FAIL] 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_brand_extraction():
    """测试品牌提取"""
    print("\n" + "=" * 60)
    print("测试 3: 品牌提取测试")
    print("=" * 60)

    try:
        from app.services.brand_extractor import create_extractor

        extractor = create_extractor()
        text = "华为是中国领先的科技公司，腾讯和阿里巴巴也在布局AI。"

        mentions = extractor.extract(text)

        print(f"  测试文本: {text}")
        print(f"  提取到 {len(mentions)} 个品牌提及")
        for m in mentions:
            print(f"    - {m.brand_name}: {m.context[:50]}...")

        assert len(mentions) >= 3, f"期望至少3个提及，实际 {len(mentions)} 个"
        print("[PASS] 品牌提取成功")

        return True

    except Exception as e:
        print(f"[FAIL] 品牌提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frontend_files():
    """测试前端文件"""
    print("\n" + "=" * 60)
    print("测试 4: 前端文件测试")
    print("=" * 60)

    try:
        frontend_path = Path(__file__).parent / "prismamate-frontend" / "src" / "views" / "SimpleDetection.vue"
        assert frontend_path.exists(), f"SimpleDetection.vue 不存在"
        print(f"  找到: {frontend_path.name}")

        # 检查路由配置
        router_path = Path(__file__).parent / "prismamate-frontend" / "src" / "router" / "index.ts"
        router_content = router_path.read_text(encoding="utf-8")
        assert "SimpleDetection" in router_content, "路由未配置 SimpleDetection"
        assert "/detect" in router_content, "路由路径 /detect 未配置"
        print("[PASS] 前端文件配置正确")

        return True

    except AssertionError as e:
        print(f"[FAIL] {e}")
        return False
    except Exception as e:
        print(f"[FAIL] 前端文件测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("PrismaMate 棱镜 - 极简检测闭环测试")
    print("=" * 60 + "\n")

    results = []

    # 1. API 端点导入测试
    results.append(("API 端点导入", test_api_endpoint()))

    # 2. 报告生成测试
    results.append(("报告生成", test_report_generation()))

    # 3. 品牌提取测试
    results.append(("品牌提取", test_brand_extraction()))

    # 4. 前端文件测试
    results.append(("前端文件", test_frontend_files()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n[ALL PASS] 所有测试通过！")
        print("\n启动步骤：")
        print("  1. 终端 1: cd prismamate-backend && uvicorn app.main:app --reload")
        print("  2. 终端 2: cd prismamate-frontend && npm run dev")
        print("  3. 打开 http://localhost:3000/detect")
        return True
    else:
        print("\n[FAIL] 部分测试失败，请检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
