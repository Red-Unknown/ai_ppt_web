"""
E2E 测试脚本 - 测试 Direct RAG、ReAct 和 Web Search 三个核心功能
测试目标：f:\college\sophomore\服务外包\backend\app\services\qa
"""

import pytest
import asyncio
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.qa.service import QAService
from backend.app.schemas.qa import ChatRequest


class EndpointCollector:
    """端点信息收集器"""

    def __init__(self):
        self.endpoints: List[Dict[str, Any]] = []

    def add_endpoint(self, method: str, path: str, description: str = "", test_case: str = "", response_data: Any = None, status_code: int = None):
        endpoint_info = {
            "method": method,
            "path": path,
            "description": description,
            "test_case": test_case,
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
            "response_data": response_data
        }
        self.endpoints.append(endpoint_info)

    def get_unique_endpoints(self) -> List[Dict[str, Any]]:
        seen = set()
        unique = []
        for ep in self.endpoints:
            key = (ep["method"], ep["path"])
            if key not in seen:
                seen.add(key)
                unique.append(ep)
        return unique

    def generate_report(self) -> str:
        unique_endpoints = self.get_unique_endpoints()
        report_lines = [
            "# API 端点测试报告",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 端点汇总",
            "",
            f"总计调用次数: {len(self.endpoints)}",
            f"唯一端点数量: {len(unique_endpoints)}",
            "",
            "---",
            ""
        ]

        for i, ep in enumerate(unique_endpoints, 1):
            report_lines.append(f"### {i}. {ep['method']} {ep['path']}")
            report_lines.append("")
            if ep['description']:
                report_lines.append(f"- **描述**: {ep['description']}")
            if ep['test_case']:
                report_lines.append(f"- **测试用例**: {ep['test_case']}")
            report_lines.append(f"- **调用次数**: {self._count_calls(ep['method'], ep['path'])}")
            if ep['status_code']:
                report_lines.append(f"- **状态码**: {ep['status_code']}")
            if ep['response_data']:
                report_lines.append(f"- **响应数据**: ")
                report_lines.append("```json")
                report_lines.append(json.dumps(ep['response_data'], ensure_ascii=False, indent=2))
                report_lines.append("```")
            report_lines.append("")

        report_lines.extend([
            "---",
            "",
            "## 测试用例与端点对应关系",
            ""
        ])

        test_cases = {}
        for ep in self.endpoints:
            tc = ep['test_case']
            if tc:
                if tc not in test_cases:
                    test_cases[tc] = []
                test_cases[tc].append({
                    "method": ep['method'],
                    "path": ep['path'],
                    "status_code": ep.get('status_code'),
                    "response_data": ep.get('response_data')
                })

        for tc, eps in test_cases.items():
            report_lines.append(f"### {tc}")
            for ep in eps:
                report_lines.append(f"- **{ep['method']} {ep['path']}**")
                if ep.get('status_code'):
                    report_lines.append(f"  - 状态码: {ep['status_code']}")
                if ep.get('response_data'):
                    report_lines.append("  - 响应数据:")
                    report_lines.append("  ```json")
                    for line in json.dumps(ep['response_data'], ensure_ascii=False, indent=2).split('\n'):
                        report_lines.append(f"  {line}")
                    report_lines.append("  ```")
            report_lines.append("")

        return "\n".join(report_lines)

    def _count_calls(self, method: str, path: str) -> int:
        return sum(1 for ep in self.endpoints if ep["method"] == method and ep["path"] == path)


