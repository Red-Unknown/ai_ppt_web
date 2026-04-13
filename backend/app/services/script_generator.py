import logging
import time
from typing import List, Optional
import requests
from app.models.cir import CIRSection
from app.core.config import settings

logger = logging.getLogger(__name__)

# ========== 模板生成（快速） ==========
def generate_script_template(node: CIRSection) -> str:
    """基于模板生成讲稿，速度快，不依赖外部 API"""
    node_name = node.node_name
    teaching_content = node.teaching_content or "这部分内容非常重要。"
    key_points = node.key_points if node.key_points else []
    
    intro = f"同学们好，今天我们来学习「{node_name}」。"
    content = teaching_content.replace("描述了", "就是讲").replace("定义为", "可以理解为")
    if key_points:
        points_text = "、".join(key_points)
        emphasis = f"这里面大家要重点掌握这几个关键点：{points_text}。"
    else:
        emphasis = ""
    ending = f"好了，关于「{node_name}」我们就先讲到这里。接下来我们继续往下看。"
    
    return f"{intro} {content} {emphasis} {ending}"


# ========== DeepSeek 润色（可选，不影响原有逻辑） ==========
def enhance_script_with_deepseek(original_script: str, node_name: str, key_points: List[str]) -> Optional[str]:
    """调用 DeepSeek API 将讲稿改写成更自然的课堂语言"""
    if not settings.DEEPSEEK_API_KEY:
        logger.warning("未配置 DEEPSEEK_API_KEY，无法润色")
        return None
    
    # 处理 BASE_URL：用户可能配置了带 /v1 或不带的
    base_url = settings.DEEPSEEK_BASE_URL.rstrip('/')
    if not base_url.endswith('/v1'):
        base_url = base_url + '/v1'
    api_url = f"{base_url}/chat/completions"
    
    prompt = f"""你是一位经验丰富的大学教师，请将以下关于「{node_name}」的讲稿改写成更自然、口语化的课堂讲授语言。
要求：
- 保留所有核心知识点：{', '.join(key_points) if key_points else '无'}
- 增加适当的语气词（“嗯”、“那么”、“大家注意”）
- 控制总字数在150字左右
- 不要改变教学内容
- 直接输出改写后的讲稿，不要添加任何解释

原始讲稿：
{original_script}
"""
    try:
        start_time = time.time()
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=10
        )
        elapsed = time.time() - start_time
        logger.info(f"DeepSeek 润色耗时: {elapsed:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            enhanced = result["choices"][0]["message"]["content"].strip()
            return enhanced
        else:
            logger.error(f"DeepSeek API 错误: {response.text}")
            return None
    except Exception as e:
        logger.error(f"调用 DeepSeek 失败: {e}")
        return None


def generate_script_for_node(node: CIRSection, use_llm: bool = False) -> str:
    """
    生成单节点讲稿
    :param use_llm: 是否尝试使用 LLM 润色（默认 False，保持快速模板）
    """
    template_script = generate_script_template(node)
    
    if use_llm and settings.DEEPSEEK_API_KEY:
        enhanced = enhance_script_with_deepseek(template_script, node.node_name, node.key_points or [])
        if enhanced:
            return enhanced
        else:
            logger.warning("LLM 润色失败，回退到模板")
    return template_script


def batch_generate_for_lesson(lesson_id: str, db_session, use_llm: bool = False) -> List[dict]:
    """批量生成课件下所有节点的讲稿（预览）"""
    from app.models.cir import CIRSection
    nodes = db_session.query(CIRSection).filter(
        CIRSection.lesson_id == lesson_id
    ).order_by(CIRSection.sort_order).all()
    
    results = []
    for node in nodes:
        script = generate_script_for_node(node, use_llm=use_llm)
        results.append({
            "node_id": node.node_id,
            "node_name": node.node_name,
            "generated_script": script,
            "original_content": node.teaching_content,
            "key_points": node.key_points
        })
    return results