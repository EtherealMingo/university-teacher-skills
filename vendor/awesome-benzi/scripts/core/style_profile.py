"""Deterministic writing-style profiling and style gate.

Reference copy is treated as a style sample only. The profiler stores
statistical fingerprints and hashes, never the original text, so it cannot
become a source of facts or copied prose.
"""

from __future__ import annotations

import hashlib
import re
import statistics
from typing import Any

AI_FILLER_PATTERN = re.compile(
    r"值得注意的是|需要指出的是|必须看到的是|众所周知|不难发现|综上所述|总而言之|"
    r"我们可以看到|可以说|由此可见|不言而喻|毋庸置疑|展望未来|迈向新的高度|"
    r"赋能|抓手|闭环管理|底层逻辑|颗粒度|倒逼|深耕|助力"
)
CHAT_RESIDUE_PATTERN = re.compile(
    r"希望这对你有帮助|如果你愿意|如需我继续|下面我将|以下是为你|作为(?:一个)?AI|"
    r"好的，|当然，"
)
COLLOQUIAL_PATTERN = re.compile(
    r"我们觉得|大家都知道|说白了|搞清楚|弄明白|效果变好|很厉害|非常牛|一大堆|"
    r"搞定|看一下|弄一下|搞起来|很有意思|挺不错"
)
SERIOUSNESS_PATTERN = re.compile(
    r"[!！]{1,}|难道|岂不是|居然|竟然|太棒了|真棒|超级|最最|无敌"
)
MECHANICAL_OPENERS = ("第一", "第二", "第三", "首先", "其次", "再次", "最后", "另外", "此外", "同时")
PREFERENCE_PATTERN = re.compile(r"正式|严谨|克制|客观|书面|学术|简洁|自然|不啰嗦|避免空话|少用套话")
NG = 8


def _compact(text: str) -> str:
    return re.sub(r"[ \t\r\n]+", "", text)


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。！？!?；;]+", text) if part.strip()]


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[ \t]*\n[ \t]*\n[ \t]*", text) if part.strip()]


def _ngram_hashes(text: str) -> set[str]:
    compact = _compact(text)
    return {
        hashlib.sha1(compact[index:index + NG].encode("utf-8")).hexdigest()[:16]
        for index in range(max(0, len(compact) - NG + 1))
        if len(compact[index:index + NG]) >= NG
    }


def extract_style_profile(
    samples: list[str],
    prompt: str = "",
    section_headings: list[str] | None = None,
) -> dict[str, Any]:
    texts = [str(sample).strip() for sample in samples if str(sample).strip()]
    corpus = chr(10) + chr(10).join(texts)
    sentences = _sentences(corpus)
    paragraphs = _paragraphs(corpus)
    lengths = [_compact_length(sentence) for sentence in sentences]
    para_lengths = [_compact_length(paragraph) for paragraph in paragraphs]
    hits: dict[str, int] = {}
    for name, pattern in (
        ("ai_filler", AI_FILLER_PATTERN),
        ("chat_residue", CHAT_RESIDUE_PATTERN),
        ("colloquial", COLLOQUIAL_PATTERN),
        ("seriousness", SERIOUSNESS_PATTERN),
    ):
        hits[name] = len(pattern.findall(corpus))
    opener_counts = {opener: corpus.count(opener) for opener in MECHANICAL_OPENERS}
    preference_signals = sorted(set(PREFERENCE_PATTERN.findall(prompt)))
    return {
        "schema_type": "style-profile",
        "schema_version": 1,
        "type": "style-profile.v1",
        "sample_count": len(texts),
        "corpus_characters": _compact_length(corpus),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "sentence_length_median": round(float(statistics.median(lengths)), 2) if lengths else 0.0,
        "sentence_length_stdev": round(float(statistics.pstdev(lengths)), 2) if len(lengths) > 1 else 0.0,
        "paragraph_length_median": round(float(statistics.median(para_lengths)), 2) if para_lengths else 0.0,
        "pattern_hits": hits,
        "opener_counts": opener_counts,
        "preference_signals": preference_signals,
        "sample_ngram_hashes": sorted(_ngram_hashes(corpus)) if corpus else [],
        "section_headings": [str(value).strip() for value in (section_headings or []) if str(value).strip()],
        "stored_original_text": False,
    }


def _compact_length(text: str) -> int:
    return len(_compact(text))


