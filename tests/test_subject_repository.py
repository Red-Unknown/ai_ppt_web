import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL_SYNC = "postgresql://postgres:yaoshun2006@10.0.0.4:5432/ai_ppt_web"


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


def test_subject_get_all(repo):
    result = repo.get_all()
    return TestResult(
        name="SubjectRepository.get_all() - 获取科目列表",
        passed=isinstance(result, list),
        expected="返回科目列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}",
        details=f"当前数据库共有 {len(result)} 个科目"
    )


def test_subject_get_by_id(repo, subject_id: int):
    result = repo.get_by_id(subject_id)
    return TestResult(
        name=f"SubjectRepository.get_by_id() - 根据ID={subject_id}查询科目",
        passed=result is not None and result.id == subject_id,
        expected=f"返回ID={subject_id}的科目",
        actual=f"返回: {result}"
    )


def test_subject_get_by_nonexistent_id(repo):
    nonexistent_id = 999999
    result = repo.get_by_id(nonexistent_id)
    return TestResult(
        name=f"SubjectRepository.get_by_id() - 查询不存在的ID={nonexistent_id}",
        passed=result is None,
        expected="返回None（ID不存在）",
        actual=f"返回: {result}"
    )


def test_subject_create(repo, test_name: str):
    result = repo.create(test_name)
    return TestResult(
        name="SubjectRepository.create() - 创建科目",
        passed=result is not None and result.name == test_name,
        expected=f"成功创建科目: name={test_name}",
        actual=f"创建结果: id={result.id}, name={result.name}"
    ), result


def test_subject_update(repo, subject_id: int, new_name: str):
    result = repo.update(subject_id, new_name)
    return TestResult(
        name=f"SubjectRepository.update() - 更新科目ID={subject_id}",
        passed=result is not None and result.name == new_name,
        expected=f"成功更新科目名称为: {new_name}",
        actual=f"更新结果: id={result.id}, name={result.name}"
    )


def test_subject_delete(repo, db, subject_id: int):
    try:
        result = repo.delete(subject_id)
        exists = repo.get_by_id(subject_id)
        return TestResult(
            name=f"SubjectRepository.delete() - 删除科目ID={subject_id}",
            passed=result is True and exists is None,
            expected=f"成功删除ID={subject_id}的科目",
            actual=f"删除操作返回: {result}, 删除后查询结果: {exists}"
        )
    except Exception as e:
        return TestResult(
            name=f"SubjectRepository.delete() - 删除科目ID={subject_id}",
            passed=False,
            expected=f"成功删除ID={subject_id}的科目",
            actual=f"删除失败: {type(e).__name__}: {str(e)[:100]}"
        )


def test_chapter_get_by_subject(repo, subject_id: int):
    result = repo.get_by_subject(subject_id)
    return TestResult(
        name=f"ChapterRepository.get_by_subject() - 根据subject_id={subject_id}获取章节列表",
        passed=isinstance(result, list),
        expected=f"返回subject_id={subject_id}的章节列表 (list)",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}"
    )


def test_chapter_get_by_nonexistent_subject(repo):
    nonexistent_id = 999999
    result = repo.get_by_subject(nonexistent_id)
    return TestResult(
        name=f"ChapterRepository.get_by_subject() - 查询不存在科目的章节",
        passed=isinstance(result, list) and len(result) == 0,
        expected="返回空列表",
        actual=f"返回类型: {type(result).__name__}, 数量: {len(result)}"
    )


def test_chapter_get_by_id(repo, chapter_id: int):
    result = repo.get_by_id(chapter_id)
    return TestResult(
        name=f"ChapterRepository.get_by_id() - 根据ID={chapter_id}查询章节",
        passed=result is not None and result.id == chapter_id,
        expected=f"返回ID={chapter_id}的章节",
        actual=f"返回: {result}"
    )


def test_chapter_get_by_nonexistent_id(repo):
    nonexistent_id = 999999
    result = repo.get_by_id(nonexistent_id)
    return TestResult(
        name=f"ChapterRepository.get_by_id() - 查询不存在的章节ID={nonexistent_id}",
        passed=result is None,
        expected="返回None（ID不存在）",
        actual=f"返回: {result}"
    )


def test_chapter_create(repo, subject_id: int, test_name: str, order: int = 0):
    result = repo.create(subject_id, test_name, order)
    return TestResult(
        name=f"ChapterRepository.create() - 创建章节",
        passed=result is not None and result.name == test_name and result.subject_id == subject_id,
        expected=f"成功创建章节: name={test_name}, subject_id={subject_id}, order={order}",
        actual=f"创建结果: id={result.id}, name={result.name}, subject_id={result.subject_id}, order={result.order}"
    ), result


def test_chapter_create_with_invalid_subject(repo):
    nonexistent_subject_id = 999999
    result = repo.create(nonexistent_subject_id, "无效章节", 1)
    return TestResult(
        name="ChapterRepository.create() - 无效subject_id创建章节",
        passed=result is None,
        expected="创建失败（subject不存在）",
        actual=f"返回: {result}"
    )


def test_chapter_update(repo, chapter_id: int, new_name: str, new_order: int):
    result = repo.update(chapter_id, new_name, new_order)
    return TestResult(
        name=f"ChapterRepository.update() - 更新章节ID={chapter_id}",
        passed=result is not None and result.name == new_name and result.order == new_order,
        expected=f"成功更新章节: name={new_name}, order={new_order}",
        actual=f"更新结果: id={result.id}, name={result.name}, order={result.order}"
    )


