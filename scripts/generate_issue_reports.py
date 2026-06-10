#!/usr/bin/env python3
r"""Generate monthly Hitachi City issue reports from an issues.csv export.

Usage examples:

  python scripts/generate_issue_reports.py

  python scripts/generate_issue_reports.py issues.csv

  python scripts/generate_issue_reports.py ^
    "z:\hh00330\OneDrive - APS-HCNETグループ\PassageDrive\Workspace\Downloads\issues.csv" ^
    --output-dir "z:\hh00330\OneDrive - APS-HCNETグループ\PassageDrive\Workspace\Downloads"

The script creates two Excel files:
  1.日立市様ヘルプデスク2026年5月分ご報告.xlsx
  2.日立市様各種賃貸借契約に対する保守対応定期報告書2026年5月分ご報告.xlsx
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import warnings
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message="Title is more than 31 characters.*",
    category=UserWarning,
    module="openpyxl.workbook.child",
)

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ModuleNotFoundError as exc:
    raise SystemExit(
        "openpyxl is required. Install it with: python -m pip install -r requirements.txt"
    ) from exc


HELP_DESK_REPORT_NAME = "1.日立市様ヘルプデスク2026年5月分ご報告.xlsx"
MAINTENANCE_REPORT_NAME = "2.日立市様各種賃貸借契約に対する保守対応定期報告書2026年5月分ご報告.xlsx"

HELP_DESK_SHEET_NAME = "日立市様ヘルプデスク2026年5月分ご報告"
MAINTENANCE_SHEET_NAME = "日立市様各種賃貸借契約に対する保守対応定期報告書2026年5月分ご報告"

ENCODINGS_TO_TRY = ("utf-8-sig", "cp932", "shift_jis", "utf-8")


HELP_DESK_KEYWORDS = (
    ("DNS/DKIM/Salesforce support", ("DNS", "DKIM", "Salesforce", "domainkey")),
    ("mail/log investigation", ("メール", "mail", "email", "@", "SIARICHVE", "ログ")),
    ("security/server support", ("ESET", "サーバ", "server", "パスワード", "ログイン")),
    ("Office/iFilter authentication support", ("office", "Office", "iFilter", "ifilter", "認証", "WiFi", "wifi")),
    ("touchpad/device setting support", ("タッチパッド", "touchpad", "Bluetooth", "デバイスマネージャ", "device manager")),
    ("software/account investigation", ("アカウント", "問い合わせ", "調査", "確認", "設定変更")),
)

MAINTENANCE_KEYWORDS = (
    ("LAN cable/port maintenance", ("LANケーブル", "LANポート", "LANコネクタ", "LAN", "コネクタ")),
    ("AC adapter or power maintenance", ("ACアダプタ", "AC", "アダプタ", "充電", "電源")),
    ("mouse maintenance", ("マウス", "ホイール")),
    ("keyboard/top-cover maintenance", ("キーボード", "キー", "トップカバー")),
    ("printer/copier maintenance", ("プリンタ", "プリンター", "複合機", "Canon", "PIXUS", "P 6520", "TR703", "PR")),
    ("hardware repair/replacement", ("HP", "修理", "交換", "破損", "故障", "不具合", "代替機", "設置")),
)

DATA_HEADERS = [
    "番号",
    "受付No",
    "受付日",
    "作業完了日",
    "状況",
    "顧客",
    "ご担当者",
    "機器名",
    "物品型式",
    "製造番号",
    "症状",
    "原因",
    "処置",
]

FIELD_ALIASES = {
    "source_id": ("#", "番号", "No", "ID", "source_id"),
    "title": ("題名", "件名", "タイトル", "title_raw"),
    "received_date": ("受付日", "受付日時", "start_date"),
    "completed_date": ("作業完了日", "完了日", "対応完了日", "作業期限", "期限", "due_date"),
    "status": ("状況", "状態", "ステータス", "work_type_raw", "classification"),
    "customer": ("顧客", "顧客名", "依頼元", "requester_or_site_raw"),
    "person": ("ご担当者", "担当者", "顧客担当者", "contact_raw"),
    "asset": ("機器名", "機器番号", "資産番号", "ホスト", "asset_id"),
    "model": ("物品型式", "型式", "機種", "モデル", "model"),
    "serial": ("製造番号", "シリアル番号", "serial_number"),
    "symptom": ("症状", "現象", "障害内容", "内容", "issue_raw"),
    "cause": ("原因", "cause_raw"),
    "action": ("処置", "処置内容", "対応", "対応内容", "action_raw"),
}

# Fallback positions for the issue export used in this task.
FIELD_POSITIONS = {
    "source_id": 0,
    "title": 1,
    "received_date": 2,
    "completed_date": 3,
    "status": 4,
    "customer": 5,
    "person": 6,
    "asset": 7,
    "model": 8,
    "serial": 9,
    "symptom": 11,
    "cause": 12,
    "action": 13,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read issues.csv and create help desk / maintenance Excel reports.",
    )
    parser.add_argument(
        "issues_csv",
        nargs="?",
        default=None,
        help="Path to issues.csv. If omitted, a file picker is opened.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory where the two Excel files are written. Default: same directory as issues.csv",
    )
    parser.add_argument(
        "--helpdesk-output",
        default=None,
        help=f"Full output path for {HELP_DESK_REPORT_NAME}. Overrides --output-dir for this file.",
    )
    parser.add_argument(
        "--maintenance-output",
        default=None,
        help=f"Full output path for {MAINTENANCE_REPORT_NAME}. Overrides --output-dir for this file.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open a file picker for issues.csv and save reports next to the selected file.",
    )
    return parser.parse_args()


def read_csv_rows(path: Path) -> tuple[list[str], list[list[str]], str]:
    raw = path.read_bytes()
    decoded_candidates: list[tuple[int, str, str]] = []

    for encoding in ENCODINGS_TO_TRY:
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        decoded_candidates.append((text.count("\ufffd"), encoding, text))

    if decoded_candidates:
        _, encoding, text = min(decoded_candidates, key=lambda item: item[0])
    else:
        encoding = "utf-8-replace"
        text = raw.decode("utf-8", errors="replace")

    reader = csv.reader(io.StringIO(text, newline=""))
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError(f"No rows found in CSV: {path}")

    max_columns = max(len(row) for row in rows)
    padded_rows = [row + [""] * (max_columns - len(row)) for row in rows]
    header = padded_rows[0]
    data_rows = padded_rows[1:]
    return header, data_rows, encoding


def contains_keyword(text: str, keyword: str) -> bool:
    if keyword.isascii():
        return keyword.lower() in text.lower()
    return keyword in text


def score_keywords(text: str, keyword_groups: tuple[tuple[str, tuple[str, ...]], ...]) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []

    for reason, keywords in keyword_groups:
        matches = [keyword for keyword in keywords if contains_keyword(text, keyword)]
        if matches:
            score += len(matches)
            reasons.append(reason)

    return score, "; ".join(reasons)


def classify_row(row: list[str]) -> tuple[str, str]:
    text = " ".join(cell for cell in row if cell)
    help_score, help_reason = score_keywords(text, HELP_DESK_KEYWORDS)
    maintenance_score, maintenance_reason = score_keywords(text, MAINTENANCE_KEYWORDS)

    if "touchpad/device setting support" in help_reason:
        return "help desk", help_reason

    # Strongly software/service-oriented rows should remain help desk even when they
    # mention devices as context. Hardware replacement/repair defaults to maintenance.
    if help_score > 0 and maintenance_score == 0:
        return "help desk", help_reason
    if help_score >= maintenance_score + 2:
        return "help desk", help_reason
    if maintenance_score > 0:
        return "maintenance", maintenance_reason
    return "maintenance", "default: no help desk keyword matched"


def normalise_header(header: list[str]) -> list[str]:
    return [cell.strip() if cell.strip() else f"source_column_{index}" for index, cell in enumerate(header, start=1)]


def build_column_map(header: list[str]) -> dict[str, int]:
    normalised = [cell.strip() for cell in header]
    column_map: dict[str, int] = {}

    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in normalised:
                column_map[field] = normalised.index(alias)
                break
        if field not in column_map:
            fallback = FIELD_POSITIONS[field]
            if fallback < len(header):
                column_map[field] = fallback

    return column_map


def get_value(row: list[str], column_map: dict[str, int], field: str) -> str:
    index = column_map.get(field)
    if index is None or index >= len(row):
        return ""
    return row[index].strip()


def ticket_number(row: list[str], column_map: dict[str, int]) -> str:
    title = get_value(row, column_map, "title")
    source_id = get_value(row, column_map, "source_id")
    for value in (title, source_id):
        start = value.find("[")
        end = value.find("]", start + 1)
        if start != -1 and end != -1:
            return value[start + 1 : end]
    return source_id


def issue_text(row: list[str], column_map: dict[str, int]) -> str:
    return " ".join(
        value
        for value in (
            get_value(row, column_map, "symptom"),
            get_value(row, column_map, "cause"),
            get_value(row, column_map, "action"),
        )
        if value
    )


def classify_issue(row: list[str], column_map: dict[str, int]) -> tuple[str, str]:
    text = issue_text(row, column_map)
    help_score, help_reason = score_keywords(text, HELP_DESK_KEYWORDS)
    maintenance_score, maintenance_reason = score_keywords(text, MAINTENANCE_KEYWORDS)

    if "touchpad/device setting support" in help_reason:
        return "help desk", help_reason
    if help_score > 0 and maintenance_score == 0:
        return "help desk", help_reason
    if help_score >= maintenance_score + 2:
        return "help desk", help_reason
    if maintenance_score > 0:
        return "maintenance", maintenance_reason
    return "maintenance", "default: no help desk keyword matched in 症状/原因/処置"


def report_row(row: list[str], column_map: dict[str, int], number: int) -> list[str]:
    status = get_value(row, column_map, "status") or "作業完了"
    return [
        number,
        ticket_number(row, column_map),
        get_value(row, column_map, "received_date"),
        get_value(row, column_map, "completed_date"),
        status,
        get_value(row, column_map, "customer"),
        get_value(row, column_map, "person"),
        get_value(row, column_map, "asset"),
        get_value(row, column_map, "model"),
        get_value(row, column_map, "serial"),
        get_value(row, column_map, "symptom"),
        get_value(row, column_map, "cause"),
        get_value(row, column_map, "action"),
    ]


def format_data_sheet(worksheet) -> None:
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    header_font = Font(bold=True)
    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border

    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = border

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column_cells in worksheet.columns:
        column_letter = get_column_letter(column_cells[0].column)
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 60)


def add_report_data_sheet(worksheet, report_rows: list[list[str]]) -> None:
    worksheet.append(DATA_HEADERS)
    for row in report_rows:
        worksheet.append(row)
    format_data_sheet(worksheet)


def add_raw_sheet(worksheet, source_header: list[str], source_rows: list[list[str]]) -> None:
    worksheet.append(normalise_header(source_header))
    for row in source_rows:
        worksheet.append(row)
    format_data_sheet(worksheet)


def count_matching(rows: list[list[str]], keywords: tuple[str, ...]) -> int:
    count = 0
    for row in rows:
        text = " ".join(str(cell) for cell in row if cell)
        if any(contains_keyword(text, keyword) for keyword in keywords):
            count += 1
    return count


def maintenance_note(rows: list[list[str]]) -> str:
    parts = [
        ("マウス交換", count_matching(rows, ("マウス", "ホイール"))),
        ("ベースエンクロージャー交換", count_matching(rows, ("ベースエンクロージャー", "LANポート"))),
        ("ACアダプタ交換", count_matching(rows, ("ACアダプタ", "充電", "電源"))),
        ("LANケーブル対応", count_matching(rows, ("LANケーブル", "LANコネクタ"))),
        ("キーボード対応", count_matching(rows, ("キーボード", "トップカバー"))),
        ("プリンタ対応", count_matching(rows, ("プリンタ", "プリンター", "複合機", "Canon", "PIXUS"))),
    ]
    visible = [f"{label}:{count}件" for label, count in parts if count]
    if not visible:
        return "特にございません。"
    return "・" + "、".join(visible) + "ございました。"


def apply_border(ws, cell_range: str, style: str = "thin") -> None:
    side = Side(style=style, color="000000")
    border = Border(left=side, right=side, top=side, bottom=side)
    for row in ws[cell_range]:
        for cell in row:
            cell.border = border


def add_maintenance_summary_sheet(worksheet, maintenance_rows: list[list[str]]) -> None:
    total = len(maintenance_rows)
    completed = sum(1 for row in maintenance_rows if "完了" in str(row[4]))
    in_progress = total - completed

    worksheet.title = "特記事項"
    worksheet.sheet_view.showGridLines = False
    for column in range(1, 12):
        worksheet.column_dimensions[get_column_letter(column)].width = 14
    worksheet.column_dimensions["A"].width = 4
    worksheet.column_dimensions["B"].width = 16
    for row in range(1, 31):
        worksheet.row_dimensions[row].height = 20

    yellow = PatternFill("solid", fgColor="FFFF00")
    green = PatternFill("solid", fgColor="C6EFCE")
    thick = Side(style="medium", color="000000")
    thin = Side(style="thin", color="000000")
    dotted = Side(style="dotted", color="808080")

    worksheet.merge_cells("A3:K3")
    title_cell = worksheet["A3"]
    title_cell.value = "日立市役所様 本庁及び出先機関 各種賃貸借契約に対する保守対応＜2026年5月度＞月次作業報告書"
    title_cell.fill = yellow
    title_cell.font = Font(bold=True, size=12)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    labels = [
        (4, "保守期間", "2026年5月1日～2026年5月31日"),
        (5, "報　告", "エイチ・シー・ネットワークス株式会社"),
        (6, "責 任 者", "宮本　良一"),
        (7, "担　当", "保守: 池田 修司　営業: 小瀬 賢弘"),
    ]
    for row_num, label, value in labels:
        worksheet.merge_cells(start_row=row_num, start_column=2, end_row=row_num, end_column=3)
        worksheet.merge_cells(start_row=row_num, start_column=4, end_row=row_num, end_column=11)
        worksheet.cell(row=row_num, column=2, value=label).alignment = Alignment(horizontal="center")
        worksheet.cell(row=row_num, column=4, value=value)

    worksheet.merge_cells("A8:K8")
    worksheet["A8"] = "特記事項"
    worksheet["A8"].fill = green
    worksheet["A8"].alignment = Alignment(horizontal="center")

    sections = [
        (9, 13, "トピックス", ["特にございません。"]),
        (
            14,
            19,
            "対応状況",
            [
                f"今月は、{total}件作業対応になります。",
                f"詳細は次頁によります。(作業完了：{completed}件、対応中：{in_progress}件)",
                f"〈内訳は、ハード修理:{total}件となっております。〉",
            ],
        ),
        (20, 25, "今月の\n問題点", ["特にございません。"]),
        (26, 29, "備考", [maintenance_note(maintenance_rows)]),
    ]
    for start_row, end_row, label, lines in sections:
        worksheet.merge_cells(start_row=start_row, start_column=1, end_row=end_row, end_column=2)
        worksheet.cell(row=start_row, column=1, value=label).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for offset, line in enumerate(lines):
            worksheet.merge_cells(start_row=start_row + offset, start_column=3, end_row=start_row + offset, end_column=11)
            worksheet.cell(row=start_row + offset, column=3, value=line).alignment = Alignment(wrap_text=True, vertical="top")
        for row_num in range(start_row, end_row + 1):
            for col_num in range(3, 12):
                worksheet.cell(row=row_num, column=col_num).border = Border(bottom=dotted)

    apply_border(worksheet, "A3:K29")
    for cell in worksheet["A3:K3"][0]:
        cell.border = Border(left=thin, right=thin, top=thick, bottom=thin)


def write_helpdesk_workbook(
    path: Path,
    source_header: list[str],
    source_rows: list[list[str]],
    helpdesk_rows: list[list[str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = HELP_DESK_SHEET_NAME
    add_report_data_sheet(worksheet, helpdesk_rows)
    raw_sheet = workbook.create_sheet("元データ")
    add_raw_sheet(raw_sheet, source_header, source_rows)
    workbook.save(path)


def write_maintenance_workbook(
    path: Path,
    source_header: list[str],
    source_rows: list[list[str]],
    maintenance_rows: list[list[str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    summary_sheet = workbook.active
    add_maintenance_summary_sheet(summary_sheet, maintenance_rows)
    data_sheet = workbook.create_sheet("データ")
    add_report_data_sheet(data_sheet, maintenance_rows)
    raw_sheet = workbook.create_sheet("元データ2")
    add_raw_sheet(raw_sheet, source_header, source_rows)
    workbook.save(path)


def output_paths(args: argparse.Namespace, issues_csv: Path) -> tuple[Path, Path]:
    output_dir = Path(args.output_dir) if args.output_dir else issues_csv.parent
    helpdesk_output = Path(args.helpdesk_output) if args.helpdesk_output else output_dir / HELP_DESK_REPORT_NAME
    maintenance_output = (
        Path(args.maintenance_output)
        if args.maintenance_output
        else output_dir / MAINTENANCE_REPORT_NAME
    )
    return helpdesk_output, maintenance_output


def generate_reports(
    issues_csv: Path,
    output_dir: Path | None = None,
    helpdesk_output: Path | None = None,
    maintenance_output: Path | None = None,
) -> dict[str, object]:
    if not issues_csv.exists():
        raise FileNotFoundError(f"CSV file not found: {issues_csv}")

    source_header, source_rows, encoding = read_csv_rows(issues_csv)
    column_map = build_column_map(source_header)
    classified_rows = [(row, *classify_issue(row, column_map)) for row in source_rows]
    helpdesk_rows = []
    maintenance_rows = []
    for row, classification, _reason in classified_rows:
        if classification == "help desk":
            helpdesk_rows.append(report_row(row, column_map, len(helpdesk_rows) + 1))
        else:
            maintenance_rows.append(report_row(row, column_map, len(maintenance_rows) + 1))

    output_dir = output_dir if output_dir else issues_csv.parent
    helpdesk_path = helpdesk_output if helpdesk_output else output_dir / HELP_DESK_REPORT_NAME
    maintenance_path = (
        maintenance_output
        if maintenance_output
        else output_dir / MAINTENANCE_REPORT_NAME
    )
    write_helpdesk_workbook(helpdesk_path, source_header, source_rows, helpdesk_rows)
    write_maintenance_workbook(maintenance_path, source_header, source_rows, maintenance_rows)

    return {
        "issues_csv": issues_csv,
        "encoding": encoding,
        "total": len(source_rows),
        "helpdesk_count": len(helpdesk_rows),
        "maintenance_count": len(maintenance_rows),
        "helpdesk_output": helpdesk_path,
        "maintenance_output": maintenance_path,
    }


def run_gui() -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except Exception as exc:
        print(f"GUI could not be started: {exc}", file=sys.stderr)
        return 1

    root = tk.Tk()
    root.withdraw()
    root.update()

    issues_file = filedialog.askopenfilename(
        title="issues.csv を選択してください",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not issues_file:
        return 0

    desktop_dir = Path.home() / "Desktop"
    initial_dir = desktop_dir if desktop_dir.exists() else Path(issues_file).parent
    output_dir = filedialog.askdirectory(
        title="Excelファイルの保存先フォルダを選択してください",
        initialdir=str(initial_dir),
    )
    output_path = Path(output_dir) if output_dir else initial_dir

    try:
        result = generate_reports(Path(issues_file), output_dir=output_path)
    except Exception as exc:
        messagebox.showerror("Report generation failed", str(exc))
        return 1

    messagebox.showinfo(
        "Report generation completed",
        "\n".join(
            [
                "Excel files were created successfully.",
                "",
                f"Total issues: {result['total']}",
                f"Help desk: {result['helpdesk_count']}",
                f"Maintenance: {result['maintenance_count']}",
                "",
                f"1) {result['helpdesk_output']}",
                f"2) {result['maintenance_output']}",
            ]
        ),
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.gui or args.issues_csv is None:
        return run_gui()

    issues_csv = Path(args.issues_csv)
    helpdesk_output, maintenance_output = output_paths(args, issues_csv)

    try:
        result = generate_reports(
            issues_csv,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            helpdesk_output=helpdesk_output,
            maintenance_output=maintenance_output,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Read CSV: {result['issues_csv']}")
    print(f"Detected encoding: {result['encoding']}")
    print(f"Total issues: {result['total']}")
    print(f"Help desk: {result['helpdesk_count']} -> {result['helpdesk_output']}")
    print(f"Maintenance: {result['maintenance_count']} -> {result['maintenance_output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
