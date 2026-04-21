import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text, Column, String, DateTime, Integer, ForeignKey, func, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

DATABASE_URL_SYNC = "postgresql://postgres:yaoshun2006@10.0.0.4:5432/ai_ppt_web"

engine = create_engine(DATABASE_URL_SYNC)


class SubjectTest(Base):
    __tablename__ = "subjects_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    courses = relationship("CourseTest", back_populates="subject", cascade="all, delete-orphan")


class CourseTest(Base):
    __tablename__ = "courses_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    subject_id = Column(Integer, ForeignKey("subjects_new.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    ppts = relationship("PPTTest", back_populates="course", cascade="all, delete-orphan")
    subject = relationship("SubjectTest", back_populates="courses")


class PPTTest(Base):
    __tablename__ = "ppts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses_new.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(50))
    slide_count = Column(Integer, default=0)
    slides = Column(JSON)
    parse_status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    course = relationship("CourseTest", back_populates="ppts")


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


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def create_test_data(db) -> tuple:
    subject = SubjectTest(name="测试科目_Python基础")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    course = CourseTest(
        title="测试课程_Python入门",
        subject_id=subject.id,
        description="这是一个测试课程"
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return subject, course


def test_ppt_get_all(db):
    result = db.query(PPTTest).all()
    return TestResult(
        name="get_all() - 获取PPT列表",
        passed=isinstance(result, list),
        expected="返回PPT列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"当前数据库共有 {len(result)} 个PPT记录"
    )


def test_ppt_get_all_with_course_filter(db, course_id: int):
    result = db.query(PPTTest).filter(PPTTest.course_id == course_id).all()
    return TestResult(
        name="get_all() - 按课程ID过滤获取PPT列表",
        passed=isinstance(result, list),
        expected=f"返回course_id={course_id}的PPT列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"当前课程共有 {len(result)} 个PPT记录"
    )


def test_ppt_get_by_id(db, ppt_id: int):
    result = db.query(PPTTest).filter(PPTTest.id == ppt_id).first()
    if result:
        return TestResult(
            name="get_by_id() - 根据ID查询PPT",
            passed=result.id == ppt_id,
            expected=f"返回ID={ppt_id}的PPT",
            actual=f"返回: id={result.id}, file_name={result.file_name}"
        )
    else:
        return TestResult(
            name="get_by_id() - 根据ID查询PPT",
            passed=False,
            expected=f"返回ID={ppt_id}的PPT",
            actual="未找到该PPT"
        )


def test_ppt_get_by_nonexistent_id(db):
    nonexistent_id = 99999
    result = db.query(PPTTest).filter(PPTTest.id == nonexistent_id).first()
    return TestResult(
        name="get_by_id() - 查询不存在的ID",
        passed=result is None,
        expected=f"返回None（ID={nonexistent_id}不存在）",
        actual=f"返回: {result}"
    )


def test_ppt_get_by_course(db, course_id: int):
    result = db.query(PPTTest).filter(
        PPTTest.course_id == course_id
    ).order_by(PPTTest.created_at.desc()).all()
    return TestResult(
        name="get_by_course() - 根据课程ID查询PPT",
        passed=isinstance(result, list),
        expected=f"返回course_id={course_id}的PPT列表",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"课程ID={course_id}共有 {len(result)} 个PPT"
    )


def test_ppt_get_by_nonexistent_course(db):
    nonexistent_course_id = 99999
    result = db.query(PPTTest).filter(
        PPTTest.course_id == nonexistent_course_id
    ).all()
    return TestResult(
        name="get_by_course() - 查询不存在的课程ID",
        passed=isinstance(result, list) and len(result) == 0,
        expected=f"返回空列表（课程ID={nonexistent_course_id}不存在）",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}"
    )


