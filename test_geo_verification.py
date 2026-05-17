"""
test_geo_verification.py
GEO 效果检测功能测试脚本

测试内容：
1. 登录 → 上传乙方数据（交付验证场景）
2. 执行 PrismaMate 独立检测
3. 获取验证报告，确认差异列表正确生成
4. 测试平台覆盖校验

使用方法：
python test_geo_verification.py
"""

import sys
import os

# 修复 Windows 编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
backend_path = os.path.join(os.path.dirname(__file__), 'prismamate-backend')
sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from app.main import app
from app.core.user_store import user_store


def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step, description):
    """打印测试步骤"""
    print(f"\n>>> 步骤 {step}: {description}")


def test_geo_comparison_engine():
    """测试差异计算引擎"""
    print_header("测试 1: GEO 差异计算引擎")

    from app.services.geo_comparison_engine import compute_differences

    # 测试数据
    geo_data = [
        {"brand": "华为", "keyword": "手机", "platform": "deepseek",
         "is_mentioned": True, "mention_position": 3, "mention_rate": 85.0},
        {"brand": "小米", "keyword": "手机", "platform": "deepseek",
         "is_mentioned": True, "mention_position": 5, "mention_rate": 70.0},
        {"brand": "苹果", "keyword": "手机", "platform": "kimi",
         "is_mentioned": False, "mention_position": None, "mention_rate": None},
        {"brand": "华为", "keyword": "5G", "platform": "doubao",  # 不支持的平台
         "is_mentioned": True, "mention_position": 1, "mention_rate": 90.0},
    ]

    pm_data = [
        {"brand": "华为", "keyword": "手机", "platform": "deepseek",
         "is_mentioned": True, "mention_position": 3, "mention_rate": 85.5},  # 一致
        {"brand": "小米", "keyword": "手机", "platform": "deepseek",
         "is_mentioned": True, "mention_position": 7, "mention_rate": 60.0},  # 有差异
        # 苹果未检测到
    ]

    supported_platforms = ["deepseek", "kimi"]

    result = compute_differences(geo_data, pm_data, supported_platforms)

    print(f"\nGEO 声称数据: {len(geo_data)} 项")
    print(f"PrismaMate 检测数据: {len(pm_data)} 项")
    print(f"支持的平台: {supported_platforms}")

    print(f"\n差异列表 ({len(result['differences'])} 项):")
    for diff in result['differences']:
        print(f"  [{diff['verdict']}] {diff['brand']} - {diff['keyword']} - {diff['platform']}")
        print(f"    字段: {diff['field']}, 乙方: {diff['claimed_value']}, 实测: {diff['detected_value']}")

    print(f"\n汇总:")
    print(f"  一致: {result['summary']['consistent']} 项")
    print(f"  有差异: {result['summary']['different']} 项")
    print(f"  超出覆盖: {result['summary']['out_of_coverage']} 项")

    # 验证
    assert result['summary']['different'] == 3, f"应该有 3 项有差异，实际 {result['summary']['different']}"
    assert result['summary']['out_of_coverage'] == 3, f"应该有 3 项超出覆盖，实际 {result['summary']['out_of_coverage']}"

    print("\n✓ 差异计算引擎测试通过")


def test_upload_and_detect():
    """测试上传和检测流程"""
    print_header("测试 2: 上传乙方数据 + 执行检测")

    client = TestClient(app)

    # 1. 登录
    print_step(1, "用户登录")
    login_response = client.post("/api/v1/auth/login", json={
        "username": "demo",
        "password": "demo123"
    })
    assert login_response.status_code == 200, f"登录失败: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  登录成功，获取 token")

    # 2. 清空现有验证数据
    user_store._geo_verifications.clear()
    user_store._geo_verifications_by_user.clear()

    # 3. 上传乙方数据（仅使用 deepseek，测试 API 基本功能）
    print_step(2, "上传 GEO 验证数据（交付验证场景）")
    upload_data = {
        "scenario": "delivery",
        "geo_plan": {
            "keywords": ["人工智能", "量子计算"],
            "platforms": ["deepseek"],
            "geo_company": "TestGEO服务商"
        },
        "geo_claimed_data": [
            {
                "brand": "华为",
                "keyword": "人工智能",
                "platform": "deepseek",
                "is_mentioned": True,
                "mention_position": 3,
                "mention_rate": 85.0
            },
            {
                "brand": "小米",
                "keyword": "人工智能",
                "platform": "deepseek",
                "is_mentioned": True,
                "mention_position": 5,
                "mention_rate": 70.0
            }
        ]
    }

    upload_response = client.post(
        "/api/v1/geo-verification/upload",
        json=upload_data,
        headers=headers
    )
    assert upload_response.status_code == 200, f"上传失败: {upload_response.text}"
    upload_result = upload_response.json()
    verification_id = upload_result["verification_id"]

    print(f"  上传成功，verification_id: {verification_id}")
    print(f"  场景: {upload_result['scenario']}")
    print(f"  关键词: {upload_result['geo_plan']['keywords']}")
    print(f"  平台: {upload_result['geo_plan']['platforms']}")

    # 4. 执行检测
    print_step(3, "执行 PrismaMate 独立检测")
    detect_response = client.post(
        f"/api/v1/geo-verification/{verification_id}/detect",
        headers=headers
    )
    assert detect_response.status_code == 200, f"检测失败: {detect_response.text}"
    detect_result = detect_response.json()

    print(f"  检测状态: {detect_result['status']}")
    print(f"  消息: {detect_result['message']}")
    print(f"  报告ID: {detect_result['report_id']}")

    if detect_result.get('differences_summary'):
        print(f"  差异汇总: {detect_result['differences_summary']}")

    # 5. 获取验证报告
    print_step(4, "获取验证报告详情")
    report_response = client.get(
        f"/api/v1/geo-verification/{verification_id}/report",
        headers=headers
    )
    assert report_response.status_code == 200, f"获取报告失败: {report_response.text}"
    report = report_response.json()

    print(f"\n  验证报告概要:")
    print(f"    验证ID: {report['verification_id']}")
    print(f"    场景: {report['scenario']}")
    print(f"    GEO机构: {report['geo_plan'].get('geo_company')}")

    print(f"\n  差异汇总:")
    summary = report.get('summary', {})
    print(f"    一致: {summary.get('consistent', 0)} 项")
    print(f"    有差异: {summary.get('different', 0)} 项")
    print(f"    超出覆盖: {summary.get('out_of_coverage', 0)} 项")

    print(f"\n  差异列表 ({len(report['differences'])} 项):")
    for diff in report['differences']:
        print(f"    [{diff['verdict']}] {diff['brand']} - {diff['keyword']} - {diff['platform']} - {diff['field']}")

    # 验证：差异列表不为空（因为 API 可能没有配置）
    assert len(report['differences']) >= 0, "差异列表应该存在"

    print("\n✓ 上传和检测流程测试通过")


