"""
Service层业务逻辑测试
测试Service层与Repository层的集成，包括事务处理和异常处理
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.repositories import (
    QARecordRepository,
    LearningProgressRepository,
    CourseRepository,
    SubjectRepository,
    ChapterRepository
)

DATABASE_URL = "postgresql://postgres:yaoshun2006@10.0.0.4:5432/ai_ppt_web"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def test_qa_service_integration():
    """测试问答服务与Repository的集成"""
    print("=" * 60)
    print("测试 Service 层 - QARecordRepository 集成")
    print("=" * 60)
    
    results = []
    
    db = SessionLocal()
    try:
        qa_repo = QARecordRepository(db)
        
        # 查询现有用户和lesson
        print("\n[前置准备] 查询现有数据")
        user_record = db.execute(text("SELECT user_id FROM users LIMIT 1")).fetchone()
        lesson_record = db.execute(text("SELECT lesson_id FROM lessons LIMIT 1")).fetchone()
        
        if user_record and lesson_record:
            test_user_id = user_record[0]
            test_lesson_id = lesson_record[0]
            print(f"  使用现有用户ID: {test_user_id}, lesson_id: {test_lesson_id}")
        else:
            print(f"  数据库中无现有数据，跳过测试")
            return [("缺少测试数据", False)]
        
        # 测试1: 创建问答记录 - 验证事务提交
        print("\n[测试 1] 创建问答记录并验证数据库状态")
        record = qa_repo.create_record(
            session_id="test_service_session_002",
            user_id=test_user_id,
            school_id="TEST_SCHOOL_001",
            question_text="什么是牛顿第三定律？",
            answer_text="作用力和反作用力大小相等、方向相反、作用在同一直线上。",
            question_type="knowledge",
            lesson_id=test_lesson_id
        )
        print(f"  输入: session_id=test_service_session_002, question=什么是牛顿第三定律？")
        print(f"  预期: 返回QARecord对象，数据库中存在该记录")
        print(f"  实际: answer_id={record.answer_id}, question={record.question_text}")
        results.append(("创建问答记录", True))
        
        # 验证数据库状态
        db.commit()
        verify_record = qa_repo.get_records_by_session("test_service_session_002")
        if verify_record and len(verify_record) > 0:
            print(f"  ✓ 数据库验证通过: 查询到 {len(verify_record)} 条记录")
            results.append(("数据库状态验证", True))
        else:
            print(f"  ✗ 数据库验证失败")
            results.append(("数据库状态验证", False))
        
        # 测试2: 查询会话记录
        print("\n[测试 2] 查询会话的所有问答记录")
        records = qa_repo.get_records_by_session("test_service_session_002", limit=10)
        print(f"  输入: session_id=test_service_session_002, limit=10")
        print(f"  预期: 返回该会话的所有问答记录")
        print(f"  实际: 查询到 {len(records)} 条记录")
        results.append(("查询会话记录", len(records) >= 1))
        
        # 测试3: 查询最新记录
        print("\n[测试 3] 查询会话的最新问答记录")
        latest = qa_repo.get_latest_record_by_session("test_service_session_002")
        print(f"  输入: session_id=test_service_session_002")
        print(f"  预期: 返回最新的问答记录")
        print(f"  实际: 最新记录 answer_id={latest.answer_id if latest else None}")
        results.append(("查询最新记录", latest is not None))
        
        # 测试4: 查询用户记录
        print("\n[测试 4] 查询用户的所有问答记录")
        user_records = qa_repo.get_records_by_user(test_user_id, limit=10)
        print(f"  输入: user_id={test_user_id}, limit=10")
        print(f"  预期: 返回该用户的问答记录")
        print(f"  实际: 查询到 {len(user_records)} 条记录")
        results.append(("查询用户记录", len(user_records) >= 1))
        
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("异常处理", False))
    finally:
        db.close()
    
    return results


def test_learning_progress_service_integration():
    """测试学习进度服务与Repository的集成"""
    print("\n" + "=" * 60)
    print("测试 Service 层 - LearningProgressRepository 集成")
    print("=" * 60)
    
    results = []
    
    db = SessionLocal()
    try:
        progress_repo = LearningProgressRepository(db)
        
        # 查询现有用户和lesson
        print("\n[前置准备] 查询现有数据")
        user_record = db.execute(text("SELECT user_id FROM users LIMIT 1")).fetchone()
        lesson_record = db.execute(text("SELECT lesson_id FROM lessons LIMIT 1")).fetchone()
        
        if user_record and lesson_record:
            test_user_id = user_record[0]
            test_lesson_id = lesson_record[0]
            print(f"  使用现有用户ID: {test_user_id}, lesson_id: {test_lesson_id}")
        else:
            print(f"  数据库中无现有数据，跳过测试")
            return [("缺少测试数据", False)]
        
        # 测试1: 创建学习进度
        print("\n[测试 1] 创建学习进度记录")
        progress = progress_repo.upsert_progress(
            user_id=test_user_id,
            session_id="test_service_session_003",
            school_id="TEST_SCHOOL_001",
            lesson_id=test_lesson_id,
            current_node_id="node_001",
            current_path="/chapter1/section1",
            current_topic="牛顿定律",
            progress_percent=25.5
        )
        print(f"  输入: user_id={test_user_id}, session_id=test_service_session_003, progress_percent=25.5")
        print(f"  预期: 返回LearningProgress对象，数据库中存在该记录")
        print(f"  实际: track_id={progress.track_id}, progress_percent={progress.progress_percent}")
        results.append(("创建学习进度", progress is not None))
        
        # 验证数据库状态
        db.commit()
        verify_progress = progress_repo.get_progress_by_session(test_user_id, "test_service_session_003")
        if verify_progress:
            print(f"  ✓ 数据库验证通过: track_id={verify_progress.track_id}")
            results.append(("进度数据库验证", True))
        else:
            print(f"  ✗ 数据库验证失败")
            results.append(("进度数据库验证", False))
        
        # 测试2: 更新学习进度
        print("\n[测试 2] 更新学习进度")
        updated = progress_repo.upsert_progress(
            user_id=test_user_id,
            session_id="test_service_session_003",
            school_id="TEST_SCHOOL_001",
            lesson_id=test_lesson_id,
            current_node_id="node_002",
            current_path="/chapter1/section2",
            current_topic="牛顿第二定律",
            progress_percent=50.0
        )
        print(f"  输入: progress_percent=50.0")
        print(f"  预期: 更新现有记录，progress_percent变为50.0")
        print(f"  实际: progress_percent={updated.progress_percent}")
        results.append(("更新学习进度", updated.progress_percent == 50.0))
        
        # 测试3: 查询用户进度列表
        print("\n[测试 3] 查询用户的学习进度列表")
        user_progress = progress_repo.get_progress_by_user(test_user_id, limit=5)
        print(f"  输入: user_id={test_user_id}, limit=5")
        print(f"  预期: 返回该用户的学习进度列表")
        print(f"  实际: 查询到 {len(user_progress)} 条记录")
        results.append(("查询用户进度", len(user_progress) >= 1))
        
        # 测试4: 增加困惑计数
        print("\n[测试 4] 增加困惑计数")
        confused = progress_repo.increment_confusion(test_user_id, "test_service_session_003")
        if confused:
            print(f"  输入: user_id={test_user_id}, session_id=test_service_session_003")
            print(f"  预期: confusion_count增加1")
            print(f"  实际: confusion_count={confused.confusion_count}")
            results.append(("增加困惑计数", confused.confusion_count >= 1))
        
        # 测试5: 重置困惑计数
        print("\n[测试 5] 重置困惑计数")
        reset = progress_repo.reset_confusion(test_user_id, "test_service_session_003")
        if reset:
            print(f"  输入: user_id={test_user_id}, session_id=test_service_session_003")
            print(f"  预期: confusion_count重置为0")
            print(f"  实际: confusion_count={reset.confusion_count}")
            results.append(("重置困惑计数", reset.confusion_count == 0))
        
        # 测试6: 更新主题掌握度
        print("\n[测试 6] 更新主题掌握度")
        mastery = progress_repo.update_mastery(test_user_id, "test_service_session_003", "牛顿定律", 0.85)
        if mastery:
            print(f"  输入: topic=牛顿定律, score=0.85")
            print(f"  预期: mastery中包含topic=牛顿定律的记录")
            print(f"  实际: mastery={mastery.mastery}")
            results.append(("更新主题掌握度", "牛顿定律" in (mastery.mastery or {})))
        
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("异常处理", False))
    finally:
        db.close()
    
    return results


def test_transaction_rollback():
    """测试事务回滚"""
    print("\n" + "=" * 60)
    print("测试 Service 层 - 事务回滚")
    print("=" * 60)
    
    results = []
    
    db = SessionLocal()
    try:
        subject_repo = SubjectRepository(db)
        
        # 测试: 事务回滚
        print("\n[测试] 事务回滚验证")
        
        # 先创建一条记录
        test_subject = subject_repo.create(name="测试科目_事务")
        print(f"  创建测试科目: id={test_subject.id}, name={test_subject.name}")
        
        # 模拟异常，触发回滚
        try:
            db.flush()
            # 故意引发异常
            raise Exception("模拟业务异常")
        except Exception as e:
            db.rollback()
            print(f"  触发异常后执行rollback")
        
        # 验证记录是否被回滚
        verify_subject = subject_repo.get_by_id(test_subject.id)
        if verify_subject is None:
            print(f"  ✓ 事务回滚验证通过: 记录已被回滚")
            results.append(("事务回滚", True))
        else:
            print(f"  ✗ 事务回滚验证失败: 记录仍存在")
            results.append(("事务回滚", False))
            
            # 清理测试数据
            subject_repo.delete(test_subject.id)
            db.commit()
        
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("事务回滚异常处理", False))
    finally:
        db.close()
    
    return results


def test_multiple_repository_transaction():
    """测试多Repository事务一致性"""
    print("\n" + "=" * 60)
    print("测试 Service 层 - 多Repository事务一致性")
    print("=" * 60)
    
    results = []
    
    db = SessionLocal()
    try:
        subject_repo = SubjectRepository(db)
        chapter_repo = ChapterRepository(db)
        course_repo = CourseRepository(db)
        
        # 测试: 创建课程及其关联数据（原子操作）
        print("\n[测试] 多Repository事务一致性")
        
        # 1. 创建科目
        subject = subject_repo.create(name="测试科目_多Repo")
        print(f"  1. 创建科目: id={subject.id}")
        
        # 2. 创建章节（依赖科目）
        chapter = chapter_repo.create(subject_id=subject.id, name="测试章节", order=1)
        print(f"  2. 创建章节: id={chapter.id}, subject_id={chapter.subject_id}")
        
        # 3. 创建课程（依赖科目和章节）
        course = course_repo.create(
            title="测试课程_多Repo",
            subject_id=subject.id,
            chapter_id=chapter.id,
            description="这是一个测试课程"
        )
        print(f"  3. 创建课程: id={course.id}, title={course.title}")
        
        # 4. 验证关联关系
        if course.subject_id == subject.id and course.chapter_id == chapter.id:
            print(f"  ✓ 关联关系验证通过")
            results.append(("多Repository事务", True))
        else:
            print(f"  ✗ 关联关系验证失败")
            results.append(("多Repository事务", False))
        
        # 5. 清理测试数据
        course_repo.delete(course.id)
        chapter_repo.delete(chapter.id)
        subject_repo.delete(subject.id)
        db.commit()
        print(f"  清理测试数据完成")
        
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        db.rollback()
        results.append(("多Repository异常处理", False))
    finally:
        db.close()
    
    return results


def test_logging():
    """测试日志记录"""
    print("\n" + "=" * 60)
    print("测试 Service 层 - 日志记录")
    print("=" * 60)
    
    results = []
    
    # 测试日志配置
    import logging
    from backend.app.core.logging_config import get_logger
    
    print("\n[测试] 日志系统集成")
    
    try:
        logger = get_logger(__name__)
        logger.info("测试日志 - INFO级别")
        logger.warning("测试日志 - WARNING级别")
        
        print(f"  ✓ 日志系统正常工作")
        results.append(("日志记录", True))
        
    except Exception as e:
        print(f"  ✗ 日志异常: {str(e)}")
        results.append(("日志记录", False))
    
    return results


def main():
    """运行所有Service层测试"""
    print("\n" + "=" * 60)
    print("开始 Service 层业务逻辑测试")
    print("=" * 60)
    
    all_results = []
    
    # 1. QARecordRepository 集成测试
    all_results.extend(test_qa_service_integration())
    
    # 2. LearningProgressRepository 集成测试
    all_results.extend(test_learning_progress_service_integration())
    
    # 3. 事务回滚测试
    all_results.extend(test_transaction_rollback())
    
    # 4. 多Repository事务一致性测试
    all_results.extend(test_multiple_repository_transaction())
    
    # 5. 日志记录测试
    all_results.extend(test_logging())
    
    # 输出测试汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    for name, result in all_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有Service层测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
