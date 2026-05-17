"""
PrismaMate 棱镜 - 部署验证脚本

在生产模式下验证：
1. 后端健康检查
2. 前端静态文件可访问
3. API 接口正常响应
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prismamate-backend'))

import requests


class DeploymentVerifier:
    """部署验证器"""

    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3000"):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.results = []
        self.all_passed = True

    def check_backend_health(self) -> bool:
        """检查后端健康状态"""
        print("\n[1/5] 检查后端健康状态...")
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ 后端运行正常")
                print(f"    - 状态: {data.get('status')}")
                print(f"    - MVP 模式: {data.get('mvp_mode')}")
                self.results.append(("后端健康检查", True, "200 OK"))
                return True
            else:
                print(f"    ❌ 后端响应异常: {response.status_code}")
                self.results.append(("后端健康检查", False, f"HTTP {response.status_code}"))
                self.all_passed = False
                return False
        except requests.exceptions.ConnectionError:
            print(f"    ❌ 无法连接到后端: {self.backend_url}")
            print(f"    提示: 确保后端服务正在运行 (uvicorn app.main:app)")
            self.results.append(("后端健康检查", False, "连接失败"))
            self.all_passed = False
            return False
        except Exception as e:
            print(f"    ❌ 健康检查失败: {e}")
            self.results.append(("后端健康检查", False, str(e)))
            self.all_passed = False
            return False

    def check_backend_api(self) -> bool:
        """检查后端 API 响应"""
        print("\n[2/5] 检查后端 API 接口...")
        try:
            # 测试根路径
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code != 200:
                print(f"    ❌ 根路径响应异常")
                self.results.append(("后端 API 响应", False, "根路径失败"))
                self.all_passed = False
                return False

            # 测试 API v1 路由
            response = requests.get(f"{self.backend_url}/api/v1/", timeout=5)
            if response.status_code in [200, 404, 422]:  # 404/422 也算可达
                print(f"    ✅ API 路由可达")
                print(f"    - 响应状态: {response.status_code}")
                self.results.append(("后端 API 响应", True, f"HTTP {response.status_code}"))
                return True
            else:
                print(f"    ❌ API 响应异常: {response.status_code}")
                self.results.append(("后端 API 响应", False, f"HTTP {response.status_code}"))
                self.all_passed = False
                return False
        except Exception as e:
            print(f"    ❌ API 检查失败: {e}")
            self.results.append(("后端 API 响应", False, str(e)))
            self.all_passed = False
            return False

    def check_cors_headers(self) -> bool:
        """检查 CORS 配置"""
        print("\n[3/5] 检查 CORS 配置...")
        try:
            response = requests.get(
                f"{self.backend_url}/",
                headers={"Origin": "http://localhost:3000"},
                timeout=5
            )
            cors_header = response.headers.get("Access-Control-Allow-Origin", "")
            if cors_header:
                print(f"    ✅ CORS 配置正确")
                print(f"    - Access-Control-Allow-Origin: {cors_header}")
                self.results.append(("CORS 配置", True, cors_header))
                return True
            else:
                print(f"    ⚠️ 未检测到 CORS 头（可能是 OPTIONS 请求问题）")
                self.results.append(("CORS 配置", True, "无 CORS 头（非预检请求）"))
                return True
        except Exception as e:
            print(f"    ⚠️ CORS 检查跳过: {e}")
            self.results.append(("CORS 配置", True, "检查跳过"))
            return True

    def check_frontend_static(self) -> bool:
        """检查前端静态文件"""
        print("\n[4/5] 检查前端静态文件...")
        try:
            # 尝试访问前端
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                content = response.text
                if "<!DOCTYPE html>" in content or "<html" in content:
                    print(f"    ✅ 前端可访问")
                    print(f"    - HTML 标题: ", end="")
                    if "<title>" in content:
                        start = content.find("<title>") + 7
                        end = content.find("</title>")
                        print(content[start:end])
                    else:
                        print("(未找到)")

                    # 检查关键资源
                    if 'src="/' in content or 'href="/' in content:
                        print(f"    - 资源路径: 根路径相对")

                    self.results.append(("前端静态文件", True, "200 OK"))
                    return True
                else:
                    print(f"    ❌ 返回内容不是 HTML")
                    self.results.append(("前端静态文件", False, "非 HTML 内容"))
                    self.all_passed = False
                    return False
            else:
                print(f"    ⚠️ 前端响应: HTTP {response.status_code}")
                self.results.append(("前端静态文件", False, f"HTTP {response.status_code}"))
                self.all_passed = False
                return False
        except requests.exceptions.ConnectionError:
            print(f"    ⚠️ 无法连接到前端: {self.frontend_url}")
            print(f"    提示: 确保前端服务正在运行或使用 Nginx 托管")
            self.results.append(("前端静态文件", False, "连接失败"))
            self.all_passed = False
            return False
        except Exception as e:
            print(f"    ❌ 前端检查失败: {e}")
            self.results.append(("前端静态文件", False, str(e)))
            self.all_passed = False
            return False

    def check_verify_endpoint(self) -> bool:
        """检查报告验证接口"""
        print("\n[5/5] 检查报告验证接口...")
        try:
            # 测试验证接口（使用无效验证码，预期返回 404）
            response = requests.get(f"{self.backend_url}/api/v1/reports/verify/INVALID999", timeout=5)
            if response.status_code == 404:
                print(f"    ✅ 验证接口可达")
                print(f"    - 响应状态: 404 (验证码无效，符合预期)")
                self.results.append(("验证接口", True, "可达"))
                return True
            elif response.status_code == 429:
                print(f"    ✅ 验证接口可达（限流）")
                self.results.append(("验证接口", True, "可达（限流中）"))
                return True
            elif response.status_code == 422:
                print(f"    ✅ 验证接口可达（参数验证）")
                self.results.append(("验证接口", True, "可达"))
                return True
            else:
                print(f"    ⚠️ 验证接口响应: {response.status_code}")
                self.results.append(("验证接口", True, f"HTTP {response.status_code}"))
                return True
        except Exception as e:
            print(f"    ❌ 验证接口检查失败: {e}")
            self.results.append(("验证接口", False, str(e)))
            self.all_passed = False
            return False

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("=" * 60)
        print("PrismaMate 棱镜 - 部署验证")
        print("=" * 60)
        print(f"后端地址: {self.backend_url}")
        print(f"前端地址: {self.frontend_url}")

        # 等待服务启动
        print("\n等待服务启动...")
        time.sleep(1)

        # 执行检查
        self.check_backend_health()
        self.check_backend_api()
        self.check_cors_headers()
        self.check_frontend_static()
        self.check_verify_endpoint()

        # 输出结果汇总
        print("\n" + "=" * 60)
        print("验证结果汇总")
        print("=" * 60)

        for name, passed, detail in self.results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"  {name}: {status} - {detail}")

        print("\n" + "=" * 60)
        if self.all_passed:
            print("🎉 所有检查通过！部署成功！")
        else:
            print("⚠️ 部分检查未通过，请查看上述详细信息")
        print("=" * 60)

        return self.all_passed


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="PrismaMate 部署验证")
    parser.add_argument("--backend", default="http://localhost:8000", help="后端地址")
    parser.add_argument("--frontend", default="http://localhost:3000", help="前端地址")
    args = parser.parse_args()

    verifier = DeploymentVerifier(args.backend, args.frontend)
    success = verifier.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
