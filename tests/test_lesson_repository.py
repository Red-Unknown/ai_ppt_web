import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from backend.app.models.course import Lesson
    from backend.app.models.course import Course as CourseModel, CourseCategory
    from backend.app.repositories.lesson_repository import LessonRepository
except ImportError:
    from app.models.course import Lesson
    from app.models.course import Course as CourseModel, CourseCategory
    from app.repositories.lesson_repository import LessonRepository


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


def test_get_all(repo: LessonRepository):
    result = repo.get_all()
    return TestResult(
        name="get_all() - 获取所有课件列表",
        passed=isinstance(result, list),
        expected="返回课件列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"当前数据库共有 {len(result)} 个课件"
    )


def test_get_all_with_course_filter(repo: LessonRepository, course_id: str):
    result = repo.get_all(course_id=course_id)
    return TestResult(
        name="get_all(course_id=xxx) - 按课程过滤获取课件列表",
        passed=isinstance(result, list),
        expected=f"返回 course_id={course_id} 的课件列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"过滤条件: course_id={course_id}"
    )


def test_get_by_id(repo: LessonRepository):
    nonexistent_id = "nonexistent_lesson_id_99999"
    result = repo.get_by_id(nonexistent_id)
    return TestResult(
        name="get_by_id() - 根据ID查询课件",
        passed=result is None,
        expected=f"返回None（ID={nonexistent_id}不存在）",
        actual=f"返回: {result}"
    )


def test_get_by_id_existing(repo: LessonRepository, lesson_id: str):
    result = repo.get_by_id(lesson_id)
    passed = result is not None and result.lesson_id == lesson_id
    return TestResult(
        name="get_by_id() - 根据ID查询课件（已存在）",
        passed=passed,
        expected=f"返回 lesson_id={lesson_id} 的课件",
        actual=f"返回: {result}" if result else "返回: None"
    )


def test_get_by_course(repo: LessonRepository, course_id: str):
    result = repo.get_by_course(course_id)
    return TestResult(
        name="get_by_course() - 根据课程ID查询课件列表",
        passed=isinstance(result, list),
        expected=f"返回 course_id={course_id} 的课件列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"课程ID: {course_id}"
    )


def test_get_by_school(repo: LessonRepository, school_id: str):
    result = repo.get_by_school(school_id)
    return TestResult(
        name="get_by_school() - 根据学校ID查询课件列表",
        passed=isinstance(result, list),
        expected=f"返回 school_id={school_id} 的课件列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"学校ID: {school_id}"
    )


def test_create(repo: LessonRepository, test_data: dict):
    lesson = repo.create(
        lesson_id=test_data["lesson_id"],
        course_id=test_data["course_id"],
        school_id=test_data["school_id"],
        title=test_data["title"],
        file_url=test_data["file_url"],
        file_type=test_data.get("file_type", "pdf"),
        category=test_data.get("category", "test")
    )
    passed = lesson is not None and lesson.lesson_id == test_data["lesson_id"]
    return TestResult(
        name="create() - 创建新课件",
        passed=passed,
        expected=f"成功创建 lesson_id={test_data['lesson_id']} 的课件",
        actual=f"创建结果: lesson_id={lesson.lesson_id}, title={lesson.title}" if lesson else "创建失败"
    ), lesson


def test_update(repo: LessonRepository, lesson_id: str, new_title: str):
    updated_lesson = repo.update(
        lesson_id=lesson_id,
        title=new_title,
        cover_image="https://example.com/new_cover.jpg"
    )
    passed = updated_lesson is not None and updated_lesson.title == new_title
    return TestResult(
        name="update() - 更新课件信息",
        passed=passed,
        expected=f"成功更新课件标题为 '{new_title}'",
        actual=f"更新后标题: {updated_lesson.title}" if updated_lesson else "更新失败"
    ), updated_lesson


def test_update_status(repo: LessonRepository, lesson_id: str, new_status: str):
    updated_lesson = repo.update_status(lesson_id, new_status)
    passed = updated_lesson is not None and updated_lesson.task_status == new_status
    return TestResult(
        name="update_status() - 更新课件任务状态",
        passed=passed,
        expected=f"成功更新状态为 '{new_status}'",
        actual=f"更新后状态: {updated_lesson.task_status}" if updated_lesson else "更新失败"
    ), updated_lesson


