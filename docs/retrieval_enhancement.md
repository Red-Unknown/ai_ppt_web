# RAG 检索系统增强与评估

本目录包含 Tree-based RAG 检索系统的增强功能与评估工具。

## 1. 检索增强 (Retrieval Enhancement)
已对 `TreeStructureRetriever` 进行重构，支持混合检索策略：
- **Dense Embedding**: 使用 OpenAI/DeepSeek Embeddings (如配置) 或 Mock 向量。
- **Sparse BM25**: 实现 `SimpleBM25` 进行关键词频率加权检索。
- **Keyword Fuzzy**: 支持标题模糊匹配与同义词扩展。
- **Structure**: 支持 `synonyms` 字段。

## 2. 评估体系 (Evaluation System)
### 生成黄金测试集
```bash
python tests/evaluation/generate_retrieval_dataset.py
```
该脚本基于 `knowledge_base.json` 自动生成包含以下类型的测试用例：
- Exact Title (精确匹配)
- Typo (错字/拼音错误模拟)
- Content Fragment (内容片段查询)
- Multi-concept (多概念混合查询)
- Synonym (同义词查询)

生成结果保存在 `tests/evaluation/retrieval_dataset_golden.json`。

### 运行自动化评测
```bash
python tests/evaluation/evaluate_retrieval.py
```
输出 Hit Rate@1/3/5, MRR 等指标，并按类别统计。

## 3. 单元测试与 CI
```bash
python -m pytest backend/tests/test_retrieval_robustness.py
```
包含针对错字容忍、混合概念、同义词扩展的鲁棒性测试用例。

## 4. 配置
在 `.env` 或环境变量中设置 `DEEPSEEK_API_KEY` 可启用真实 Embedding 检索，否则使用 Mock 模式。
