import psycopg2
import json
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    "host": "10.0.0.4",
    "port": 5432,
    "user": "postgres",
    "password": "yaoshun2006",
    "database": "ai_ppt_web"
}

# 测试数据
TEST_DATA = {
    # 用户表
    "users": [
        {
            "user_id": "student_001",
            "school_id": "school_001",
            "grade": "大一",
            "major": "物理学",
            "phone_number": "13800138001",
            "user_name": "张三",
            "role": "student"
        },
        {
            "user_id": "teacher_001",
            "school_id": "school_001",
            "grade": "教师",
            "major": "物理学",
            "phone_number": "13900139001",
            "user_name": "李老师",
            "role": "teacher"
        }
    ],
    # 课程分类表
    "course_categories": [
        {
            "school_id": "school_001",
            "category_name": "自然科学",
            "sort_order": 1
        }
    ],
    # 课程表
    "courses": [
        {
            "course_id": "course_001",
            "school_id": "school_001",
            "category_id": 1,
            "course_name": "大学物理",
            "teacher_id": "teacher_001",
            "term": "2024秋"
        }
    ],
    # 课件表
    "lessons": [
        {
            "lesson_id": "lesson_001",
            "course_id": "course_001",
            "school_id": "school_001",
            "title": "质点运动学",
            "cover_image": "https://example.com/cover/lesson_001.jpg",
            "file_type": "pptx",
            "file_url": "https://example.com/files/lesson_001.pptx",
            "category": "physics",
            "task_status": "completed"
        },
        {
            "lesson_id": "lesson_002",
            "course_id": "course_001",
            "school_id": "school_001",
            "title": "牛顿运动定律",
            "cover_image": "https://example.com/cover/lesson_002.jpg",
            "file_type": "pptx",
            "file_url": "https://example.com/files/lesson_002.pptx",
            "category": "physics",
            "task_status": "completed"
        }
    ],
    # CIR节点表
    "cir_sections": [
        {
            "node_id": "node_001",
            "lesson_id": "lesson_001",
            "school_id": "school_001",
            "node_name": "课程概述",
            "node_type": "chapter",
            "sort_order": 1,
            "path": "/course/intro",
            "page_num": 1,
            "key_points": json.dumps(["课程介绍", "教学目标", "学习方法"]),
            "teaching_content": "本课程是《大学物理》，主要涵盖力学、热学、电磁学、光学和量子力学等基础内容。"
        },
        {
            "node_id": "node_002",
            "lesson_id": "lesson_001",
            "school_id": "school_001",
            "node_name": "质点运动学",
            "parent_id": "node_001",
            "node_type": "subchapter",
            "sort_order": 2,
            "path": "/course/intro/kinematics",
            "page_num": 5,
            "key_points": json.dumps(["位移", "速度", "加速度"]),
            "teaching_content": "质点运动学主要研究质点的位置、速度和加速度随时间的变化关系。"
        },
        {
            "node_id": "node_003",
            "lesson_id": "lesson_002",
            "school_id": "school_001",
            "node_name": "牛顿第一定律",
            "parent_id": None,
            "node_type": "subchapter",
            "sort_order": 1,
            "path": "/course/newton/first",
            "page_num": 10,
            "key_points": json.dumps(["惯性", "静止", "匀速直线运动"]),
            "teaching_content": "牛顿第一定律：一切物体在没有外力作用时，总保持静止或匀速直线运动状态。"
        },
        {
            "node_id": "node_004",
            "lesson_id": "lesson_002",
            "school_id": "school_001",
            "node_name": "牛顿第二定律",
            "parent_id": "node_003",
            "node_type": "point",
            "sort_order": 2,
            "path": "/course/newton/second",
            "page_num": 12,
            "key_points": json.dumps(["F=ma", "合外力", "加速度"]),
            "teaching_content": "牛顿第二定律：F=ma，合外力等于质量乘以加速度。"
        }
    ],
    # 学习进度表
    "learning_progress": [
        {
            "track_id": "track_001",
            "user_id": "student_001",
            "session_id": "session_001",
            "school_id": "school_001",
            "lesson_id": "lesson_001",
            "current_node_id": "node_002",
            "current_path": "/course/intro/kinematics",
            "current_topic": "质点运动学",
            "last_qa_query": "什么是位移",
            "confusion_count": 0,
            "mastery": json.dumps({"位移": 0.8, "速度": 0.6}),
            "last_position_seconds": 120,
            "progress_percent": 35.0,
            "adjust_type": "normal",
            "needs_supplement": False
        }
    ],
    # 问答记录表
    "qa_records": [
        {
            "session_id": "session_001",
            "user_id": "student_001",
            "school_id": "school_001",
            "lesson_id": "lesson_001",
            "question_type": "FACTOID",
            "question_text": "什么是位移",
            "answer_text": "位移是描述质点位置变化的物理量，等于终点位置减初始位置，是矢量。",
            "cited_node_id": "node_002",
            "source_page_num": 5,
            "sources": json.dumps([
                {
                    "node_id": "node_002",
                    "content": "位移是描述质点位置变化的物理量",
                    "path": "/course/intro/kinematics",
                    "relevance_score": 0.95,
                    "page_num": 5
                }
            ]),
            "current_path": "/course/intro/kinematics",
            "video_timestamp": 120.5,
            "understanding_level": "understood",
            "response_ms": 1500,
            "is_accurate": True,
            "reasoning_content": None,
            "tool_calls": None
        }
    ]
}

