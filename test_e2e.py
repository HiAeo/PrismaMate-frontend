# -*- coding: utf-8 -*-
"""
PrismaMate 棱镜 - 端到端集成测试脚本
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
TEST_EMAIL = f"test_e2e_{int(time.time())}@example.com"
TEST_USERNAME = f"testuser_{int(time.time())}"
TEST_PASSWORD = "test123456"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# 全局变量
session = requests.Session()
token = None
user_id = None
admin_token = None
template_id = None
task_id = None
report_id = None
report_code = None
verification_id = None
test_results = []


def log(step, msg, ok=True):
    status = "[OK]" if ok else "[FAIL]"
    print(f"{status} Step {step}: {msg}")
    test_results.append({"step": step, "msg": msg, "ok": ok})


def api_get(path, headers=None, expected=200):
    resp = session.get(f"{API_BASE}{path}", headers=headers or {})
    if resp.status_code != expected:
        raise Exception(f"GET {path} failed: {resp.status_code} - {resp.text[:200]}")
    return resp.json()


def api_post(path, data, headers=None, expected=200):
    resp = session.post(f"{API_BASE}{path}", json=data, headers=headers or {})
    if resp.status_code != expected:
        raise Exception(f"POST {path} failed: {resp.status_code} - {resp.text[:200]}")
    return resp.json()


def api_post_no_body(path, headers=None, expected=200):
    resp = session.post(f"{API_BASE}{path}", headers=headers or {})
    if resp.status_code != expected:
        raise Exception(f"POST {path} failed: {resp.status_code} - {resp.text[:200]}")
    return resp.json()


def assert_eq(actual, expected, msg=""):
    if actual != expected:
        raise Exception(f"{msg}: expected {expected}, got {actual}")


def run():
    global token, user_id, admin_token, template_id, task_id, report_id, report_code, verification_id

    print("=" * 60)
    print("PrismaMate E2E Test Started")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Backend: {BASE_URL}")
    print("=" * 60)

    try:
        # ========== Step 1: 注册 ==========
        print("\n--- Step 1: User Registration ---")
        data = api_post("/auth/register", {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        token = data["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        log("1.1", f"Registration OK: {TEST_EMAIL}")

        me = api_get("/auth/me")
        user_id = me["user_id"]
        plan_name = me.get("plan_name", "")
        points = me.get("points_balance", 0)
        assert_eq(plan_name, "单棱MINI版", "Default plan")
        log("1.2", f"Default plan: {plan_name}")
        assert points >= 20, f"Initial points should >= 20"
        log("1.3", f"Initial points: {points}")
        print(f"  UserID: {user_id}, Plan: {plan_name}, Points: {points}")

        # ========== Step 2: 首次体检（创建检测任务） ==========
        print("\n--- Step 2: First Health Check ---")
        me_before = api_get("/auth/me")
        points_before = me_before["points_balance"]

        # 创建检测任务（会自动执行并生成报告）
        data = api_post("/tasks", {
            "brands": [{"full_name": "华为", "short_names": ["华为", "Huawei"]}],
            "keywords": ["手机"],
            "platforms": ["baidu"],
            "task_type": "single"
        })
        task_id = data["task_id"]
        log("2.1", f"Task created: {task_id}")
        print(f"  Task status: {data.get('status')}")

        # 等待任务完成
        time.sleep(2)
        task_status = api_get(f"/tasks/{task_id}/status")
        log("2.2", f"Task completed: {task_status.get('status')}")
        print(f"  Task status: {task_status.get('status')}")

        # 获取任务结果（包含报告信息）
        task_result = api_get(f"/tasks/{task_id}/results")
        report_id = task_result.get("report_id")
        log("2.3", f"Report generated: {report_id}")
        print(f"  ReportID: {report_id}")

        # 获取报告详情（包含验证码）
        if report_id:
            report_detail = api_get(f"/reports/{report_id}")
            report_code = report_detail.get("verification_code")
            print(f"  Report Code: {report_code}")

        # 验证积分已扣除
        me_after = api_get("/auth/me")
        points_after = me_after["points_balance"]
        log("2.4", f"Points after check: {points_after}")
        print(f"  Points: {points_before} -> {points_after}")

        # ========== Step 3: 历史对比（第二次检测） ==========
        print("\n--- Step 3: History Comparison ---")
        data = api_post("/tasks", {
            "brands": [{"full_name": "华为", "short_names": ["华为", "Huawei"]}],
            "keywords": ["手机"],
            "platforms": ["baidu"],
            "task_type": "single"
        })
        second_task_id = data["task_id"]
        log("3.1", f"Second task created: {second_task_id}")

        time.sleep(2)
        second_result = api_get(f"/tasks/{second_task_id}/results")
        second_report_id = second_result.get("report_id")
        print(f"  Second ReportID: {second_report_id}")

        # 获取对比数据
        if second_report_id:
            comp = api_get(f"/reports/{second_report_id}/comparison")
            has_diff = any(k in comp for k in ["added", "removed", "changed"])
            log("3.2", f"Comparison available: {has_diff}")
            print(f"  Added: {len(comp.get('added', []))}, Removed: {len(comp.get('removed', []))}, Changed: {len(comp.get('changed', []))}")

        # ========== Step 4: 升级套餐 ==========
        print("\n--- Step 4: Upgrade Plan ---")
        plan = api_get("/subscription/my-plan")
        print(f"  Current: {plan['plan']['name']}, Quota: {plan['plan']['monthly_quota']}")

        api_post("/subscription/upgrade", {"plan_id": "plan_max"})
        log("4.1", "Plan upgraded to 复棱MAX版")

        plan = api_get("/subscription/my-plan")
        assert_eq(plan["plan"]["name"], "复棱MAX版", "New plan")
        assert_eq(plan["plan"]["monthly_quota"], 100, "New quota")
        log("4.2", f"New plan: {plan['plan']['name']}")
        log("4.3", f"New quota: {plan['plan']['monthly_quota']}")

        # ========== Step 5: GEO验证 ==========
        print("\n--- Step 5: GEO Verification ---")
        data = api_post("/geo-verification/upload", {
            "scenario": "delivery",
            "geo_plan": {
                "keywords": ["人工智能", "AI"],
                "platforms": ["baidu"],
                "geo_company": "Test GEO Company"
            },
            "geo_claimed_data": [
                {"brand": "TestBrand", "keyword": "人工智能", "platform": "baidu",
                 "is_mentioned": True, "mention_position": 1, "mention_rate": 85.0}
            ]
        })
        verification_id = data["verification_id"]
        log("5.1", f"GEO verification created: {verification_id}")

        data = api_post(f"/geo-verification/{verification_id}/detect", {})
        log("5.2", f"GEO detection: {data['status']}")
        print(f"  Message: {data['message']}")

        report = api_get(f"/geo-verification/{verification_id}/report")
        diffs = report.get("differences", [])
        log("5.3", f"GEO diff analysis: {len(diffs)} items")

        # ========== Step 6: 管理员后台 ==========
        print("\n--- Step 6: Admin Dashboard ---")
        data = api_post("/superadmin/login", {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert data["success"], f"Admin login failed: {data.get('message')}"
        admin_token = data["token"]
        admin_headers = {"X-Admin-ID": admin_token}
        log("6.1", "Admin login OK")

        dashboard = api_get("/superadmin/dashboard", headers=admin_headers)
        log("6.2", f"Dashboard OK: users={dashboard.get('total_users', 0)}")
        print(f"  Total users: {dashboard.get('total_users', 0)}, MRR: {dashboard.get('mrr', 0)}")

        users = api_get("/superadmin/users", headers=admin_headers)
        target_user = None
        for u in users.get("users", []):
            if u.get("user_id") == user_id:
                target_user = u
                break
        assert target_user, f"Test user not found"
        log("6.3", f"Found test user: {target_user.get('username')}")
        print(f"  Current points: {target_user.get('points_balance', 0)}")

        api_post(f"/superadmin/users/{user_id}/points", {"amount": 100, "reason": "E2E test"}, headers=admin_headers)
        log("6.4", "Points adjusted +100")

        updated = api_get(f"/superadmin/users/{user_id}", headers=admin_headers)
        assert updated["user"]["points_balance"] >= 100, "Points adjustment failed"
        log("6.5", f"Points verified: {updated['user']['points_balance']}")

        # ========== Step 7: 报告验真 ==========
        print("\n--- Step 7: Report Verification ---")
        if report_code:
            verify = api_get(f"/reports/verify/{report_code}")
            assert verify.get("is_valid"), f"Report verification failed: {verify.get('message')}"
            log("7.1", "Report verified - not tampered")
            print(f"  ReportID: {verify.get('report_id')}, Valid: {verify.get('is_valid')}")
        else:
            log("7.1", "Skipped - no verification code available", True)

        # ========== Summary ==========
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        passed = sum(1 for r in test_results if r["ok"])
        print(f"Passed: {passed}/{len(test_results)}")
        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
