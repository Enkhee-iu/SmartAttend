#!/usr/bin/env python3
"""HCNET-style launcher for monthly report generators."""

from __future__ import annotations

from pathlib import Path

from generate_issue_reports import generate_reports
from generate_cloud_report import run_gui as run_cloud_report_gui


HCNET_BLUE = "#005BAC"
HCNET_GREEN = "#00A95F"
BACKGROUND = "#F4F8FB"
PANEL = "#FFFFFF"
TEXT = "#1F2933"
MUTED = "#5F6B76"


def run_maintenance_report(root) -> None:
    from tkinter import filedialog, messagebox

    issues_file = filedialog.askopenfilename(
        parent=root,
        title="issues.csv を選択してください",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not issues_file:
        return

    try:
        result = generate_reports(Path(issues_file), output_dir=Path(issues_file).parent)
    except Exception as exc:
        messagebox.showerror("月次保守定期報告書", f"作成に失敗しました。\n\n{exc}", parent=root)
        return

    messagebox.showinfo(
        "月次保守定期報告書",
        "\n".join(
            [
                "レポート作成が完了しました。",
                "",
                f"入力: {result['issues_csv']}",
                f"文字コード: {result['encoding']}",
                f"総件数: {result['total']}",
                f"ヘルプデスク: {result['helpdesk_count']}",
                f"保守: {result['maintenance_count']}",
                "",
                "出力先:",
                f"1) {result['helpdesk_output']}",
                f"2) {result['maintenance_output']}",
            ]
        ),
        parent=root,
    )


def make_button(parent, text, description, command, accent_color):
    import tkinter as tk

    frame = tk.Frame(parent, bg=PANEL, highlightbackground="#D8E2EC", highlightthickness=1)
    frame.pack(fill="x", padx=28, pady=10)

    title = tk.Label(
        frame,
        text=text,
        bg=PANEL,
        fg=TEXT,
        font=("Yu Gothic UI", 15, "bold"),
        anchor="w",
    )
    title.pack(fill="x", padx=18, pady=(16, 2))

    desc = tk.Label(
        frame,
        text=description,
        bg=PANEL,
        fg=MUTED,
        font=("Yu Gothic UI", 10),
        anchor="w",
        justify="left",
    )
    desc.pack(fill="x", padx=18, pady=(0, 12))

    button = tk.Button(
        frame,
        text="作成を開始",
        command=command,
        bg=accent_color,
        fg="white",
        activebackground=accent_color,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        font=("Yu Gothic UI", 11, "bold"),
        padx=16,
        pady=8,
    )
    button.pack(anchor="e", padx=18, pady=(0, 16))
    return frame


def main() -> int:
    import tkinter as tk

    root = tk.Tk()
    root.title("HCNET 月次報告書作成ツール")
    root.geometry("640x430")
    root.minsize(600, 400)
    root.configure(bg=BACKGROUND)

    header = tk.Frame(root, bg=HCNET_BLUE)
    header.pack(fill="x")

    logo = tk.Label(
        header,
        text="HCNET",
        bg=HCNET_BLUE,
        fg="white",
        font=("Yu Gothic UI", 24, "bold"),
        anchor="w",
    )
    logo.pack(fill="x", padx=28, pady=(20, 0))

    subtitle = tk.Label(
        header,
        text="月次報告書作成ツール",
        bg=HCNET_BLUE,
        fg="white",
        font=("Yu Gothic UI", 11),
        anchor="w",
    )
    subtitle.pack(fill="x", padx=30, pady=(0, 20))

    intro = tk.Label(
        root,
        text="作成するレポートを選択してください。",
        bg=BACKGROUND,
        fg=TEXT,
        font=("Yu Gothic UI", 12),
        anchor="w",
    )
    intro.pack(fill="x", padx=28, pady=(24, 8))

    make_button(
        root,
        "1. 月次保守定期報告書",
        "issues.csv を選択し、ヘルプデスク報告書と保守対応定期報告書を作成します。",
        lambda: run_maintenance_report(root),
        HCNET_BLUE,
    )

    make_button(
        root,
        "2. HCNETクラウド月次報告書",
        "今後追加予定のクラウド月次報告書作成機能です。",
        lambda: run_cloud_report_gui(root),
        HCNET_GREEN,
    )

    footer = tk.Label(
        root,
        text="High quality, Confidence, Networks",
        bg=BACKGROUND,
        fg=MUTED,
        font=("Yu Gothic UI", 9),
    )
    footer.pack(side="bottom", pady=12)

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
