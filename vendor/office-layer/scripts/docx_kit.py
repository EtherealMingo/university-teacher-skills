#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docx_kit — 中文 Word 文档生产工具（office-layer 自建，非上游复制）

设计目标：为高校教师场景产出可直接交给教务/学院的中文 Word 文档。
核心能力：
  md        Markdown → DOCX（中文字体、标题层级、表格、页码）
  comment   在既有 DOCX 上按锚点文本写「真批注」（Word 原生 comments）
  spec      JSON 规格 → DOCX（复杂排版：页眉页脚、评语模板、留空位）
  inspect   读回 DOCX 结构与批注（自检用）

依赖：python-docx >= 1.2.0（1.2.0 起原生支持批注）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:  # pragma: no cover
    sys.exit("缺少 python-docx：请运行 vendor/office-layer/bootstrap.sh")

# ---------------------------------------------------------------- 中文字体常量
CN_SONG = "宋体"      # 正文（学术/公文标准）
CN_HEI = "黑体"       # 标题
CN_KAI = "楷体"       # 引文、批注性文字
EN_SERIF = "Times New Roman"
EN_SANS = "Arial"

# 字号（磅）：公文常用「三号=16 四号=14 小四=12 五号=10.5」
SZ_TITLE, SZ_H1, SZ_H2, SZ_H3, SZ_BODY, SZ_SMALL = 16, 15, 14, 12, 12, 10.5


def set_run_font(run, cn=CN_SONG, en=EN_SERIF, size=SZ_BODY, bold=False, italic=False):
    """设置 run 的中英文字体。中文必须通过 w:rFonts/@w:eastAsia 指定，否则 Word 回退。"""
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.insert(0, rf)
    rf.set(qn("w:eastAsia"), cn)
    rf.set(qn("w:ascii"), en)
    rf.set(qn("w:hAnsi"), en)
    return run


def _style_base(doc):
    """把 Normal 样式钉成中文正文规格，避免继承 Word 默认 Calibri/等线。"""
    st = doc.styles["Normal"]
    st.font.name = EN_SERIF
    st.font.size = Pt(SZ_BODY)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), CN_SONG)
    pf = st.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(0)


def add_page_number_footer(section, prefix=""):
    """页脚居中页码，中文公文常见「- 1 -」格式。"""
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if prefix:
        set_run_font(p.add_run(prefix), size=SZ_SMALL)
    r = p.add_run()
    set_run_font(r, size=SZ_SMALL)
    for el, attr in (("w:fldChar", "w:fldCharType"),):
        fld = OxmlElement(el)
        fld.set(qn(attr), "begin")
        r._element.append(fld)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = " PAGE "
    r._element.append(it)
    fld = OxmlElement("w:fldChar")
    fld.set(qn("w:fldCharType"), "end")
    r._element.append(fld)


# ---------------------------------------------------------------- Markdown 解析
_RE_H = re.compile(r"^(#{1,6})\s+(.*)$")
_RE_UL = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_RE_OL = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
_RE_TBL_SEP = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")


def _split_inline(text):
    """拆 **粗体** / *斜体* / `等宽`，返回 [(片段, 样式)]。"""
    out, buf, i = [], "", 0
    while i < len(text):
        if text.startswith("**", i):
            j = text.find("**", i + 2)
            if j > i:
                if buf:
                    out.append((buf, ""))
                    buf = ""
                out.append((text[i + 2:j], "b"))
                i = j + 2
                continue
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j > i:
                if buf:
                    out.append((buf, ""))
                    buf = ""
                out.append((text[i + 1:j], "c"))
                i = j + 1
                continue
        buf += text[i]
        i += 1
    if buf:
        out.append((buf, ""))
    return out or [("", "")]


def _emit_runs(p, text, cn=CN_SONG, size=SZ_BODY):
    for frag, kind in _split_inline(text):
        r = p.add_run(frag)
        set_run_font(r, cn=cn, size=size, bold=(kind == "b"))
        if kind == "c":
            r.font.name = "Consolas"
            r._element.get_or_add_rPr().find(qn("w:rFonts")).set(qn("w:eastAsia"), CN_SONG)
    return p


def _add_table(doc, rows):
    if not rows:
        return
    cols = max(len(r) for r in rows)
    t = doc.add_table(rows=0, cols=cols)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci in range(cols):
            txt = row[ci] if ci < len(row) else ""
            cp = cells[ci].paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER if ri == 0 else WD_ALIGN_PARAGRAPH.LEFT
            _emit_runs(cp, txt, size=SZ_SMALL)
            if ri == 0:
                for r in cp.runs:
                    r.font.bold = True
    doc.add_paragraph()


