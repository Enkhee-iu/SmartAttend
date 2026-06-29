"""Placeholder for the HCNET cloud monthly report workflow."""

from __future__ import annotations


def run_gui(parent=None) -> None:
    try:
        from tkinter import messagebox
    except Exception:
        return

    messagebox.showinfo(
        "HCNETクラウド月次報告書",
        "HCNETクラウド月次報告書の作成機能はまだ準備中です。\n"
        "後続の指示に合わせて、この機能を別モジュールとして実装します。",
        parent=parent,
    )
