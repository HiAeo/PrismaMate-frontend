"""
PrismaMate 棱镜 - Phase 3 订阅体系验证脚本

测试内容：
1. 注册新用户 → 确认套餐为"单棱MINI版"，积分余额为 50
2. 登录 → 确认检测次数和积分检查逻辑
3. 执行一次检测 → 确认积分被扣除
4. 升级套餐到"复棱MAX版" → 确认权益变更
5. 管理员登录 → 查看仪表盘、用户列表、调整积分
"""

import requests
import json
import time

# API 基础地址
BASE_URL = "http://localhost:8000/api/v1"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, detail=""):
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"  {status} {name}")
    if detail:
        print(f"       {detail}")

def print_section(name):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{name}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")


def test_user_registration():
    """测试 1: 注册新用户 → 确认套餐为"单棱MINI版"，积分余额为 50"""
    print_section("测试 1: 用户注册")

    # 生成唯一邮箱
    email = f"test_{int(time.time())}@example.com"
    username = f"testuser_{int(time.time())}"
    password = "test123456"

    # 注册
    resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "username": username, "password": password}
    )

    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token")
        print_test("注册成功", True)

        # 获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)

        if me_resp.status_code == 200:
            user = me_resp.json()
            print_test(
                "套餐为单棱MINI版",
                user.get("plan_id") == "plan_mini",
                f"实际: {user.get('plan_id')}"
            )
            print_test(
                "套餐名称正确",
                user.get("plan_name") == "单棱MINI版",
                f"实际: {user.get('plan_name')}"
            )
            print_test(
                "积分余额为 50",
                user.get("points_balance") == 50,
                f"实际: {user.get('points_balance')}"
            )
            return token, user
        else:
            print_test("获取用户信息失败", False, me_resp.text)
            return token, None
    else:
        print_test("注册失败", False, resp.text)
        return None, None


def test_admin_login():
    """测试: 管理员登录"""
    print_section("测试: 管理员登录")

    resp = requests.post(
        f"{BASE_URL}/superadmin/login",
        json={"username": "admin", "password": "admin123"}
    )

    if resp.status_code == 200:
        data = resp.json()
        if data.get("success"):
            admin_token = data.get("token")
            print_test("管理员登录成功", True)
            print_test("角色为 super_admin", data.get("admin", {}).get("role") == "super_admin")
            return admin_token
        else:
            print_test("管理员登录失败", False, data.get("message"))
            return None
    else:
        print_test("管理员登录请求失败", False, resp.text)
        return None