def markdown_to_docx(md_text, out_path, title=None, footer=True, toc=False):
    doc = Document()
    _style_base(doc)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.8)
        s.top_margin = s.bottom_margin = Cm(2.5)
        if footer:
            add_page_number_footer(s)

    if title:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run_font(p.add_run(title), cn=CN_HEI, size=SZ_TITLE, bold=True)
        p.paragraph_format.space_after = Pt(12)

    lines = md_text.splitlines()
    i, tbl_buf = 0, []
    while i < len(lines):
        ln = lines[i]
        # 表格聚合
        if ln.strip().startswith("|"):
            tbl_buf.append(ln)
            i += 1
            continue
        if tbl_buf:
            rows = []
            for tl in tbl_buf:
                if _RE_TBL_SEP.match(tl):
                    continue
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                rows.append(cells)
            _add_table(doc, rows)
            tbl_buf = []

        if not ln.strip():
            i += 1
            continue
        m = _RE_H.match(ln)
        if m:
            lvl = len(m.group(1))
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10 if lvl <= 2 else 6)
            p.paragraph_format.space_after = Pt(4)
            size = {1: SZ_H1, 2: SZ_H2, 3: SZ_H3}.get(lvl, SZ_BODY)
            set_run_font(p.add_run(m.group(2)), cn=CN_HEI, size=size, bold=True)
            p.style = doc.styles[f"Heading {min(lvl,4)}"]
            for r in p.runs:
                set_run_font(r, cn=CN_HEI, size=size, bold=True)
            i += 1
            continue
        m = _RE_UL.match(ln)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            _emit_runs(p, m.group(2))
            i += 1
            continue
        m = _RE_OL.match(ln)
        if m:
            p = doc.add_paragraph(style="List Number")
            _emit_runs(p, m.group(3))
            i += 1
            continue
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(SZ_BODY * 2)  # 中文首行缩进两字
        _emit_runs(p, ln)
        i += 1
    if tbl_buf:
        rows = [[c.strip() for c in tl.strip().strip("|").split("|")]
                for tl in tbl_buf if not _RE_TBL_SEP.match(tl)]
        _add_table(doc, rows)

    doc.save(str(out_path))
    return out_path


# ---------------------------------------------------------------- 批注（核心）
def iter_paragraphs(doc):
    """正文段落 + 所有表格单元格段落（含嵌套表）。
    审查意见表/成绩表通篇是表格，只遍历 doc.paragraphs 会漏掉锚点。"""
    for p in doc.paragraphs:
        yield p
    def walk_tables(tables):
        for t in tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        yield p
                    yield from walk_tables(cell.tables)
    yield from walk_tables(doc.tables)


def _merge_identical_runs(paragraph):
    """把相邻同格式 run 合并，否则锚点文本会被拆散导致定位失败。"""
    runs = paragraph.runs
    i = 0
    while i < len(runs) - 1:
        a, b = runs[i], runs[i + 1]
        if a._element.xml.split(">", 1)[0] == b._element.xml.split(">", 1)[0] and \
           a.bold == b.bold and a.italic == b.italic and a.font.size == b.font.size:
            a.text = a.text + b.text
            b._element.getparent().remove(b._element)
            runs = paragraph.runs
            continue
        i += 1


def _runs_for_span(paragraph, start, end):
    """把字符区间映射到 run 序列（批注只能锚在 run 边界上）。"""
    pos, hit = 0, []
    for r in paragraph.runs:
        rlen = len(r.text)
        if rlen == 0:
            continue
        r_start, r_end = pos, pos + rlen
        if r_end > start and r_start < end:
            hit.append(r)
        pos = r_end
        if pos >= end:
            break
    return hit


def add_comments(in_path, out_path, comments, author="导师", initials="T"):
    """
    comments: [{"anchor": "原文片段", "text": "批注内容", "author": 可选}]
    锚点支持同段落内任意子串；找不到时记录到 failed 列表而非静默跳过。
    """
    doc = Document(str(in_path))
    for p in iter_paragraphs(doc):
        _merge_identical_runs(p)

    ok, failed = [], []
    for item in comments:
        anchor = item.get("anchor", "").strip()
        body = item.get("text", "").strip()
        if not anchor:
            failed.append({"anchor": anchor, "reason": "空锚点"})
            continue
        placed = False
        for p in iter_paragraphs(doc):
            txt = p.text
            idx = txt.find(anchor)
            if idx < 0:
                continue
            hit = _runs_for_span(p, idx, idx + len(anchor))
            if not hit:
                continue
            try:
                doc.add_comment(hit, text=body,
                                author=item.get("author", author),
                                initials=item.get("initials", initials))
                ok.append({"anchor": anchor[:30], "chars": len(anchor)})
                placed = True
                break
            except Exception as e:  # noqa: BLE001
                failed.append({"anchor": anchor[:30], "reason": f"{type(e).__name__}: {e}"})
                placed = True
                break
        if not placed:
            failed.append({"anchor": anchor[:30], "reason": "正文中未找到该文本（可能跨段落或被拆分）"})

    doc.save(str(out_path))
    return {"placed": len(ok), "failed": failed, "detail": ok}


