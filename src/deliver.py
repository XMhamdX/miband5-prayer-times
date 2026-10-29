# -*- coding: utf-8 -*-
"""
إرسال ملف الواجهة إلى تليجرام عبر الموزّع (n8n).

المشروع لا يحمل رمز البوت — يدفع الملف لويبهوك الموزّع بالسرّ المشترك،
والموزّع في n8n يتولّى الإرسال الفعلي. هكذا يبقى الرمز في مكان واحد.

إن كان TG_BOT_TOKEN مملوءاً في config.py استُخدم الطريق المباشر بدلاً
من الموزّع — احتياط لو سقط الموزّع.
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C

DIRECT_API = "https://api.telegram.org/bot{token}/{method}"


# ── الطريق المباشر (احتياطي فقط) ─────────────────────────────────────
def _direct_message(text: str) -> dict:
    r = requests.post(
        DIRECT_API.format(token=C.TG_BOT_TOKEN, method="sendMessage"),
        data={"chat_id": C.TG_CHAT_ID, "text": text},
        timeout=C.HTTP_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def _direct_watchface(path: Path, caption: str) -> dict:
    with path.open("rb") as fh:
        r = requests.post(
            DIRECT_API.format(token=C.TG_BOT_TOKEN, method="sendDocument"),
            data={"chat_id": C.TG_CHAT_ID, "caption": caption[:1024]},
            files={"document": (path.name, fh, "application/octet-stream")},
            timeout=120,
        )
    r.raise_for_status()
    payload = r.json()
    if not payload.get("ok"):
        raise RuntimeError(f"تليجرام ردّ بخطأ: {payload}")
    return payload


# ── الطريق عبر الموزّع (الأساسي) ─────────────────────────────────────
def _dispatch_message(text: str) -> dict:
    r = requests.post(
        C.DISPATCH_URL,
        data={"secret": C.DISPATCH_SECRET, "caption": text},
        timeout=C.HTTP_TIMEOUT,
    )
    r.raise_for_status()
    payload = r.json()
    if not payload.get("ok"):
        raise RuntimeError(f"الموزّع ردّ بخطأ: {payload}")
    return payload


def _dispatch_watchface(path: Path, caption: str) -> dict:
    with path.open("rb") as fh:
        r = requests.post(
            C.DISPATCH_URL,
            data={"secret": C.DISPATCH_SECRET, "caption": caption[:1024],
                  "type": "file"},
            files={"document": (path.name, fh, "application/octet-stream")},
            timeout=120,
        )
    r.raise_for_status()
    payload = r.json()
    if not payload.get("ok"):
        raise RuntimeError(f"الموزّع ردّ بخطأ: {payload}")
    return payload


# ── الواجهة العامّة: تختار الموزّع ما لم يُفرض الطريق المباشر ─────────
def send_message(text: str) -> dict:
    if C.TG_BOT_TOKEN:
        return _direct_message(text)
    return _dispatch_message(text)


def send_watchface(path: Path, caption: str = "") -> dict:
    if not path.exists():
        raise RuntimeError(f"الملف غير موجود: {path}")
    if C.TG_BOT_TOKEN:
        return _direct_watchface(path, caption)
    return _dispatch_watchface(path, caption)


if __name__ == "__main__":
    print(send_message("اختبار اتصال من مشروع أوقات الصلاة عبر الموزّع."))
