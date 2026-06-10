#!/usr/bin/env python3
"""Generate HCNET-inspired PowerPoint template from hcnet.co.jp brand colors."""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "templates" / "assets"
LOGO_PATH = ASSETS / "hcnet_logo.jpg"
FOOTER_LOGO_PATH = ASSETS / "hcnet_footer_logo.png"

COLORS = {
    "primary": RGBColor(0x00, 0x8C, 0x41),
    "accent": RGBColor(0x00, 0xC0, 0x5B),
    "dark": RGBColor(0x24, 0x59, 0x3D),
    "light_bg": RGBColor(0xE5, 0xF9, 0xEE),
    "text": RGBColor(0x33, 0x33, 0x33),
    "text_light": RGBColor(0x66, 0x66, 0x66),
    "bg": RGBColor(0xF8, 0xF8, 0xF8),
    "white": RGBColor(0xFF, 0xFF, 0xFF),
    "cyan": RGBColor(0x00, 0x98, 0xA6),
}

FONT_JP = "Yu Gothic"
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
COMPANY = "エイチ・シー・ネットワークス株式会社"


def set_font(run, size: int, bold: bool = False, color=None, name: str = FONT_JP) -> None:
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = name
    if color:
        run.font.color.rgb = color


def add_rect(slide, left, top, width, height, fill_color, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape


def add_textbox(slide, left, top, width, height, text, size=18, bold=False, color=None, align=PP_ALIGN.LEFT):
    if color is None:
        color = COLORS["text"]
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_font(run, size, bold, color)
    return tb


def add_logo(slide, left, top, width, logo_path: Path = LOGO_PATH) -> None:
    if logo_path.exists():
        slide.shapes.add_picture(str(logo_path), left, top, width=width)


def add_header_bar(slide, title_text: str, subtitle: str | None = None, with_logo: bool = True) -> None:
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.12), COLORS["accent"])
    add_rect(slide, Inches(0), Inches(0.12), SLIDE_W, Inches(0.95), COLORS["primary"])
    title_left = Inches(0.6)
    if with_logo and LOGO_PATH.exists():
        add_logo(slide, Inches(11.2), Inches(0.28), Inches(1.8))
        title_left = Inches(0.6)
    add_textbox(slide, title_left, Inches(0.25), Inches(10), Inches(0.5), title_text, 24, True, COLORS["white"])
    if subtitle:
        add_textbox(slide, title_left, Inches(0.65), Inches(10), Inches(0.35), subtitle, 12, False, COLORS["light_bg"])
    add_rect(slide, Inches(0), Inches(7.2), SLIDE_W, Inches(0.3), COLORS["dark"])


def add_footer(slide, page_num: int | None = None, company: str = COMPANY, with_logo: bool = True) -> None:
    if with_logo and FOOTER_LOGO_PATH.exists():
        add_logo(slide, Inches(0.55), Inches(7.0), Inches(1.0), FOOTER_LOGO_PATH)
        add_textbox(slide, Inches(1.7), Inches(7.05), Inches(8), Inches(0.25), company, 9, False, COLORS["text_light"])
    else:
        add_textbox(slide, Inches(0.6), Inches(7.05), Inches(8), Inches(0.25), company, 9, False, COLORS["text_light"])
    if page_num:
        add_textbox(slide, Inches(12), Inches(7.05), Inches(0.8), Inches(0.25), str(page_num), 9, False, COLORS["text_light"], PP_ALIGN.RIGHT)


def add_bullets(slide, left, top, width, height, items, size=18, prefix="●  "):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(12)
        run = p.add_run()
        run.text = f"{prefix}{item}"
        set_font(run, size, False, COLORS["text"])
    return tb


