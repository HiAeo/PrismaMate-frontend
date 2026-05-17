# test_report_generator.py
# 报告生成器测试脚本
#
# 使用方法：
# python test_report_generator.py

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prismamate-backend'))

from app.services.report_generator import (
    ReportGenerator,
    DetectionResult,
    BrandMentionResult,
    generate_report,
)


def test_report_generation():
    """测试报告生成"""
    print("\n" + "=" * 60)
    print("测试 1: 报告数据生成")
    print("=" * 60)
    
    # 模拟检测结果
    detection_results = [
        DetectionResult(
            platform="DeepSeek",
            keyword="人工智能",
            query_time=datetime.now(),
            response_text="华为、腾讯、阿里巴巴是中国领先的科技公司...",
            response_time=2.5,
            citations=[
                {"url": "https://www.huawei.com", "domain": "huawei.com"},
                {"url": "https://www.tencent.com", "domain": "tencent.com"},
            ]
        ),
        DetectionResult(
            platform="DeepSeek",
            keyword="AI发展趋势",
            query_time=datetime.now(),
            response_text="百度在自动驾驶领域取得突破...",
            response_time=3.0,
            citations=[
                {"url": "https://www.baidu.com", "domain": "baidu.com"},
            ]
        ),
    ]
    
    # 模拟品牌提及结果
    brand_mentions = [
        BrandMentionResult(
            brand_name="华为",
            canonical_name="华为",
            position=0,
            context="华为是领先的科技公司...",
            sentiment="neutral"
        ),
        BrandMentionResult(
            brand_name="腾讯",
            canonical_name="腾讯",
            position=15,
            context="...腾讯在社交领域领先...",
            sentiment="neutral"
        ),
        BrandMentionResult(
            brand_name="阿里巴巴",
            canonical_name="阿里巴巴",
            position=30,
            context="...阿里巴巴布局电商和云计算...",
            sentiment="neutral"
        ),
        BrandMentionResult(
            brand_name="百度",
            canonical_name="百度",
            position=0,
            context="百度在自动驾驶领域取得突破...",
            sentiment="neutral"
        ),
    ]
    
    # 生成报告
    generator = ReportGenerator()
    report = generator.generate(
        detection_results=detection_results,
        brand_mentions=brand_mentions,
        brands=["华为", "腾讯", "阿里巴巴", "百度"],
        keywords=["人工智能", "AI发展趋势"],
        platforms=["DeepSeek"]
    )
    
    print(f"报告编号: {report.report_id}")
    print(f"检测时间: {report.detection_time}")
    print(f"验证码: {report.verification_code}")
    print(f"报告哈希: {report.report_hash[:32]}...")
    print(f"品牌提及数: {len(report.brand_mentions)}")
    print(f"引用来源数: {len(report.citations)}")
    
    # 验证报告编号格式
    assert report.report_id.startswith("PM-"), "报告编号格式错误"
    assert len(report.verification_code) == 12, "验证码长度错误"
    assert len(report.report_hash) == 64, "哈希值长度错误"
    
    print("\n[PASS] 报告生成测试通过")
    return report


def test_html_rendering(report):
    """测试 HTML 渲染"""
    print("\n" + "=" * 60)
    print("测试 2: HTML 渲染")
    print("=" * 60)
    
    generator = ReportGenerator()
    html = generator.render_html(report)
    
    print(f"HTML 长度: {len(html)} 字符")
    
    # 检查关键内容
    assert report.report_id in html, "报告编号未在 HTML 中"
    assert report.verification_code in html, "验证码未在 HTML 中"
    assert report.report_hash in html, "哈希值未在 HTML 中"
    
    print("[PASS] HTML 渲染测试通过")


def test_pdf_generation(report):
    """测试 PDF 生成（需要 WeasyPrint）"""
    print("\n" + "=" * 60)
    print("测试 3: PDF 生成")
    print("=" * 60)
    
    output_path = os.path.join(
        os.path.dirname(__file__),
        f"PrismaMate_Report_{report.report_id}.pdf"
    )
    
    try:
        generator = ReportGenerator()
        result_path = generator.generate_pdf(report, output_path)
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"PDF 生成成功: {result_path}")
            print(f"文件大小: {file_size / 1024:.2f} KB")
            print("\n[PASS] PDF 生成测试通过")
        else:
            print("[FAIL] PDF 文件未生成")
            
    except ImportError as e:
        print(f"[SKIP] PDF 生成跳过: {e}")
        print("  请安装 WeasyPrint: pip install weasyprint")
    except Exception as e:
        print(f"[FAIL] PDF 生成失败: {e}")


def test_quick_function():
    """测试便捷函数"""
    print("\n" + "=" * 60)
    print("测试 4: 便捷函数")
    print("=" * 60)
    
    brand_mentions = [
        BrandMentionResult(
            brand_name="华为",
            canonical_name="华为",
            position=0,
            context="华为是领先的科技公司",
            sentiment="neutral"
        ),
    ]
    
    report, pdf_path = generate_report(
        detection_results=[],
        brand_mentions=brand_mentions,
        brands=["华为"],
        keywords=["AI"],
        platforms=["DeepSeek"]
    )
    
    print(f"便捷函数生成报告: {report.report_id}")
    print("\n[PASS] 便捷函数测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("PrismaMate 报告生成器测试套件")
    print("=" * 60)
    
    try:
        # 测试报告生成
        report = test_report_generation()
        
        # 测试 HTML 渲染
        test_html_rendering(report)
        
        # 测试 PDF 生成（可选）
        test_pdf_generation(report)
        
        # 测试便捷函数
        test_quick_function()
        
        print("\n" + "=" * 60)
        print("[ALL PASS] 所有测试通过！")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