def render_style_brief(profile: dict[str, Any] | None) -> dict[str, Any]:
    if not profile:
        return {"schema_type": "style-brief", "schema_version": 1, "mode": "default-serious-academic", "rules": [
            "使用客观、克制、书面、具体的说明性语体。",
            "一句承担一个命题；主语具体；先给结论，再给依据和边界。",
            "避免 AI 套话、口水话、网络流行语和营销腔。",
            "长短句交替；避免连续三段以同一词开头。",
            "参考文案只用于校准语体、句式与转承，不复制其句子、事实或观点。",
        ]}
    hits = profile.get("pattern_hits", {})
    median = float(profile.get("sentence_length_median", 0) or 0)
    rules: list[str] = []
    if median and median < 18:
        rules.append("参考样本句长偏短：正文以中长句为主，短句只用于结论、指标和边界。")
    elif median and median > 60:
        rules.append("参考样本句长偏长：正文要拆成单一命题的句子，避免多层嵌套。")
    else:
        rules.append("参考样本句长适中：保持长短句交替。")
    if hits.get("ai_filler"):
        rules.append("参考样本含 AI 套话：正文不得沿用这些套话。")
    if hits.get("colloquial"):
        rules.append("参考样本有口语残留：只吸收其正式部分，不沿用口语词。")
    preferences = profile.get("preference_signals") or []
    if preferences:
        rules.append("任务偏好：" + "、".join(preferences) + "。")
    return {"schema_type": "style-brief", "schema_version": 1, "mode": "sample-calibrated", "rules": rules}


def check_style(text: str, style_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    compact = _compact(text)
    for match in CHAT_RESIDUE_PATTERN.finditer(text):
        issues.append({"kind": "chat-residue", "level": "blocked", "message": "删除聊天机器人残留和口语承接。", "excerpt": match.group(0)})
    for match in COLLOQUIAL_PATTERN.finditer(text):
        issues.append({"kind": "colloquial", "level": "blocked", "message": "用具体、书面的说明替代口语表达。", "excerpt": match.group(0)})
    for match in SERIOUSNESS_PATTERN.finditer(text):
        issues.append({"kind": "seriousness-violation", "level": "blocked", "message": "申报书不使用感叹、反问、网络夸张和情绪化表达。", "excerpt": match.group(0)})
    for match in list(AI_FILLER_PATTERN.finditer(text))[:6]:
        issues.append({"kind": "ai-filler", "level": "blocked", "message": "删除无信息套话，直接陈述对象、依据、机制或边界。", "excerpt": match.group(0)})
    sentences = _sentences(text)
    paragraphs = _paragraphs(text)
    opener_positions: dict[str, list[int]] = {}
    for index, sentence in enumerate(sentences, start=1):
        prefix = sentence.strip()
        for ch in (" ", "	", chr(34), chr(39), "“", "”", "（", "("):
            prefix = prefix.lstrip(ch)
        prefix = prefix[:4]
        if prefix:
            opener_positions.setdefault(prefix, []).append(index)
    repeated = {key: value for key, value in opener_positions.items() if len(value) >= 3}
    if repeated:
        issues.append({"kind": "repeated-openers", "level": "blocked", "message": "连续或高频复用相同句首会产生机械感；改写句式。", "repeated": repeated})
    mechanical_total = sum(text.count(opener) for opener in MECHANICAL_OPENERS)
    mechanical_pairs = sum(1 for opener in ("首先", "其次", "再次", "最后") if text.count(opener) > 0)
    if mechanical_total >= 5 or mechanical_pairs >= 3:
        issues.append({"kind": "mechanical-connectives", "level": "needs-review", "message": "机械转承词偏多；改为栏目顺序、任务关系或直接陈述。", "count": mechanical_total})
    lengths = [_compact_length(sentence) for sentence in sentences]
    long_ratio = sum(1 for value in lengths if value > 60) / max(len(lengths), 1)
    short_ratio = sum(1 for value in lengths if value < 12) / max(len(lengths), 1)
    if long_ratio > 0.55:
        issues.append({"kind": "monotone-long-sentences", "level": "needs-review", "message": "长句占比过高，拆成单一命题句。", "ratio": round(long_ratio, 3)})
    if short_ratio > 0.35 and len(lengths) >= 6:
        issues.append({"kind": "fragment-clusters", "level": "needs-review", "message": "短句占比偏高，把同一命题的句子合并展开。", "ratio": round(short_ratio, 3)})
    para_lengths = [_compact_length(paragraph) for paragraph in paragraphs if _compact_length(paragraph) > 0]
    if len(para_lengths) >= 3:
        median_para = float(statistics.median(para_lengths))
        if median_para < 100:
            issues.append({"kind": "thin-paragraphs", "level": "needs-review", "message": "段落中位长度偏低；只保留承担完整命题的段落。", "median": median_para})
    if style_profile:
        hashes = set(style_profile.get("sample_ngram_hashes") or [])
        if hashes:
            overlap = len(_ngram_hashes(text) & hashes)
            if overlap >= 6:
                issues.append({"kind": "reference-copy-overlap", "level": "needs-review", "message": "正文与参考文案出现较长连续重合，只允许保留术语和固定名称。", "overlap_ngrams": overlap})
    hard = [item for item in issues if item.get("level") == "blocked"]
    soft = [item for item in issues if item.get("level") == "needs-review"]
    return {
        "schema_type": "style-gate", "schema_version": 1, "type": "style-gate.v1",
        "gate": "blocked" if hard else "needs-review" if soft else "passed",
        "issues": issues,
        "metrics": {
            "characters": len(compact),
            "sentences": len(sentences),
            "paragraphs": len(paragraphs),
            "hard_issues": len(hard),
            "review_issues": len(soft),
        },
    }