def slide_title(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_rect(slide, Inches(0), Inches(0), Inches(0.35), SLIDE_H, COLORS["primary"])
    add_rect(slide, Inches(0), Inches(2.8), SLIDE_W, Inches(2.2), COLORS["primary"])
    add_rect(slide, Inches(0), Inches(2.75), SLIDE_W, Inches(0.08), COLORS["accent"])
    add_logo(slide, Inches(1), Inches(0.5), Inches(3.5))
    add_textbox(slide, Inches(1), Inches(3.0), Inches(11), Inches(0.8), "プレゼンテーションタイトル", 36, True, COLORS["white"])
    add_textbox(slide, Inches(1), Inches(3.85), Inches(11), Inches(0.5), "サブタイトル / 部署名 / 日付", 18, False, COLORS["light_bg"])
    add_textbox(slide, Inches(1), Inches(6.2), Inches(8), Inches(0.4), COMPANY, 14, False, COLORS["primary"])
    add_textbox(slide, Inches(1), Inches(6.55), Inches(8), Inches(0.35), "ネットワークのトータルソリューション", 11, False, COLORS["text_light"])


def slide_section(prs, page: int, num: str = "01") -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["bg"])
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.12), COLORS["accent"])
    add_logo(slide, Inches(0.6), Inches(0.35), Inches(2.2))
    add_rect(slide, Inches(0), Inches(2.5), Inches(8), Inches(2.5), COLORS["primary"])
    add_textbox(slide, Inches(0.8), Inches(3.0), Inches(7), Inches(0.9), num, 48, True, COLORS["accent"])
    add_textbox(slide, Inches(0.8), Inches(3.7), Inches(7), Inches(0.8), "セクションタイトル", 32, True, COLORS["white"])
    add_textbox(slide, Inches(8.5), Inches(3.2), Inches(4), Inches(1.5), "Section\nSubtitle", 14, False, COLORS["text_light"])
    add_footer(slide, page)


def slide_agenda(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "アジェンダ", "Agenda / Table of Contents")
    items = [
        ("01", "会社概要"),
        ("02", "製品・サービス"),
        ("03", "ソリューション"),
        ("04", "導入事例"),
        ("05", "まとめ"),
    ]
    for i, (num, title) in enumerate(items):
        y = 1.55 + i * 1.05
        add_rect(slide, Inches(0.8), Inches(y), Inches(0.9), Inches(0.7), COLORS["primary"])
        add_textbox(slide, Inches(0.8), Inches(y + 0.12), Inches(0.9), Inches(0.5), num, 20, True, COLORS["white"], PP_ALIGN.CENTER)
        add_textbox(slide, Inches(2.0), Inches(y + 0.15), Inches(9), Inches(0.5), title, 22, False, COLORS["text"])
        add_rect(slide, Inches(2.0), Inches(y + 0.65), Inches(10.5), Inches(0.02), COLORS["light_bg"])
    add_footer(slide, page)


def slide_content(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "コンテンツスライド", "Content Slide")
    add_bullets(slide, Inches(0.9), Inches(1.5), Inches(11), Inches(5), [
        "統合ITインフラソリューションの提案",
        "ネットワーク・セキュリティ・無線LAN",
        "構築から保守サービスまでワンストップ対応",
        "高い品質（High quality）と信頼（Confidence）",
    ], 20)
    add_rect(slide, Inches(0.6), Inches(1.35), Inches(0.08), Inches(4.5), COLORS["accent"])
    add_footer(slide, page)


def slide_two_column(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "2カラムレイアウト", "Two Column Layout")
    add_rect(slide, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.3), COLORS["light_bg"])
    add_rect(slide, Inches(0.6), Inches(1.4), Inches(5.8), Inches(0.06), COLORS["primary"])
    add_textbox(slide, Inches(0.9), Inches(1.6), Inches(5.2), Inches(0.5), "左カラム", 20, True, COLORS["primary"])
    add_textbox(slide, Inches(0.9), Inches(2.2), Inches(5.2), Inches(4), "製品・サービス\n\n● Adapterシリーズ\n● ネットワーク\n● 無線LAN\n● セキュリティ", 16)
    add_rect(slide, Inches(6.9), Inches(1.4), Inches(5.8), Inches(5.3), COLORS["bg"])
    add_rect(slide, Inches(6.9), Inches(1.4), Inches(5.8), Inches(0.06), COLORS["accent"])
    add_textbox(slide, Inches(7.2), Inches(1.6), Inches(5.2), Inches(0.5), "右カラム", 20, True, COLORS["primary"])
    add_textbox(slide, Inches(7.2), Inches(2.2), Inches(5.2), Inches(4), "ソリューション\n\n● 企業向けDX\n● キャンパスネットワーク\n● 医療ネットワーク\n● 社会インフラ", 16)
    add_footer(slide, page)


