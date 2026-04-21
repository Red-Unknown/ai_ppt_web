import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from backend.app.models.cir import CIRSection
    from backend.app.repositories.script_repository import CIRSectionRepository
except ImportError:
    from app.models.cir import CIRSection
    from app.repositories.script_repository import CIRSectionRepository


DATABASE_URL_SYNC = "postgresql://postgres:yaoshun2006@10.0.0.4:5432/ai_ppt_web"

engine = create_engine(
    DATABASE_URL_SYNC,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=10000",
        "client_encoding": "utf8"
    }
)


class TestResult:
    def __init__(self, name: str, passed: bool, expected: str, actual: str, details: str = ""):
        self.name = name
        self.passed = passed
        self.expected = expected
        self.actual = actual
        self.details = details

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        result = f"\n{'=' * 60}\n"
        result += f"测试用例: {self.name}\n"
        result += f"状态: {status}\n"
        result += f"预期结果: {self.expected}\n"
        result += f"实际结果: {self.actual}\n"
        if self.details:
            result += f"详细信息: {self.details}\n"
        result += '=' * 60
        return result


def print_section(title: str):
    print(f"\n{'#' * 60}")
    print(f"# {title}")
    print('#' * 60)


def test_get_by_lesson(repo: CIRSectionRepository, lesson_id: str):
    result = repo.get_by_lesson(lesson_id)
    return TestResult(
        name="get_by_lesson() - 根据课件ID查询节点",
        passed=isinstance(result, list),
        expected=f"返回 lesson_id={lesson_id} 的节点列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"查询条件: lesson_id={lesson_id}"
    )


def test_get_by_id(repo: CIRSectionRepository, node_id: str):
    result = repo.get_by_id(node_id)
    passed = result is None or (result is not None and result.node_id == node_id)
    return TestResult(
        name="get_by_id() - 根据节点ID查询",
        passed=passed,
        expected=f"返回 node_id={node_id} 的节点（如果存在）",
        actual=f"返回: {result}" if result else "返回: None"
    )


def test_get_by_course(repo: CIRSectionRepository, course_id: str):
    result = repo.get_by_course(course_id)
    return TestResult(
        name="get_by_course() - 根据课程ID查询节点",
        passed=isinstance(result, list),
        expected=f"返回 course_id 以 {course_id}% 开头的节点列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"查询条件: course_id LIKE {course_id}%"
    )


def test_create(repo: CIRSectionRepository, test_data: dict):
    section = repo.create(**test_data)
    passed = section is not None and section.node_id == test_data["node_id"]
    return TestResult(
        name="create() - 创建CIR节点",
        passed=passed,
        expected=f"成功创建 node_id={test_data['node_id']} 的节点",
        actual=f"创建结果: node_id={section.node_id}, node_name={section.node_name}" if section else "创建失败"
    ), section


def test_bulk_create(repo: CIRSectionRepository, sections_data: List[dict]):
    sections = repo.bulk_create(sections_data)
    passed = len(sections) == len(sections_data)
    return TestResult(
        name="bulk_create() - 批量创建CIR节点",
        passed=passed,
        expected=f"成功创建 {len(sections_data)} 个节点",
        actual=f"创建数量: {len(sections)}"
    ), sections


def test_update_script(repo: CIRSectionRepository, node_id: str, script_content: str):
    section = repo.update_script(node_id, script_content)
    passed = section is not None and section.script_content == script_content
    return TestResult(
        name="update_script() - 更新节点讲稿内容",
        passed=passed,
        expected=f"成功更新 node_id={node_id} 的讲稿内容为 '{script_content}'",
        actual=f"更新后讲稿: {section.script_content[:50] if section and section.script_content else 'None'}..." if section else "更新失败"
    ), section


def test_bulk_update_scripts(repo: CIRSectionRepository, scripts: dict):
    updated = repo.bulk_update_scripts(scripts)
    passed = len(updated) > 0
    return TestResult(
        name="bulk_update_scripts() - 批量更新讲稿内容",
        passed=passed,
        expected=f"成功更新 {len(scripts)} 个节点的讲稿",
        actual=f"更新数量: {len(updated)}, 更新节点: {updated}"
    ), updated


def test_delete(repo: CIRSectionRepository, node_id: str):
    result = repo.delete(node_id)
    exists = repo.get_by_id(node_id)
    passed = result is True and exists is None
    return TestResult(
        name="delete() - 删除单个节点",
        passed=passed,
        expected=f"成功删除 node_id={node_id} 的节点",
        actual=f"删除操作返回: {result}, 删除后查询结果: {exists}"
    )


def test_delete_by_lesson(repo: CIRSectionRepository, lesson_id: str):
    count = repo.delete_by_lesson(lesson_id)
    sections = repo.get_by_lesson(lesson_id)
    passed = len(sections) == 0
    return TestResult(
        name="delete_by_lesson() - 删除课件的所有节点",
        passed=passed,
        expected=f"成功删除 lesson_id={lesson_id} 的所有节点",
        actual=f"删除数量: {count}, 删除后剩余: {len(sections)}"
    )


def test_delete_nonexistent(repo: CIRSectionRepository):
    nonexistent_id = "nonexistent_node_999999"
    result = repo.delete(nonexistent_id)
    return TestResult(
        name="delete() - 删除不存在的节点",
        passed=result is False,
        expected="返回 False（节点不存在）",
        actual=f"返回: {result}"
    )


