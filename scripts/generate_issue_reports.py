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
    from openpyxl.styles import Alignment, Font, PatternFill
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
    ("mouse maintenance", ("マウス", "ホイール", "}�E�X")),
    ("keyboard/top-cover maintenance", ("キーボード", "キー", "トップカバー", "�L�[")),
    ("printer/copier maintenance", ("プリンタ", "プリンター", "複合機", "Canon", "PIXUS", "P 6520", "TR703", "PR")),
    ("hardware repair/replacement", ("HP", "修理", "交換", "破損", "故障", "不具合", "代替機", "設置")),
)


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


def add_rows_to_sheet(
    worksheet,
    source_header: list[str],
    classified_rows: list[tuple[list[str], str, str]],
) -> None:
    output_header = ["分類", "分類理由", *normalise_header(source_header)]
    worksheet.append(output_header)

    for row, classification, reason in classified_rows:
        worksheet.append([classification, reason, *row])


def format_sheet(worksheet) -> None:
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    header_font = Font(bold=True)

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column_cells in worksheet.columns:
        column_letter = get_column_letter(column_cells[0].column)
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 60)


def write_workbook(
    path: Path,
    sheet_name: str,
    source_header: list[str],
    classified_rows: list[tuple[list[str], str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name
    add_rows_to_sheet(worksheet, source_header, classified_rows)
    format_sheet(worksheet)
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
    classified_rows = [(row, *classify_row(row)) for row in source_rows]
    helpdesk_rows = [row for row in classified_rows if row[1] == "help desk"]
    maintenance_rows = [row for row in classified_rows if row[1] == "maintenance"]

    output_dir = output_dir if output_dir else issues_csv.parent
    helpdesk_path = helpdesk_output if helpdesk_output else output_dir / HELP_DESK_REPORT_NAME
    maintenance_path = (
        maintenance_output
        if maintenance_output
        else output_dir / MAINTENANCE_REPORT_NAME
    )
    write_workbook(helpdesk_path, HELP_DESK_SHEET_NAME, source_header, helpdesk_rows)
    write_workbook(maintenance_path, MAINTENANCE_SHEET_NAME, source_header, maintenance_rows)

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
