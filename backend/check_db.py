from app.core.database import engine
from sqlalchemy import inspect

# 创建数据库检查器
inspector = inspect(engine)

# 获取数据库中的表
print('Tables in database:', inspector.get_table_names())

# 检查users表
print('\nUsers table columns:')
if 'users' in inspector.get_table_names():
    print([c['name'] for c in inspector.get_columns('users')])
else:
    print('Users table does not exist')

# 检查courses表
print('\nCourses table columns:')
if 'courses' in inspector.get_table_names():
    print([c['name'] for c in inspector.get_columns('courses')])
else:
    print('Courses table does not exist')

# 检查其他可能的表
print('\nOther tables:')
for table in inspector.get_table_names():
    if table not in ['users', 'courses']:
        print(f'Table: {table}')
        print(f'Columns: {[c["name"] for c in inspector.get_columns(table)]}')
        print()
