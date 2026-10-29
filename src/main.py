# -*- coding: utf-8 -*-
"""
المُنسّق: جلب الأوقات ← رسم الموارد ← حزم الواجهة ← إرسالها عبر تليجرام.

الاستعمال:
    python src\main.py            الدورة كاملة مع الإرسال
    python src\main.py --no-send  توليد الملف فقط بلا إرسال
"""
from __future__ import annotations

import shutil
import sys
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config as C
from times import get_times, validity_range
from render import render_all
from pack import build


def run(send: bool = True) -> Path:
    print(f"[1/4] جلب أوقات {C.CITY} بطريقة ديانيت...")
    result = get_times()
    day = result["date"]
    times = result["times"]
    for key, label in C.PRAYERS:
        print(f"      {label:<8} {times[key]}")

    print(f"[2/4] رسم الموارد ({C.SCREEN_W}x{C.SCREEN_H})...")
    render_all(times)

    print("[3/4] حزم الواجهة...")
    packed, mode = build(with_animation=C.ANIM_ON)
    print(f"      الصيغة المقبولة: {mode}")

    C.OUT_DIR.mkdir(parents=True, exist_ok=True)
    final = C.OUT_DIR / f"prayer-{day.isoformat()}.bin"
    shutil.copy2(packed, final)
    print(f"      {final.name}  ({final.stat().st_size:,} بايت)")

    if send:
        print("[4/4] الإرسال عبر تليجرام...")
        from deliver import send_watchface
        start, end = validity_range()
        caption = (
            f"أوقات الصلاة — {C.CITY}\n"
            f"سارية من {start.isoformat()} إلى {end.isoformat()}\n"
            f"محسوبة ليوم {day.isoformat()} (ديانيت)\n\n"
            "التركيب: افتح الملف ← Gadgetbridge ← Install"
        )
        send_watchface(final, caption)
        print("      أُرسل.")
    else:
        print("[4/4] تخطّي الإرسال (--no-send)")

    return final


def main() -> int:
    send = "--no-send" not in sys.argv
    try:
        final = run(send=send)
        print(f"\nتمّ: {final}")
        return 0
    except Exception as exc:
        print(f"\nفشل: {exc}", file=sys.stderr)
        traceback.print_exc()
        if send:
            try:
                from deliver import send_message
                send_message(f"فشل توليد واجهة أوقات الصلاة:\n{exc}")
            except Exception:
                pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