def connect_db():
    """连接数据库"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ 成功连接到数据库: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def insert_data(conn, table_name, data_list):
    """插入数据"""
    if not data_list:
        print(f"⚠️ {table_name} 没有数据需要插入")
        return True

    cursor = conn.cursor()

    for data in data_list:
        try:
            # 构建INSERT语句
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

            cursor.execute(sql, list(data.values()))
            print(f"✅ 插入 {table_name} 成功: {data.get(list(data.keys())[0])}")
        except Exception as e:
            print(f"❌ 插入 {table_name} 失败: {e}")
            print(f"   数据: {data}")
            conn.rollback()
            return False

    conn.commit()
    cursor.close()
    return True

def main():
    print("=" * 60)
    print("开始写入测试数据...")
    print("=" * 60)

    # 连接数据库
    conn = connect_db()
    if not conn:
        return

    try:
        # 1. 插入用户
        print("\n[1] 插入用户数据...")
        insert_data(conn, "users", TEST_DATA["users"])

        # 2. 插入课程分类
        print("\n[2] 插入课程分类数据...")
        insert_data(conn, "course_categories", TEST_DATA["course_categories"])

        # 3. 插入课程
        print("\n[3] 插入课程数据...")
        insert_data(conn, "courses", TEST_DATA["courses"])

        # 4. 插入课件
        print("\n[4] 插入课件数据...")
        insert_data(conn, "lessons", TEST_DATA["lessons"])

        # 5. 插入CIR节点
        print("\n[5] 插入CIR节点数据...")
        insert_data(conn, "cir_sections", TEST_DATA["cir_sections"])

        # 6. 插入学习进度
        print("\n[6] 插入学习进度数据...")
        insert_data(conn, "learning_progress", TEST_DATA["learning_progress"])

        # 7. 插入问答记录
        print("\n[7] 插入问答记录数据...")
        insert_data(conn, "qa_records", TEST_DATA["qa_records"])

        print("\n" + "=" * 60)
        print("✅ 所有测试数据写入完成！")
        print("=" * 60)

        # 验证数据
        cursor = conn.cursor()
        for table in TEST_DATA.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} 条记录")

        cursor.close()

    except Exception as e:
        print(f"❌ 写入数据时发生错误: {e}")
    finally:
        conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()