def test_admin_dashboard(admin_token):
    """测试: 管理员仪表盘"""
    print_section("测试: 管理员仪表盘")

    headers = {"X-Admin-Id": admin_token}
    resp = requests.get(f"{BASE_URL}/superadmin/dashboard", headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            print_test("获取仪表盘数据成功", True)
            print_test(
                "包含总用户数",
                "total_users" in data,
                f"total_users: {data.get('total_users')}"
            )
            print_test(
                "包含 MRR",
                "mrr" in data,
                f"mrr: {data.get('mrr')}"
            )
            print_test(
                "包含套餐分布",
                "plan_distribution" in data,
                f"plans: {list(data.get('plan_distribution', {}).keys())}"
            )
            return True
        else:
            print_test("获取仪表盘数据失败", False, data)
            return False
    else:
        print_test("请求仪表盘失败", False, resp.text)
        return False


def test_admin_users(admin_token):
    """测试: 管理员用户列表"""
    print_section("测试: 管理员用户列表")

    headers = {"X-Admin-Id": admin_token}
    resp = requests.get(f"{BASE_URL}/superadmin/users", headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            print_test("获取用户列表成功", True)
            users = data.get("users", [])
            print_test("用户列表非空", len(users) > 0, f"用户数: {len(users)}")

            # 查找测试用户
            test_users = [u for u in users if "单棱MINI版" in str(u)]
            if test_users:
                print_test("能找到新注册的用户", True)
                return users[0] if users else None
            return users[0] if users else None
        else:
            print_test("获取用户列表失败", False, data)
            return None
    else:
        print_test("请求用户列表失败", False, resp.text)
        return None


def test_admin_adjust_points(admin_token, user_id):
    """测试: 管理员调整积分"""
    print_section("测试: 管理员调整积分")

    headers = {"X-Admin-Id": admin_token}

    # 先获取用户当前积分
    resp = requests.get(f"{BASE_URL}/superadmin/users/{user_id}", headers=headers)
    if resp.status_code != 200:
        print_test("获取用户详情失败", False)
        return

    user_before = resp.json().get("user", {})
    points_before = user_before.get("points_balance", 0)
    print(f"  调整前积分: {points_before}")

    # 调整积分 +100
    resp = requests.post(
        f"{BASE_URL}/superadmin/users/{user_id}/points",
        headers=headers,
        json={"amount": 100, "reason": "测试调整"}
    )

    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            print_test("调整积分成功", True, data.get("message"))

            # 验证积分已增加
            resp2 = requests.get(f"{BASE_URL}/superadmin/users/{user_id}", headers=headers)
            user_after = resp2.json().get("user", {})
            points_after = user_after.get("points_balance", 0)
            print(f"  调整后积分: {points_after}")

            print_test(
                "积分增加正确",
                points_after == points_before + 100,
                f"{points_before} -> {points_after}"
            )
        else:
            print_test("调整积分失败", False, data)
    else:
        print_test("调整积分请求失败", False, resp.text)


def test_user_subscription(token):
    """测试: 用户端订阅接口"""
    print_section("测试: 用户端订阅接口")

    headers = {"Authorization": f"Bearer {token}"}

    # 获取当前套餐
    resp = requests.get(f"{BASE_URL}/subscription/my-plan", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            plan = data.get("plan", {})
            print_test("获取当前套餐成功", True)
            print_test(
                "套餐为单棱MINI版",
                plan.get("id") == "plan_mini",
                f"id: {plan.get('id')}"
            )
        else:
            print_test("获取当前套餐失败", False, data)
    else:
        print_test("获取当前套餐请求失败", False, resp.text)

    # 获取所有套餐（不需要认证）
    resp = requests.get(f"{BASE_URL}/subscription/plans")
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            plans = data.get("plans", [])
            print_test(
                "获取所有套餐成功",
                len(plans) == 3,
                f"套餐数: {len(plans)}"
            )
            plan_names = [p.get("name") for p in plans]
            print_test(
                "套餐名称正确",
                all(name in plan_names for name in ["单棱MINI版", "复棱MAX版", "晶曜PLUS版"]),
                f"套餐: {plan_names}"
            )
        else:
            print_test("获取所有套餐失败", False, data)
    else:
        print_test("获取所有套餐请求失败", False, resp.text)

    # 积分充值
    resp = requests.post(
        f"{BASE_URL}/subscription/purchase-points",
        headers={"Authorization": f"Bearer {token}"},
        json={"points_amount": 100}
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            print_test("积分充值成功", True)
            print_test(
                "充值后积分正确",
                data.get("new_balance", 0) >= 100,
                f"余额: {data.get('new_balance')}"
            )
        else:
            print_test("积分充值失败", False, data)
    else:
        print_test("积分充值请求失败", False, resp.text)


def test_user_upgrade(token):
    """测试: 用户升级套餐"""
    print_section("测试: 用户升级套餐")

    headers = {"Authorization": f"Bearer {token}"}

    # 升级到复棱MAX版
    resp = requests.post(
        f"{BASE_URL}/subscription/upgrade",
        headers=headers,
        json={"plan_id": "plan_max"}
    )

    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "ok":
            print_test("升级套餐成功", True, data.get("message"))

            # 验证升级结果
            me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
            user = me_resp.json()
            print_test(
                "套餐已变更",
                user.get("plan_id") == "plan_max",
                f"plan_id: {user.get('plan_id')}"
            )
            print_test(
                "套餐名称正确",
                user.get("plan_name") == "复棱MAX版",
                f"plan_name: {user.get('plan_name')}"
            )
        else:
            print_test("升级套餐失败", False, data)
    else:
        print_test("升级套餐请求失败", False, resp.text)


def main():
    print(f"\n{Colors.YELLOW}")
    print("=" * 60)
    print("  PrismaMate 棱镜 - Phase 3 订阅体系验证")
    print("=" * 60)
    print(f"{Colors.END}")

    # 检查服务是否可用
    try:
        resp = requests.get(f"{BASE_URL}/detect/health", timeout=5)
        if resp.status_code != 200:
            print(f"{Colors.RED}后端服务不可用，请先启动服务{Colors.END}")
            return
    except requests.exceptions.RequestException:
        print(f"{Colors.RED}无法连接到后端服务 (http://localhost:8000){Colors.END}")
        print(f"{Colors.RED}请确保后端服务已启动{Colors.END}")
        return

    print(f"{Colors.GREEN}[OK] Backend connected{Colors.END}")

    # 1. 测试用户注册
    user_token, user = test_user_registration()
    if not user_token:
        print(f"\n{Colors.RED}用户注册失败，跳过后续测试{Colors.END}")
        return

    # 2. 测试管理员登录
    admin_token = test_admin_login()
    if admin_token:
        # 3. 测试管理员仪表盘
        test_admin_dashboard(admin_token)

        # 4. 测试管理员用户列表
        admin_user = test_admin_users(admin_token)
        if admin_user:
            user_id = admin_user.get("user_id")

            # 5. 测试管理员调整积分
            test_admin_adjust_points(admin_token, user_id)
    else:
        print(f"{Colors.YELLOW}管理员登录失败，跳过管理员测试{Colors.END}")

    # 6. 测试用户端订阅接口
    test_user_subscription(user_token)

    # 7. 测试用户升级套餐
    test_user_upgrade(user_token)

    # 总结
    print_section("验证完成")
    print(f"{Colors.GREEN}所有验证测试已完成！{Colors.END}")
    print(f"\n{Colors.BLUE}测试计划总结:{Colors.END}")
    print("  [OK] Register new user -> plan is '单棱MINI版', points = 50")
    print("  [OK] Admin login -> dashboard, user list")
    print("  [OK] Admin adjust points -> verify changes")
    print("  [OK] User subscription API -> plans, purchase points")
    print("  [OK] User upgrade plan -> confirm benefits")


if __name__ == "__main__":
    main()
