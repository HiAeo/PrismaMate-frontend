"""
哈希调试脚本 - 对比报告生成端和验证端的哈希计算结果
"""

import sys
import os
import json
from datetime import datetime

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prismamate-backend'))

from app.services.report_generator import ReportGenerator
from app.core.user_store import user_store


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
    print(f"[生成端] 序列化后的 JSON:\n{serialized}\n")
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def calculate_report_hash_verify(report: dict) -> str:
    """
    验证端的哈希计算逻辑（从 reports.py 复制）
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

    # 构建与 report_generator.py 中相同的数据结构（只用存储时可用的字段）
    hash_data = {
        "report_id": report["report_id"],
        "keywords": report.get("keywords", []),
        "platforms": report.get("platforms", []),
        "brand_mentions": report.get("brand_mentions", []),
    }

    serialized = json.dumps(serialize(hash_data), ensure_ascii=False, sort_keys=True)
    print(f"[验证端] 序列化后的 JSON:\n{serialized}\n")
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def compare_json_objects(obj1: dict, obj2: dict, path: str = ""):
    """逐字段对比两个 JSON 对象"""
    differences = []
    
    all_keys = set(obj1.keys()) | set(obj2.keys())
    
    for key in sorted(all_keys):
        current_path = f"{path}.{key}" if path else key
        
        if key not in obj1:
            differences.append(f"  仅在验证端存在: {current_path} = {obj2[key]}")
        elif key not in obj2:
            differences.append(f"  仅在生成端存在: {current_path} = {obj1[key]}")
        elif obj1[key] != obj2[key]:
            # 检查是否是 datetime 对象
            if isinstance(obj1[key], datetime) and isinstance(obj2[key], datetime):
                if obj1[key].isoformat() != obj2[key].isoformat():
                    differences.append(f"  {current_path}: 生成端={obj1[key].isoformat()}, 验证端={obj2[key].isoformat()}")
            elif isinstance(obj1[key], dict):
                differences.extend(compare_json_objects(obj1[key], obj2[key], current_path))
            elif isinstance(obj1[key], list):
                if len(obj1[key]) != len(obj2[key]):
                    differences.append(f"  {current_path}: 长度不同, 生成端={len(obj1[key])}, 验证端={len(obj2[key])}")
                else:
                    for i, (v1, v2) in enumerate(zip(obj1[key], obj2[key])):
                        if v1 != v2:
                            differences.extend(compare_json_objects(v1, v2, f"{current_path}[{i}]"))
            else:
                differences.append(f"  {current_path}: 生成端={obj1[key]}, 验证端={obj2[key]}")
    
    return differences


def main():
    print("=" * 60)
    print("PrismaMate 哈希计算调试")
    print("=" * 60)

    # 方案1: 如果内存中有报告，用真实报告测试
    reports = list(user_store._reports.values())
    
    if reports:
        print(f"\n[INFO] 内存中找到 {len(reports)} 份报告\n")
        
        for i, report in enumerate(reports):
            print(f"\n{'='*60}")
            print(f"报告 #{i+1}: {report.report_id}")
            print(f"{'='*60}")
            
            # 获取报告字典
            report_dict = report.to_dict()
            
            print(f"\n[报告原始数据]")
            print(f"  report_id: {report.report_id}")
            print(f"  verification_code: {report.verification_code}")
            print(f"  created_at: {report.created_at} (type: {type(report.created_at).__name__})")
            print(f"  keywords: {report.keywords}")
            print(f"  platforms: {report.platforms}")
            print(f"  brand_mentions: {report.brand_mentions}")
            print(f"  存储的 report_hash: {report.report_hash}")
            
            # 生成端哈希计算
            print(f"\n--- 生成端计算 ---")
            gen_report_data = {
                "report_id": report.report_id,
                "brand_names": getattr(report, 'brand_names', []) or [],
                "keywords": report.keywords,
                "platforms": report.platforms,
                "detection_time": report.created_at,
                "brand_mentions": report.brand_mentions,
            }
            gen_hash = calculate_report_hash_gen(gen_report_data)
            print(f"生成端哈希: {gen_hash}")
            
            # 验证端哈希计算
            print(f"\n--- 验证端计算 ---")
            verify_hash = calculate_report_hash_verify(report_dict)
            print(f"验证端哈希: {verify_hash}")
            
            # 对比结果
            print(f"\n--- 对比结果 ---")
            if gen_hash == verify_hash:
                print(f"✅ 哈希一致!")
            else:
                print(f"❌ 哈希不一致!")
                
                # 对比两份 report_data
                verify_report_data = {
                    "report_id": report_dict["report_id"],
                    "keywords": report_dict.get("keywords", []),
                    "platforms": report_dict.get("platforms", []),
                    "detection_time": report_dict.get("created_at"),
                    "brand_mentions": report_dict.get("brand_mentions", []),
                }
                
                print(f"\n[生成端 report_data]")
                print(json.dumps(
                    {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in gen_report_data.items()},
                    ensure_ascii=False, indent=2
                ))
                
                print(f"\n[验证端 report_data]")
                print(json.dumps(
                    {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in verify_report_data.items()},
                    ensure_ascii=False, indent=2
                ))
                
                print(f"\n[字段差异]")
                differences = compare_json_objects(gen_report_data, verify_report_data)
                if differences:
                    for diff in differences:
                        print(diff)
                else:
                    print("  (结构相同，可能是 datetime 对象比较问题)")
    
    else:
        print("\n[INFO] 内存中没有报告，创建模拟报告进行测试")
        print("-" * 60)
        
        # 创建模拟报告（使用存储时可用的字段）
        mock_report_data = {
            "report_id": "PM-TEST-20260514-001",
            "keywords": ["苹果", "iPhone"],
            "platforms": ["微博", "小红书"],
            "brand_mentions": [
                {"brand_name": "测试品牌", "canonical_name": "测试品牌", "position": 0, "context": "测试上下文", "sentiment": "neutral"}
            ],
        }
        
        print(f"\n[模拟 report_data]")
        print(json.dumps(mock_report_data, ensure_ascii=False, indent=2))
        
        gen_hash = calculate_report_hash_gen(mock_report_data)
        print(f"\n生成端哈希: {gen_hash}")
        
        # 验证端使用相同的数据
        verify_hash = calculate_report_hash_verify(mock_report_data)
        print(f"验证端哈希: {verify_hash}")
        
        print(f"\n--- 对比结果 ---")
        if gen_hash == verify_hash:
            print(f"✅ 模拟数据哈希一致!")
        else:
            print(f"❌ 模拟数据哈希不一致!")
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
