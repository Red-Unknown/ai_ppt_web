"""
讲稿生成脚本 - 根据JSON课程内容生成讲稿并填充script_content字段
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
import argparse

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from backend.app.utils.llm_pool import initialize_pool, LLMPoolContext
from langchain_core.messages import HumanMessage, SystemMessage


SCRIPT_PROMPT_TEMPLATE = """请根据以下课程内容，为每个章节生成口语化的课堂讲稿。

要求：
1. 口语化表达，适合课堂讲授
2. 适当添加互动环节
3. 保持学术内容的准确性
4. 输出JSON数组，每个元素包含 "node_name" 和 "script_content" 字段

课程内容：
{content}

输出示例：
[{"node_name": "1.1 什么是人工智能", "script_content": "同学们好..."}]
"""


def log_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
        sys.stdout.flush()
    except UnicodeEncodeError:
        s = str(args[0]) if args else ''
        print(s.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
        sys.stdout.flush()


def call_llm(prompt: str) -> str:
    """使用LLM连接池调用模型"""
    try:
        with LLMPoolContext(model="qwen") as client:
            messages = [
                SystemMessage(content="你是一位经验丰富的教师，擅长将学术内容转化为生动有趣的课堂讲稿。"),
                HumanMessage(content=prompt)
            ]
            response = client.invoke(messages)
            return response.content
    except Exception as e:
        log_print(f"LLM调用错误: {e}")
        raise


def generate_prompt_for_all_sections(sections: list, lesson_name: str) -> str:
    """一次性生成所有章节的提示词"""
    content_parts = []
    content_parts.append(f"课程名称：{lesson_name}")
    content_parts.append(f"共有 {len(sections)} 个章节")

    for i, section in enumerate(sections):
        node_name = section.get('node_name', '')
        teaching_content = section.get('teaching_content', '') if section.get('teaching_content') else ''
        content_parts.append(f"\n章节{i+1}: {node_name}")
        if teaching_content:
            content_parts.append(f"内容: {teaching_content}")

    content = "\n".join(content_parts)
    prompt = SCRIPT_PROMPT_TEMPLATE.replace("{content}", content)
    return prompt


def process_lesson_json(input_file: str, output_file: str):
    """处理课程JSON文件，一次性生成所有讲稿"""
    log_print(f"\n处理文件: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lesson_data = json.load(f)
    except Exception as e:
        log_print(f"  [FAIL] 读取文件失败: {e}")
        return None

    lesson_name = lesson_data.get('lesson_name', '未知课程')
    sections = lesson_data.get('cir_sections', [])

    log_print(f"课程名称: {lesson_name}")
    log_print(f"章节节点数量: {len(sections)}")

    # 筛选出有教学内容的章节（只筛选subchapter类型）
    target_sections = [s for s in sections if s.get('teaching_content') and s.get('node_type') == 'subchapter']
    log_print(f"有教学内容的章节: {len(target_sections)} 个")

    if not target_sections:
        log_print("没有需要生成讲稿的章节")
        save_result(lesson_data, output_file)
        return output_file

    # 一次性生成所有章节的提示词
    prompt = generate_prompt_for_all_sections(target_sections, lesson_name)
    log_print(f"提示词长度: {len(prompt)} 字符")

    try:
        # 调用一次LLM生成所有讲稿
        llm_response = call_llm(prompt)
        log_print(f"LLM响应长度: {len(llm_response)} 字符")

        # 解析JSON响应
        json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
        if json_match:
            try:
                scripts_data = json.loads(json_match.group())
                log_print(f"解析到 {len(scripts_data)} 个讲稿")

                # 创建node_name到script_content的映射
                scripts_map = {}
                for item in scripts_data:
                    node_name = item.get('node_name', '')
                    script_content = item.get('script_content', '')
                    if node_name and script_content:
                        scripts_map[node_name] = script_content

                # 填充讲稿到原始sections中
                filled_count = 0
                for section in sections:
                    node_name = section.get('node_name', '')
                    if node_name in scripts_map:
                        section['script_content'] = scripts_map[node_name]
                        filled_count += 1

                log_print(f"成功填充: {filled_count}/{len(target_sections)} 个章节")
            except json.JSONDecodeError as e:
                log_print(f"JSON解析错误: {e}")
        else:
            log_print("未找到JSON格式的响应")
    except Exception as e:
        log_print(f"生成讲稿时出错: {e}")

    save_result(lesson_data, output_file)
    log_print(f"保存结果: {output_file}")
    return output_file


def save_result(lesson_data, output_file):
    """保存结果到文件"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(lesson_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='生成课程讲稿脚本')
    parser.add_argument('--input', '-i', type=str, nargs='+', help='输入文件')
    parser.add_argument('--output', '-o', type=str, help='输出文件（默认：源文件名加时间戳后缀）')
    parser.add_argument('--batch', '-b', type=int, default=2, help='批大小（已废弃，保留参数兼容性）')
    parser.add_argument('--length', '-l', type=int, default=800, help='内容长度（已废弃，保留参数兼容性）')
    args = parser.parse_args()

    # 初始化LLM连接池
    log_print("初始化LLM连接池...")
    initialize_pool()

    if args.input:
        input_files = [Path(f) for f in args.input]
    else:
        sandbox_dir = Path(__file__).parent
        script_output_dir = sandbox_dir / "script_output"
        input_files = [
            script_output_dir / "cir_sample_ai_intro.json",
            script_output_dir / "cir_sample_material_mechanics.json"
        ]

    for input_file in input_files:
        if input_file.exists():
            # 默认输出到新文件（源文件名 + 时间戳）
            if args.output:
                output_file = Path(args.output)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = input_file.parent / f"{input_file.stem}_{timestamp}{input_file.suffix}"

            try:
                process_lesson_json(str(input_file), str(output_file))
            except Exception as e:
                log_print(f"错误: {e}")
        else:
            log_print(f"文件不存在: {input_file}")

    log_print("\n完成!")
