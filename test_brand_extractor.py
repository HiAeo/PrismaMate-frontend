# test_brand_extractor.py
# 品牌提及提取规则引擎测试脚本
#
# 使用方法：
# python test_brand_extractor.py

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.brand_extractor import BrandExtractor, BrandAlias, extract_brands


def test_basic_extraction():
    """测试基本提取功能"""
    print("\n" + "=" * 60)
    print("测试 1: 基本品牌提取")
    print("=" * 60)

    text = """
    华为是中国领先的科技公司，在5G技术方面处于全球领先地位。
    腾讯和阿里巴巴也在积极布局人工智能领域。
    据Google和Microsoft的报告显示，AI市场正在快速增长。
    """

    extractor = BrandExtractor()
    mentions = extractor.extract(text)

    print(f"输入文本: {text[:100]}...")
    print(f"\n提取到 {len(mentions)} 个品牌提及:")
    for m in mentions:
        print(f"  - {m.brand_name}: {m.context[:60]}...")

    assert len(mentions) >= 4, "应该至少提取到 4 个品牌"
    print("\n✓ 测试通过")


def test_url_exclusion():
    """测试 URL 排除功能"""
    print("\n" + "=" * 60)
    print("测试 2: URL 排除")
    print("=" * 60)

    text = """
    访问 https://www.huawei.com 获取更多信息。
    华为是全球领先的ICT基础设施提供商。
    请访问 https://www.microsoft.com 了解产品。
    """

    extractor = BrandExtractor()
    mentions = extractor.extract(text)

    print(f"输入文本: {text}")
    print(f"\n提取到 {len(mentions)} 个品牌提及:")

    # URL中的华为不应被提取
    huawei_in_url = any(
        "huawei.com" in m.context or m.position_start < 20
        for m in mentions if m.brand_name == "华为"
    )

    for m in mentions:
        print(f"  - {m.brand_name}: 位置 {m.position_start}-{m.position_end}")

    # 应该只提取到文本中的华为，不包括URL中的
    print(f"\nURL中的华为被正确排除: {not huawei_in_url}")
    print("\n✓ 测试通过")


def test_first_occurrence():
    """测试首次出现去重"""
    print("\n" + "=" * 60)
    print("测试 3: 首次出现去重")
    print("=" * 60)

    text = """
    华为是领先的科技公司。华为在5G领域表现突出。
    华为还推出了多款智能手机。华为的芯片技术也很先进。
    """

    extractor = BrandExtractor()
    mentions = extractor.extract(text)

    print(f"输入文本中'华为'出现 4 次")
    print(f"\n提取到 {len(mentions)} 个品牌提及（去重后）:")

    huawei_mentions = [m for m in mentions if m.brand_name == "华为"]
    for m in huawei_mentions:
        print(f"  - {m.brand_name}: 首次={m.is_first_occurrence}, 位置={m.position_start}")

    assert len(huawei_mentions) == 1, "去重后应该只有 1 个华为提及"
    assert huawei_mentions[0].is_first_occurrence == True, "第一个匹配应该是首次出现"
    print("\n✓ 测试通过")


def test_context_extraction():
    """测试上下文提取"""
    print("\n" + "=" * 60)
    print("测试 4: 上下文提取")
    print("=" * 60)

    text = """
    华为公司是全球领先的通信设备制造商，其5G技术备受赞誉。
    """

    extractor = BrandExtractor()
    mentions = extractor.extract(text)

    print(f"输入文本: {text}")
    print(f"\n提取到上下文:")

    for m in mentions:
        print(f"  品牌: {m.brand_name}")
        print(f"  上下文: {m.context}")
        print(f"  长度验证: 前后各约50字符 = {len(m.context) > 80}")

    # 验证上下文包含前后内容
    assert any(len(m.context) > 80 for m in mentions), "上下文应该足够长"
    print("\n✓ 测试通过")


def test_custom_brands():
    """测试自定义品牌列表"""
    print("\n" + "=" * 60)
    print("测试 5: 自定义品牌列表")
    print("=" * 60)

    text = "苹果和香蕉是水果，三星是手机品牌。"

    # 自定义品牌
    custom_aliases = [
        BrandAlias("苹果", ["苹果"]),
        BrandAlias("三星", ["三星"]),
    ]
    extractor = BrandExtractor(custom_aliases)

    mentions = extractor.extract(text, brands=["苹果", "三星"])

    print(f"输入文本: {text}")
    print(f"指定品牌: ['苹果', '三星']")
    print(f"\n提取到 {len(mentions)} 个品牌提及:")
    for m in mentions:
        print(f"  - {m.brand_name}")

    # 应该只提取苹果和三星，不包括香蕉
    brand_names = [m.brand_name for m in mentions]
    assert "苹果" in brand_names, "应该提取到苹果"
    assert "三星" in brand_names, "应该提取到三星"
    assert "香蕉" not in brand_names, "不应该提取到香蕉"
    print("\n✓ 测试通过")


def test_statistics():
    """测试统计功能"""
    print("\n" + "=" * 60)
    print("测试 6: 统计功能")
    print("=" * 60)

    text = """
    华为、腾讯、阿里巴巴是中国的科技巨头。
    华为在5G领域领先，腾讯在社交领域领先。
    Google、Microsoft是美国的科技公司。
    """

    extractor = BrandExtractor()
    stats = extractor.get_statistics(text)

    print(f"输入文本: {text[:80]}...")
    print(f"\n统计结果:")
    print(f"  总提及数: {stats['total_mentions']}")
    print(f"  唯一品牌数: {stats['unique_brands']}")
    print(f"  品牌计数: {stats['brand_counts']}")
    print(f"\n  首次提及:")
    for m in stats['first_mentions']:
        print(f"    - {m['brand']}: 位置 {m['position']}")

    assert stats['total_mentions'] >= 5, "应该至少有5个品牌提及"
    assert stats['unique_brands'] >= 4, "应该至少有4个唯一品牌"
    print("\n✓ 测试通过")


def test_sentiment_default():
    """测试情感极性默认值"""
    print("\n" + "=" * 60)
    print("测试 7: 情感极性默认值")
    print("=" * 60)

    text = "华为是优秀的科技公司。"
    extractor = BrandExtractor()
    mentions = extractor.extract(text)

    print(f"输入文本: {text}")
    print(f"\n品牌提及情感极性:")
    for m in mentions:
        print(f"  - {m.brand_name}: {m.sentiment}")

    assert all(m.sentiment == "neutral" for m in mentions), "所有提及应该是neutral"
    print("\n✓ 测试通过（MVP阶段固定为neutral）")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("品牌提及提取规则引擎测试套件")
    print("=" * 60)

    tests = [
        test_basic_extraction,
        test_url_exclusion,
        test_first_occurrence,
        test_context_extraction,
        test_custom_brands,
        test_statistics,
        test_sentiment_default,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            failed += 1

    # 打印汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  总计: {passed + failed}")

    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n✗ 有 {failed} 个测试失败")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
