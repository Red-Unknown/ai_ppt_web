import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from backend.app.models.progress import LearningProgress
    from backend.app.repositories.learning_progress_repository import LearningProgressRepository
except ImportError:
    from app.models.progress import LearningProgress
    from app.repositories.learning_progress_repository import LearningProgressRepository


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


def test_upsert_progress_create(repo: LearningProgressRepository, test_data: dict):
    progress = repo.upsert_progress(
        user_id=test_data["user_id"],
        session_id=test_data["session_id"],
        school_id=test_data["school_id"],
        lesson_id=test_data["lesson_id"],
        current_node_id=test_data["current_node_id"],
        current_path=test_data["current_path"],
        current_topic=test_data["current_topic"],
        confusion_count=test_data["confusion_count"],
        mastery=test_data["mastery"],
        progress_percent=test_data["progress_percent"]
    )
    passed = progress is not None and progress.track_id == f"{test_data['user_id']}_{test_data['session_id']}"
    return TestResult(
        name="upsert_progress() - 创建学习进度记录",
        passed=passed,
        expected=f"成功创建学习进度记录 (track_id={test_data['user_id']}_{test_data['session_id']})",
        actual=f"返回: track_id={progress.track_id if progress else 'None'}" if progress else "返回: None",
        details=f"输入数据: user_id={test_data['user_id']}, session_id={test_data['session_id']}, school_id={test_data['school_id']}"
    ), progress


def test_upsert_progress_update(repo: LearningProgressRepository, test_data: dict, updated_topic: str):
    progress = repo.upsert_progress(
        user_id=test_data["user_id"],
        session_id=test_data["session_id"],
        school_id=test_data["school_id"],
        current_topic=updated_topic,
        progress_percent=50.0
    )
    passed = progress is not None and progress.current_topic == updated_topic and progress.progress_percent == 50.0
    return TestResult(
        name="upsert_progress() - 更新学习进度记录",
        passed=passed,
        expected=f"成功更新 current_topic='{updated_topic}', progress_percent=50.0",
        actual=f"返回: current_topic={progress.current_topic if progress else 'None'}, progress_percent={progress.progress_percent if progress else 'None'}",
        details=f"更新字段: current_topic, progress_percent"
    ), progress


def test_get_progress_by_session(repo: LearningProgressRepository, user_id: str, session_id: str):
    progress = repo.get_progress_by_session(user_id, session_id)
    track_id = f"{user_id}_{session_id}"
    passed = progress is not None and progress.track_id == track_id
    return TestResult(
        name="get_progress_by_session() - 查询会话学习进度",
        passed=passed,
        expected=f"返回 track_id={track_id} 的学习进度",
        actual=f"返回: track_id={progress.track_id if progress else 'None'}",
        details=f"查询条件: user_id={user_id}, session_id={session_id}"
    ), progress


def test_get_progress_by_user(repo: LearningProgressRepository, user_id: str):
    progresses = repo.get_progress_by_user(user_id, limit=10)
    passed = isinstance(progresses, list)
    return TestResult(
        name="get_progress_by_user() - 查询用户学习进度列表",
        passed=passed,
        expected=f"返回 user_id={user_id} 的学习进度列表",
        actual=f"返回类型: {type(progresses).__name__}, 数量: {len(progresses)}",
        details=f"查询条件: user_id={user_id}, limit=10"
    ), progresses


def test_increment_confusion(repo: LearningProgressRepository, user_id: str, session_id: str):
    progress_before = repo.get_progress_by_session(user_id, session_id)
    count_before = progress_before.confusion_count if progress_before else 0

    progress = repo.increment_confusion(user_id, session_id)
    count_after = progress.confusion_count if progress else 0
    passed = progress is not None and count_after == count_before + 1

    return TestResult(
        name="increment_confusion() - 增加困惑计数",
        passed=passed,
        expected=f"困惑计数从 {count_before} 增加到 {count_before + 1}",
        actual=f"困惑计数: {count_before} -> {count_after}",
        details=f"查询条件: user_id={user_id}, session_id={session_id}"
    ), progress


def test_increment_confusion_not_found(repo: LearningProgressRepository):
    fake_user = "nonexistent_user_99999"
    fake_session = "nonexistent_session_99999"
    progress = repo.increment_confusion(fake_user, fake_session)
    passed = progress is None
    return TestResult(
        name="increment_confusion() - 记录不存在时返回None",
        passed=passed,
        expected="返回 None（学习进度记录不存在）",
        actual=f"返回: {progress}",
        details=f"查询条件: user_id={fake_user}, session_id={fake_session}"
    ), progress


def test_reset_confusion(repo: LearningProgressRepository, user_id: str, session_id: str):
    progress = repo.reset_confusion(user_id, session_id)
    passed = progress is not None and progress.confusion_count == 0

    return TestResult(
        name="reset_confusion() - 重置困惑计数",
        passed=passed,
        expected="困惑计数重置为 0",
        actual=f"困惑计数: {progress.confusion_count if progress else 'None'}",
        details=f"查询条件: user_id={user_id}, session_id={session_id}"
    ), progress