def test_chapter_update_partial(repo, chapter_id: int):
    result = repo.update(chapter_id, name="仅更新名称")
    return TestResult(
        name=f"ChapterRepository.update() - 部分更新章节ID={chapter_id}",
        passed=result is not None and result.name == "仅更新名称",
        expected="成功更新章节名称",
        actual=f"更新结果: id={result.id}, name={result.name}, order={result.order}"
    )


def test_chapter_delete(repo, chapter_id: int):
    try:
        result = repo.delete(chapter_id)
        exists = repo.get_by_id(chapter_id)
        return TestResult(
            name=f"ChapterRepository.delete() - 删除章节ID={chapter_id}",
            passed=result is True and exists is None,
            expected=f"成功删除ID={chapter_id}的章节",
            actual=f"删除操作返回: {result}, 删除后查询结果: {exists}"
        )
    except Exception as e:
        return TestResult(
            name=f"ChapterRepository.delete() - 删除章节ID={chapter_id}",
            passed=False,
            expected=f"成功删除ID={chapter_id}的章节",
            actual=f"删除失败: {type(e).__name__}: {str(e)[:100]}"
        )


def run_all_tests():
    print_section("SubjectRepository 和 ChapterRepository 数据层功能测试")

    engine = create_engine(DATABASE_URL_SYNC)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from backend.app.repositories.subject_repository import SubjectRepository, ChapterRepository
    db = SessionLocal()

    subject_repo = SubjectRepository(db)
    chapter_repo = ChapterRepository(db)

    results: List[TestResult] = []
    test_subject = None
    test_chapter = None

    def cleanup_using_sql(subject_id: int = None, chapter_id: int = None):
        with engine.connect() as conn:
            if chapter_id:
                conn.execute(text("DELETE FROM chapters WHERE id = :chapter_id"), {"chapter_id": chapter_id})
                conn.commit()
            if subject_id:
                conn.execute(text("DELETE FROM chapters WHERE subject_id = :subject_id"), {"subject_id": subject_id})
                conn.execute(text("DELETE FROM subjects WHERE id = :subject_id"), {"subject_id": subject_id})
                conn.commit()

    try:
        print_section("1. 测试 SubjectRepository.get_all()")
        results.append(test_subject_get_all(subject_repo))

        print_section("2. 测试 SubjectRepository.get_by_id()")
        all_subjects = subject_repo.get_all()
        if all_subjects:
            test_subject_for_get = all_subjects[0]
            results.append(test_subject_get_by_id(subject_repo, test_subject_for_get.id))
        results.append(test_subject_get_by_nonexistent_id(subject_repo))

        print_section("3. 测试 SubjectRepository.create()")
        result, test_subject = test_subject_create(subject_repo, "测试科目_Python基础")
        results.append(result)

        print_section("4. 测试 SubjectRepository.update()")
        if test_subject:
            results.append(test_subject_update(subject_repo, test_subject.id, "测试科目_Python基础_更新版"))

        print_section("5. 测试 SubjectRepository.delete()")
        if test_subject:
            subject_id_to_delete = test_subject.id
            results.append(test_subject_delete(subject_repo, db, subject_id_to_delete))
            test_subject = None

        print_section("6. 测试 SubjectRepository - 重新创建用于后续测试")
        result, test_subject = test_subject_create(subject_repo, "测试科目_数学")
        results.append(result)

        print_section("7. 测试 ChapterRepository.get_by_subject()")
        if test_subject:
            results.append(test_chapter_get_by_subject(chapter_repo, test_subject.id))
        results.append(test_chapter_get_by_nonexistent_subject(chapter_repo))

        print_section("8. 测试 ChapterRepository.get_by_id()")
        all_chapters = chapter_repo.get_by_subject(test_subject.id) if test_subject else []
        if all_chapters:
            test_chapter_for_get = all_chapters[0]
            results.append(test_chapter_get_by_id(chapter_repo, test_chapter_for_get.id))
        results.append(test_chapter_get_by_nonexistent_id(chapter_repo))

        print_section("9. 测试 ChapterRepository.create()")
        if test_subject:
            result, test_chapter = test_chapter_create(chapter_repo, test_subject.id, "测试章节_代数", 1)
            results.append(result)

        print_section("10. 测试 ChapterRepository.create() - 无效subject_id")
        results.append(test_chapter_create_with_invalid_subject(chapter_repo))

        print_section("11. 测试 ChapterRepository.update()")
        if test_chapter:
            results.append(test_chapter_update(chapter_repo, test_chapter.id, "测试章节_代数_更新版", 2))

        print_section("12. 测试 ChapterRepository.update() - 部分更新")
        if test_chapter:
            original_order = test_chapter.order
            results.append(test_chapter_update_partial(chapter_repo, test_chapter.id))

        print_section("13. 测试 ChapterRepository.delete()")
        if test_chapter:
            chapter_id_to_delete = test_chapter.id
            results.append(test_chapter_delete(chapter_repo, chapter_id_to_delete))
            test_chapter = None

    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("清理测试数据")
        try:
            if test_chapter:
                chapter_repo.delete(test_chapter.id)
            if test_subject:
                cleanup_using_sql(subject_id=test_subject.id)
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
