# 后端日志系统使用规范

## 📋 快速入门

### 1. 基本用法

在任意模块中使用日志系统：

```python
from backend.app.core.logging_config import get_logger

logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("业务操作记录")
logger.warning("潜在问题警告")
logger.error("业务错误")
logger.critical("系统级严重错误")
```

### 2. 日志级别标准

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| **DEBUG** | 详细调试信息 | `logger.debug(f"Processing user {user_id}")` |
| **INFO** | 业务操作记录 | `logger.info("User login successful")` |
| **WARNING** | 潜在问题警告 | `logger.warning("API response time exceeded threshold")` |
| **ERROR** | 业务错误 | `logger.error("Database connection failed", exc_info=True)` |
| **CRITICAL** | 系统级严重错误 | `logger.critical("System running out of memory")` |

### 3. 结构化日志格式

所有日志自动包含以下信息：
- 时间戳
- 模块名称
- 日志级别
- 自定义消息
- 文件名和行号

示例输出：
```
2026-02-28 14:30:25,123 - app.services.qa.service - INFO - QA service initialized successfully [service.py:45]
```

## 🎯 最佳实践

### 1. 错误日志记录

```python
try:
    # 业务代码
    result = some_operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
    # exc_info=True 会自动记录完整的堆栈跟踪
```

### 2. 带上下文的日志

```python
# 好的做法：包含上下文信息
logger.info(f"Processing order {order_id} for user {user_id}")

# 不好的做法：信息不完整
logger.info("Processing order")
```

### 3. 性能监控日志

```python
import time

def expensive_operation():
    start_time = time.time()
    
    # 执行操作
    result = do_something()
    
    elapsed_time = (time.time() - start_time) * 1000  # 毫秒
    logger.info(f"Operation completed in {elapsed_time:.2f}ms")
    
    return result
```

## 📁 日志文件管理

### 文件位置
所有日志文件存储在：`f:\college\sophomore\服务外包\log\`

### 文件轮转策略
- **app.log**: 主日志文件，最大10MB，保留5个备份
- **error.log**: 错误日志文件，最大5MB，保留3个备份

### 查看日志
```bash
# 查看实时日志
tail -f f:\college\sophomore\服务外包\log\app.log

# 查看错误日志
tail -f f:\college\sophomore\服务外包\log\error.log
```

## 🔧 配置说明

### 环境变量配置
在 `.env` 文件中可以配置：

```bash
# 调试模式（启用DEBUG级别和控制台输出）
DEBUG=true

# 默认日志级别
LOG_LEVEL=INFO

# 日志文件大小限制（MB）
LOG_FILE_MAX_SIZE=10

# 备份文件数量
LOG_BACKUP_COUNT=5
```

### 开发环境 vs 生产环境
- **开发环境**: 启用DEBUG级别，同时在控制台和文件输出
- **生产环境**: 仅INFO级别，只输出到文件

## 🚨 常见问题

### Q: 日志文件太大怎么办？
A: 系统会自动轮转，保留最近的几个备份文件

### Q: 如何查看特定模块的日志？
A: 使用grep命令过滤：
```bash
grep "app.services.qa" f:\college\sophomore\服务外包\log\app.log
```

### Q: 日志没有输出？
A: 检查：
1. 日志目录是否存在且有写入权限
2. 环境变量配置是否正确
3. 日志级别是否设置过高

## 📝 代码示例

### 完整的使用示例

```python
from backend.app.core.logging_config import get_logger

logger = get_logger(__name__)

class UserService:
    def create_user(self, user_data):
        try:
            logger.info(f"Creating user with email: {user_data['email']}")
            
            # 验证数据
            self._validate_user_data(user_data)
            
            # 创建用户
            user = User.create(**user_data)
            
            logger.info(f"User created successfully: {user.id}")
            return user
            
        except ValidationError as e:
            logger.warning(f"User data validation failed: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}", exc_info=True)
            raise
```

遵循这些规范，可以确保日志系统的一致性和可维护性。