def slide_three_column(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "3カラムレイアウト", "Three Column Layout")
    columns = [
        ("ネットワーク", ["スイッチ", "ルータ", "SD-WAN"]),
        ("セキュリティ", ["FW", "SSE", "ZTNA"]),
        ("サービス", ["HiVAS", "運用管理", "コンサル"]),
    ]
    for i, (title, items) in enumerate(columns):
        x = 0.5 + i * 4.2
        add_rect(slide, Inches(x), Inches(1.4), Inches(3.9), Inches(5.3), COLORS["light_bg"] if i % 2 == 0 else COLORS["bg"])
        add_rect(slide, Inches(x), Inches(1.4), Inches(3.9), Inches(0.06), COLORS["primary"] if i == 0 else COLORS["accent"])
        add_textbox(slide, Inches(x + 0.2), Inches(1.55), Inches(3.5), Inches(0.4), title, 18, True, COLORS["primary"])
        add_bullets(slide, Inches(x + 0.2), Inches(2.1), Inches(3.5), Inches(4), items, 15)
    add_footer(slide, page)


def slide_image_text(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "画像＋テキスト", "Image + Text")
    add_rect(slide, Inches(0.6), Inches(1.4), Inches(6), Inches(5.3), COLORS["bg"])
    add_textbox(slide, Inches(1.5), Inches(3.5), Inches(4), Inches(0.5), "[ 画像をここに配置 ]", 16, False, COLORS["text_light"], PP_ALIGN.CENTER)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.4), Inches(6), Inches(5.3))
    shape.fill.background()
    shape.line.color.rgb = COLORS["primary"]
    shape.line.width = Pt(1)
    add_rect(slide, Inches(7), Inches(1.4), Inches(5.7), Inches(0.06), COLORS["primary"])
    add_textbox(slide, Inches(7), Inches(1.6), Inches(5.5), Inches(0.5), "ポイント", 22, True, COLORS["primary"])
    for i, pt in enumerate(["HiVAS運用サービス", "IT Asset管理", "SSEセキュリティ", "IEEE802.11ah対応"]):
        y = 2.3 + i * 0.9
        add_rect(slide, Inches(7), Inches(y), Inches(0.35), Inches(0.35), COLORS["accent"])
        add_textbox(slide, Inches(7.5), Inches(y - 0.05), Inches(5), Inches(0.4), pt, 16)
    add_footer(slide, page)