def test_ppt_create(db, course_id: int):
    ppt = PPTTest(
        course_id=course_id,
        file_name="测试PPT_第一章.pptx",
        file_path="/uploads/ppt/test_chapter1.pptx",
        file_size=1024000,
        file_type="pptx",
        parse_status="pending"
    )
    db.add(ppt)
    db.commit()
    db.refresh(ppt)

    return TestResult(
        name="create() - 创建PPT记录",
        passed=ppt is not None and ppt.course_id == course_id,
        expected=f"成功创建PPT，course_id={course_id}",
        actual=f"创建结果: id={ppt.id}, file_name={ppt.file_name}, parse_status={ppt.parse_status}",
        details=f"文件大小: {ppt.file_size} bytes, 文件类型: {ppt.file_type}"
    ), ppt


def test_ppt_create_with_minimal_data(db, course_id: int):
    ppt = PPTTest(
        course_id=course_id,
        file_name="minimal_ppt.pptx",
        parse_status="pending"
    )
    db.add(ppt)
    db.commit()
    db.refresh(ppt)

    return TestResult(
        name="create() - 创建PPT记录（最小数据）",
        passed=ppt is not None,
        expected=f"成功创建PPT（仅必填字段）",
        actual=f"创建结果: id={ppt.id}, file_name={ppt.file_name}, parse_status={ppt.parse_status}"
    ), ppt


def test_ppt_update_parse_status(db, ppt_id: int):
    ppt = db.query(PPTTest).filter(PPTTest.id == ppt_id).first()
    if not ppt:
        return TestResult(
            name="update_parse_status() - 更新解析状态",
            passed=False,
            expected=f"更新ID={ppt_id}的PPT",
            actual="PPT不存在"
        ), None

    ppt.parse_status = "completed"
    ppt.slide_count = 15
    ppt.slides = [{"index": 1, "title": "封面"}, {"index": 2, "title": "目录"}]
    db.commit()
    db.refresh(ppt)

    return TestResult(
        name="update_parse_status() - 更新解析状态",
        passed=ppt.parse_status == "completed" and ppt.slide_count == 15,
        expected=f"更新parse_status=completed, slide_count=15",
        actual=f"parse_status={ppt.parse_status}, slide_count={ppt.slide_count}, slides={ppt.slides}"
    ), ppt


def test_ppt_update_parse_status_to_parsing(db, course_id: int):
    ppt = PPTTest(
        course_id=course_id,
        file_name="parsing_test.pptx",
        parse_status="pending"
    )
    db.add(ppt)
    db.commit()
    db.refresh(ppt)

    ppt.parse_status = "parsing"
    db.commit()
    db.refresh(ppt)

    return TestResult(
        name="update_parse_status() - 更新解析状态为parsing",
        passed=ppt.parse_status == "parsing",
        expected="parse_status=parsing",
        actual=f"parse_status={ppt.parse_status}"
    ), ppt


def test_ppt_update_parse_status_to_failed(db, course_id: int):
    ppt = PPTTest(
        course_id=course_id,
        file_name="failed_test.pptx",
        parse_status="pending"
    )
    db.add(ppt)
    db.commit()
    db.refresh(ppt)

    ppt.parse_status = "failed"
    db.commit()
    db.refresh(ppt)

    return TestResult(
        name="update_parse_status() - 更新解析状态为failed",
        passed=ppt.parse_status == "failed",
        expected="parse_status=failed",
        actual=f"parse_status={ppt.parse_status}"
    ), ppt


def test_ppt_delete(db, ppt_id: int):
    ppt = db.query(PPTTest).filter(PPTTest.id == ppt_id).first()
    if not ppt:
        return TestResult(
            name="delete() - 删除PPT记录",
            passed=False,
            expected=f"删除ID={ppt_id}的PPT",
            actual="PPT不存在"
        )

    db.delete(ppt)
    db.commit()

    exists = db.query(PPTTest).filter(PPTTest.id == ppt_id).first()
    return TestResult(
        name="delete() - 删除PPT记录",
        passed=exists is None,
        expected=f"成功删除ID={ppt_id}的PPT",
        actual=f"删除后查询结果: {exists}"
    )


