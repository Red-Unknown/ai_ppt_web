import json
import time
import sys
import os
from typing import Dict, Any, List
import statistics

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def load_criteria() -> Dict[str, Any]:
    criteria_path = os.path.join(os.path.dirname(__file__), "tool_evaluation_criteria.json")
    with open(criteria_path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_latency_score(avg_latency_ms: float, thresholds: Dict[str, float]) -> float:
    min_s = thresholds["latency_ms_max_score"]
    max_s = thresholds["latency_ms_min_score"]
    if avg_latency_ms <= min_s:
        return 100.0
    if avg_latency_ms >= max_s:
        return 0.0
    # Linear interpolation
    return 100.0 * (1 - (avg_latency_ms - min_s) / (max_s - min_s))

def calculate_score(tool_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    criteria = load_criteria()
    dimensions = criteria["dimensions"]
    thresholds = criteria["thresholds"]
    
    scores = {}
    weighted_sum = 0.0
    
    # 1. Functionality (Success Rate)
    success_rate = metrics.get("success_rate", 0.0) * 100.0
    scores["functionality"] = min(100.0, max(0.0, success_rate))
    
    # 2. Latency
    avg_latency = metrics.get("avg_latency_ms", 1000.0)
    scores["latency"] = calculate_latency_score(avg_latency, thresholds)
    
    # 3. Stability (Variance Score)
    # Lower variance is better. 
    # Heuristic: If std_dev > 50% of mean, score drops.
    latencies = metrics.get("latencies", [])
    if len(latencies) > 1:
        stdev = statistics.stdev(latencies)
        mean = statistics.mean(latencies) if statistics.mean(latencies) > 0 else 1
        cv = stdev / mean # Coefficient of Variation
        # Score: 0 CV -> 100, 1.0 CV -> 0
        scores["stability"] = max(0.0, 100.0 * (1 - cv))
    else:
        scores["stability"] = 100.0 if metrics.get("success_rate", 0) == 1.0 else 0.0

    # 4. Error Handling
    # Based on passing negative test cases
    error_pass_rate = metrics.get("error_test_pass_rate", 0.0) * 100.0
    scores["error_handling"] = error_pass_rate
    
    # 5. Resource Usage (Mocked/Estimated)
    # Using memory usage metric if available, else default
    mem_usage = metrics.get("peak_memory_mb", 0.0)
    if mem_usage <= thresholds["memory_mb_max_score"]:
        scores["resource_usage"] = 100.0
    elif mem_usage >= thresholds["memory_mb_min_score"]:
        scores["resource_usage"] = 0.0
    else:
        scores["resource_usage"] = 100.0 * (1 - (mem_usage - thresholds["memory_mb_max_score"]) / (thresholds["memory_mb_min_score"] - thresholds["memory_mb_max_score"]))
        
    # 6. Scalability (Static Check for async)
    is_async = metrics.get("is_async", True)
    scores["scalability"] = 100.0 if is_async else 50.0
    
    # 7. Security (Static Check)
    # Check if API keys are exposed in logs or errors (Mock check)
    secure = metrics.get("security_check", True)
    scores["security"] = 100.0 if secure else 0.0
    
    # Calculate Final Weighted Score
    for dim, config in dimensions.items():
        weight = config["weight"]
        score = scores.get(dim, 0.0)
        weighted_sum += score * weight
        
    result = {
        "tool_name": tool_name,
        "final_score": round(weighted_sum, 2),
        "dimension_scores": {k: round(v, 2) for k, v in scores.items()},
        "metrics": metrics
    }
    
    return result

def save_score(tool_name: str, result: Dict[str, Any]):
    output_path = os.path.join(os.path.dirname(__file__), f"{tool_name}_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Score saved to {output_path}")

if __name__ == "__main__":
    # Example Usage
    sample_metrics = {
        "success_rate": 0.9,
        "avg_latency_ms": 150.0,
        "latencies": [140, 160, 150],
        "error_test_pass_rate": 1.0,
        "peak_memory_mb": 20.0,
        "is_async": True,
        "security_check": True
    }
    print(json.dumps(calculate_score("sample_tool", sample_metrics), indent=2))
