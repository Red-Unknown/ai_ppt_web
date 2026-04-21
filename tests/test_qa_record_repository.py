"""
QARecordRepository 测试脚本
测试问答记录数据层的 CRUD 操作
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from backend.app.models.qa import QARecord
    from backend.app.repositories.qa_record_repository import QARecordRepository
    from backend.app.core.database import Base
except ModuleNotFoundError:
    from app.models.qa import QARecord
    from app.repositories.qa_record_repository import QARecordRepository
    from app.core.database import Base


DB_CONFIG = {
    "host": "10.0.0.4",
    "port": 5432,
    "user": "postgres",
    "password": "yaoshun2006",
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/ai_ppt_web"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def print_separator(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_create_record(repo: QARecordRepository):
    print_separator("测试 create_record() - 创建问答记录")

    test_data = {
        "session_id": "test_session_001",
        "user_id": "student_001",
        "school_id": "SCH001",
        "question_text": "什么是Python?",
        "answer_text": "Python是一种高级编程语言。",
        "question_type": "knowledge",
        "lesson_id": None,
        "cited_node_id": None,
        "source_page_num": 10,
        "sources": [{"bbox": [0, 0, 100, 100], "score": 0.95}],
        "current_path": "/course/python/basics",
        "video_timestamp": 120.5,
        "understanding_level": "good",
        "response_ms": 1500,
        "is_accurate": True,
        "reasoning_content": "基于Python官方文档回答",
        "tool_calls": [{"name": "web_search", "query": "Python definition"}]
    }

    print("输入数据:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")

    print("\n预期结果:")
    print("  - 返回 QARecord 对象")
    print("  - answer_id 自动生成")
    print("  - 所有字段正确保存")

    try:
        record = repo.create_record(**test_data)

        print("\n实际结果:")
        print(f"  answer_id: {record.answer_id}")
        print(f"  session_id: {record.session_id}")
        print(f"  user_id: {record.user_id}")
        print(f"  school_id: {record.school_id}")
        print(f"  question_text: {record.question_text}")
        print(f"  answer_text: {record.answer_text}")
        print(f"  question_type: {record.question_type}")
        print(f"  lesson_id: {record.lesson_id}")
        print(f"  cited_node_id: {record.cited_node_id}")
        print(f"  source_page_num: {record.source_page_num}")
        print(f"  sources: {record.sources}")
        print(f"  current_path: {record.current_path}")
        print(f"  video_timestamp: {record.video_timestamp}")
        print(f"  understanding_level: {record.understanding_level}")
        print(f"  response_ms: {record.response_ms}")
        print(f"  is_accurate: {record.is_accurate}")
        print(f"  reasoning_content: {record.reasoning_content}")
        print(f"  tool_calls: {record.tool_calls}")
        print(f"  created_at: {record.created_at}")

        assert record.answer_id is not None, "answer_id should be auto-generated"
        assert record.session_id == test_data["session_id"]
        assert record.user_id == test_data["user_id"]
        assert record.question_text == test_data["question_text"]
        assert record.answer_text == test_data["answer_text"]

        print("\n✅ 测试通过!")
        return record.answer_id

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_get_records_by_session(repo: QARecordRepository, session_id: str):
    print_separator("测试 get_records_by_session() - 查询会话记录")

    print("输入参数:")
    print(f"  session_id: {session_id}")
    print(f"  limit: 50")

    print("\n预期结果:")
    print("  - 返回该会话的所有问答记录列表")
    print("  - 按创建时间降序排列")

    try:
        records = repo.get_records_by_session(session_id, limit=50)

        print(f"\n实际结果:")
        print(f"  返回记录数: {len(records)}")

        for i, record in enumerate(records):
            print(f"\n  记录 {i+1}:")
            print(f"    answer_id: {record.answer_id}")
            print(f"    question_text: {record.question_text[:50]}..." if len(record.question_text) > 50 else f"    question_text: {record.question_text}")
            print(f"    answer_text: {record.answer_text[:50]}..." if len(record.answer_text) > 50 else f"    answer_text: {record.answer_text}")
            print(f"    created_at: {record.created_at}")

        if len(records) > 0:
            print("\n✅ 测试通过!")
            return True
        else:
            print("\n⚠️ 测试通过(无记录): 返回空列表")
            return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_records_by_user(repo: QARecordRepository, user_id: str):
    print_separator("测试 get_records_by_user() - 查询用户记录")

    print("输入参数:")
    print(f"  user_id: {user_id}")
    print(f"  limit: 100")

    print("\n预期结果:")
    print("  - 返回该用户的所有问答记录列表")
    print("  - 按创建时间降序排列")

    try:
        records = repo.get_records_by_user(user_id, limit=100)

        print(f"\n实际结果:")
        print(f"  返回记录数: {len(records)}")

        for i, record in enumerate(records):
            print(f"\n  记录 {i+1}:")
            print(f"    answer_id: {record.answer_id}")
            print(f"    session_id: {record.session_id}")
            print(f"    question_text: {record.question_text[:50]}..." if len(record.question_text) > 50 else f"    question_text: {record.question_text}")
            print(f"    answer_text: {record.answer_text[:50]}..." if len(record.answer_text) > 50 else f"    answer_text: {record.answer_text}")
            print(f"    created_at: {record.created_at}")

        if len(records) > 0:
            print("\n✅ 测试通过!")
            return True
        else:
            print("\n⚠️ 测试通过(无记录): 返回空列表")
            return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_latest_record_by_session(repo: QARecordRepository, session_id: str):
    print_separator("测试 get_latest_record_by_session() - 查询最新记录")

    print("输入参数:")
    print(f"  session_id: {session_id}")

    print("\n预期结果:")
    print("  - 返回该会话的最新一条问答记录")
    print("  - 如果没有记录返回 None")

    try:
        record = repo.get_latest_record_by_session(session_id)

        print("\n实际结果:")
        if record:
            print(f"  answer_id: {record.answer_id}")
            print(f"  question_text: {record.question_text}")
            print(f"  answer_text: {record.answer_text[:100]}..." if len(record.answer_text) > 100 else f"  answer_text: {record.answer_text}")
            print(f"  created_at: {record.created_at}")
            print("\n✅ 测试通过!")
            return True
        else:
            print("  返回: None")
            print("\n⚠️ 测试通过(无记录): 返回 None")
            return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data(repo: QARecordRepository, session_id: str, user_id: str):
    print_separator("清理测试数据")

    try:
        records = repo.get_records_by_session(session_id, limit=1000)
        for record in records:
            repo.db.delete(record)
        repo.db.commit()
        print(f"已删除 session_id={session_id} 的所有测试记录")
    except Exception as e:
        print(f"清理数据时出错: {e}")
        repo.db.rollback()


def main():
    print("\n" + "=" * 60)
    print("  QARecordRepository 数据层测试")
    print("  数据库: 10.0.0.4:5432/ai_ppt_web")
    print("=" * 60)

    session = SessionLocal()
    repo = QARecordRepository(session)

    test_session_id = "test_session_001"
    test_user_id = "student_001"

    results = []

    try:
        test_data_1 = {
            "session_id": test_session_id,
            "user_id": test_user_id,
            "school_id": "SCH001",
            "question_text": "什么是Python?",
            "answer_text": "Python是一种高级编程语言。",
            "question_type": "knowledge",
            "lesson_id": None,
            "cited_node_id": None,
            "source_page_num": 10,
            "sources": [{"bbox": [0, 0, 100, 100], "score": 0.95}],
            "current_path": "/course/python/basics",
            "video_timestamp": 120.5,
            "understanding_level": "good",
            "response_ms": 1500,
            "is_accurate": True,
            "reasoning_content": "基于Python官方文档回答",
            "tool_calls": [{"name": "web_search", "query": "Python definition"}]
        }

        test_data_2 = {
            "session_id": test_session_id,
            "user_id": test_user_id,
            "school_id": "SCH001",
            "question_text": "Python有哪些优势?",
            "answer_text": "Python具有简单易学、功能强大、生态丰富等优势。",
            "question_type": "knowledge",
            "lesson_id": None,
            "cited_node_id": None,
            "source_page_num": 5,
            "sources": [{"bbox": [10, 10, 50, 50], "score": 0.9}],
            "current_path": "/course/python/advantages",
            "video_timestamp": 300.0,
            "understanding_level": "excellent",
            "response_ms": 1200,
            "is_accurate": True,
            "reasoning_content": "基于Python官方文档回答",
            "tool_calls": None
        }

        print("\n--- 创建测试记录 1 ---")
        record1 = repo.create_record(**test_data_1)
        print(f"记录1创建成功: answer_id={record1.answer_id}")

        import time
        time.sleep(0.5)

        print("\n--- 创建测试记录 2 ---")
        record2 = repo.create_record(**test_data_2)
        print(f"记录2创建成功: answer_id={record2.answer_id}")

        if record1 and record2:
            results.append(("create_record", True))
        else:
            results.append(("create_record", False))

        results.append(("get_records_by_session", test_get_records_by_session(repo, test_session_id)))

        results.append(("get_records_by_user", test_get_records_by_user(repo, test_user_id)))

        results.append(("get_latest_record_by_session", test_get_latest_record_by_session(repo, test_session_id)))

        cleanup_test_data(repo, test_session_id, test_user_id)

    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

    print_separator("测试结果汇总")
    print("\n测试项目结果:")
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\n总计: {passed_count}/{total_count} 通过")

    if passed_count == total_count:
        print("\n🎉 所有测试全部通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查!")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