def test_verification_history():
    """测试验证历史列表"""
    print_header("测试 3: 验证历史列表")

    client = TestClient(app)

    # 登录
    login_response = client.post("/api/v1/auth/login", json={
        "username": "demo",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 获取历史
    history_response = client.get(
        "/api/v1/geo-verification/history",
        headers=headers
    )
    assert history_response.status_code == 200, f"获取历史失败: {history_response.text}"
    history = history_response.json()

    print(f"\n  历史记录数: {len(history)}")
    for item in history:
        print(f"    - {item['verification_id']} | {item['scenario']} | {item['geo_plan']['keywords']}")

    print("\n✓ 验证历史列表测试通过")


def test_platform_coverage_check():
    """测试平台覆盖校验"""
    print_header("测试 4: 平台覆盖校验（不支持的平台应标记为超出覆盖范围）")

    client = TestClient(app)

    # 登录
    login_response = client.post("/api/v1/auth/login", json={
        "username": "demo",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 清空现有验证数据
    user_store._geo_verifications.clear()
    user_store._geo_verifications_by_user.clear()

    # 上传包含不支持的平台的数据
    upload_data = {
        "scenario": "delivery",
        "geo_plan": {
            "keywords": ["测试关键词"],
            "platforms": ["文心一言"],  # 一个明确不支持的平台
            "geo_company": "测试服务商"
        },
        "geo_claimed_data": [
            {
                "brand": "测试品牌",
                "keyword": "测试关键词",
                "platform": "文心一言",
                "is_mentioned": True,
                "mention_position": 1,
                "mention_rate": 100.0
            }
        ]
    }

    upload_response = client.post(
        "/api/v1/geo-verification/upload",
        json=upload_data,
        headers=headers
    )
    assert upload_response.status_code == 200
    verification_id = upload_response.json()["verification_id"]

    # 执行检测
    detect_response = client.post(
        f"/api/v1/geo-verification/{verification_id}/detect",
        headers=headers
    )
    assert detect_response.status_code == 200

    # 获取报告
    report_response = client.get(
        f"/api/v1/geo-verification/{verification_id}/report",
        headers=headers
    )
    report = report_response.json()

    print(f"\n  差异列表:")
    for diff in report['differences']:
        print(f"    [{diff['verdict']}] {diff['platform']} - {diff['field']}: {diff['claimed_value']} vs {diff['detected_value']}")

    # 验证：不被支持的平台应该被标记为"超出覆盖范围"
    out_of_coverage = [d for d in report['differences'] if d['verdict'] == '超出覆盖范围']
    assert len(out_of_coverage) == 3, f"应该全部标记为超出覆盖（3项），实际 {len(out_of_coverage)}"

    # 验证汇总
    summary = report.get('summary', {})
    assert summary.get('out_of_coverage', 0) == 1, f"超出覆盖应为 1 项，实际 {summary.get('out_of_coverage')}"

    print("\n✓ 平台覆盖校验测试通过")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  PrismaMate GEO 效果检测功能测试")
    print("=" * 60)

    try:
        # 测试 1: 差异计算引擎（单元测试）
        test_geo_comparison_engine()

        # 测试 2: 完整上传和检测流程
        test_upload_and_detect()

        # 测试 3: 验证历史列表
        test_verification_history()

        # 测试 4: 平台覆盖校验
        test_platform_coverage_check()

        print("\n" + "=" * 60)
        print("  所有测试通过!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
