# -*- coding: utf-8 -*-
"""
رسم موارد الواجهة.

يُنتج:
  0000            الخلفية 127×294: أوقات الصلوات + النقطتان الملوّنتان
  0001..0010      أرقام الساعات — خضراء
  0011..0020      أرقام الدقائق — بيضاء
  0021..0030      أرقام نسبة الشحن — صغيرة بيضاء
  0031            علامة %
  0032..          إطارات الشعار: قبّة مفرّغة ⇄ هلال مفرّغ

الشعار مفرّغ عمداً (خطوط بلا حشو) ليبقى جوفه فارغاً تظهر فيه نسبة الشحن،
وهي عنصر حيّ يرسمه السوار فوق الإطارات لا صورة مطبوعة فيها.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError as exc:
        raise RuntimeError(f"تعذّر تحميل الخط {path}: {exc}") from exc


def _tw(d: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    return r - l, b - t


def _brand_color(t: float) -> tuple[int, int, int]:
    """
    لون على تدرّج هوية البوتات: أخضر زمرّدي ← فيروزي ← أزرق كهربي.
    t=0 عند الفجر و t=1 عند العشاء.
    """
    if t <= 0.5:
        a, b, k = C.BRAND_START, C.BRAND_MID, t * 2
    else:
        a, b, k = C.BRAND_MID, C.BRAND_END, (t - 0.5) * 2
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


# ── الخلفية ──────────────────────────────────────────────────────────
def draw_background(times: dict[str, str], out: Path) -> Path:
    img = Image.new("RGB", (C.SCREEN_W, C.SCREEN_H), C.COLOR_BG)
    d = ImageDraw.Draw(img)

    f_label = _font(C.FONT_LABEL, C.SIZE_LABEL)
    f_time = _font(C.FONT_TIME, C.SIZE_TIME)

    # النقطتان: العليا خضراء والسفلى بيضاء
    r = 2
    cx = C.COLON_X + 3
    for cy, color in ((C.CLOCK_Y + 11, C.COLOR_COLON_TOP),
                      (C.CLOCK_Y + 25, C.COLOR_COLON_BOT)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    if C.TOP_RULE:
        rule_y = C.LIST_TOP - 12
        d.line([(C.PAD_X, rule_y), (C.SCREEN_W - C.PAD_X, rule_y)],
               fill=C.COLOR_RULE, width=1)

    n = len(C.PRAYERS) - 1
    for i, (key, label) in enumerate(C.PRAYERS):
        y = C.LIST_TOP + i * C.ROW_H
        value = times[key]
        lw, _ = _tw(d, label, f_label)
        vw, _ = _tw(d, value, f_time)
        color = _brand_color(i / n)

        if C.RTL:
            # الاسم يميناً والوقت يساراً — القراءة الطبيعية بالعربية
            d.text((C.SCREEN_W - C.PAD_X - lw, y), label,
                   font=f_label, fill=color)
            d.text((C.PAD_X, y + C.SIZE_LABEL - 3), value,
                   font=f_time, fill=C.COLOR_TIME)
        else:
            d.text((C.PAD_X, y), label, font=f_label, fill=color)
            d.text((C.SCREEN_W - C.PAD_X - vw, y + C.SIZE_LABEL - 3),
                   value, font=f_time, fill=C.COLOR_TIME)
        if C.ROW_LINES and i < len(C.PRAYERS) - 1:
            sep = y + C.ROW_LINE_Y
            d.line([(C.PAD_X, sep), (C.SCREEN_W - C.PAD_X, sep)],
                   fill=C.COLOR_RULE, width=1)

    img.save(out)
    return out


# ── مجموعات الأرقام ──────────────────────────────────────────────────
def draw_digit_set(out_dir: Path, first_index: int, w: int, h: int,
                   size: int, color, suffix: str | None = None,
                   suffix_index: int | None = None) -> None:
    """يرسم 0..9 بمقاس ولون محدّدين، وعلامة اختيارية بعدها."""
    f = _font(C.FONT_DIGIT, size)
    for n in range(10):
        img = Image.new("RGB", (w, h), C.COLOR_BG)
        d = ImageDraw.Draw(img)
        s = str(n)
        l, t, r, b = d.textbbox((0, 0), s, font=f)
        d.text(((w - (r - l)) // 2 - l, (h - (b - t)) // 2 - t),
               s, font=f, fill=color)
        img.save(out_dir / f"{first_index + n:04d}.png")

    if suffix and suffix_index is not None:
        img = Image.new("RGB", (w, h), C.COLOR_BG)
        d = ImageDraw.Draw(img)
        l, t, r, b = d.textbbox((0, 0), suffix, font=f)
        d.text(((w - (r - l)) // 2 - l, (h - (b - t)) // 2 - t),
               suffix, font=f, fill=color)
        img.save(out_dir / f"{suffix_index:04d}.png")


# ── الشعار المتحرّك ──────────────────────────────────────────────────
def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _logo_frame(t: float, size: int) -> Image.Image:
    """
    إطار واحد من التحوّل: قبّة (t=0) ⇄ هلال (t=1)، مفرّغ بالكامل.

    التحوّل هندسي لا مزج ضبابي:
      - القوس الخارجي يتّسع تدريجياً من نصف دائرة إلى قوس هلالي
      - قاعدة القبّة تنكمش حتى تختفي
      - الصاري والكرة يتلاشيان مبكراً
      - القوس الداخلي (بطن الهلال) يظهر متأخّراً ويتعمّق
    """
    if C.ANIM_TRANSPARENT:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        col = C.COLOR_ANIM + (255,)
    else:
        img = Image.new("RGB", (size, size), C.COLOR_BG)
        col = C.COLOR_ANIM
    d = ImageDraw.Draw(img)
    w = C.ANIM_STROKE

    m = 3
    box = [m, m + 2, size - m, size - m - 1]
    cx = size / 2
    base_y = box[3]

    # القوس الخارجي: 180→360 (قبّة) يتّسع إلى 35→325 (هلال)
    a0 = _lerp(180, 35, t)
    a1 = _lerp(360, 325, t)
    d.arc(box, a0, a1, fill=col, width=w)

    # القاعدة تنكمش من الحافّة إلى المركز
    half = (box[2] - box[0]) / 2 * (1 - t)
    if half > 1.5:
        d.line([(cx - half, base_y), (cx + half, base_y)], fill=col, width=w)

    # الصاري والكرة — للقبّة وحدها
    if t < 0.45:
        fin = int(_lerp(size // 5, 0, t / 0.45))
        if fin > 1:
            top = box[1]
            d.line([(cx, top - fin), (cx, top + 1)], fill=col, width=w)
            d.ellipse([cx - 2, top - fin - 3, cx + 2, top - fin + 1],
                      outline=col, width=1)

    # بطن الهلال: قوس داخلي مزاح يميناً، يظهر بعد منتصف التحوّل
    if t > 0.35:
        k = (t - 0.35) / 0.65
        shift = _lerp(0, size * 0.30, k)
        inner = [box[0] + shift, box[1] + 2, box[2] + shift, box[3] - 2]
        d.arc(inner, 120, 240, fill=col, width=w)

    return img


def draw_animation(out_dir: Path) -> None:
    half = C.ANIM_FRAMES // 2
    for i in range(C.ANIM_FRAMES):
        t = i / half if i <= half else (C.ANIM_FRAMES - i) / half
        t = min(max(t, 0.0), 1.0)
        # تنعيم بمنحنى جيبي بدل الخطّي — حركة أقرب إلى الطبيعية
        t = (1 - math.cos(t * math.pi)) / 2
        _logo_frame(t, C.ANIM_W).save(
            out_dir / f"{C.ANIM_FIRST_INDEX + i:04d}.png")


def draw_weekdays(out_dir: Path) -> None:
    """سبع صور لأيام الأسبوع — السوار يختار الصورة الموافقة لليوم."""
    f = _font(C.FONT_LABEL, C.SIZE_WEEKDAY)
    for i, name in enumerate(C.WEEKDAY_NAMES):
        img = Image.new("RGB", (C.WEEKDAY_W, C.WEEKDAY_H), C.COLOR_BG)
        d = ImageDraw.Draw(img)
        l, t, r, b = d.textbbox((0, 0), name, font=f)
        d.text(((C.WEEKDAY_W - (r - l)) // 2 - l,
                (C.WEEKDAY_H - (b - t)) // 2 - t),
               name, font=f, fill=C.COLOR_WEEKDAY)
        img.save(out_dir / f"{C.WEEKDAY_INDEX + i:04d}.png")


def draw_battery_warning(out_dir: Path) -> None:
    """
    عشر صور لعنصر BatteryIcon — السوار يختار واحدة بحسب شريحة الشحن.
    الشريحتان الأدنى (0–19%) علامة تعجّب حمراء، والبقية سوداء غير مرئية.
    هذه أقرب ما تسمح به الصيغة لطلب «الأحمر عند الشحن المنخفض»،
    لأن أرقام النسبة نفسها مربوطة بمجموعة صور واحدة لا تقبل التلوين الشرطي.
    """
    w, h = C.BATWARN_W, C.BATWARN_H
    for lvl in range(10):
        img = Image.new("RGB", (w, h), C.COLOR_BG)
        if lvl < C.BATWARN_LEVELS:
            d = ImageDraw.Draw(img)
            cx = w // 2
            d.line([(cx, 2), (cx, h - 5)], fill=C.COLOR_WARN, width=2)
            d.ellipse([cx - 1, h - 3, cx + 1, h - 1], fill=C.COLOR_WARN)
        img.save(out_dir / f"{C.BATWARN_INDEX + lvl:04d}.png")


# ── المُنسّق ─────────────────────────────────────────────────────────
def render_all(times: dict[str, str], out_dir: Path | None = None) -> Path:
    out_dir = out_dir or C.WF_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    bg = draw_background(times, out_dir / "0000.png")

    draw_digit_set(out_dir, C.HOUR_FIRST_INDEX, C.DIGIT_W, C.DIGIT_H,
                   C.SIZE_DIGIT, C.COLOR_HOUR)
    draw_digit_set(out_dir, C.MIN_FIRST_INDEX, C.DIGIT_W, C.DIGIT_H,
                   C.SIZE_DIGIT, C.COLOR_MINUTE)

    if C.BAT_ON:
        draw_digit_set(out_dir, C.BAT_FIRST_INDEX, C.BAT_W, C.BAT_H,
                       C.SIZE_BAT, C.COLOR_BATTERY,
                       suffix="%" if C.BAT_SUFFIX else None,
                       suffix_index=C.BAT_SUFFIX_INDEX if C.BAT_SUFFIX else None)

    if C.DATE_ON:
        draw_digit_set(out_dir, C.MONTH_INDEX, C.DATE_W, C.DATE_H,
                       C.SIZE_DATE, C.COLOR_MONTH)
        draw_digit_set(out_dir, C.DAY_INDEX, C.DATE_W, C.DATE_H,
                       C.SIZE_DATE, C.COLOR_DAY)

    if C.WEEKDAY_ON:
        draw_weekdays(out_dir)

    if C.BATWARN_ON:
        draw_battery_warning(out_dir)

    if C.ANIM_ON:
        draw_animation(out_dir)

    return bg


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from times import get_times

    r = get_times()
    render_all(r["times"])
    print(f"رُسمت الموارد في {C.WF_DIR} لتاريخ {r['date']}")