def inspect(path):
    doc = Document(str(path))
    cmts = []
    try:
        for c in doc.comments:
            cmts.append({"id": str(c.comment_id), "author": c.author, "text": c.text})
    except Exception:  # noqa: BLE001
        pass
    heads = [p.text for p in doc.paragraphs
             if p.style.name.startswith("Heading") and p.text.strip()]
    return {
        "paragraphs": len([p for p in doc.paragraphs if p.text.strip()]),
        "tables": len(doc.tables),
        "comments": len(cmts),
        "comment_detail": cmts,
        "headings": heads,
        "chars": sum(len(p.text) for p in doc.paragraphs),
    }


# ---------------------------------------------------------------- spec 构建
def build_from_spec(spec, out_path):
    """spec: {title, sections:[{heading, level, paras:[], table:{header,rows}, placeholder:bool}]}"""
    doc = Document()
    _style_base(doc)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.8)
        s.top_margin = s.bottom_margin = Cm(2.5)
        add_page_number_footer(s)
    if spec.get("title"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run_font(p.add_run(spec["title"]), cn=CN_HEI, size=SZ_TITLE, bold=True)
        p.paragraph_format.space_after = Pt(14)
    if spec.get("subtitle"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run_font(p.add_run(spec["subtitle"]), cn=CN_KAI, size=SZ_BODY)
        p.paragraph_format.space_after = Pt(10)
    for sec in spec.get("sections", []):
        if sec.get("heading"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            set_run_font(p.add_run(sec["heading"]), cn=CN_HEI, size=SZ_H2, bold=True)
        for para in sec.get("paras", []):
            p = doc.add_paragraph()
            if not sec.get("no_indent"):
                p.paragraph_format.first_line_indent = Pt(SZ_BODY * 2)
            _emit_runs(p, para)
        t = sec.get("table")
        if t:
            _add_table(doc, [t.get("header", [])] + t.get("rows", []))
        if sec.get("placeholder"):
            # 人工确认位：显式占位，提醒教师必须手改
            p = doc.add_paragraph()
            set_run_font(p.add_run(sec["placeholder"]), cn=CN_KAI, size=SZ_BODY, italic=True)
    doc.save(str(out_path))
    return out_path


def main():
    ap = argparse.ArgumentParser(prog="docx_kit", description="中文 Word 文档生产工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("md", help="Markdown → DOCX")
    a.add_argument("--in", dest="src", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--title")
    a.add_argument("--no-footer", action="store_true")

    b = sub.add_parser("comment", help="按锚点写 Word 原生批注")
    b.add_argument("--in", dest="src", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--comments", required=True, help="JSON 文件或 '-' 读 stdin")
    b.add_argument("--author", default="导师")
    b.add_argument("--initials", default="T")

    c = sub.add_parser("spec", help="JSON 规格 → DOCX")
    c.add_argument("--spec", required=True)
    c.add_argument("--out", required=True)

    d = sub.add_parser("inspect", help="读回结构与批注")
    d.add_argument("--in", dest="src", required=True)

    args = ap.parse_args()
    if args.cmd == "md":
        markdown_to_docx(Path(args.src).read_text(encoding="utf-8"), args.out,
                         title=args.title, footer=not args.no_footer)
        print(json.dumps(inspect(args.out), ensure_ascii=False, indent=2))
    elif args.cmd == "comment":
        raw = sys.stdin.read() if args.comments == "-" else Path(args.comments).read_text(encoding="utf-8")
        res = add_comments(args.src, args.out, json.loads(raw), args.author, args.initials)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        if res["failed"]:
            sys.exit(2)
    elif args.cmd == "spec":
        build_from_spec(json.loads(Path(args.spec).read_text(encoding="utf-8")), args.out)
        print(json.dumps(inspect(args.out), ensure_ascii=False, indent=2))
    elif args.cmd == "inspect":
        print(json.dumps(inspect(args.src), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
