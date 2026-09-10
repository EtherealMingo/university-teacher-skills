#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pptx_kit — 中文演示文稿生产工具（office-layer 自建）

面向高校场景：日常课件、学术汇报、科普讲座。共同点是「中文必须显式设字体」，
否则 PowerPoint 会用主题默认字体渲染出等线/Calibri，中文标题会掉字重。

能力：
  build    JSON 规格 → PPTX（16:9，标题/要点/表格/图片/备注页）
  notes    为既有 PPTX 批量写入演讲者备注
  inspect  读回结构与字数（自检信息密度用）

依赖：python-pptx
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Emu, Inches, Pt
except ImportError:  # pragma: no cover
    sys.exit("缺少 python-pptx：请运行 vendor/office-layer/bootstrap.sh")

CN_HEI = "微软雅黑"     # 投屏可读性优于宋体
CN_SONG = "宋体"
EN_FONT = "Arial"

# 学术汇报配色（低饱和、投影不刺眼）
CLR_TITLE = RGBColor(0x1F, 0x2D, 0x3D)
CLR_BODY = RGBColor(0x33, 0x33, 0x33)
CLR_ACCENT = RGBColor(0x0B, 0x5C, 0x8A)


def _font(run, cn=CN_HEI, size=18, bold=False, color=CLR_BODY, en=EN_FONT):
    from pptx.oxml.ns import qn
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", cn if tag == "a:ea" else en)
    return run


def _run(paragraph, text, **kw):
    """python-pptx 的 add_run() 不接受文本参数，只能先建后赋。"""
    r = paragraph.add_run()
    r.text = text
    return _font(r, **kw)


def _blank(prs):
    # 6 = blank layout，避免占位符继承主题字体
    return prs.slides.add_slide(prs.slide_layouts[6])


def _textbox(slide, l, t, w, h):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def add_title_slide(prs, title, subtitle=None, presenter=None):
    s = _blank(prs)
    tf = _textbox(s, 0.9, 2.2, 11.5, 2.0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    _run(p, title, size=40, bold=True, color=CLR_TITLE)
    if subtitle:
        p2 = tf.add_paragraph()
        p2.space_before = Pt(14)
        _run(p2, subtitle, cn=CN_SONG, size=20, color=CLR_ACCENT)
    if presenter:
        tf3 = _textbox(s, 0.9, 4.9, 11.5, 0.8)
        _run(tf3.paragraphs[0], presenter, cn=CN_SONG, size=16, color=CLR_BODY)
    # 左侧强调竖条
    from pptx.enum.shapes import MSO_SHAPE
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(2.35), Inches(0.085), Inches(1.1))
    bar.fill.solid(); bar.fill.fore_color.rgb = CLR_ACCENT; bar.line.fill.background()
    return s


