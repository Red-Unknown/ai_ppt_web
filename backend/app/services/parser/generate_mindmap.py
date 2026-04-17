#!/usr/bin/env python3
"""
根据out_put.txt内容调用DeepSeek推理模型生成树状思维导图
"""
import os
import json
import sys
from pathlib import Path

# 添加backend到路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")

# 检查环境变量
api_key = os.getenv("DEEPSEEK_API_KEY", "")
print(f"API Key是否存在: {bool(api_key)}")
print(f"API Key长度: {len(api_key)}")

if not api_key:
    print("错误: 请设置DEEPSEEK_API_KEY环境变量")
    print("示例: $env:DEEPSEEK_API_KEY='your-api-key'")
    sys.exit(1)

base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 读取out_put.txt内容
output_file = Path("d:/ai_ppt_web/out_put.txt")
if not output_file.exists():
    print(f"错误: 文件不存在 {output_file}")
    sys.exit(1)

content = output_file.read_text(encoding='utf-8')
print(f"已读取文件，内容长度: {len(content)} 字符")
print(f"文件前500字符:\n{content[:500]}\n...")

# 导入依赖
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    print("✅ 依赖导入成功")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)

# 初始化DeepSeek客户端（使用推理模型）
print(f"\n正在初始化DeepSeek客户端...")
print(f"模型: deepseek-reasoner")
print(f"Base URL: {base_url}")

llm = ChatOpenAI(
    model="deepseek-reasoner",
    api_key=api_key,
    base_url=base_url,
    temperature=0.3,
    max_tokens=4000,
)

# 系统提示词
system_prompt = """你是一个专业的教育内容分析专家。你的任务是根据提供的课程讲义内容，分析其知识结构并生成树状思维导图。

要求：
1. 提取核心主题作为根节点
2. 识别主要章节作为一级子节点
3. 提取每个章节的关键概念、公式、原理作为二级及以下子节点
4. 保持内容的逻辑层次关系
5. 输出标准JSON格式，符合以下结构：

{
  "root": {
    "name": "主题名称",
    "children": [
      {
        "name": "章节1",
        "children": [
          {"name": "概念1"},
          {"name": "概念2", "children": [{"name": "子概念"}]}
        ]
      }
    ]
  }
}

注意：
- 只输出JSON，不要有任何其他文字说明
- 确保JSON格式完整且可解析
- 节点名称要简洁明了
- 保持与原文内容的对应关系"""

# 用户提示词 - 分段处理避免token超限
content_segment = content[:12000]  # 限制长度
user_prompt = f"""请分析以下材料力学课程讲义（第二章 轴向拉伸与压缩），生成树状思维导图JSON：

{content_segment}

请生成完整的思维导图JSON结构。只输出JSON，不要其他文字。"""

print("\n正在调用DeepSeek推理模型...")
print("这可能需要一些时间，请等待...")

# 调用模型
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_prompt)
]

try:
    response = llm.invoke(messages)
    result = response.content
    
    print(f"\n✅ 模型调用成功！")
    print(f"响应长度: {len(result)} 字符")
    print(f"\n模型响应前1000字符:\n{result[:1000]}\n...")
    
    # 提取JSON部分
    json_start = result.find('{')
    json_end = result.rfind('}')
    
    if json_start != -1 and json_end != -1:
        json_str = result[json_start:json_end+1]
        print(f"\n提取的JSON长度: {len(json_str)} 字符")
        
        mind_map_data = json.loads(json_str)
        
        # 保存到文件
        output_path = Path("d:/ai_ppt_web/mind_map.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mind_map_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 思维导图已生成: {output_path}")
        print(f"\n完整内容预览:")
        print(json.dumps(mind_map_data, ensure_ascii=False, indent=2))
    else:
        print("❌ 错误: 无法从响应中提取JSON")
        print("完整响应:", result)
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