def test_delete(repo: LessonRepository, lesson_id: str):
    result = repo.delete(lesson_id)
    exists = repo.get_by_id(lesson_id)
    passed = result is True and exists is None
    return TestResult(
        name="delete() - 删除课件",
        passed=passed,
        expected=f"成功删除 lesson_id={lesson_id} 的课件",
        actual=f"删除操作返回: {result}, 删除后查询结果: {exists}"
    )


def test_delete_nonexistent(repo: LessonRepository):
    nonexistent_id = "nonexistent_lesson_999999"
    result = repo.delete(nonexistent_id)
    return TestResult(
        name="delete() - 删除不存在的课件",
        passed=result is False,
        expected="返回 False（课件不存在）",
        actual=f"返回: {result}"
    )


def cleanup_test_data(db, lesson_id: str):
    try:
        db.execute(text(f"DELETE FROM lessons WHERE lesson_id = '{lesson_id}'"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"清理数据失败: {e}")


def run_all_tests():
    print_section("LessonRepository 数据层功能测试")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    repo = LessonRepository(db)

    results: List[TestResult] = []
    test_lesson = None
    test_lesson_id = "test_lesson_001"
    test_course_id = "course_001"
    test_school_id = "school_001"

    test_data = {
        "lesson_id": test_lesson_id,
        "course_id": test_course_id,
        "school_id": test_school_id,
        "title": "测试课件_Python基础",
        "file_url": "https://example.com/test_lesson.pdf",
        "file_type": "pdf",
        "category": "test"
    }

    try:
        print_section("准备测试数据 - 检查课程")
        existing_course = db.query(CourseModel).filter(CourseModel.course_id == test_course_id).first()
        if existing_course:
            print(f"✅ 测试课程已存在: course_id={test_course_id}, course_name={existing_course.course_name}")
        else:
            print(f"⚠️ 课程 {test_course_id} 不存在，将跳过需要课程的外键测试")

        print_section("1. 测试 LessonRepository.get_all() - 获取所有课件")
        results.append(test_get_all(repo))

        print_section("2. 测试 LessonRepository.get_by_id() - 根据ID查询（不存在）")
        results.append(test_get_by_id(repo))

        print_section("3. 测试 LessonRepository.get_by_course() - 根据课程ID查询")
        results.append(test_get_by_course(repo, test_course_id))

        print_section("4. 测试 LessonRepository.get_by_school() - 根据学校ID查询")
        results.append(test_get_by_school(repo, test_school_id))

        print_section("5. 测试 LessonRepository.create() - 创建新课件")
        result, test_lesson = test_create(repo, test_data)
        results.append(result)

        print_section("6. 测试 LessonRepository.get_all(course_id=xxx) - 按课程过滤")
        results.append(test_get_all_with_course_filter(repo, test_data["course_id"]))

        if test_lesson:
            print_section("7. 测试 LessonRepository.get_by_id() - 根据ID查询（已存在）")
            results.append(test_get_by_id_existing(repo, test_lesson_id))

            print_section("8. 测试 LessonRepository.update() - 更新课件信息")
            new_title = "测试课件_Python基础_更新版"
            result, updated_lesson = test_update(repo, test_lesson_id, new_title)
            results.append(result)

            print_section("9. 测试 LessonRepository.update_status() - 更新任务状态")
            result, updated_lesson = test_update_status(repo, test_lesson_id, "completed")
            results.append(result)

        print_section("10. 测试 LessonRepository.delete() - 删除课件")
        if test_lesson:
            results.append(test_delete(repo, test_lesson_id))
            test_lesson = None

            result, test_lesson = test_create(repo, test_data)
            results.append(result)

        print_section("11. 测试 LessonRepository.delete() - 删除不存在的课件")
        results.append(test_delete_nonexistent(repo))

    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("清理测试数据")
        try:
            cleanup_test_data(db, test_lesson_id)
            print(f"✅ 测试数据清理完成 (lesson_id={test_lesson_id})")
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