def slide_process(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "プロセス / フロー", "Process Flow")
    steps = [
        ("1", "ヒアリング", "要件定義"),
        ("2", "設計・提案", "最適な構成"),
        ("3", "構築", "導入・設定"),
        ("4", "保守", "運用サポート"),
    ]
    for i, (num, title, desc) in enumerate(steps):
        x = 0.7 + i * 3.1
        add_rect(slide, Inches(x), Inches(2.5), Inches(2.7), Inches(3.2), COLORS["light_bg"])
        add_rect(slide, Inches(x), Inches(2.5), Inches(2.7), Inches(0.55), COLORS["primary"])
        add_textbox(slide, Inches(x), Inches(2.58), Inches(2.7), Inches(0.4), f"STEP {num}", 14, True, COLORS["white"], PP_ALIGN.CENTER)
        add_textbox(slide, Inches(x + 0.15), Inches(3.3), Inches(2.4), Inches(0.5), title, 18, True, COLORS["primary"], PP_ALIGN.CENTER)
        add_textbox(slide, Inches(x + 0.15), Inches(3.9), Inches(2.4), Inches(0.8), desc, 13, False, COLORS["text_light"], PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            add_textbox(slide, Inches(x + 2.75), Inches(3.5), Inches(0.4), Inches(0.4), "→", 24, True, COLORS["accent"], PP_ALIGN.CENTER)
    add_footer(slide, page)


def slide_kpi(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "KPI / 数値", "Key Metrics")
    metrics = [
        ("30+", "年の実績", COLORS["primary"]),
        ("500+", "導入事例", COLORS["accent"]),
        ("99.9%", "可用性", COLORS["cyan"]),
        ("24/7", "サポート", COLORS["dark"]),
    ]
    for i, (value, label, color) in enumerate(metrics):
        x = 0.7 + i * 3.1
        add_rect(slide, Inches(x), Inches(2.2), Inches(2.8), Inches(3.5), COLORS["bg"])
        add_rect(slide, Inches(x), Inches(2.2), Inches(2.8), Inches(0.08), color)
        add_textbox(slide, Inches(x), Inches(2.8), Inches(2.8), Inches(1.0), value, 40, True, color, PP_ALIGN.CENTER)
        add_textbox(slide, Inches(x), Inches(4.0), Inches(2.8), Inches(0.5), label, 16, False, COLORS["text"], PP_ALIGN.CENTER)
    add_footer(slide, page)


def slide_comparison(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "比較", "Before / After Comparison")
    add_rect(slide, Inches(0.6), Inches(1.95), Inches(5.8), Inches(4.75), COLORS["bg"])
    add_rect(slide, Inches(6.9), Inches(1.95), Inches(5.8), Inches(4.75), COLORS["light_bg"])
    add_rect(slide, Inches(0.6), Inches(1.4), Inches(5.8), Inches(0.55), COLORS["text_light"])
    add_textbox(slide, Inches(0.6), Inches(1.48), Inches(5.8), Inches(0.4), "Before（導入前）", 18, True, COLORS["white"], PP_ALIGN.CENTER)
    add_bullets(slide, Inches(0.9), Inches(2.2), Inches(5.2), Inches(4), [
        "手作業による管理",
        "セキュリティリスク",
        "運用負荷が高い",
    ], 16)
    add_rect(slide, Inches(6.9), Inches(1.4), Inches(5.8), Inches(0.55), COLORS["primary"])
    add_textbox(slide, Inches(6.9), Inches(1.48), Inches(5.8), Inches(0.4), "After（導入後）", 18, True, COLORS["white"], PP_ALIGN.CENTER)
    add_bullets(slide, Inches(7.2), Inches(2.2), Inches(5.2), Inches(4), [
        "自動化された運用",
        "統合セキュリティ",
        "HiVASによる効率化",
    ], 16)
    add_textbox(slide, Inches(6.2), Inches(3.5), Inches(0.8), Inches(0.8), "→", 36, True, COLORS["accent"], PP_ALIGN.CENTER)
    add_footer(slide, page)


def slide_team(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "チーム / プロフィール", "Team / Profile")
    members = [
        ("営業部", "提案・見積"),
        ("技術部", "設計・構築"),
        ("サポート", "保守・運用"),
    ]
    for i, (dept, role) in enumerate(members):
        x = 0.9 + i * 4.0
        add_rect(slide, Inches(x), Inches(1.8), Inches(3.5), Inches(4.5), COLORS["bg"])
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 1.1), Inches(2.1), Inches(1.3), Inches(1.3))
        circle.fill.solid()
        circle.fill.fore_color.rgb = COLORS["light_bg"]
        circle.line.color.rgb = COLORS["primary"]
        add_textbox(slide, Inches(x + 1.1), Inches(2.45), Inches(1.3), Inches(0.5), "Photo", 11, False, COLORS["text_light"], PP_ALIGN.CENTER)
        add_textbox(slide, Inches(x), Inches(3.6), Inches(3.5), Inches(0.5), dept, 20, True, COLORS["primary"], PP_ALIGN.CENTER)
        add_textbox(slide, Inches(x), Inches(4.2), Inches(3.5), Inches(0.5), role, 14, False, COLORS["text_light"], PP_ALIGN.CENTER)
    add_footer(slide, page)


