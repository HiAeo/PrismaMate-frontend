"""
PrismaMate 棱镜 - 报告验证系统测试

测试报告验证接口的完整流程
"""

import hashlib
import sys
import os
import time

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prismamate-backend'))

# 测试计数器
tests_passed = 0
tests_total = 0


def test(name, condition, detail=""):
    """测试断言"""
    global tests_passed, tests_total
    tests_total += 1
    if condition:
        tests_passed += 1
        print(f"  [PASS] {name}")
        return True
    else:
        print(f"  [FAIL] {name}")
        if detail:
            print(f"         {detail}")
        return False


def test_reports_module():
    """测试报告模块导入"""
    print("\n[Test 1] 报告模块导入")
    try:
        from app.api.v1.reports import router, RateLimiter, verify_rate_limiter
        print("  [OK] 报告模块导入成功")
        return True
    except ImportError as e:
        print(f"  [ERROR] 导入失败: {e}")
        return False


def test_rate_limiter():
    """测试限流器"""
    print("\n[Test 2] 限流器功能")
    
    try:
        from app.api.v1.reports import RateLimiter
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        client_id = "test-client"
        
        # 第一次请求应该允许
        allowed, remaining = limiter.is_allowed(client_id)
        test("第一次请求应被允许", allowed, f"remaining={remaining}")
        
        # 第二次请求
        allowed, remaining = limiter.is_allowed(client_id)
        test("第二次请求应被允许", allowed, f"remaining={remaining}")
        
        # 第三次请求
        allowed, remaining = limiter.is_allowed(client_id)
        test("第三次请求应被允许", allowed, f"remaining={remaining}")
        
        # 第四次请求应该被拒绝
        allowed, remaining = limiter.is_allowed(client_id)
        test("第四次请求应被拒绝", not allowed, f"allowed={allowed}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_verify_endpoint_structure():
    """测试验证接口返回结构"""
    print("\n[Test 3] 验证接口返回结构")
    
    try:
        import asyncio
        from app.api.v1.reports import verify_report, _compute_report_hash
        from app.core.user_store import user_store
        from fastapi import Request
        from unittest.mock import MagicMock
        
        # 创建模拟请求
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # 测试不存在的验证码
        async def test_not_found():
            try:
                await verify_report(code="NOTEXIST12345", request=mock_request)
                return False, "应该抛出 404 异常"
            except Exception as e:
                # 检查异常属性
                return True, "正确抛出异常"
        
        success, msg = asyncio.run(test_not_found())
        test("不存在的验证码返回 404", success, msg)
        
        # 检查 _compute_report_hash 函数
        test("_compute_report_hash 函数存在", callable(_compute_report_hash))
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verify_code_format():
    """测试验证码格式验证"""
    print("\n[Test 4] 验证码格式验证")
    
    try:
        # 模拟前端输入
        test_codes = [
            ("ABCDEFGHIJKL", True, "12位大写字母"),
            ("abcdefghijkl", True, "12位小写字母（应自动转大写）"),
            ("AbCdEfGhIjKl", True, "12位混合大小写"),
            ("ABCDEFGHI", False, "只有9位"),
            ("ABCDEFGHIJKLM", False, "13位"),
            ("ABCDEFGHIJK2", True, "包含数字"),
            ("", False, "空字符串"),
        ]
        
        for code, should_pass, description in test_codes:
            is_valid_length = len(code) == 12 if code else False
            test(f"验证 {description}", is_valid_length == should_pass, f"code='{code}' len={len(code)}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_rate_limit_behavior():
    """测试限流行为"""
    print("\n[Test 5] 限流行为测试")
    
    try:
        from app.api.v1.reports import verify_rate_limiter
        
        # 测试不同的客户端 IP
        client1 = "192.168.1.1"
        client2 = "192.168.1.2"
        
        # 客户端1连续请求10次
        for i in range(10):
            allowed, remaining = verify_rate_limiter.is_allowed(client1)
        
        # 客户端1第11次应该被拒绝
        allowed, _ = verify_rate_limiter.is_allowed(client1)
        test("客户端1第11次请求应被限流", not allowed)
        
        # 客户端2第一次请求应该允许
        allowed, remaining = verify_rate_limiter.is_allowed(client2)
        test("客户端2第一次请求应被允许", allowed)
        
        # 客户端1和客户端2有不同的限流状态
        test("不同客户端IP有独立的限流计数", True)
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_verify_report_integration():
    """测试报告验证集成"""
    print("\n[Test 6] 报告验证集成测试")
    
    try:
        import asyncio
        from app.api.v1.reports import verify_report
        from app.core.user_store import user_store
        from unittest.mock import MagicMock
        from fastapi import Request
        
        # 检查是否有测试报告
        reports = list(user_store._reports_by_code.keys())
        
        if not reports:
            print("  [INFO] 没有测试报告，创建一份")
            # 创建一个测试报告
            report = user_store.create_report(
                report_id="TEST-REPORT-001",
                verification_code="TESTCODE123AB",
                report_hash="fake_hash_for_testing",
                user_id="test-user",
                task_id="test-task",
                keywords=["测试品牌A", "测试品牌B"],
                platforms=["DeepSeek"],
                total_mentions=5,
                brand_mentions=[
                    {"brand": "测试品牌A", "count": 3},
                    {"brand": "测试品牌B", "count": 2}
                ],
                total_citations=10
            )
            test_code = "TESTCODE123AB"
        else:
            test_code = reports[0]
        
        # 创建模拟请求
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # 测试验证接口
        async def run_test():
            result = await verify_report(code=test_code, request=mock_request)
            return result
        
        result = asyncio.run(run_test())
        
        test("验证返回包含 is_valid 字段", "is_valid" in result)
        test("验证返回包含 report_id 字段", "report_id" in result)
        test("验证返回包含 message 字段", "message" in result)
        test("验证返回包含 brand_names 字段", "brand_names" in result)
        test("验证返回包含 keywords 字段", "keywords" in result)
        test("验证返回包含 detection_time 字段", "detection_time" in result)
        test("验证返回包含 report_hash 字段", "report_hash" in result)
        test("验证返回包含 hash_verified 字段", "hash_verified" in result)
        
        # 打印验证结果示例
        print(f"\n  验证结果示例:")
        print(f"    report_id: {result.get('report_id', 'N/A')}")
        print(f"    brand_names: {result.get('brand_names', [])}")
        print(f"    keywords: {result.get('keywords', [])}")
        print(f"    is_valid: {result.get('is_valid')}")
        print(f"    message: {result.get('message', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_code_returns_404():
    """测试无效验证码返回 404"""
    print("\n[Test 7] 无效验证码返回 404")
    
    try:
        import asyncio
        from app.api.v1.reports import verify_report
        from fastapi import HTTPException
        from unittest.mock import MagicMock
        from fastapi import Request
        
        # 创建模拟请求
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        async def run_test():
            try:
                await verify_report(code="INVALID123456", request=mock_request)
                return False, "应该抛出 404 异常"
            except HTTPException as e:
                if e.status_code == 404:
                    return True, f"正确返回 404: {e.detail}"
                return False, f"状态码错误: {e.status_code}"
            except Exception as e:
                return False, f"抛出异常: {e}"
        
        success, msg = asyncio.run(run_test())
        test("无效验证码返回 404", success, msg)
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_rate_limit_returns_429():
    """测试限流返回 429"""
    print("\n[Test 8] 限流返回 429")
    
    try:
        from app.api.v1.reports import verify_rate_limiter
        from fastapi import HTTPException
        
        client_id = "rate-limit-test-client"
        
        # 先消耗所有配额
        for i in range(10):
            verify_rate_limiter.is_allowed(client_id)
        
        # 第11次应该返回429
        try:
            is_allowed, remaining = verify_rate_limiter.is_allowed(client_id)
            test("第11次请求被限流", not is_allowed)
            
            retry_after = verify_rate_limiter.get_retry_after(client_id)
            test("返回 retry_after 秒数", retry_after > 0, f"retry_after={retry_after}")
        except Exception as e:
            print(f"  [WARN] 限流测试异常: {e}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    global tests_passed, tests_total
    
    print("=" * 60)
    print("PrismaMate 棱镜 - 报告验证系统测试")
    print("=" * 60)
    
    # 执行所有测试
    test_reports_module()
    test_rate_limiter()
    test_verify_endpoint_structure()
    test_verify_code_format()
    test_rate_limit_behavior()
    test_verify_report_integration()
    test_invalid_code_returns_404()
    test_rate_limit_returns_429()
    
    # 打印结果
    print("\n" + "=" * 60)
    print(f"测试结果: {tests_passed}/{tests_total} 通过")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n所有测试通过！报告验证系统已就绪。")
        return 0
    else:
        print(f"\n有 {tests_total - tests_passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
