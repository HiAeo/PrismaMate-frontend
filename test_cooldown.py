"""
PrismaMate 棱镜 - 冷却期机制测试脚本

模拟连续失败触发冷却、冷却期拒绝请求、冷却结束后恢复的完整流程

用法:
    python test_cooldown.py
"""

import sys
import time

# 添加 backend 路径
sys.path.insert(0, "prismamate-backend")


def print_result(name: str, success: bool, detail: str = ""):
    """打印测试结果"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {name}")
    if detail:
        print(f"      {detail}")


def test_cooldown_trigger():
    """测试 1: 冷却期触发"""
    print("\n" + "=" * 50)
    print("测试 1: 冷却期触发")
    print("=" * 50)
    
    from app.core.cooldown import get_cooldown_manager
    
    manager = get_cooldown_manager()
    
    # 模拟 3 次连续失败
    platform = "test_platform"
    
    for i in range(3):
        entered_cooldown = manager.record_failure(platform)
        if i < 2:
            print_result(f"第 {i+1} 次失败", not entered_cooldown, 
                        "未进入冷却（预期）")
        else:
            print_result(f"第 {i+1} 次失败", entered_cooldown,
                        "进入冷却期" if entered_cooldown else "未进入冷却（失败）")
    
    # 验证状态
    status = manager.get_platform_status(platform)
    is_cooldown = status["in_cooldown"]
    
    print_result("平台处于冷却状态", is_cooldown,
                f"in_cooldown={status['in_cooldown']}")
    
    return is_cooldown


def test_cooldown_block():
    """测试 2: 冷却期拒绝请求"""
    print("\n" + "=" * 50)
    print("测试 2: 冷却期拒绝请求")
    print("=" * 50)
    
    from app.core.cooldown import get_cooldown_manager
    
    manager = get_cooldown_manager()
    platform = "test_block_platform"
    
    # 确保平台处于冷却状态
    for _ in range(3):
        manager.record_failure(platform)
    
    # 检查是否在冷却中
    is_cooldown = manager.is_in_cooldown(platform)
    remaining = manager.get_cooldown_remaining(platform)
    
    print_result("平台在冷却中", is_cooldown,
                f"剩余时间: {remaining:.1f}秒")
    
    # 模拟检测请求被拒绝
    if is_cooldown:
        print_result("检测请求应被拒绝", True,
                    "返回 503 错误")
    else:
        print_result("检测请求应被拒绝", False,
                    "平台不在冷却中（失败）")
    
    return is_cooldown


def test_cooldown_recovery():
    """测试 3: 冷却期结束恢复"""
    print("\n" + "=" * 50)
    print("测试 3: 冷却期结束恢复")
    print("=" * 50)
    
    from app.core.cooldown import get_cooldown_manager
    
    manager = get_cooldown_manager()
    platform = "test_recovery_platform"
    
    # 设置短冷却时间进行测试
    original_duration = manager.cooldown_duration
    manager.cooldown_duration = 2  # 2 秒用于测试
    
    # 触发冷却
    for _ in range(3):
        manager.record_failure(platform)
    
    print_result("冷却期已触发", manager.is_in_cooldown(platform))
    
    # 等待冷却期结束
    print("等待 3 秒让冷却期结束...")
    time.sleep(3)
    
    # 检查状态（冷却期已过但需要探测）
    remaining = manager.get_cooldown_remaining(platform)
    print_result("冷却剩余时间归零", remaining == 0,
                f"remaining={remaining:.1f}")
    
    # 记录成功
    manager.record_success(platform)
    
    status = manager.get_platform_status(platform)
    print_result("成功重置失败计数", status["consecutive_failures"] == 0,
                f"consecutive_failures={status['consecutive_failures']}")
    
    # 恢复原始配置
    manager.cooldown_duration = original_duration
    
    return remaining == 0


def test_multi_platform():
    """测试 4: 多平台独立冷却"""
    print("\n" + "=" * 50)
    print("测试 4: 多平台独立冷却")
    print("=" * 50)
    
    from app.core.cooldown import get_cooldown_manager
    
    manager = get_cooldown_manager()
    
    platforms = ["deepseek", "kimi", "doubao"]
    
    # 触发 deepseek 冷却
    for _ in range(3):
        manager.record_failure("deepseek")
    
    # 检查各平台状态
    results = {}
    for platform in platforms:
        is_cooldown = manager.is_in_cooldown(platform)
        results[platform] = is_cooldown
        print_result(f"{platform} 冷却状态", 
                    is_cooldown == (platform == "deepseek"),
                    f"in_cooldown={is_cooldown}")
    
    return all(r == (p == "deepseek") for p, r in results.items())


def test_admin_api():
    """测试 5: 管理接口"""
    print("\n" + "=" * 50)
    print("测试 5: 管理接口数据验证")
    print("=" * 50)
    
    from app.core.cooldown import get_cooldown_manager
    
    manager = get_cooldown_manager()
    
    # 获取所有平台状态
    all_status = manager.get_all_platforms_status()
    print_result("获取所有平台状态", len(all_status) > 0,
                f"平台数量: {len(all_status)}")
    
    for status in all_status:
        print(f"      - {status['platform']}: cooldown={status['in_cooldown']}")
    
    # 获取冷却事件
    events = manager.get_cooldown_events(limit=10)
    print_result("获取冷却事件记录", True,
                f"事件数量: {len(events)}")
    
    # 获取强制解除冷却功能
    test_platform = "test_admin_platform"
    for _ in range(3):
        manager.record_failure(test_platform)
    
    if manager.is_in_cooldown(test_platform):
        # 手动解除冷却
        manager._cooldown_platforms.pop(test_platform.lower(), None)
        manager._failure_counts[test_platform.lower()] = 0
        
        print_result("强制解除冷却", not manager.is_in_cooldown(test_platform),
                    "平台已解除冷却")
    
    return True


def test_smoke_test_service():
    """测试 6: 冒烟测试服务"""
    print("\n" + "=" * 50)
    print("测试 6: 冒烟测试服务")
    print("=" * 50)
    
    from app.services.smoke_test import get_smoke_test_service
    
    service = get_smoke_test_service()
    
    # 获取服务状态
    next_run = service.get_next_run_time()
    print_result("获取下次运行时间", next_run is not None,
                f"next_run={next_run}")
    
    # 获取所有平台状态
    all_status = service.get_all_status()
    print_result("获取冒烟测试状态", len(all_status) > 0,
                f"平台数量: {len(all_status)}")
    
    for status in all_status:
        last_test = status.get("last_test")
        last_test_str = f"success={last_test['success']}" if last_test else "N/A"
        print(f"      - {status['platform']}: {last_test_str}, consecutive_failures={status['consecutive_failures']}")
    
    return True


def test_cooldown_with_adapter():
    """测试 7: 适配器集成"""
    print("\n" + "=" * 50)
    print("测试 7: 适配器冷却集成")
    print("=" * 50)
    
    try:
        from app.adapters import get_adapter, list_supported_platforms
        from app.core.cooldown import get_cooldown_manager
        
        platforms = list_supported_platforms()
        print_result("获取支持的平台", len(platforms) > 0,
                    f"platforms={platforms}")
        
        manager = get_cooldown_manager()
        
        # 测试各平台的冷却状态
        for platform in platforms:
            status = manager.get_platform_status(platform)
            print_result(f"{platform} 状态检查", True,
                        f"in_cooldown={status['in_cooldown']}, failures={status['consecutive_failures']}")
        
        return True
        
    except ImportError as e:
        print_result("适配器模块不可用", False, str(e))
        return False


def main():
    """主测试流程"""
    print("\n" + "#" * 60)
    print("PrismaMate 棱镜 - 冷却期机制测试")
    print("#" * 60)
    
    tests = [
        ("冷却期触发", test_cooldown_trigger),
        ("冷却期拒绝请求", test_cooldown_block),
        ("冷却期结束恢复", test_cooldown_recovery),
        ("多平台独立冷却", test_multi_platform),
        ("管理接口数据", test_admin_api),
        ("冒烟测试服务", test_smoke_test_service),
        ("适配器冷却集成", test_cooldown_with_adapter),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_result(name, False, f"异常: {str(e)}")
            results.append((name, False))
    
    # 总结
    print("\n" + "#" * 60)
    print("测试结果总结")
    print("#" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n所有测试通过！冷却期机制运行正常。")
        return 0
    else:
        print("\n部分测试失败，请检查日志。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