def slide_table(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "表・データ", "Table / Data")
    table_shape = slide.shapes.add_table(5, 4, Inches(0.6), Inches(1.5), Inches(12), Inches(4.5))
    table = table_shape.table
    headers = ["項目", "内容", "担当", "ステータス"]
    data = [
        ["製品A", "ネットワーク機器", "営業部", "対応中"],
        ["製品B", "セキュリティ", "技術部", "完了"],
        ["製品C", "無線LAN", "営業部", "計画中"],
        ["製品D", "サービス", "サポート", "対応中"],
    ]
    for j, header in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS["primary"]
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                set_font(run, 14, True, COLORS["white"])
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = value
            if i % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLORS["light_bg"]
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    set_font(run, 13, False, COLORS["text"])
    add_footer(slide, page)


def slide_quote(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["primary"])
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.12), COLORS["accent"])
    add_logo(slide, Inches(0.6), Inches(0.35), Inches(2.0))
    add_textbox(slide, Inches(1.5), Inches(2.5), Inches(10), Inches(1.5), '"高い品質と信頼できる\nネットワークを基本に"', 32, True, COLORS["white"], PP_ALIGN.CENTER)
    add_textbox(slide, Inches(1.5), Inches(4.5), Inches(10), Inches(0.5), "— HCNET Vision —", 16, False, COLORS["light_bg"], PP_ALIGN.CENTER)
    add_footer(slide, page, with_logo=False)


def slide_contact(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_header_bar(slide, "お問い合わせ / Q&A", "Contact / Q&A")
    add_rect(slide, Inches(0.6), Inches(1.5), Inches(5.5), Inches(5.2), COLORS["light_bg"])
    add_textbox(slide, Inches(0.9), Inches(1.7), Inches(5), Inches(0.4), "お問い合わせ先", 20, True, COLORS["primary"])
    add_textbox(slide, Inches(0.9), Inches(2.3), Inches(5), Inches(3.5),
                f"{COMPANY}\n\n"
                "🌐 www.hcnet.co.jp\n"
                "📧 inquiry@hcnet.co.jp\n"
                "📍 東京都台東区浅草橋\n\n"
                "お見積もり・技術相談は\n"
                "お気軽にお問い合わせください", 14, False, COLORS["text"])
    add_logo(slide, Inches(7.0), Inches(2.0), Inches(4.5))
    add_rect(slide, Inches(7.0), Inches(4.5), Inches(5.5), Inches(2.0), COLORS["primary"])
    add_textbox(slide, Inches(7.0), Inches(4.8), Inches(5.5), Inches(0.5), "Q & A", 24, True, COLORS["white"], PP_ALIGN.CENTER)
    add_textbox(slide, Inches(7.2), Inches(5.4), Inches(5.1), Inches(0.8), "ご質問をお待ちしております", 14, False, COLORS["light_bg"], PP_ALIGN.CENTER)
    add_footer(slide, page)


def slide_thank_you(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["white"])
    add_logo(slide, Inches(5.2), Inches(1.2), Inches(3.0))
    add_rect(slide, Inches(0), Inches(3.0), SLIDE_W, Inches(1.5), COLORS["primary"])
    add_rect(slide, Inches(0), Inches(2.95), SLIDE_W, Inches(0.08), COLORS["accent"])
    add_textbox(slide, Inches(0), Inches(3.2), SLIDE_W, Inches(0.8), "Thank You", 40, True, COLORS["white"], PP_ALIGN.CENTER)
    add_textbox(slide, Inches(0), Inches(4.0), SLIDE_W, Inches(0.5), "ご清聴ありがとうございました", 18, False, COLORS["light_bg"], PP_ALIGN.CENTER)
    add_textbox(slide, Inches(0), Inches(5.5), SLIDE_W, Inches(0.4), "www.hcnet.co.jp  |  お問い合わせ", 12, False, COLORS["text_light"], PP_ALIGN.CENTER)


def slide_guide(prs, page: int) -> None:
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, COLORS["bg"])
    add_header_bar(slide, "テンプレート使用ガイド", "Template Guide")
    guide = [
        "1: タイトル（表紙）",
        "2: セクション区切り",
        "3: アジェンダ",
        "4: 箇条書きコンテンツ",
        "5: 2カラム",
        "6: 3カラム",
        "7: 画像＋テキスト",
        "8: プロセス / フロー",
        "9: KPI / 数値",
        "10: 比較（Before/After）",
        "11: チーム / プロフィール",
        "12: 表・データ",
        "13: 引用・ハイライト",
        "14: お問い合わせ / Q&A",
        "15: Thank You",
    ]
    add_bullets(slide, Inches(0.9), Inches(1.35), Inches(5.5), Inches(5.5), guide, 13, "")
    colors_info = [
        ("Primary Green", "#008C41", COLORS["primary"]),
        ("Accent Green", "#00C05B", COLORS["accent"]),
        ("Dark Green", "#24593D", COLORS["dark"]),
        ("Light BG", "#E5F9EE", COLORS["light_bg"]),
        ("Text", "#333333", COLORS["text"]),
        ("Background", "#F8F8F8", COLORS["bg"]),
    ]
    add_textbox(slide, Inches(7), Inches(1.35), Inches(5), Inches(0.4), "カラーパレット（HCNET公式サイトより）", 16, True, COLORS["primary"])
    for i, (name, hex_code, rgb) in enumerate(colors_info):
        y = 1.85 + i * 0.75
        add_rect(slide, Inches(7), Inches(y), Inches(0.6), Inches(0.5), rgb)
        add_textbox(slide, Inches(7.8), Inches(y + 0.05), Inches(4.5), Inches(0.4), f"{name}  {hex_code}", 13)
    add_textbox(slide, Inches(7), Inches(6.3), Inches(5.5), Inches(0.5),
                "ファイル: .pptx / .potx\nOffice 365対応", 11, False, COLORS["text_light"])
    add_footer(slide, page)


