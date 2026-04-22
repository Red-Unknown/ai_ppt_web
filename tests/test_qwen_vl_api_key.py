import argparse
import base64
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import Settings


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def encode_image(image_path: Path) -> str:
    with image_path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test whether QWEN_API_KEY is valid by calling qwen-vl-plus to parse an image."
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the image file, e.g. sandbox/test.png",
    )
    parser.add_argument(
        "--prompt",
        default="请识别并简要描述这张图片中的主要内容。",
        help="Prompt sent to qwen-vl-plus.",
    )
    args = parser.parse_args()

    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        print(f"[ERROR] 图片不存在: {image_path}")
        return 1

    settings = Settings()
    api_key = settings.EFFECTIVE_QWEN_API_KEY
    model = settings.QWEN_VISION_MODEL or "qwen-vl-plus"
    try:
        base_url = settings.EFFECTIVE_QWEN_BASE_URL.rstrip("/")
    except ValueError as exc:
        print(f"[ERROR] QWEN_BASE_URL 配置错误: {exc}")
        return 1

    if not api_key:
        print("[ERROR] QWEN_API_KEY/DASHSCOPE_API_KEY 未配置（请检查 .env）")
        return 1

    image_base64 = encode_image(image_path)
    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": args.prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ],
    }

    print(f"-> 请求模型: {model}")
    print(f"-> 请求地址: {endpoint}")
    print(f"-> 图片: {image_path}")
    print("-> 正在调用 qwen-vl-plus ...")

    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    except requests.RequestException as exc:
        print(f"[ERROR] 网络请求失败: {exc}")
        return 1

    print(f"HTTP {resp.status_code}")
    try:
        data = resp.json()
    except ValueError:
        print("[ERROR] 响应不是 JSON:")
        print(resp.text)
        return 1

    if resp.status_code != 200:
        print("[ERROR] 接口调用失败，可能是 API Key 无效、权限不足或请求格式错误。")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 1

    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message", {})
    content = message.get("content")
    print("[OK] 调用成功，QWEN_API_KEY 有效。")
    print("模型返回：")
    if isinstance(content, str):
        print(content)
    else:
        print(json.dumps(content, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
