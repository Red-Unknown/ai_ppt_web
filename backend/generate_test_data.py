import bcrypt
from app.core.database import get_db, User

# 生成测试数据
def generate_test_data():
    db = next(get_db())
    try:
        # 检查是否已有测试数据
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"数据库中已有 {existing_users} 个用户，跳过生成测试数据")
            return
        
        # 测试用户数据
        test_users = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "teacher",
                "name": "管理员",
                "phone": "13800138000",
                "teacher_id": "T000000"
            },
            {
                "username": "teacher1",
                "password": "Teacher123",
                "role": "teacher",
                "name": "张老师",
                "phone": "13800138001",
                "teacher_id": "T000001"
            },
            {
                "username": "student1",
                "password": "Student123",
                "role": "student",
                "name": "李同学",
                "phone": "13800138002",
                "student_id": "20240001"
            },
            {
                "username": "student2",
                "password": "Student123",
                "role": "student",
                "name": "王同学",
                "phone": "13800138003",
                "student_id": "20240002"
            }
        ]
        
        # 添加测试用户
        for user_data in test_users:
            # 哈希密码
            hashed_password = bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt()).decode()
            
            # 创建用户对象
            user = User(
                username=user_data["username"],
                password_hash=hashed_password,
                role=user_data["role"],
                name=user_data["name"],
                phone=user_data["phone"],
                student_id=user_data.get("student_id"),
                teacher_id=user_data.get("teacher_id")
            )
            
            db.add(user)
            print(f"添加测试用户: {user_data['username']} - {user_data['name']}")
        
        # 提交事务
        db.commit()
        print(f"成功添加 {len(test_users)} 个测试用户")
        
    except Exception as e:
        db.rollback()
        print(f"生成测试数据失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_data()
