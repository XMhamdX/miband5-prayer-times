# -*- coding: utf-8 -*-
"""
جلب أوقات الصلاة بطريقة ديانيت التركية.

المصدر الأساسي: Aladhan API (method=13) — يطابق أوقات ديانيت الرسمية.
الاحتياطي: نسخة الشهر المخزّنة محلياً إن سقط الاتصال.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C


def _cache_path(year: int, month: int) -> Path:
    return C.CACHE_DIR / f"{year}-{month:02d}.json"


def _fetch_month(year: int, month: int) -> dict:
    """يجلب تقويم الشهر كاملاً من Aladhan ويخزّنه محلياً."""
    params = {
        "latitude": C.LATITUDE,
        "longitude": C.LONGITUDE,
        "method": C.METHOD_ID,
        "school": C.SCHOOL,
        "month": month,
        "year": year,
    }
    r = requests.get(C.ALADHAN_URL, params=params, timeout=C.HTTP_TIMEOUT)
    r.raise_for_status()
    payload = r.json()
    if payload.get("code") != 200:
        raise RuntimeError(f"Aladhan returned code {payload.get('code')}")

    C.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(year, month).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    return payload


def _load_month(year: int, month: int) -> dict:
    """يحاول الشبكة أولاً، ثم يسقط إلى النسخة المخزّنة."""
    try:
        return _fetch_month(year, month)
    except Exception as exc:  # الشبكة ساقطة أو الخدمة معطّلة
        cached = _cache_path(year, month)
        if cached.exists():
            print(f"  [times] الشبكة فشلت ({exc}) — استُخدمت النسخة المخزّنة")
            return json.loads(cached.read_text(encoding="utf-8"))
        raise RuntimeError(
            f"تعذّر جلب أوقات {year}-{month:02d} ولا توجد نسخة مخزّنة: {exc}"
        ) from exc


def _clean(value: str) -> str:
    """Aladhan يعيد '04:32 (+03)' — نأخذ الوقت وحده."""
    return value.split(" ")[0].strip()


def target_date(today: date | None = None) -> date:
    """
    اليوم المُعتمد لتوليد الواجهة.

    مع دورية أسبوعية نأخذ منتصف الأسبوع القادم بدل أوّله،
    فينخفض الانحراف الأقصى من ~7 دقائق إلى ~3.
    """
    today = today or date.today()
    return today + timedelta(days=C.OFFSET_DAYS)


def get_times(day: date | None = None) -> dict:
    """
    يعيد: {"date": date, "times": {"Fajr": "04:32", ...}}
    """
    day = day or target_date()
    payload = _load_month(day.year, day.month)
    entry = payload["data"][day.day - 1]
    timings = entry["timings"]

    times = {key: _clean(timings[key]) for key, _label in C.PRAYERS}
    return {"date": day, "times": times}


def validity_range(day: date | None = None) -> tuple[date, date]:
    """مدى الأيام التي تسري فيها هذه الواجهة."""
    start = (day or date.today())
    return start, start + timedelta(days=C.CADENCE_DAYS - 1)


if __name__ == "__main__":
    result = get_times()
    print(f"التاريخ المُعتمد: {result['date']}  ({C.CITY}, ديانيت)")
    for key, label in C.PRAYERS:
        print(f"  {label:<8} {result['times'][key]}")