def cleanup_test_data(db, node_ids: List[str]):
    try:
        for node_id in node_ids:
            db.execute(text(f"DELETE FROM cir_sections WHERE node_id = '{node_id}'"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"清理数据失败: {e}")


def run_all_tests():
    print_section("CIRSectionRepository (ScriptRepository) 数据层功能测试")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    repo = CIRSectionRepository(db)

    results: List[TestResult] = []
    test_lesson_id = "lesson_002"
    test_course_id = "course_001"
    test_school_id = "school_001"
    test_node_ids = []

    test_data = {
        "node_id": "test_node_001",
        "lesson_id": test_lesson_id,
        "school_id": test_school_id,
        "node_name": "测试节点_章节1",
        "parent_id": None,
        "node_type": "chapter",
        "sort_order": 100,
        "path": "/chapter1",
        "page_num": 1,
    }

    bulk_test_data = [
        {
            "node_id": "test_node_002",
            "lesson_id": test_lesson_id,
            "school_id": test_school_id,
            "node_name": "测试节点_章节2",
            "parent_id": None,
            "node_type": "chapter",
            "sort_order": 101,
            "path": "/chapter2",
            "page_num": 2,
        },
        {
            "node_id": "test_node_003",
            "lesson_id": test_lesson_id,
            "school_id": test_school_id,
            "node_name": "测试节点_章节3",
            "parent_id": None,
            "node_type": "chapter",
            "sort_order": 102,
            "path": "/chapter3",
            "page_num": 3,
        },
    ]

    try:
        print_section("准备测试数据 - 检查现有数据")
        existing_sections = repo.get_by_lesson(test_lesson_id)
        if existing_sections:
            print(f"⚠️ 测试课件 {test_lesson_id} 已存在节点，将先清理")
            repo.delete_by_lesson(test_lesson_id)

        print_section("1. 测试 get_by_lesson() - 根据课件ID查询节点（空结果）")
        results.append(test_get_by_lesson(repo, test_lesson_id))

        print_section("2. 测试 get_by_id() - 根据节点ID查询（不存在）")
        results.append(test_get_by_id(repo, "nonexistent_node_999"))

        print_section("3. 测试 get_by_course() - 根据课程ID查询节点")
        results.append(test_get_by_course(repo, test_course_id))

        print_section("4. 测试 create() - 创建CIR节点")
        result, test_section = test_create(repo, test_data)
        results.append(result)
        if test_section:
            test_node_ids.append(test_section.node_id)

        print_section("5. 测试 bulk_create() - 批量创建节点")
        result, bulk_sections = test_bulk_create(repo, bulk_test_data)
        results.append(result)
        if bulk_sections:
            test_node_ids.extend([s.node_id for s in bulk_sections])

        print_section("6. 测试 get_by_lesson() - 根据课件ID查询节点（有数据）")
        results.append(test_get_by_lesson(repo, test_lesson_id))

        print_section("7. 测试 get_by_id() - 根据节点ID查询（已存在）")
        if test_section:
            results.append(test_get_by_id(repo, test_section.node_id))

        print_section("8. 测试 get_by_course() - 根据课程ID查询节点（有数据）")
        results.append(test_get_by_course(repo, test_course_id))

        print_section("9. 测试 update_script() - 更新讲稿内容")
        if test_section:
            script_content = "这是测试讲稿内容，用于验证更新功能。"
            result, updated_section = test_update_script(repo, test_section.node_id, script_content)
            results.append(result)

        print_section("10. 测试 bulk_update_scripts() - 批量更新讲稿内容")
        if bulk_sections:
            scripts = {
                bulk_sections[0].node_id: "批量更新讲稿1",
                bulk_sections[1].node_id: "批量更新讲稿2",
            }
            result, updated = test_bulk_update_scripts(repo, scripts)
            results.append(result)

        print_section("11. 测试 delete() - 删除单个节点")
        if test_section:
            results.append(test_delete(repo, test_section.node_id))
            test_node_ids.remove(test_section.node_id)

        print_section("12. 测试 delete_by_lesson() - 删除课件的所有节点")
        results.append(test_delete_by_lesson(repo, test_lesson_id))

        print_section("13. 测试 delete() - 删除不存在的节点")
        results.append(test_delete_nonexistent(repo))

        print_section("14. 重新创建测试数据用于验证")
        result, test_section2 = test_create(repo, test_data)
        results.append(result)
        if test_section2:
            test_node_ids.append(test_section2.node_id)

        print_section("15. 再次测试 delete_by_lesson() - 删除剩余测试数据")
        results.append(test_delete_by_lesson(repo, test_lesson_id))

    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("清理测试数据")
        try:
            cleanup_test_data(db, test_node_ids)
            print(f"✅ 测试数据清理完成 (node_ids={test_node_ids})")
        except Exception as e:
            print(f"⚠️ 清理测试数据失败: {e}")
            db.rollback()
        db.close()
        engine.dispose()

    print_section("测试结果汇总")
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n总计: {total} 个测试用例")
    print(f"通过: {passed} 个 ✅")
    print(f"失败: {total - passed} 个 ❌")

    for result in results:
        print(result)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
