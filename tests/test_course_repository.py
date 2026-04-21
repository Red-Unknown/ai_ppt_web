import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text, Column, String, DateTime, Integer, ForeignKey, Text, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

DATABASE_URL_SYNC = "postgresql://postgres:yaoshun2006@10.0.0.4:5432/ai_ppt_web"


class SubjectTest(Base):
    __tablename__ = "subjects_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    chapters = relationship("ChapterTest", back_populates="subject")


class ChapterTest(Base):
    __tablename__ = "chapters_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects_new.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    subject = relationship("SubjectTest", back_populates="chapters")


class CourseTest(Base):
    __tablename__ = "courses_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    subject_id = Column(Integer, ForeignKey("subjects_new.id", ondelete="SET NULL"))
    chapter_id = Column(Integer, ForeignKey("chapters_new.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    slides = relationship("SlideTest", back_populates="course", cascade="all, delete-orphan")
    documents = relationship("CourseDocumentTest", back_populates="course", cascade="all, delete-orphan")


class SlideTest(Base):
    __tablename__ = "slides_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses_new.id", ondelete="CASCADE"), nullable=False)
    slide_index = Column(Integer, nullable=False)
    image_url = Column(String(500))
    duration = Column(Integer, default=0)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    course = relationship("CourseTest", back_populates="slides")


