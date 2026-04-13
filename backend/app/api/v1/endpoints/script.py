from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.cir import CIRSection
from app.services.script_generator import batch_generate_for_lesson, generate_script_for_node

router = APIRouter(prefix="/script", tags=["讲稿管理"])
logger = logging.getLogger(__name__)

class ScriptItem(BaseModel):
    node_id: str
    script_content: str

class SingleNodeScript(BaseModel):
    node_id: str
    script_content: Optional[str] = None
    use_llm: bool = False

@router.get("/generate/{lesson_id}")
def generate_preview(
    lesson_id: str,
    use_llm: bool = Query(False, description="是否使用LLM润色"),
    db: Session = Depends(get_db)
):
    """为指定课件生成讲稿预览（不保存）"""
    try:
        result = batch_generate_for_lesson(lesson_id, db, use_llm=use_llm)
        return {"lesson_id": lesson_id, "generated": result}
    except Exception as e:
        logger.error(f"生成预览失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
def save_scripts(scripts: List[ScriptItem], db: Session = Depends(get_db)):
    """保存教师编辑后的讲稿"""
    updated = []
    for item in scripts:
        node = db.query(CIRSection).filter(CIRSection.node_id == item.node_id).first()
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {item.node_id} not found")
        node.script_content = item.script_content
        updated.append(node.node_id)
    db.commit()
    return {"message": f"已保存 {len(updated)} 个节点的讲稿", "node_ids": updated}

@router.get("/get/{lesson_id}")
def get_final_scripts(lesson_id: str, db: Session = Depends(get_db)):
    """获取最终讲稿（优先已保存）"""
    nodes = db.query(CIRSection).filter(CIRSection.lesson_id == lesson_id).order_by(CIRSection.sort_order).all()
    result = []
    for node in nodes:
        script = node.script_content
        if not script:
            script = generate_script_for_node(node, use_llm=False)
        result.append({
            "node_id": node.node_id,
            "node_name": node.node_name,
            "script_content": script,
            "page_num": node.page_num
        })
    return {"lesson_id": lesson_id, "nodes": result}

@router.get("/node/{node_id}")
def get_node_script(node_id: str, db: Session = Depends(get_db)):
    node = db.query(CIRSection).filter(CIRSection.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    script = node.script_content
    if not script:
        script = generate_script_for_node(node, use_llm=False)
    return {
        "node_id": node.node_id,
        "node_name": node.node_name,
        "script_content": script,
        "page_num": node.page_num,
        "key_points": node.key_points
    }

@router.put("/node/{node_id}")
def update_node_script(node_id: str, data: SingleNodeScript, db: Session = Depends(get_db)):
    node = db.query(CIRSection).filter(CIRSection.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if data.script_content is not None:
        node.script_content = data.script_content
    elif data.use_llm:
        generated = generate_script_for_node(node, use_llm=True)
        node.script_content = generated
    db.commit()
    return {"message": "更新成功", "node_id": node_id, "script_content": node.script_content}

@router.delete("/reset/{node_id}")
def reset_script(node_id: str, db: Session = Depends(get_db)):
    node = db.query(CIRSection).filter(CIRSection.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.script_content = None
    db.commit()
    return {"message": "讲稿已重置", "node_id": node_id}

@router.post("/apply-preview/{lesson_id}")
def apply_preview(
    lesson_id: str,
    use_llm: bool = Query(False),
    db: Session = Depends(get_db)
):
    nodes = db.query(CIRSection).filter(CIRSection.lesson_id == lesson_id).all()
    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")
    for node in nodes:
        script = generate_script_for_node(node, use_llm=use_llm)
        node.script_content = script
    db.commit()
    return {"message": f"已为 {len(nodes)} 个节点生成并保存讲稿", "lesson_id": lesson_id}