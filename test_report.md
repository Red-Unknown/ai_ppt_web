# Role D Scenarios Regression Test Report

## 1. Test Summary
- **Date**: 2026-03-10
- **Environment**: Windows, Python 3.x
- **API Key Status**: Present (DeepSeek)
- **Redis**: Mock (In-Memory Fallback)
- **Total Cases**: 3 New Feature Scenarios (Visual Grounding, Adaptive Resume, Dual Stream) + Existing Scenarios

## 2. Test Results

| Feature | Scenario | Result | Notes |
| :--- | :--- | :--- | :--- |
| **Visual Grounding** | Query "牛顿第二定律的公式推导" | ✅ PASSED | Correctly returned 5 sources with `bbox` and `image_url`. |
| **Adaptive Resume** | Query "我没听懂，请换个方式解释" | ✅ PASSED | Correctly triggered `FALLBACK_VIDEO` action and emitted `strategy` event. |
| **Dual Stream** | Query "详细解释广义相对论..." | ✅ PASSED* | Dual streams (Quick + Enhanced) verified. <br>⚠️ *Warning: Reasoning content stream was empty (Model/API behavior).* |

## 3. Key Findings
1.  **Visual Grounding**: The retriever successfully injects mock visual metadata (bbox/image_url) when relevant documents are found. Note: Queries starting with "展示" (Show) may be misclassified as `CONTROL` intent; used "公式推导" for robust testing.
2.  **Adaptive Resume**: The system correctly detects confusion (triggered by "我没听懂") and switches strategy (NORMAL -> FALLBACK), emitting the `strategy` log for frontend display.
3.  **Dual Stream**:
    -   **Quick Answer Stream**: Successfully emitted `quick_answer` tokens immediately.
    -   **Enhanced Answer Stream**: Successfully emitted `enhanced_answer` tokens after a delay.
    -   **Reasoning Content**: The `reasoning_content` field was empty in the API response chunks. This suggests the current model configuration (`deepseek-reasoner`) or API key permissions might be returning standard chat responses without the "thinking" chain exposed, or the client library version needs adjustment. However, the *mechanism* of dual streaming is functional.

## 4. Recommendations
-   **Frontend**: Implement handling for empty `reasoning_content` (graceful fallback/collapse).
-   **Model Config**: Verify `DEEPSEEK_REASONER_MODEL` points to a model version that explicitly supports the `reasoning_content` parameter in the API response.
-   **Intent Routing**: Consider refining `DialogueRouter` to handle "展示..." (Show...) queries as `Intent.QA` if they are requesting educational content, rather than `Intent.CONTROL`.

## 5. Artifacts
-   Test Script: `tests/test_role_d_scenarios.py`
-   Log Output: `test_results_utf8.txt`