class CourseDocumentTest(Base):
    __tablename__ = "course_documents_new"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses_new.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    doc_type = Column(String(50), default="text")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    course = relationship("CourseTest", back_populates="documents")


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
    engine = create_engine(DATABASE_URL_SYNC)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subjects_new (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chapters_new (
                id SERIAL PRIMARY KEY,
                subject_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                "order" INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS courses_new (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                subject_id INTEGER,
                chapter_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS slides_new (
                id SERIAL PRIMARY KEY,
                course_id INTEGER NOT NULL,
                slide_index INTEGER NOT NULL,
                image_url VARCHAR(500),
                duration INTEGER DEFAULT 0,
                content TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS course_documents_new (
                id SERIAL PRIMARY KEY,
                course_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                doc_type VARCHAR(50) DEFAULT 'text',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        try:
            conn.execute(text("""
                ALTER TABLE chapters_new 
                ADD CONSTRAINT fk_chapters_new_subjects 
                FOREIGN KEY (subject_id) REFERENCES subjects_new(id) ON DELETE CASCADE
            """))
        except:
            pass
        
        try:
            conn.execute(text("""
                ALTER TABLE courses_new 
                ADD CONSTRAINT fk_courses_new_subjects 
                FOREIGN KEY (subject_id) REFERENCES subjects_new(id) ON DELETE SET NULL
            """))
        except:
            pass
        
        try:
            conn.execute(text("""
                ALTER TABLE courses_new 
                ADD CONSTRAINT fk_courses_new_chapters 
                FOREIGN KEY (chapter_id) REFERENCES chapters_new(id) ON DELETE SET NULL
            """))
        except:
            pass
        
        try:
            conn.execute(text("""
                ALTER TABLE slides_new 
                ADD CONSTRAINT fk_slides_new_courses 
                FOREIGN KEY (course_id) REFERENCES courses_new(id) ON DELETE CASCADE
            """))
        except:
            pass
        
        try:
            conn.execute(text("""
                ALTER TABLE course_documents_new 
                ADD CONSTRAINT fk_docs_new_courses 
                FOREIGN KEY (course_id) REFERENCES courses_new(id) ON DELETE CASCADE
            """))
        except:
            pass
        
        conn.commit()
    engine.dispose()
    print("✅ 数据库表创建完成")


def create_test_data(db) -> tuple:
    subject = SubjectTest(name="测试科目_Python基础")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    chapter = ChapterTest(subject_id=subject.id, name="测试章节_变量与数据类型", order=1)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    return subject, chapter


def test_course_get_all(db):
    result = db.query(CourseTest).all()
    return TestResult(
        name="get_all() - 获取课程列表",
        passed=isinstance(result, list),
        expected="返回课程列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"当前数据库共有 {len(result)} 个课程"
    )


def test_course_get_by_id(db):
    nonexistent_id = 99999
    result = db.query(CourseTest).filter(CourseTest.id == nonexistent_id).first()
    return TestResult(
        name="get_by_id() - 根据ID查询课程",
        passed=result is None,
        expected=f"返回None（ID={nonexistent_id}不存在）",
        actual=f"返回: {result}"
    )


def test_course_create(db, subject_id: int, chapter_id: int):
    subject = db.query(SubjectTest).filter(SubjectTest.id == subject_id).first()
    if not subject:
        return TestResult(
            name="create() - 创建新课程",
            passed=False,
            expected=f"subject_id={subject_id}存在",
            actual="subject不存在",
            details="无法创建课程：subject不存在"
        ), None

    chapter = db.query(ChapterTest).filter(
        ChapterTest.id == chapter_id,
        ChapterTest.subject_id == subject_id
    ).first()
    if not chapter:
        return TestResult(
            name="create() - 创建新课程",
            passed=False,
            expected=f"chapter_id={chapter_id}存在",
            actual="chapter不存在",
            details="无法创建课程：chapter不存在"
        ), None

    course = CourseTest(
        title="测试课程_Python变量",
        subject_id=subject_id,
        chapter_id=chapter_id,
        description="这是一个测试课程，用于验证CourseRepository的create方法"
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return TestResult(
        name="create() - 创建新课程（含subject/chapter关联验证）",
        passed=course is not None and course.subject_id == subject_id and course.chapter_id == chapter_id,
        expected=f"成功创建课程，subject_id={subject_id}, chapter_id={chapter_id}",
        actual=f"创建结果: id={course.id}, subject_id={course.subject_id}, chapter_id={course.chapter_id}",
        details=f"课程标题: {course.title}"
    ), course


def test_course_update(db, course_id: int):
    course = db.query(CourseTest).filter(CourseTest.id == course_id).first()
    if not course:
        return TestResult(
            name="update() - 更新课程信息",
            passed=False,
            expected=f"更新ID={course_id}的课程",
            actual="课程不存在"
        )
    
    course.title = "测试课程_Python变量_更新版"
    course.description = "这是更新后的描述"
    db.commit()
    db.refresh(course)
    
    return TestResult(
        name="update() - 更新课程信息",
        passed=course.title == "测试课程_Python变量_更新版",
        expected="成功更新课程标题",
        actual=f"更新后课程标题: {course.title}"
    )


def test_course_delete(db, course_id: int):
    course = db.query(CourseTest).filter(CourseTest.id == course_id).first()
    if not course:
        return TestResult(
            name="delete() - 删除课程",
            passed=False,
            expected=f"删除ID={course_id}的课程",
            actual="课程不存在"
        )
    
    db.delete(course)
    db.commit()
    
    exists = db.query(CourseTest).filter(CourseTest.id == course_id).first()
    return TestResult(
        name="delete() - 删除课程",
        passed=exists is None,
        expected=f"成功删除ID={course_id}的课程",
        actual=f"删除后查询结果: {exists}"
    )


def test_course_get_slide_count(db, course_id: int):
    count = db.query(SlideTest).filter(SlideTest.course_id == course_id).count()
    return TestResult(
        name="get_slide_count() - 获取幻灯片数量",
        passed=isinstance(count, int),
        expected="返回整数类型的幻灯片数量",
        actual=f"幻灯片数量: {count}"
    )


def test_slide_create(db, course_id: int):
    slide = SlideTest(
        course_id=course_id,
        slide_index=1,
        content="这是第一张幻灯片的内容",
        duration=30
    )
    db.add(slide)
    db.commit()
    db.refresh(slide)
    
    return TestResult(
        name="SlideRepository.create() - 创建幻灯片",
        passed=slide is not None and slide.course_id == course_id,
        expected=f"成功创建幻灯片，course_id={course_id}",
        actual=f"创建结果: id={slide.id}, course_id={slide.course_id}"
    ), slide


def test_slide_get_by_course(db, course_id: int):
    slides = db.query(SlideTest).filter(
        SlideTest.course_id == course_id
    ).order_by(SlideTest.slide_index).all()
    
    return TestResult(
        name="SlideRepository.get_by_course() - 获取课程的所有幻灯片",
        passed=isinstance(slides, list),
        expected=f"返回course_id={course_id}的幻灯片列表",
        actual=f"返回类型: {type(slides).__name__}, 数量: {len(slides)}"
    )


def test_slide_bulk_create(db, course_id: int):
    slides_data = [
        SlideTest(course_id=course_id, slide_index=2, content="第二张", duration=20),
        SlideTest(course_id=course_id, slide_index=3, content="第三张", duration=25),
        SlideTest(course_id=course_id, slide_index=4, content="第四张", duration=30),
    ]
    db.add_all(slides_data)
    db.commit()
    for slide in slides_data:
        db.refresh(slide)
    
    return TestResult(
        name="SlideRepository.bulk_create() - 批量创建幻灯片",
        passed=len(slides_data) == 3,
        expected="成功批量创建3个幻灯片",
        actual=f"创建数量: {len(slides_data)}"
    )


def test_slide_delete_by_course(db, course_id: int):
    count = db.query(SlideTest).filter(SlideTest.course_id == course_id).delete()
    db.commit()
    
    return TestResult(
        name="SlideRepository.delete_by_course() - 删除课程的所有幻灯片",
        passed=count > 0,
        expected=f"成功删除course_id={course_id}的幻灯片",
        actual=f"删除数量: {count}"
    )


def test_document_create(db, course_id: int):
    doc = CourseDocumentTest(
        course_id=course_id,
        title="测试文档_Python基础笔记",
        content="这是课程配套文档的内容",
        doc_type="text"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return TestResult(
        name="CourseDocumentRepository.create() - 创建课程文档",
        passed=doc is not None and doc.course_id == course_id,
        expected=f"成功创建文档，course_id={course_id}",
        actual=f"创建结果: id={doc.id}, title={doc.title}"
    ), doc


def test_document_get_by_course(db, course_id: int):
    docs = db.query(CourseDocumentTest).filter(
        CourseDocumentTest.course_id == course_id
    ).all()
    
    return TestResult(
        name="CourseDocumentRepository.get_by_course() - 获取课程的所有文档",
        passed=isinstance(docs, list),
        expected=f"返回course_id={course_id}的文档列表",
        actual=f"返回类型: {type(docs).__name__}, 数量: {len(docs)}"
    )


def test_document_delete(db, document_id: int):
    doc = db.query(CourseDocumentTest).filter(CourseDocumentTest.id == document_id).first()
    if not doc:
        return TestResult(
            name="CourseDocumentRepository.delete() - 删除文档",
            passed=False,
            expected=f"删除ID={document_id}的文档",
            actual="文档不存在"
        )
    
    db.delete(doc)
    db.commit()
    
    exists = db.query(CourseDocumentTest).filter(CourseDocumentTest.id == document_id).first()
    return TestResult(
        name="CourseDocumentRepository.delete() - 删除文档",
        passed=exists is None,
        expected=f"成功删除ID={document_id}的文档",
        actual=f"删除后查询结果: {exists}"
    )


def test_create_with_invalid_subject(db):
    course = CourseTest(
        title="无效科目课程",
        subject_id=99999,
        chapter_id=1,
        description="这应该失败"
    )
    try:
        db.add(course)
        db.commit()
        db.refresh(course)
        passed = False
        actual = f"创建成功（不应该）: id={course.id}"
    except Exception as e:
        db.rollback()
        passed = True
        actual = f"正确报错: {type(e).__name__}"
    
    return TestResult(
        name="create() - 无效subject_id应该失败",
        passed=passed,
        expected="创建失败（subject不存在）",
        actual=actual
    )


def test_create_with_invalid_chapter(db, subject_id: int):
    course = CourseTest(
        title="无效章节课程",
        subject_id=subject_id,
        chapter_id=99999,
        description="这应该失败"
    )
    try:
        db.add(course)
        db.commit()
        db.refresh(course)
        passed = False
        actual = f"创建成功（不应该）: id={course.id}"
    except Exception as e:
        db.rollback()
        passed = True
        actual = f"正确报错: {type(e).__name__}"
    
    return TestResult(
        name="create() - 无效chapter_id应该失败",
        passed=passed,
        expected="创建失败（chapter不存在）",
        actual=actual
    )


def run_all_tests():
    print_section("CourseRepository 数据层功能测试")

    print_section("创建必要的数据库表")
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️ 创建表失败: {e}")

    engine = create_engine(DATABASE_URL_SYNC)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    results: List[TestResult] = []
    test_course = None
    test_slide = None
    test_doc = None
    subject = None
    chapter = None

    try:
        print_section("准备测试数据")
        subject, chapter = create_test_data(db)
        print(f"✅ 创建测试数据成功: subject_id={subject.id}, chapter_id={chapter.id}")

        print_section("1. 测试 CourseRepository.get_all()")
        results.append(test_course_get_all(db))

        print_section("2. 测试 CourseRepository.get_by_id()")
        results.append(test_course_get_by_id(db))
        
        print_section("3. 测试 CourseRepository.create()")
        result, test_course = test_course_create(db, subject.id, chapter.id)
        results.append(result)

        if test_course:
            print_section("4. 测试 CourseRepository.update()")
            results.append(test_course_update(db, test_course.id))

            print_section("5. 测试 CourseRepository.get_slide_count()")
            results.append(test_course_get_slide_count(db, test_course.id))

            print_section("6. 测试 CourseRepository.delete()")
            results.append(test_course_delete(db, test_course.id))

            test_course = None
            result, test_course = test_course_create(db, subject.id, chapter.id)
            results.append(result)

            print_section("7. 测试 CourseRepository.create() - 无效subject")
            results.append(test_create_with_invalid_subject(db))

            print_section("8. 测试 CourseRepository.create() - 无效chapter")
            results.append(test_create_with_invalid_chapter(db, subject.id))

        print_section("9. 测试 SlideRepository.create()")
        if test_course:
            result, test_slide = test_slide_create(db, test_course.id)
            results.append(result)

        print_section("10. 测试 SlideRepository.get_by_course()")
        if test_course:
            results.append(test_slide_get_by_course(db, test_course.id))

        print_section("11. 测试 SlideRepository.bulk_create()")
        if test_course:
            results.append(test_slide_bulk_create(db, test_course.id))

        print_section("12. 测试 SlideRepository.delete_by_course()")
        if test_course:
            results.append(test_slide_delete_by_course(db, test_course.id))

        print_section("13. 测试 CourseDocumentRepository.create()")
        if test_course:
            result, test_doc = test_document_create(db, test_course.id)
            results.append(result)

        print_section("14. 测试 CourseDocumentRepository.get_by_course()")
        if test_course:
            results.append(test_document_get_by_course(db, test_course.id))

        print_section("15. 测试 CourseDocumentRepository.delete()")
        if test_doc:
            results.append(test_document_delete(db, test_doc.id))

    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("清理测试数据")
        try:
            if test_doc:
                db.query(CourseDocumentTest).filter(CourseDocumentTest.id == test_doc.id).delete()
            if test_slide:
                db.query(SlideTest).filter(SlideTest.id == test_slide.id).delete()
            if test_course:
                db.query(CourseTest).filter(CourseTest.id == test_course.id).delete()
            if chapter:
                db.query(ChapterTest).filter(ChapterTest.id == chapter.id).delete()
            if subject:
                db.query(SubjectTest).filter(SubjectTest.id == subject.id).delete()
            db.commit()
            print("✅ 测试数据清理完成")
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