def add_content_slide(prs, title, bullets=None, notes=None, table=None, image=None):
    s = _blank(prs)
    tf = _textbox(s, 0.7, 0.45, 12.0, 1.0)
    _run(tf.paragraphs[0], title, size=28, bold=True, color=CLR_TITLE)
    # 标题下分隔线
    from pptx.enum.shapes import MSO_SHAPE
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.72), Inches(1.22), Inches(11.9), Inches(0.022))
    ln.fill.solid(); ln.fill.fore_color.rgb = CLR_ACCENT; ln.line.fill.background()

    top = 1.5
    if table:
        rows = [table.get("header", [])] + table.get("rows", [])
        nr, nc = len(rows), max(len(r) for r in rows) if rows else 0
        shp = s.shapes.add_table(nr, nc, Inches(table.get("left", 0.8)),
                                 Inches(table.get("top", top)),
                                 Inches(table.get("width", 11.7)), Inches(0.42 * nr))
        tbl = shp.table
        for ri, row in enumerate(rows):
            for ci in range(nc):
                cell = tbl.cell(ri, ci)
                cell.text = str(row[ci]) if ci < len(row) else ""
                for p in cell.text_frame.paragraphs:
                    for r in p.runs:
                        _font(r, size=14 if ri == 0 else 13, bold=(ri == 0))
        top = table.get("top", top) + 0.42 * nr + 0.25

    if bullets:
        tf = _textbox(s, 0.8, top, 7.4 if image else 11.6, 5.4)
        first = True
        for b in bullets:
            lvl = 0
            txt = b
            if isinstance(b, dict):
                txt, lvl = b.get("text", ""), b.get("level", 0)
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.level = lvl
            p.space_after = Pt(10 if lvl == 0 else 6)
            mark = "▍" if lvl == 0 else "·"
            _run(p, f"{mark} {txt}" if lvl == 0 else f"    {mark} {txt}",
                 cn=CN_HEI if lvl == 0 else CN_SONG,
                 size=18 if lvl == 0 else 15,
                 color=CLR_BODY if lvl == 0 else RGBColor(0x55, 0x5F, 0x6B))
    if image:
        s.shapes.add_picture(image, Inches(8.5), Inches(top), width=Inches(4.0))
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def build_from_spec(spec, out_path):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)  # 16:9
    meta = spec.get("meta", {})
    add_title_slide(prs, meta.get("title", "未命名"), meta.get("subtitle"), meta.get("presenter"))
    for sl in spec.get("slides", []):
        add_content_slide(prs, sl.get("title", ""), sl.get("bullets"),
                          sl.get("notes"), sl.get("table"), sl.get("image"))
    prs.save(str(out_path))
    return out_path


def write_notes(path, notes_map, out_path=None):
    """notes_map: {slide_index(1-based): "备注文本"}"""
    prs = Presentation(str(path))
    written = []
    for idx, txt in notes_map.items():
        i = int(idx) - 1
        if 0 <= i < len(prs.slides):
            prs.slides[i].notes_slide.notes_text_frame.text = txt
            written.append(int(idx))
    prs.save(str(out_path or path))
    return {"written": written, "total_slides": len(prs.slides)}


def inspect(path):
    prs = Presentation(str(path))
    slides = []
    for i, s in enumerate(prs.slides, 1):
        txt, notes = [], ""
        for shp in s.shapes:
            if shp.has_text_frame and shp.text_frame.text.strip():
                txt.append(shp.text_frame.text.strip())
            if shp.has_table:
                txt.append(f"[表格 {len(shp.table.rows)}x{len(shp.table.columns)}]")
        if s.has_notes_slide:
            notes = s.notes_slide.notes_text_frame.text.strip()
        body = "\n".join(txt)
        slides.append({"n": i, "title": txt[0].split("\n")[0][:40] if txt else "",
                       "chars": len(body), "notes_chars": len(notes),
                       "has_notes": bool(notes),
                       "density_warn": len(body) > 220})
    return {"slides": len(slides), "size": f"{prs.slide_width}x{prs.slide_height}",
            "detail": slides,
            "overdense": [s["n"] for s in slides if s["density_warn"]]}


def main():
    ap = argparse.ArgumentParser(prog="pptx_kit", description="中文演示文稿生产工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("build", help="JSON 规格 → PPTX")
    a.add_argument("--spec", required=True)
    a.add_argument("--out", required=True)

    b = sub.add_parser("notes", help="批量写入演讲者备注")
    b.add_argument("--in", dest="src", required=True)
    b.add_argument("--notes", required=True, help="JSON: {slide_index: text}")
    b.add_argument("--out")

    c = sub.add_parser("inspect", help="读回结构与信息密度")
    c.add_argument("--in", dest="src", required=True)

    args = ap.parse_args()
    if args.cmd == "build":
        build_from_spec(json.loads(Path(args.spec).read_text(encoding="utf-8")), args.out)
        print(json.dumps(inspect(args.out), ensure_ascii=False, indent=2))
    elif args.cmd == "notes":
        res = write_notes(args.src, json.loads(Path(args.notes).read_text(encoding="utf-8")), args.out)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(inspect(args.src), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
