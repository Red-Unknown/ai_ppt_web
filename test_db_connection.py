import psycopg2

try:
    # 尝试连接到数据库
    conn = psycopg2.connect(
        host="10.0.0.4",
        port="5432",
        database="A12database",
        user="postgres",
        password="yaoshun2006"
    )
    
    # 创建游标
    cur = conn.cursor()
    
    # 执行简单查询
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"成功连接到数据库！")
    print(f"PostgreSQL版本: {version[0]}")
    
    # 关闭游标和连接
    cur.close()
    conn.close()
    
    print("数据库连接测试成功！")
    
except Exception as e:
    print(f"数据库连接失败: {str(e)}")
    print("请检查网络连接和数据库配置是否正确。")