def test_reset_confusion_not_found(repo: LearningProgressRepository):
    fake_user = "nonexistent_user_99999"
    fake_session = "nonexistent_session_99999"
    progress = repo.reset_confusion(fake_user, fake_session)
    passed = progress is None
    return TestResult(
        name="reset_confusion() - 记录不存在时返回None",
        passed=passed,
        expected="返回 None（学习进度记录不存在）",
        actual=f"返回: {progress}",
        details=f"查询条件: user_id={fake_user}, session_id={fake_session}"
    ), progress


def test_update_mastery(repo: LearningProgressRepository, user_id: str, session_id: str):
    topic = "Python基础"
    score = 0.85

    progress = repo.update_mastery(user_id, session_id, topic, score)
    passed = progress is not None and progress.mastery is not None and progress.mastery.get(topic) == score

    mastery_display = progress.mastery if progress else {}
    return TestResult(
        name="update_mastery() - 更新主题掌握度",
        passed=passed,
        expected=f"主题 '{topic}' 掌握度更新为 {score}",
        actual=f"mastery={mastery_display}",
        details=f"查询条件: user_id={user_id}, session_id={session_id}, topic={topic}, score={score}"
    ), progress


def test_update_mastery_not_found(repo: LearningProgressRepository):
    fake_user = "nonexistent_user_99999"
    fake_session = "nonexistent_session_99999"
    progress = repo.update_mastery(fake_user, fake_session, "测试主题", 0.5)
    passed = progress is None
    return TestResult(
        name="update_mastery() - 记录不存在时返回None",
        passed=passed,
        expected="返回 None（学习进度记录不存在）",
        actual=f"返回: {progress}",
        details=f"查询条件: user_id={fake_user}, session_id={fake_session}"
    ), progress


def cleanup_test_data(db, track_id: str):
    try:
        db.execute(text(f"DELETE FROM learning_progress WHERE track_id = '{track_id}'"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"清理数据失败: {e}")


def run_all_tests():
    print_section("LearningProgressRepository 数据层功能测试")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    repo = LearningProgressRepository(db)

    results: List[TestResult] = []
    test_progress = None
    test_user_id = "student_001"
    test_session_id = "test_session_001"
    test_school_id = "SCH001"
    test_track_id = f"{test_user_id}_{test_session_id}"

    test_data = {
        "user_id": test_user_id,
        "session_id": test_session_id,
        "school_id": test_school_id,
        "lesson_id": "lesson_001",
        "current_node_id": "node_001",
        "current_path": "/path/to/lesson",
        "current_topic": "测试主题_Python基础",
        "confusion_count": 0,
        "mastery": {"测试主题": 0.5},
        "progress_percent": 25.0
    }

    try:
        print_section("准备测试数据 - 清理可能存在的旧数据")
        cleanup_test_data(db, test_track_id)

        print_section("1. 测试 upsert_progress() - 创建学习进度记录")
        result, test_progress = test_upsert_progress_create(repo, test_data)
        results.append(result)

        print_section("2. 测试 upsert_progress() - 更新学习进度记录")
        updated_topic = "测试主题_Python进阶"
        result, test_progress = test_upsert_progress_update(repo, test_data, updated_topic)
        results.append(result)

        print_section("3. 测试 get_progress_by_session() - 查询会话学习进度")
        result, test_progress = test_get_progress_by_session(repo, test_user_id, test_session_id)
        results.append(result)

        print_section("4. 测试 get_progress_by_user() - 查询用户学习进度列表")
        result, progresses = test_get_progress_by_user(repo, test_user_id)
        results.append(result)

        print_section("5. 测试 increment_confusion() - 增加困惑计数")
        result, test_progress = test_increment_confusion(repo, test_user_id, test_session_id)
        results.append(result)

        print_section("6. 测试 increment_confusion() - 记录不存在时返回None")
        result, _ = test_increment_confusion_not_found(repo)
        results.append(result)

        print_section("7. 测试 reset_confusion() - 重置困惑计数")
        result, test_progress = test_reset_confusion(repo, test_user_id, test_session_id)
        results.append(result)

        print_section("8. 测试 reset_confusion() - 记录不存在时返回None")
        result, _ = test_reset_confusion_not_found(repo)
        results.append(result)

        print_section("9. 测试 update_mastery() - 更新主题掌握度")
        result, test_progress = test_update_mastery(repo, test_user_id, test_session_id)
        results.append(result)

        print_section("10. 测试 update_mastery() - 记录不存在时返回None")
        result, _ = test_update_mastery_not_found(repo)
        results.append(result)

    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("清理测试数据")
        try:
            cleanup_test_data(db, test_track_id)
            print(f"✅ 测试数据清理完成 (track_id={test_track_id})")
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
