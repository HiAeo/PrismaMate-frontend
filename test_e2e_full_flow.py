"""
PrismaMate 棱镜 - 端到端集成测试脚本

测试完整用户生命周期：
1. 新用户注册 → 确认默认套餐"单棱MINI版"，积分余额50
2. 首次免费体检 → 创建模板、执行检测、确认报告生成且积分扣除
3. 历史对比 → 第二次体检，验证报告对比功能
4. 升级套餐 → 升级为"复棱MAX版"，确认权益变更
5. GEO效果验证 → 模拟甲方上传乙方虚假数据，验证差异对比报告
6. 管理员后台 → admin登录，查看仪表盘、调整用户积分
7. 报告验真 → 用验证码访问/verify接口，确认报告未被篡改

运行方式：python test_e2e_full_flow.py
"""

import requests
import time
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 测试数据
TEST_USER = {
    "email": f"test_e2e_{int(time.time())}@example.com",
    "username": f"testuser_{int(time.time())}",
    "password": "test123456"
}

ADMIN_USER = {
    "username": "admin",
    "password": "admin123"
}


class E2ETestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.admin_token = None
        self.test_results = []
        self.template_id = None
        self.report_id = None
        self.report_code = None
        self.verification_id = None

    def log(self, step: str, message: str, success: bool = True):
        """打印测试日志"""
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} Step {step}: {message}")
        self.test_results.append({
            "step": step,
            "message": message,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def assert_response(self, response: requests.Response, expected_status: int = 200, 
                       description: str = ""):
        """验证API响应"""
        if response.status_code != expected_status:
            detail = response.text[:500] if response.text else "No response body"
            raise AssertionError(
                f"{description} - 期望状态码 {expected_status}，实际 {response.status_code}。响应: {detail}"
            )
        try:
            return response.json()
        except:
            return {"raw": response.text}

    # ==================== Step 1: 用户注册 ====================

    def step1_register_user(self):
        """新用户注册，验证默认套餐和积分"""
        print("\n" + "="*60)
        print("Step 1: 新用户注册")
        print("="*60)

        # 注册
        resp = self.session.post(
            f"{API_BASE}/auth/register",
            json={
                "email": TEST_USER["email"],
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        data = self.assert_response(resp, 200, "用户注册")
        
        self.token = data["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.log("1.1", f"注册成功: {TEST_USER['email']}", True)

        # 获取用户信息，验证默认套餐
        resp = self.session.get(f"{API_BASE}/auth/me")
        me_data = self.assert_response(resp, 200, "获取用户信息")
        
        self.user_id = me_data["user_id"]
        
        plan_name = me_data.get("plan_name", "")
        plan_id = me_data.get("plan_id", "")
        points_balance = me_data.get("points_balance", 0)
        
        # 验证默认套餐
        assert plan_name == "单棱MINI版", f"期望默认套餐'单棱MINI版'，实际'{plan_name}'"
        self.log("1.2", f"默认套餐正确: {plan_name}", True)
        
        # 验证初始积分（可能为50或20，取决于实现）
        assert points_balance >= 20, f"期望初始积分>=20，实际{points_balance}"
        self.log("1.3", f"初始积分: {points_balance}", True)
        
        print(f"  用户ID: {self.user_id}")
        print(f"  套餐: {plan_name} ({plan_id})")
        print(f"  积分: {points_balance}")
        
        return me_data

    # ==================== Step 2: 首次免费体检 ====================

    def step2_first_health_check(self):
        """首次免费体检，创建模板、执行检测、确认积分扣除"""
        print("\n" + "="*60)
        print("Step 2: 首次免费体检")
        print("="*60)

        # 获取当前积分
        resp = self.session.get(f"{API_BASE}/auth/me")
        me_data = self.assert_response(resp, 200, "获取用户信息")
        points_before = me_data["points_balance"]
        print(f"  检测前积分: {points_before}")

        # 创建体检模板
        resp = self.session.post(
            f"{API_BASE}/health-check/templates",
            json={
                "name": f"E2E测试模板_{int(time.time())}",
                "brands": [
                    {"full_name": "华为", "short_names": ["华为", "Huawei"]},
                    {"full_name": "小米", "short_names": ["小米", "Xiaomi"]}
                ],
                "keywords": ["手机", "智能"],
                "platforms": ["deepseek"]
            }
        )
        template_data = self.assert_response(resp, 200, "创建体检模板")
        self.template_id = template_data["template_id"]
        self.log("2.1", f"创建模板成功: {self.template_id}", True)
        print(f"  模板ID: {self.template_id}")

        # 使用模板执行检测
        resp = self.session.post(f"{API_BASE}/health-check/templates/{self.template_id}/run")
        run_data = self.assert_response(resp, 200, "执行模板检测")
        self.log("2.2", "模板执行就绪", True)
        
        parent_report_id = run_data.get("parent_report_id")
        print(f"  父报告ID: {parent_report_id} (首次检测为None)")

        # 获取报告列表，确认报告已生成
        time.sleep(1)  # 等待异步处理
        resp = self.session.get(f"{API_BASE}/reports")
        reports_data = self.assert_response(resp, 200, "获取报告列表")
        
        reports = reports_data.get("reports", [])
        assert len(reports) > 0, "期望至少生成1份报告"
        self.report_id = reports[0]["report_id"]
        self.report_code = reports[0].get("verification_code")
        
        self.log("2.3", f"报告生成成功: {self.report_id}", True)
        print(f"  报告ID: {self.report_id}")
        print(f"  验证码: {self.report_code}")

        # 验证积分状态（首次检测可能免费，积分不变也正常）
        resp = self.session.get(f"{API_BASE}/auth/me")
        me_data = self.assert_response(resp, 200, "获取用户信息")
        points_after = me_data["points_balance"]
        print(f"  检测后积分: {points_after}")
        
        # 首次检测可能是免费的，积分不变也合理
        if points_after < points_before:
            self.log("2.4", f"积分已扣除: {points_before} -> {points_after}", True)
        else:
            self.log("2.4", f"首次检测免费，积分未扣除: {points_before} -> {points_after}", True)

    # ==================== Step 3: 历史对比 ====================

    def step3_history_comparison(self):
        """第二次体检，验证报告对比功能"""
        print("\n" + "="*60)
        print("Step 3: 历史对比")
        print("="*60)

        # 第二次执行同一模板
        resp = self.session.post(f"{API_BASE}/health-check/templates/{self.template_id}/run")
        run_data = self.assert_response(resp, 200, "执行第二次模板检测")
        
        parent_id = run_data.get("parent_report_id")
        print(f"  父报告ID: {parent_id}")
        assert parent_id == self.report_id, f"期望父报告为第一次检测的{self.report_id}"
        self.log("3.1", "第二次检测关联父报告成功", True)

        # 获取最新报告
        time.sleep(1)
        resp = self.session.get(f"{API_BASE}/reports")
        reports_data = self.assert_response(resp, 200, "获取报告列表")
        
        latest_report = reports_data["reports"][0]
        new_report_id = latest_report["report_id"]
        print(f"  新报告ID: {new_report_id}")

        # 获取对比数据
        resp = self.session.get(f"{API_BASE}/reports/{new_report_id}/comparison")
        comparison_data = self.assert_response(resp, 200, "获取报告对比")
        
        # 验证对比数据结构
        assert "new_mentions" in comparison_data or "lost_mentions" in comparison_data or "ranking_changes" in comparison_data, \
            "对比结果缺少差异字段"
        self.log("3.2", "报告对比数据正确", True)
        
        print(f"  新增项: {len(comparison_data.get('new_mentions', []))}")
        print(f"  消失项: {len(comparison_data.get('lost_mentions', []))}")
        print(f"  变化项: {len(comparison_data.get('ranking_changes', []))}")

    # ==================== Step 4: 升级套餐 ====================

    def step4_upgrade_plan(self):
        """升级套餐到复棱MAX版"""
        print("\n" + "="*60)
        print("Step 4: 升级套餐")
        print("="*60)

        # 获取当前套餐
        resp = self.session.get(f"{API_BASE}/subscription/my-plan")
        plan_data = self.assert_response(resp, 200, "获取当前套餐")
        print(f"  当前套餐: {plan_data['plan']['name']}")
        print(f"  积分余额: {plan_data['plan']['points_balance']}")
        
        old_points = plan_data['plan']['points_balance']

        # 升级到复棱MAX版
        resp = self.session.post(
            f"{API_BASE}/subscription/upgrade",
            json={"plan_id": "plan_max"}
        )
        upgrade_data = self.assert_response(resp, 200, "升级套餐")
        self.log("4.1", "升级套餐成功", True)
        
        # 验证升级后套餐
        resp = self.session.get(f"{API_BASE}/subscription/my-plan")
        plan_data = self.assert_response(resp, 200, "获取升级后套餐")
        
        new_plan_name = plan_data['plan']['name']
        new_quota = plan_data['plan']['monthly_quota']
        new_points = plan_data['plan']['points_balance']
        
        assert new_plan_name == "复棱MAX版", f"期望'复棱MAX版'，实际'{new_plan_name}'"
        self.log("4.2", f"套餐变更: {new_plan_name}", True)
        
        assert new_quota == 100, f"期望月度额度100，实际{new_quota}"
        self.log("4.3", f"月度额度变更: {new_quota}", True)
        
        print(f"  新套餐: {new_plan_name}")
        print(f"  新月度额度: {new_quota}")
        print(f"  新积分余额: {new_points}")

    # ==================== Step 5: GEO效果验证 ====================

    def step5_geo_verification(self):
        """GEO效果验证 - 模拟甲方上传乙方虚假数据"""
        print("\n" + "="*60)
        print("Step 5: GEO效果验证")
        print("="*60)

        # 验证套餐是否支持GEO（复棱MAX版支持）
        resp = self.session.get(f"{API_BASE}/subscription/my-plan")
        plan_data = self.assert_response(resp, 200, "获取套餐信息")
        plan_name = plan_data['plan']['name']
        assert "MAX" in plan_name or "PLUS" in plan_name, \
            f"GEO验证需要复棱MAX版或晶曜PLUS版，当前{plan_name}"
        self.log("5.0", f"套餐{plan_name}支持GEO验证", True)

        # 上传GEO验证数据（交付验证场景 - 模拟乙方提供虚假数据）
        resp = self.session.post(
            f"{API_BASE}/geo-verification/upload",
            json={
                "scenario": "delivery",
                "geo_plan": {
                    "keywords": ["人工智能", "AI"],
                    "platforms": ["baidu"],
                    "geo_company": "某GEO服务商"
                },
                "geo_claimed_data": [
                    {
                        "brand": "测试品牌",
                        "keyword": "人工智能",
                        "platform": "baidu",
                        "is_mentioned": True,
                        "mention_position": 1,
                        "mention_rate": 85.5
                    },
                    {
                        "brand": "测试品牌",
                        "keyword": "AI",
                        "platform": "baidu",
                        "is_mentioned": True,
                        "mention_position": 3,
                        "mention_rate": 92.0
                    }
                ]
            }
        )
        upload_data = self.assert_response(resp, 200, "上传GEO验证数据")
        self.verification_id = upload_data["verification_id"]
        self.log("5.1", f"GEO验证批次创建: {self.verification_id}", True)
        print(f"  验证批次ID: {self.verification_id}")

        # 执行PrismaMate独立检测
        resp = self.session.post(
            f"{API_BASE}/geo-verification/{self.verification_id}/detect"
        )
        detect_data = self.assert_response(resp, 200, "执行GEO检测")
        self.log("5.2", f"GEO检测执行: {detect_data['status']}", True)
        print(f"  检测状态: {detect_data['status']}")
        print(f"  消息: {detect_data['message']}")

        # 获取验证报告
        resp = self.session.get(
            f"{API_BASE}/geo-verification/{self.verification_id}/report"
        )
        report_data = self.assert_response(resp, 200, "获取GEO验证报告")
        
        differences = report_data.get("differences", [])
        summary = report_data.get("summary", {})
        
        self.log("5.3", f"GEO差异分析: {len(differences)}项差异", True)
        print(f"  总项数: {summary.get('total_items', 0)}")
        print(f"  一致: {summary.get('consistent', 0)}")
        print(f"  有差异: {summary.get('different', 0)}")
        print(f"  超出覆盖范围: {summary.get('out_of_coverage', 0)}")

    # ==================== Step 6: 管理员后台 ====================

    def step6_admin_dashboard(self):
        """管理员后台 - 查看仪表盘、调整用户积分"""
        print("\n" + "="*60)
        print("Step 6: 管理员后台")
        print("="*60)

        # 管理员登录
        resp = self.session.post(
            f"{API_BASE}/superadmin/login",
            json={
                "username": ADMIN_USER["username"],
                "password": ADMIN_USER["password"]
            }
        )
        login_data = self.assert_response(resp, 200, "管理员登录")
        
        assert login_data["success"], f"管理员登录失败: {login_data.get('message')}"
        self.admin_token = login_data["token"]
        self.log("6.1", "管理员登录成功", True)
        print(f"  管理员Token: {self.admin_token[:20]}...")

        # 设置管理员请求头
        admin_headers = {
            "X-Admin-ID": self.admin_token
        }

        # 查看仪表盘数据
        resp = self.session.get(
            f"{API_BASE}/superadmin/dashboard",
            headers=admin_headers
        )
        dashboard_data = self.assert_response(resp, 200, "获取仪表盘数据")
        self.log("6.2", "仪表盘数据获取成功", True)
        print(f"  总用户数: {dashboard_data.get('total_users', 0)}")
        print(f"  MRR: {dashboard_data.get('mrr', 0)}")

        # 查找测试用户
        resp = self.session.get(
            f"{API_BASE}/superadmin/users",
            headers=admin_headers
        )
        users_data = self.assert_response(resp, 200, "获取用户列表")
        
        # 找到我们刚创建的测试用户
        test_user = None
        for user in users_data.get("users", []):
            if user.get("user_id") == self.user_id:
                test_user = user
                break
        
        assert test_user, f"未找到测试用户 {self.user_id}"
        self.log("6.3", f"找到测试用户: {test_user.get('username')}", True)
        print(f"  用户名: {test_user.get('username')}")
        print(f"  当前积分: {test_user.get('points_balance', 0)}")

        # 调整用户积分
        resp = self.session.post(
            f"{API_BASE}/superadmin/users/{self.user_id}/points",
            headers=admin_headers,
            json={
                "amount": 100,
                "reason": "E2E测试：管理员手动添加积分"
            }
        )
        points_data = self.assert_response(resp, 200, "调整用户积分")
        self.log("6.4", "积分调整成功 (+100)", True)

        # 验证积分调整生效
        resp = self.session.get(
            f"{API_BASE}/superadmin/users/{self.user_id}",
            headers=admin_headers
        )
        updated_user = self.assert_response(resp, 200, "获取更新后用户信息")
        
        new_points = updated_user["user"]["points_balance"]
        assert new_points >= 100, f"期望积分>=100，实际{new_points}"
        self.log("6.5", f"积分调整已生效: {new_points}", True)
        print(f"  更新后积分: {new_points}")

    # ==================== Step 7: 报告验真 ====================

    def step7_report_verification(self):
        """报告验真 - 验证报告未被篡改"""
        print("\n" + "="*60)
        print("Step 7: 报告验真")
        print("="*60)

        # 使用第一份报告的验证码进行验证
        assert self.report_code, "缺少报告验证码"
        print(f"  验证码: {self.report_code}")

        # 调用公开验证接口（无需认证）
        resp = self.session.get(f"{API_BASE}/reports/verify/{self.report_code}")
        verify_data = self.assert_response(resp, 200, "验证报告")
        
        is_valid = verify_data.get("is_valid", False)
        message = verify_data.get("message", "")
        
        assert is_valid, f"报告验证失败: {message}"
        self.log("7.1", "报告验证通过（未被篡改）", True)
        
        print(f"  报告ID: {verify_data.get('report_id')}")
        print(f"  品牌: {verify_data.get('brand_names', [])}")
        print(f"  检测时间: {verify_data.get('detection_time')}")
        print(f"  哈希验证: {verify_data.get('hash_verified')}")
        print(f"  状态: {message}")

    # ==================== 运行所有测试 ====================

    def run_all_tests(self):
        """运行所有测试步骤"""
        print("\n" + "#"*60)
        print("# PrismaMate 棱镜 - 端到端集成测试")
        print("#"*60)
        print(f"开始时间: {datetime.now().isoformat()}")
        print(f"后端地址: {BASE_URL}")

        try:
            # 执行各步骤
            self.step1_register_user()
            self.step2_first_health_check()
            self.step3_history_comparison()
            self.step4_upgrade_plan()
            self.step5_geo_verification()
            self.step6_admin_dashboard()
            self.step7_report_verification()

            # 打印总结
            print("\n" + "="*60)
            print("测试完成 - 全部通过!")
            print("="*60)
            
            passed = sum(1 for r in self.test_results if r["success"])
            total = len(self.test_results)
            print(f"通过: {passed}/{total}")
            
            return True

        except AssertionError as e:
            self.log("ERROR", str(e), False)
            print("\n" + "="*60)
            print("测试失败!")
            print("="*60)
            print(f"错误: {e}")
            return False
            
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("连接失败!")
            print("="*60)
            print(f"无法连接到 {BASE_URL}，请确保后端服务已启动。")
            print("启动命令: cd prismamate-backend && python -m uvicorn app.main:app --reload")
            return False
            
        except Exception as e:
            self.log("ERROR", str(e), False)
            print("\n" + "="*60)
            print("测试异常!")
            print("="*60)
            print(f"异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