def build_template() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_title(prs, 1)
    slide_section(prs, 2)
    slide_agenda(prs, 3)
    slide_content(prs, 4)
    slide_two_column(prs, 5)
    slide_three_column(prs, 6)
    slide_image_text(prs, 7)
    slide_process(prs, 8)
    slide_kpi(prs, 9)
    slide_comparison(prs, 10)
    slide_team(prs, 11)
    slide_table(prs, 12)
    slide_quote(prs, 13)
    slide_contact(prs, 14)
    slide_thank_you(prs, 15)
    slide_guide(prs, 16)

    return prs


def convert_pptx_to_potx(pptx_path: Path, potx_path: Path) -> None:
    """Convert PPTX to POTX by updating OOXML content types."""
    shutil.copy2(pptx_path, potx_path)
    with zipfile.ZipFile(potx_path, "r") as zin:
        content_types = zin.read("[Content_Types].xml").decode("utf-8")

    content_types = content_types.replace(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
        "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml",
    )
    if "presentationml.template.main+xml" not in content_types:
        content_types = re.sub(
            r'(PartName="/ppt/presentation\.xml"\s+ContentType=")[^"]+(")',
            r"\1application/vnd.openxmlformats-officedocument.presentationml.template.main+xml\2",
            content_types,
        )

    temp_path = potx_path.with_suffix(".potx.tmp")
    with zipfile.ZipFile(potx_path, "r") as zin, zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = content_types.encode("utf-8")
            zout.writestr(item, data)

    temp_path.replace(potx_path)


def main() -> None:
    out_dir = ROOT / "docs" / "templates"
    out_dir.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    pptx_path = out_dir / "HCNET_PowerPoint_Template.pptx"
    potx_path = out_dir / "HCNET_PowerPoint_Template.potx"

    prs = build_template()
    prs.save(pptx_path)
    convert_pptx_to_potx(pptx_path, potx_path)

    print(f"Saved: {pptx_path} ({len(prs.slides)} slides)")
    print(f"Saved: {potx_path} (Office 365 template)")


if __name__ == "__main__":
    main()