def test_ppt_delete_nonexistent(db):
    nonexistent_id = 99999
    ppt = db.query(PPTTest).filter(PPTTest.id == nonexistent_id).first()
    if ppt:
        db.delete(ppt)
        db.commit()

    result = db.query(PPTTest).filter(PPTTest.id == nonexistent_id).first()
    return TestResult(
        name="delete() - 删除不存在的PPT",
        passed=result is None,
        expected=f"返回False（ID={nonexistent_id}不存在）",
        actual=f"删除不存在的PPT，返回: {result is None}"
    )


def run_all_tests():
    print_section("PPTRepository 数据层功能测试")

    print_section("创建必要的数据库表")
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️ 创建表失败: {e}")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    results: List[TestResult] = []
    test_course = None
    test_ppts = []
    subject = None

    try:
        print_section("准备测试数据")
        subject, test_course = create_test_data(db)
        print(f"✅ 创建测试数据成功: subject_id={subject.id}, course_id={test_course.id}")

        print_section("1. 测试 PPTRepository.get_all() - 获取所有PPT")
        results.append(test_ppt_get_all(db))

        print_section("2. 测试 PPTRepository.get_all() - 按课程ID过滤")
        results.append(test_ppt_get_all_with_course_filter(db, test_course.id))

        print_section("3. 测试 PPTRepository.get_by_id() - 查询存在的PPT")
        result, test_ppt = test_ppt_create(db, test_course.id)
        results.append(result)
        if test_ppt:
            test_ppts.append(test_ppt)
            results.append(test_ppt_get_by_id(db, test_ppt.id))

        print_section("4. 测试 PPTRepository.get_by_id() - 查询不存在的PPT")
        results.append(test_ppt_get_by_nonexistent_id(db))

        print_section("5. 测试 PPTRepository.get_by_course() - 根据课程ID查询PPT")
        results.append(test_ppt_get_by_course(db, test_course.id))

        print_section("6. 测试 PPTRepository.get_by_course() - 查询不存在的课程")
        results.append(test_ppt_get_by_nonexistent_course(db))

        print_section("7. 测试 PPTRepository.create() - 创建PPT记录")
        result, test_ppt = test_ppt_create(db, test_course.id)
        results.append(result)
        if test_ppt:
            test_ppts.append(test_ppt)

        print_section("8. 测试 PPTRepository.create() - 创建PPT记录（最小数据）")
        result, test_ppt = test_ppt_create_with_minimal_data(db, test_course.id)
        results.append(result)
        if test_ppt:
            test_ppts.append(test_ppt)

        print_section("9. 测试 PPTRepository.update_parse_status() - 更新为completed")
        if test_ppts:
            result, updated_ppt = test_ppt_update_parse_status(db, test_ppts[0].id)
            results.append(result)

        print_section("10. 测试 PPTRepository.update_parse_status() - 更新为parsing")
        result, test_ppt = test_ppt_update_parse_status_to_parsing(db, test_course.id)
        results.append(result)
        if test_ppt:
            test_ppts.append(test_ppt)

        print_section("11. 测试 PPTRepository.update_parse_status() - 更新为failed")
        result, test_ppt = test_ppt_update_parse_status_to_failed(db, test_course.id)
        results.append(result)
        if test_ppt:
            test_ppts.append(test_ppt)

        print_section("12. 测试 PPTRepository.delete() - 删除PPT记录")
        if test_ppts:
            results.append(test_ppt_delete(db, test_ppts[0].id))
            test_ppts.pop(0)

        print_section("13. 测试 PPTRepository.delete() - 删除不存在的PPT")
        results.append(test_ppt_delete_nonexistent(db))

    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("清理测试数据")
        try:
            for ppt in test_ppts:
                db.query(PPTTest).filter(PPTTest.id == ppt.id).delete()
            if test_course:
                db.query(CourseTest).filter(CourseTest.id == test_course.id).delete()
            if subject:
                db.query(SubjectTest).filter(SubjectTest.id == subject.id).delete()
            db.commit()
            print("✅ 测试数据清理完成")
        except Exception as e:
            print(f"⚠️ 清理测试数据失败: {e}")
            db.rollback()
        db.close()

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
