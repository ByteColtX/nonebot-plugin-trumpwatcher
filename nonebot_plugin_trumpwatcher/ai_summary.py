from __future__ import annotations

from urllib.parse import urlparse
from typing import Any

import httpx
from nonebot import logger

from .config import config
from .data_source import TruthPost

_SYSTEM_PROMPT = (
    "你是新闻编辑助手。请把用户提供的特朗普 Truth Social 动态先翻译成简体中文，"
    "再给出最多 3 条要点总结。输出要简洁、客观，不要编造信息。"
)


class _MultimodalNotSupportedError(Exception):
    pass


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _looks_like_multimodal_unsupported(text: str) -> bool:
    lowered = text.lower()
    keywords = ("multimodal", "image", "vision", "图片", "图像", "不支持")
    return any(keyword in lowered for keyword in keywords)


def _collect_image_urls(media: tuple[str, ...]) -> list[str]:
    if not config.trumpwatcher_ai_multimodal_enabled:
        return []
    max_images = config.trumpwatcher_ai_multimodal_max_images
    if max_images <= 0:
        return []
    image_urls = [item for item in media if _looks_like_url(item)]
    return image_urls[:max_images]


def _build_input(source_text: str, image_urls: list[str]) -> list[dict[str, Any]]:
    """构建 /v1/responses 接口所需的 input 消息数组（带 role）。"""
    user_content: list[dict[str, Any]] = [{"type": "input_text", "text": source_text}]
    for image_url in image_urls:
        user_content.append({"type": "input_image", "image_url": image_url})
    return [
        {"role": "system", "content": [{"type": "input_text", "text": _SYSTEM_PROMPT}]},
        {"role": "user", "content": user_content},
    ]


def _extract_content(payload: dict[str, Any]) -> str | None:
    """从 /v1/responses 响应中提取文本内容。"""
    output = payload.get("output")
    if not isinstance(output, list) or not output:
        return None
    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        # output 项类型为 message
        if item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "output_text":
                text = block.get("text", "")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
    return "\n".join(parts).strip() or None


async def _request_summary(source_text: str, image_urls: list[str]) -> str | None:
    api_key = config.trumpwatcher_ai_api_key.strip()
    if not api_key:
        return None

    url = f"{config.trumpwatcher_ai_api_base.rstrip('/')}/responses"
    payload: dict[str, Any] = {
        "model": config.trumpwatcher_ai_model,
        "temperature": config.trumpwatcher_ai_temperature,
        "input": _build_input(source_text, image_urls),
    }
    try:
        async with httpx.AsyncClient(timeout=config.trumpwatcher_ai_timeout) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        response_text = exc.response.text if exc.response is not None else ""
        if image_urls and _looks_like_multimodal_unsupported(response_text):
            raise _MultimodalNotSupportedError from exc
        raise
    return _extract_content(resp.json())


async def summarize_post(post: TruthPost) -> str | None:
    api_key = config.trumpwatcher_ai_api_key.strip()
    if not api_key:
        return None

    source_text = post.content.strip()
    if not source_text:
        return None

    source_text = source_text[: config.trumpwatcher_ai_max_chars]
    image_urls = _collect_image_urls(post.media)
    try:
        content = await _request_summary(source_text, image_urls)
    except _MultimodalNotSupportedError:
        logger.warning("当前模型不支持图片输入，已降级为纯文本总结")
        try:
            content = await _request_summary(source_text, [])
        except Exception:
            logger.exception("AI 文本总结请求失败")
            return None
    except Exception:
        logger.exception("AI 翻译总结请求失败")
        return None

    if not content:
        logger.warning("AI 翻译总结返回为空")
        return None
    return f"AI翻译总结:\n{content}"
