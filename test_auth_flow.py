"""
PrismaMate 棱镜 - 认证流程测试脚本

测试完整流程：
1. 用户注册
2. 用户登录（获取 Token）
3. 携带 Token 调用检测接口
4. 查询历史报告
5. 查询用户信息
"""

import requests
import json
import sys

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}


def print_result(name: str, success: bool, data: any = None, error: str = None):
    """打印测试结果"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {name}")
    if success and data:
        print(f"      数据: {json.dumps(data, ensure_ascii=False, indent=8)}")
    if not success and error:
        print(f"      错误: {error}")


def test_register(email: str, username: str, password: str) -> dict:
    """测试用户注册"""
    print("\n" + "="*50)
    print("测试 1: 用户注册")
    print("="*50)

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            print_result("注册成功", True, {
                "token_type": data.get("token_type"),
                "expires_in": data.get("expires_in")
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("注册失败", False, error=error)
            return None

    except requests.exceptions.ConnectionError:
        print_result("连接失败", False, error="无法连接到后端服务，请确保 uvicorn 已启动")
        return None
    except Exception as e:
        print_result("注册异常", False, error=str(e))
        return None


def test_login(email: str, password: str) -> dict:
    """测试用户登录"""
    print("\n" + "="*50)
    print("测试 2: 用户登录")
    print("="*50)

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            print_result("登录成功", True, {
                "token_type": data.get("token_type"),
                "expires_in": data.get("expires_in")
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("登录失败", False, error=error)
            return None

    except requests.exceptions.ConnectionError:
        print_result("连接失败", False, error="无法连接到后端服务")
        return None
    except Exception as e:
        print_result("登录异常", False, error=str(e))
        return None


def test_demo_login() -> dict:
    """测试演示用户登录"""
    print("\n" + "="*50)
    print("测试 2b: 演示用户登录")
    print("="*50)

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": "demo",
                "password": "demo123"
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            print_result("演示用户登录成功", True, {
                "token_type": data.get("token_type"),
                "expires_in": data.get("expires_in")
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("演示用户登录失败", False, error=error)
            return None

    except Exception as e:
        print_result("登录异常", False, error=str(e))
        return None


def test_get_me(token: str) -> dict:
    """测试获取当前用户信息"""
    print("\n" + "="*50)
    print("测试 3: 获取当前用户信息")
    print("="*50)

    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print_result("获取用户信息成功", True, data)
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("获取用户信息失败", False, error=error)
            return None

    except Exception as e:
        print_result("获取用户信息异常", False, error=str(e))
        return None


def test_detection(token: str, keywords: list = None, platform: str = "deepseek") -> dict:
    """测试品牌检测（带认证）"""
    print("\n" + "="*50)
    print(f"测试 4: 品牌检测 - {platform}（携带 Token）")
    print("="*50)

    if keywords is None:
        keywords = ["华为 AI 发展战略", "人工智能在中国"]

    try:
        response = requests.post(
            f"{BASE_URL}/detect/detect",
            json={
                "keywords": keywords,
                "brands": ["华为", "腾讯", "阿里巴巴"],
                "platform": platform
            },
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print_result(f"{platform} 检测成功", True, {
                "report_id": data.get("report_id"),
                "verification_code": data.get("verification_code"),
                "total_mentions": data.get("total_mentions"),
                "platform_used": data.get("platforms", [platform])[0] if data.get("platforms") else platform,
                "task_id": data.get("task_id"),
                "user_id": data.get("user_id")
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result(f"{platform} 检测失败", False, error=error)
            return None

    except Exception as e:
        print_result(f"{platform} 检测异常", False, error=str(e))
        return None


def test_detection_no_auth(keywords: list = None) -> dict:
    """测试品牌检测（不带认证 - MVP 模式）"""
    print("\n" + "="*50)
    print("测试 4b: 品牌检测（无认证 - MVP 模式）")
    print("="*50)

    if keywords is None:
        keywords = ["腾讯云服务"]

    try:
        response = requests.post(
            f"{BASE_URL}/detect/detect",
            json={
                "keywords": keywords,
                "brands": ["腾讯", "阿里巴巴"],
                "platform": "DeepSeek"
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            print_result("MVP 检测成功", True, {
                "report_id": data.get("report_id"),
                "verification_code": data.get("verification_code"),
                "total_mentions": data.get("total_mentions"),
                "user_id": data.get("user_id")  # 应该为 None
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("MVP 检测失败", False, error=error)
            return None

    except Exception as e:
        print_result("检测异常", False, error=str(e))
        return None


def test_reports(token: str) -> dict:
    """测试获取报告列表"""
    print("\n" + "="*50)
    print("测试 5: 查询报告列表")
    print("="*50)

    try:
        response = requests.get(
            f"{BASE_URL}/reports",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print_result("查询报告列表成功", True, {
                "total": data.get("total"),
                "reports_count": len(data.get("reports", []))
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("查询报告列表失败", False, error=error)
            return None

    except Exception as e:
        print_result("查询报告列表异常", False, error=str(e))
        return None


def test_verify_report(code: str) -> dict:
    """测试验证报告"""
    print("\n" + "="*50)
    print(f"测试 6: 验证报告 (验证码: {code})")
    print("="*50)

    try:
        response = requests.get(
            f"{BASE_URL}/reports/verify/{code}",
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            print_result("验证报告成功", True, {
                "valid": data.get("valid"),
                "report_id": data.get("report_id"),
                "report_hash": data.get("report_hash", "")[:32] + "..."
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("验证报告失败", False, error=error)
            return None

    except Exception as e:
        print_result("验证报告异常", False, error=str(e))
        return None


def test_tasks(token: str) -> dict:
    """测试获取任务列表"""
    print("\n" + "="*50)
    print("测试 7: 查询任务列表")
    print("="*50)

    try:
        response = requests.get(
            f"{BASE_URL}/tasks",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print_result("查询任务列表成功", True, {
                "total": data.get("total"),
                "tasks_count": len(data.get("tasks", []))
            })
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("查询任务列表失败", False, error=error)
            return None

    except Exception as e:
        print_result("查询任务列表异常", False, error=str(e))
        return None


def test_usage(token: str) -> dict:
    """测试获取用户用量"""
    print("\n" + "="*50)
    print("测试 8: 查询用户用量统计")
    print("="*50)

    try:
        response = requests.get(
            f"{BASE_URL}/user/usage",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print_result("查询用户用量成功", True, data)
            return data
        else:
            error = response.json().get("detail", response.text)
            print_result("查询用户用量失败", False, error=error)
            return None

    except Exception as e:
        print_result("查询用户用量异常", False, error=str(e))
        return None


def test_health():
    """测试健康检查"""
    print("\n" + "="*50)
    print("测试 0: 健康检查")
    print("="*50)

    try:
        response = requests.get(f"{BASE_URL}/detect/health", headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            print_result("健康检查通过", True, data)
            return data
        else:
            print_result("健康检查失败", False, error=response.text)
            return None

    except requests.exceptions.ConnectionError:
        print_result("连接失败", False, error="后端服务未启动，请运行: uvicorn app.main:app --reload --port 8000")
        return None
    except Exception as e:
        print_result("健康检查异常", False, error=str(e))
        return None


def main():
    """主测试流程"""
    print("\n" + "#"*60)
    print("PrismaMate 棱镜 - 认证流程完整测试")
    print("#"*60)

    # 0. 健康检查
    health = test_health()
    if not health:
        print("\n后端服务未启动，测试终止")
        print("\n请在 prismamate-backend 目录下运行：")
        print("  uvicorn app.main:app --reload --port 8000")
        sys.exit(1)

    # 显示支持的平台
    print("\n支持的平台:")
    platforms = health.get("supported_platforms", [])
    for p in platforms:
        print(f"  - {p}")

    # 1. 测试演示用户登录
    demo_token = test_demo_login()
    if not demo_token:
        print("\n演示用户登录失败，尝试其他测试...")

    # 2. 测试新用户注册
    test_email = f"test_{int(__import__('time').time())}@example.com"
    test_username = f"testuser_{int(__import__('time').time())}"
    test_password = "test123456"

    reg_result = test_register(test_email, test_username, test_password)
    if reg_result:
        token = reg_result.get("access_token")

        # 3. 获取用户信息
        test_get_me(token)

        # 4. 执行检测（测试多个平台）
        print("\n" + "="*50)
        print("测试 4: 多平台检测")
        print("="*50)

        for platform in ["deepseek", "kimi"]:
            detection = test_detection(token, platform=platform)
            if detection:
                # 5. 验证报告
                test_verify_report(detection.get("verification_code"))
                break  # 只验证第一个成功的

        # 6. 查询报告列表
        test_reports(token)

        # 7. 查询任务列表
        test_tasks(token)

        # 8. 查询用户用量
        test_usage(token)
    else:
        print("\n注册失败，跳过后续认证测试")
        # 仍然测试无认证检测
        test_detection_no_auth()

    # 总结
    print("\n" + "#"*60)
    print("测试完成")
    print("#"*60)
    print("\n可选的进一步测试：")
    print("1. 启动前端: npm run dev (在 prismamate-frontend 目录)")
    print("2. 访问: http://localhost:3000/login")
    print("3. 使用演示账号登录: demo / demo123")


if __name__ == "__main__":
    main()
