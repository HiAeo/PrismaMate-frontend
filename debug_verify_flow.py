"""
完整验证流程调试脚本 - 模拟报告生成到验证的完整数据流
"""

import sys
import os
import json
from datetime import datetime

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prismamate-backend'))

from app.services.report_generator import ReportGenerator, DetectionResult, BrandMentionResult
from app.core.user_store import user_store
from app.api.v1.reports import _compute_report_hash


def calculate_report_hash_gen(report_data: dict) -> str:
    """
    报告生成端的哈希计算逻辑（从 report_generator.py 复制）
    """
    import hashlib
    import json
    from datetime import datetime

    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: serialize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [serialize(item) for item in obj]
        return obj

    # 只使用存储时可用的字段
    hash_data = {
        "report_id": report_data.get("report_id"),
        "keywords": report_data.get("keywords", []),
        "platforms": report_data.get("platforms", []),
        "brand_mentions": report_data.get("brand_mentions", []),
    }

    serialized = json.dumps(serialize(hash_data), ensure_ascii=False, sort_keys=True)
    print(f"\n[生成端] 序列化后的 JSON:\n{serialized}\n")
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def main():
    print("=" * 70)
    print("PrismaMate 完整验证流程调试")
    print("=" * 70)

    # 步骤1: 生成报告
    print("\n" + "=" * 70)
    print("步骤1: 生成报告")
    print("=" * 70)

    generator = ReportGenerator()

    # 模拟检测结果
    detection_results = [
        DetectionResult(
            platform="微博",
            keyword="苹果",
            query_time=datetime.now(),
            response_text="苹果公司发布了新产品",
            response_time=0.5,
            citations=[]
        )
    ]

    # 模拟品牌提及
    brand_mentions = [
        BrandMentionResult(
            brand_name="苹果",
            canonical_name="Apple",
            position=0,
            context="苹果公司发布了新产品",
            sentiment="positive"
        )
    ]

    # 生成报告
    report = generator.generate(
        detection_results=detection_results,
        brand_mentions=brand_mentions,
        brands=["苹果"],
        keywords=["苹果", "iPhone"],
        platforms=["微博"]
    )

    print(f"\n[生成的报告]")
    print(f"  report_id: {report.report_id}")
    print(f"  verification_code: {report.verification_code}")
    print(f"  report_hash (原始): {report.report_hash}")
    print(f"  detection_time: {report.detection_time} (type: {type(report.detection_time).__name__})")
    print(f"  keywords: {report.keywords}")
    print(f"  platforms: {report.platforms}")
    print(f"  brand_mentions: {report.brand_mentions}")

    # 步骤2: 保存报告到内存存储（模拟 detect.py 的行为）
    print("\n" + "=" * 70)
    print("步骤2: 保存报告到内存存储")
    print("=" * 70)

    stored_report = user_store.create_report(
        report_id=report.report_id,
        verification_code=report.verification_code,
        report_hash=report.report_hash,
        user_id="test-user-001",
        task_id="test-task-001",
        keywords=report.keywords,
        platforms=report.platforms,
        total_mentions=len(brand_mentions),
        brand_mentions=[
            {
                "brand_name": m.brand_name,
                "canonical_name": m.canonical_name,
                "position": m.position,
                "context": m.context,
                "sentiment": m.sentiment
            }
            for m in brand_mentions
        ],
        total_citations=0
    )

    print(f"\n[保存的报告]")
    print(f"  report_id: {stored_report.report_id}")
    print(f"  verification_code: {stored_report.verification_code}")
    print(f"  report_hash (存储): {stored_report.report_hash}")
    print(f"  created_at: {stored_report.created_at} (type: {type(stored_report.created_at).__name__})")
    print(f"  keywords: {stored_report.keywords} (type: {type(stored_report.keywords).__name__})")
    print(f"  platforms: {stored_report.platforms} (type: {type(stored_report.platforms).__name__})")
    print(f"  brand_mentions: {stored_report.brand_mentions}")

    # 步骤3: 从内存存储读取报告（模拟验证接口的行为）
    print("\n" + "=" * 70)
    print("步骤3: 从内存存储读取报告")
    print("=" * 70)

    fetched_report = user_store.get_report_by_code(report.verification_code)

    if not fetched_report:
        print("❌ 无法从存储中获取报告!")
        return

    print(f"\n[读取的报告]")
    print(f"  report_id: {fetched_report.report_id}")
    print(f"  verification_code: {fetched_report.verification_code}")
    print(f"  report_hash (存储): {fetched_report.report_hash}")
    print(f"  created_at: {fetched_report.created_at} (type: {type(fetched_report.created_at).__name__})")
    print(f"  keywords: {fetched_report.keywords} (type: {type(fetched_report.keywords).__name__})")
    print(f"  platforms: {fetched_report.platforms} (type: {type(fetched_report.platforms).__name__})")
    print(f"  brand_mentions: {fetched_report.brand_mentions}")

    # 步骤4: 打印完整的 to_dict() 输出
    print("\n" + "=" * 70)
    print("步骤4: report.to_dict() 完整输出")
    print("=" * 70)

    report_dict = fetched_report.to_dict()
    print(json.dumps(report_dict, ensure_ascii=False, indent=2, default=str))

    # 步骤5: 对比两组哈希
    print("\n" + "=" * 70)
    print("步骤5: 哈希对比")
    print("=" * 70)

    # 生成端：使用报告生成时的原始数据
    print("\n--- 生成端哈希计算 ---")
    gen_report_data = {
        "report_id": report.report_id,
        "keywords": report.keywords,
        "platforms": report.platforms,
        "brand_mentions": [
            {
                "brand_name": m.brand_name,
                "canonical_name": m.canonical_name,
                "position": m.position,
                "context": m.context,
                "sentiment": m.sentiment
            }
            for m in report.brand_mentions
        ],
    }
    print(f"[生成端原始数据]")
    print(json.dumps(gen_report_data, ensure_ascii=False, indent=2))
    gen_hash = calculate_report_hash_gen(gen_report_data)
    print(f"生成端哈希: {gen_hash}")

    # 验证端：使用从存储读取的数据
    print("\n--- 验证端哈希计算 ---")
    verify_report_data = {
        "report_id": fetched_report.report_id,
        "keywords": fetched_report.keywords,
        "platforms": fetched_report.platforms,
        "brand_mentions": fetched_report.brand_mentions,
    }
    print(f"[验证端数据]")
    print(json.dumps(verify_report_data, ensure_ascii=False, indent=2, default=str))

    import hashlib
    import json as json_module

    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: serialize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [serialize(item) for item in obj]
        return obj

    serialized = json_module.dumps(serialize(verify_report_data), ensure_ascii=False, sort_keys=True)
    print(f"\n[验证端] 序列化后的 JSON:\n{serialized}\n")
    verify_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    print(f"验证端哈希: {verify_hash}")

    # 存储的哈希
    print(f"\n存储的原始哈希: {report.report_hash}")

    # 对比结果
    print("\n" + "=" * 70)
    print("对比结果")
    print("=" * 70)
    print(f"生成端哈希: {gen_hash}")
    print(f"验证端哈希: {verify_hash}")
    print(f"存储的原始哈希: {report.report_hash}")

    if gen_hash == verify_hash == report.report_hash:
        print("\n✅ 三者完全一致!")
    else:
        print("\n❌ 哈希不一致!")
        if gen_hash != report.report_hash:
            print(f"   生成端 vs 存储: 不同")
        if verify_hash != report.report_hash:
            print(f"   验证端 vs 存储: 不同")
        if gen_hash != verify_hash:
            print(f"   生成端 vs 验证端: 不同")

        # 逐字段对比
        print("\n--- 逐字段对比 ---")

        # 对比 keywords
        print(f"\nkeywords:")
        print(f"  生成端: {gen_report_data['keywords']} (type: {type(gen_report_data['keywords']).__name__})")
        print(f"  验证端: {verify_report_data['keywords']} (type: {type(verify_report_data['keywords']).__name__})")
        print(f"  一致: {gen_report_data['keywords'] == verify_report_data['keywords']}")

        # 对比 platforms
        print(f"\nplatforms:")
        print(f"  生成端: {gen_report_data['platforms']} (type: {type(gen_report_data['platforms']).__name__})")
        print(f"  验证端: {verify_report_data['platforms']} (type: {type(verify_report_data['platforms']).__name__})")
        print(f"  一致: {gen_report_data['platforms'] == verify_report_data['platforms']}")

        # 对比 brand_mentions
        print(f"\nbrand_mentions:")
        print(f"  生成端: {json.dumps(gen_report_data['brand_mentions'], ensure_ascii=False)}")
        print(f"  验证端: {json.dumps(verify_report_data['brand_mentions'], ensure_ascii=False)}")
        print(f"  一致: {gen_report_data['brand_mentions'] == verify_report_data['brand_mentions']}")

        # 如果 brand_mentions 是字符串描述（检测 API 返回），打印原样
        if verify_report_data['brand_mentions'] and isinstance(verify_report_data['brand_mentions'][0], str):
            print(f"\n[警告] brand_mentions 是字符串类型，不是字典列表!")
            print(f"验证端 brand_mentions[0]: {verify_report_data['brand_mentions'][0]}")

    print("\n" + "=" * 70)
    print("调试完成")
    print("=" * 70)

    # 返回验证码供用户测试
    print(f"\n\n验证码: {report.verification_code}")
    print(f"请访问: http://localhost:3000/verify?code={report.verification_code}")


if __name__ == "__main__":
    main()
