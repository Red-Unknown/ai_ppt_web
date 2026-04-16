import sys
sys.path.insert(0, 'f:/college/sophomore/服务外包')

from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever
import asyncio

async def test():
    r = TwoLayerRetriever()
    res = await r.retrieve('什么是轴向拉伸', 'lesson_mm_001', 3)
    print('CIR:', len(res['cir_results']), 'Raw:', len(res['raw_results']))
    print('Answer:', res['answer'][:100] if res['answer'] else 'None')
    print('Bbox:', len(res['bbox_list']))

asyncio.run(test())
