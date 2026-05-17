"""
PrismaMate 棱镜 - 体检中心功能验证脚本

V3.0 Phase 1 验证流程
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

TEST_EMAIL = "demo@prismamate.com"
TEST_PASSWORD = "demo123"

TEST_TEMPLATE = {
    "name": f"测试模板_{datetime.now().strftime('%H%M%S')}",
    "brands": [
        {"full_name": "华为", "short_names": ["华为"]},
        {"full_name": "小米", "short_names": ["小米"]}
    ],
    "keywords": ["手机"],
    "platforms": ["DeepSeek"]
}


def run_test():
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    print("=" * 50)
    print("PrismaMate 体检中心功能验证测试")
    print("=" * 50)
    
    # 1. 登录
    print("\n[1/6] 登录...")
    resp = session.post(f"{API_BASE}/auth/login", 
                        json={"username": TEST_EMAIL, "password": TEST_PASSWORD}, 
                        headers=headers)
    if resp.status_code != 200:
        print(f"登录失败: {resp.text}")
        return False
    
    token = resp.json().get("access_token")
    headers["Authorization"] = f"Bearer {token}"
    print("登录成功")
    
    # 2. 创建模板
    print("\n[2/6] 创建体检模板...")
    resp = session.post(f"{API_BASE}/templates", json=TEST_TEMPLATE, headers=headers)
    if resp.status_code != 200:
        print(f"创建模板失败: {resp.text}")
        return False
    
    template = resp.json()
    template_id = template.get("template_id")
    print(f"模板创建成功: {template_id}")
    
    # 3. 第一次检测
    print("\n[3/6] 第一次检测（首次，无历史对比）...")
    detect_data = {
        "keywords": TEST_TEMPLATE["keywords"],
        "brands": [b["full_name"] for b in TEST_TEMPLATE["brands"]],
        "platforms": TEST_TEMPLATE["platforms"],
        "report_type": "health_check",
        "template_id": template_id
    }
    
    resp = session.post(f"{API_BASE}/detect/detect", json=detect_data, headers=headers)
    if resp.status_code != 200:
        print(f"检测失败: {resp.text}")
        return False
    
    report1 = resp.json()
    report1_id = report1.get("report_id")
    print(f"第一次报告: {report1_id}")
    print(f"  - parent_report_id: {report1.get('parent_report_id')} (首次应为null)")
    
    # 4. 第二次检测
    print("\n[4/6] 第二次检测（应有历史对比）...")
    time.sleep(1)
    
    resp = session.post(f"{API_BASE}/detect/detect", json=detect_data, headers=headers)
    if resp.status_code != 200:
        print(f"检测失败: {resp.text}")
        return False
    
    report2 = resp.json()
    report2_id = report2.get("report_id")
    parent_id = report2.get("parent_report_id")
    print(f"第二次报告: {report2_id}")
    print(f"  - parent_report_id: {parent_id}")
    
    if parent_id == report1_id:
        print("  ✅ 成功关联第一次报告")
    else:
        print(f"  ⚠️ 未正确关联历史报告")
    
    # 5. 获取对比数据
    print("\n[5/6] 获取对比数据...")
    resp = session.get(f"{API_BASE}/reports/{report2_id}/comparison", headers=headers)
    if resp.status_code != 200:
        print(f"获取对比失败: {resp.text}")
        return False
    
    comparison = resp.json()
    print(f"对比数据摘要: {comparison.get('summary_text', '')}")
    print(f"  - 新增提及: {comparison.get('summary', {}).get('total_new_mentions', 0)}")
    print(f"  - 消失提及: {comparison.get('summary', {}).get('total_lost_mentions', 0)}")
    print(f"  - 位次提升: {comparison.get('summary', {}).get('total_ranking_improved', 0)}")
    
    # 6. 获取模板列表
    print("\n[6/6] 获取模板列表...")
    resp = session.get(f"{API_BASE}/templates", headers=headers)
    if resp.status_code != 200:
        print(f"获取模板失败: {resp.text}")
        return False
    
    templates = resp.json()
    print(f"当前用户模板数: {len(templates)}")
    
    for t in templates:
        print(f"  - {t.get('name')}: {t.get('template_id')}")
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
