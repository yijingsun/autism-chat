"""
情绪关键词检测模块
通过简单的关键词匹配检测用户输入的情绪倾向
不需要训练模型，规则匹配在 demo 阶段足够
"""
from config import EMOTION_KEYWORDS


def detect_emotion(text: str) -> str:
    """
    检测文本中的情绪倾向

    Args:
        text: 用户输入的文本

    Returns:
        "negative" | "positive" | "neutral"
    """
    text_lower = text.lower()

    negative_score = sum(1 for kw in EMOTION_KEYWORDS["negative"] if kw in text_lower)
    positive_score = sum(1 for kw in EMOTION_KEYWORDS["positive"] if kw in text_lower)

    if negative_score > positive_score:
        return "negative"
    elif positive_score > negative_score:
        return "positive"
    else:
        return "neutral"


def get_matched_keywords(text: str) -> dict:
    """返回匹配到的情绪关键词（用于调试/展示）"""
    text_lower = text.lower()
    return {
        "negative": [kw for kw in EMOTION_KEYWORDS["negative"] if kw in text_lower],
        "positive": [kw for kw in EMOTION_KEYWORDS["positive"] if kw in text_lower],
    }