class TestResult:
    """测试结果类"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0
        self.details = {}

    def __repr__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"[{status}] {self.name} ({self.duration:.2f}s)"


class QAE2ETestRunner:
    """QA 功能 E2E 测试运行器"""

    def __init__(self):
        self.client = TestClient(app)
        self.results: List[TestResult] = []
        self.endpoint_collector = EndpointCollector()

    def print_header(self, title: str):
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_result(self, result: TestResult):
        status = "\033[92m✓ PASSED\033[0m" if result.passed else "\033[91m✗ FAILED\033[0m"
        print(f"\n{status} - {result.name}")
        if result.error:
            print(f"  Error: {result.error}")
        if result.details:
            print(f"  Details: {json.dumps(result.details, ensure_ascii=False, indent=4)}")
        print(f"  Duration: {result.duration:.2f}s")

    def print_summary(self):
        self.print_header("测试结果汇总")
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        for r in self.results:
            self.print_result(r)

        print("\n" + "-" * 60)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        print("-" * 60)

        if failed > 0:
            print("\n\033[91m测试失败！请检查上述错误。\033[0m")
        else:
            print("\n\033[92m所有测试通过！\033[0m")

        return failed == 0

    def save_endpoint_report(self, output_path: str = None):
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent / "reports" / f"endpoint_report_{timestamp}.md"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.endpoint_collector.generate_report()
        output_path.write_text(report, encoding="utf-8")

        self.print_header("端点报告已生成")
        print(f"报告路径: {output_path}")
        print(f"\n{report}")
        print("-" * 60)


class TestDirectRAG:
    """Direct RAG 功能测试"""

    @staticmethod
    def test_direct_rag_simple_query(runner: QAE2ETestRunner):
        """测试1: Direct RAG - 简单知识库查询 (使用 SSE)"""
        result = TestResult("Direct RAG - 简单知识库查询 (SSE)")
        test_case_name = "Direct RAG - 简单知识库查询"

        try:
            start_time = time.time()

            # 启动会话
            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            session_response_data = session_response.json() if session_response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name,
                response_data=session_response_data,
                status_code=session_response.status_code
            )
            assert session_response.status_code == 200, f"启动会话失败: {session_response.status_code}"
            session_id = session_response.json()["session_id"]

            # 发送简单查询（使用 SSE 端点）
            query = "什么是牛顿第一定律？"
            params = {
                "query": query,
                "session_id": session_id
            }

            # 使用 SSE 端点
            with runner.client.stream("get", "/api/v1/chat/sse", params=params) as response:
                assert response.status_code == 200, f"SSE 请求失败: {response.status_code}"

                chunks = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            chunks.append(event)
                        except:
                            pass

                runner.endpoint_collector.add_endpoint(
                    "GET", "/api/v1/chat/sse",
                    "SSE 流式聊天端点", test_case_name,
                    response_data={"events": chunks, "event_count": len(chunks)},
                    status_code=response.status_code
                )

                result.details = {
                    "query": query,
                    "event_count": len(chunks),
                    "event_types": list(set(c.get("type") for c in chunks))
                }

                # 验证响应
                has_answer = any(c.get("type") in ["token", "quick_answer"] for c in chunks)
                assert has_answer, "未收到回答内容"

                result.passed = True
                result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = f"Unexpected error: {str(e)}"
            result.duration = time.time() - start_time

        runner.results.append(result)

    @staticmethod
    def test_direct_rag_with_sources(runner: QAE2ETestRunner):
        """测试2: Direct RAG - 带来源的知识查询"""
        result = TestResult("Direct RAG - 带来源的知识查询")
        test_case_name = "Direct RAG - 带来源的知识查询"

        try:
            start_time = time.time()

            # 启动会话
            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            session_response_data = session_response.json() if session_response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name,
                response_data=session_response_data,
                status_code=session_response.status_code
            )
            assert session_response.status_code == 200
            session_id = session_response.json()["session_id"]

            # 发送查询
            query = "简述动能定理"
            params = {
                "query": query,
                "session_id": session_id
            }

            with runner.client.stream("get", "/api/v1/chat/sse", params=params) as response:
                assert response.status_code == 200

                chunks = []
                sources = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            chunks.append(event)
                            if event.get("type") == "sources":
                                sources = event.get("content", [])
                        except:
                            pass

                runner.endpoint_collector.add_endpoint(
                    "GET", "/api/v1/chat/sse",
                    "SSE 流式聊天端点", test_case_name,
                    response_data={"events": chunks, "event_count": len(chunks), "sources": sources},
                    status_code=response.status_code
                )

                result.details = {
                    "query": query,
                    "event_count": len(chunks),
                    "has_sources": len(sources) > 0,
                    "source_count": len(sources)
                }

                result.passed = True
                result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)


class TestReAct:
    """ReAct 功能测试"""

    @staticmethod
    def test_react_multistep_reasoning(runner: QAE2ETestRunner):
        """测试3: ReAct - 多步推理"""
        result = TestResult("ReAct - 多步推理")
        test_case_name = "ReAct - 多步推理"

        try:
            start_time = time.time()

            # 启动会话
            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name
            )
            assert session_response.status_code == 200
            session_id = session_response.json()["session_id"]

            # 发送复杂查询（触发 ReAct 模式）
            query = "请逐步分析动能和势能的转换关系"
            params = {
                "query": query,
                "session_id": session_id
            }

            with runner.client.stream("get", "/api/v1/chat/sse", params=params) as response:
                assert response.status_code == 200

                chunks = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            chunks.append(event)
                        except:
                            pass

                runner.endpoint_collector.add_endpoint(
                    "GET", "/api/v1/chat/sse",
                    "SSE 流式聊天端点", test_case_name,
                    response_data={"events": chunks, "event_count": len(chunks)},
                    status_code=response.status_code
                )

                result.details = {
                    "query": query,
                    "event_count": len(chunks),
                    "event_types": list(set(c.get("type") for c in chunks))
                }

                result.passed = True
                result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)

    @staticmethod
    def test_react_math_calculation(runner: QAE2ETestRunner):
        """测试4: ReAct - 数学计算"""
        result = TestResult("ReAct - 数学计算")
        test_case_name = "ReAct - 数学计算"

        try:
            start_time = time.time()

            # 启动会话
            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name
            )
            assert session_response.status_code == 200
            session_id = session_response.json()["session_id"]

            # 发送数学计算查询
            query = "计算 123 * 456 = ?"
            params = {
                "query": query,
                "session_id": session_id
            }

            with runner.client.stream("get", "/api/v1/chat/sse", params=params) as response:
                assert response.status_code == 200

                chunks = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            chunks.append(event)
                        except:
                            pass

                runner.endpoint_collector.add_endpoint(
                    "GET", "/api/v1/chat/sse",
                    "SSE 流式聊天端点", test_case_name,
                    response_data={"events": chunks, "event_count": len(chunks)},
                    status_code=response.status_code
                )

                result.details = {
                    "query": query,
                    "event_count": len(chunks)
                }

                result.passed = True
                result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)


class TestWebSearch:
    """Web Search 功能测试"""

    @staticmethod
    def test_web_search_time_sensitive(runner: QAE2ETestRunner):
        """测试5: Web Search - 时间敏感查询"""
        result = TestResult("Web Search - 时间敏感查询")
        test_case_name = "Web Search - 时间敏感查询"

        try:
            start_time = time.time()

            # 启动会话
            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            session_response_data = session_response.json() if session_response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name,
                response_data=session_response_data,
                status_code=session_response.status_code
            )
            assert session_response.status_code == 200
            session_id = session_response.json()["session_id"]

            # 发送时间敏感查询（触发 Web Search）
            query = "2024年诺贝尔物理学奖获得者是谁？"
            params = {
                "query": query,
                "session_id": session_id
            }

            with runner.client.stream("get", "/api/v1/chat/sse", params=params) as response:
                assert response.status_code == 200

                chunks = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            chunks.append(event)
                        except:
                            pass

                runner.endpoint_collector.add_endpoint(
                    "GET", "/api/v1/chat/sse",
                    "SSE 流式聊天端点", test_case_name,
                    response_data={"events": chunks, "event_count": len(chunks)},
                    status_code=response.status_code
                )

                result.details = {
                    "query": query,
                    "event_count": len(chunks),
                    "event_types": list(set(c.get("type") for c in chunks))
                }

                result.passed = True
                result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)

    @staticmethod
    def test_web_search_latest_info(runner: QAE2ETestRunner):
        """测试6: Web Search - 最新信息查询"""
        result = TestResult("Web Search - 最新信息查询")
        test_case_name = "Web Search - 最新信息查询"

        try:
            start_time = time.time()

            # 启动会话
            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            session_response_data = session_response.json() if session_response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name,
                response_data=session_response_data,
                status_code=session_response.status_code
            )
            assert session_response.status_code == 200
            session_id = session_response.json()["session_id"]

            # 发送最新信息查询
            query = "今天天气怎么样？"
            params = {
                "query": query,
                "session_id": session_id
            }

            with runner.client.stream("get", "/api/v1/chat/sse", params=params) as response:
                assert response.status_code == 200

                chunks = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            chunks.append(event)
                        except:
                            pass

                runner.endpoint_collector.add_endpoint(
                    "GET", "/api/v1/chat/sse",
                    "SSE 流式聊天端点", test_case_name,
                    response_data={"events": chunks, "event_count": len(chunks)},
                    status_code=response.status_code
                )

                result.details = {
                    "query": query,
                    "event_count": len(chunks)
                }

                result.passed = True
                result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)


class TestErrorHandling:
    """错误处理测试"""

    @staticmethod
    def test_empty_query(runner: QAE2ETestRunner):
        """测试7: 错误处理 - 空查询"""
        result = TestResult("错误处理 - 空查询")
        test_case_name = "错误处理 - 空查询"

        try:
            start_time = time.time()

            session_response = runner.client.post(
                "/api/v1/chat/session/start",
                json={
                    "course_id": "test_course",
                    "mode": "learning",
                    "target_node_id": "node_1"
                }
            )
            session_response_data = session_response.json() if session_response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "POST", "/api/v1/chat/session/start",
                "启动聊天会话", test_case_name,
                response_data=session_response_data,
                status_code=session_response.status_code
            )
            assert session_response.status_code == 200
            session_id = session_response.json()["session_id"]

            # 发送空查询
            params = {
                "query": "",
                "session_id": session_id
            }

            response = runner.client.get("/api/v1/chat/sse", params=params)
            response_data = response.json() if response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "GET", "/api/v1/chat/sse",
                "SSE 流式聊天端点", test_case_name,
                response_data=response_data,
                status_code=response.status_code
            )

            # 应该返回错误或空响应
            result.details = {
                "status_code": response.status_code,
            }

            # 空查询可能被拒绝或返回错误提示
            result.passed = response.status_code in [400, 422, 200]
            result.duration = time.time() - start_time

        except AssertionError as e:
            result.error = str(e)
            result.duration = time.time() - start_time
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)

    @staticmethod
    def test_invalid_session(runner: QAE2ETestRunner):
        """测试8: 错误处理 - 无效会话"""
        result = TestResult("错误处理 - 无效会话")
        test_case_name = "错误处理 - 无效会话"

        try:
            start_time = time.time()

            # 使用无效session_id
            params = {
                "query": "测试问题",
                "session_id": "invalid_session_12345"
            }

            response = runner.client.get("/api/v1/chat/sse", params=params)
            response_data = response.json() if response.status_code == 200 else None
            runner.endpoint_collector.add_endpoint(
                "GET", "/api/v1/chat/sse",
                "SSE 流式聊天端点", test_case_name,
                response_data=response_data,
                status_code=response.status_code
            )

            result.details = {
                "status_code": response.status_code,
            }

            # 应该能处理（可能创建新会话或返回错误）
            result.passed = response.status_code in [200, 400, 404]
            result.duration = time.time() - start_time

        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time

        runner.results.append(result)


def run_all_tests():
    """运行所有测试"""
    runner = QAE2ETestRunner()
    runner.print_header("QA 功能 E2E 测试")

    # 检查服务是否可用
    try:
        health_check = runner.client.get("/")
        health_check_data = health_check.json() if health_check.status_code == 200 else None
        runner.endpoint_collector.add_endpoint(
            "GET", "/",
            "健康检查端点", "服务健康检查",
            response_data=health_check_data,
            status_code=health_check.status_code
        )
        print(f"\n服务状态: {health_check.status_code}")
        print(f"服务信息: {health_check.json().get('message', 'N/A')}")
    except Exception as e:
        print(f"\n\033[91m无法连接到服务: {e}\033[0m")
        return False

    # 运行 Direct RAG 测试
    runner.print_header("Direct RAG 功能测试")
    TestDirectRAG.test_direct_rag_simple_query(runner)
    TestDirectRAG.test_direct_rag_with_sources(runner)

    # 运行 ReAct 测试
    runner.print_header("ReAct 功能测试")
    TestReAct.test_react_multistep_reasoning(runner)
    TestReAct.test_react_math_calculation(runner)

    # 运行 Web Search 测试
    runner.print_header("Web Search 功能测试")
    TestWebSearch.test_web_search_time_sensitive(runner)
    TestWebSearch.test_web_search_latest_info(runner)

    # 运行错误处理测试
    runner.print_header("错误处理测试")
    TestErrorHandling.test_empty_query(runner)
    TestErrorHandling.test_invalid_session(runner)

    # 输出汇总
    test_success = runner.print_summary()

    # 保存端点报告
    runner.save_endpoint_report()

    return test_success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
