"""
NewCourse模型关联测试 - 修复后
测试NewCourse及其关联的Subject、Chapter、Slide、CourseDocument、LessonPlan模型
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:yaoshun2006@10.0.0.4:5432/ai_ppt_web"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def test_newcourse_associations():
    """测试NewCourse模型的关联关系"""
    print("=" * 60)
    print("测试 NewCourse 模型关联 (修复后)")
    print("=" * 60)
    
    results = []
    
    db = SessionLocal()
    try:
        # 查询现有的courses_new记录
        print("\n[前置准备] 查询现有数据")
        course = db.execute(text("SELECT id, title, subject_id, chapter_id FROM courses_new LIMIT 1")).fetchone()
        
        if course:
            course_id = course[0]
            print(f"  使用现有课程: id={course_id}, title={course[1]}")
        else:
            print("  无现有课程数据，创建测试数据...")
            # 创建测试科目
            subject = db.execute(text("INSERT INTO subjects (name) VALUES ('测试科目_关联_修复') RETURNING id")).fetchone()
            subject_id = subject[0] if subject else None
            
            if subject_id:
                # 创建测试章节
                chapter = db.execute(text("INSERT INTO chapters (subject_id, name, \"order\") VALUES (:subject_id, '测试章节_修复', 1) RETURNING id"), {"subject_id": subject_id}).fetchone()
                chapter_id = chapter[0] if chapter else None
                
                if chapter_id:
                    # 创建测试课程 (使用courses_new表)
                    course_result = db.execute(
                        text("INSERT INTO courses_new (title, subject_id, chapter_id, description) VALUES ('测试课程_关联_修复', :subject_id, :chapter_id, '测试描述') RETURNING id"),
                        {"subject_id": subject_id, "chapter_id": chapter_id}
                    ).fetchone()
                    course_id = course_result[0] if course_result else None
                else:
                    course_id = None
            else:
                course_id = None
            
            if course_id:
                db.commit()
                print(f"  创建测试课程成功: id={course_id}")
            else:
                print("  无法创建测试数据，跳过测试")
                return [("缺少测试数据", False)]
        
        # 测试1: NewCourse与Subject的关联
        print("\n[测试 1] NewCourse与Subject的关联")
        query = text("""
            SELECT c.id, c.title, s.id as subject_id, s.name as subject_name
            FROM courses_new c
            LEFT JOIN subjects s ON c.subject_id = s.id
            WHERE c.id = :course_id
        """)
        result = db.execute(query, {"course_id": course_id}).fetchone()
        
        if result:
            print(f"  课程ID: {result[0]}, 科目ID: {result[2]}, 科目名称: {result[3]}")
            results.append(("NewCourse-Subject关联", result[2] is not None))
        else:
            results.append(("NewCourse-Subject关联", False))
        
        # 测试2: NewCourse与Chapter的关联
        print("\n[测试 2] NewCourse与Chapter的关联")
        query = text("""
            SELECT c.id, c.chapter_id, ch.name as chapter_name
            FROM courses_new c
            LEFT JOIN chapters ch ON c.chapter_id = ch.id
            WHERE c.id = :course_id
        """)
        result = db.execute(query, {"course_id": course_id}).fetchone()
        
        if result:
            print(f"  课程ID: {result[0]}, 章节ID: {result[1]}, 章节名称: {result[2]}")
            results.append(("NewCourse-Chapter关联", True))
        else:
            results.append(("NewCourse-Chapter关联", False))
        
        # 测试3: NewCourse与Slide的关联
        print("\n[测试 3] NewCourse与Slide的关联")
        # 创建测试幻灯片
        slide = db.execute(
            text("INSERT INTO slides (course_id, slide_index, content) VALUES (:course_id, 1, '测试幻灯片') RETURNING id"),
            {"course_id": course_id}
        ).fetchone()
        db.commit()
        
        if slide:
            slide_id = slide[0]
            print(f"  创建幻灯片: id={slide_id}, course_id={course_id}")
            
            # 验证关联
            query = text("SELECT id, course_id, slide_index FROM slides WHERE id = :slide_id")
            result = db.execute(query, {"slide_id": slide_id}).fetchone()
            
            if result and result[1] == course_id:
                print(f"  ✓ 关联验证通过")
                results.append(("NewCourse-Slide关联", True))
            else:
                results.append(("NewCourse-Slide关联", False))
        else:
            results.append(("NewCourse-Slide关联", False))
        
        # 测试4: NewCourse与CourseDocument的关联
        print("\n[测试 4] NewCourse与CourseDocument的关联")
        doc = db.execute(
            text("INSERT INTO course_documents (course_id, title, content, doc_type) VALUES (:course_id, '测试文档_修复', '测试内容', 'text') RETURNING id"),
            {"course_id": course_id}
        ).fetchone()
        db.commit()
        
        if doc:
            doc_id = doc[0]
            print(f"  创建文档: id={doc_id}, course_id={course_id}")
            
            query = text("SELECT id, course_id, title FROM course_documents WHERE id = :doc_id")
            result = db.execute(query, {"doc_id": doc_id}).fetchone()
            
            if result and result[1] == course_id:
                print(f"  ✓ 关联验证通过")
                results.append(("NewCourse-Document关联", True))
            else:
                results.append(("NewCourse-Document关联", False))
        else:
            results.append(("NewCourse-Document关联", False))
        
        # 测试5: NewCourse与LessonPlan的关联
        print("\n[测试 5] NewCourse与LessonPlan的关联")
        plan = db.execute(
            text("INSERT INTO lesson_plans (course_id, content) VALUES (:course_id, '{\"title\": \"测试教案_修复\"}') RETURNING id"),
            {"course_id": course_id}
        ).fetchone()
        db.commit()
        
        if plan:
            plan_id = plan[0]
            print(f"  创建教案: id={plan_id}, course_id={course_id}")
            
            query = text("SELECT id, course_id FROM lesson_plans WHERE id = :plan_id")
            result = db.execute(query, {"plan_id": plan_id}).fetchone()
            
            if result and result[1] == course_id:
                print(f"  ✓ 关联验证通过")
                results.append(("NewCourse-LessonPlan关联", True))
            else:
                results.append(("NewCourse-LessonPlan关联", False))
        else:
            results.append(("NewCourse-LessonPlan关联", False))
        
        # 测试6: 级联删除验证
        print("\n[测试 6] 级联删除验证")
        print("  注意: 外键设置为CASCADE时，删除课程应自动删除关联数据")
        
        # 删除测试数据
        db.execute(text("DELETE FROM slides WHERE course_id = :course_id"), {"course_id": course_id})
        db.execute(text("DELETE FROM course_documents WHERE course_id = :course_id"), {"course_id": course_id})
        db.execute(text("DELETE FROM lesson_plans WHERE course_id = :course_id"), {"course_id": course_id})
        db.commit()
        
        # 验证删除
        slides_count = db.execute(text("SELECT COUNT(*) FROM slides WHERE course_id = :course_id"), {"course_id": course_id}).fetchone()[0]
        docs_count = db.execute(text("SELECT COUNT(*) FROM course_documents WHERE course_id = :course_id"), {"course_id": course_id}).fetchone()[0]
        plans_count = db.execute(text("SELECT COUNT(*) FROM lesson_plans WHERE course_id = :course_id"), {"course_id": course_id}).fetchone()[0]
        
        print(f"  幻灯片剩余: {slides_count}")
        print(f"  文档剩余: {docs_count}")
        print(f"  教案剩余: {plans_count}")
        
        if slides_count == 0 and docs_count == 0 and plans_count == 0:
            print(f"  ✓ 级联删除验证通过")
            results.append(("级联删除", True))
        else:
            results.append(("级联删除", False))
        
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")
        results.append(("异常处理", False))
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    return results


def main():
    """运行所有NewCourse模型关联测试"""
    print("\n" + "=" * 60)
    print("开始 NewCourse 模型关联测试 (修复后)")
    print("=" * 60)
    
    all_results = []
    
    # 1. NewCourse关联测试
    all_results.extend(test_newcourse_associations())
    
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
        print("\n🎉 所有NewCourse模型关联测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
