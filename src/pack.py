# -*- coding: utf-8 -*-
"""
حزم الواجهة إلى ملف .bin عبر MiBandWFTool.

الأداة تعمل أصلياً على الويندوز (.NET Framework). جُرِّبت تحت mono على لينكس
ففشلت لأن نسخة Band 5 مُشوَّشة الكود — ولهذا يعمل هذا المشروع على الويندوز.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C

# قالب الواجهة — يتجمّد بعد ضبطه، ولا يتغيّر إلا صورة الخلفية 0000.png
WATCHFACE_TEMPLATE = {
    "Background": {
        "Image": {"X": 0, "Y": 0, "ImageIndex": 0}
    },
    "Time": {
        # الساعات من المجموعة الخضراء، والدقائق من البيضاء
        "Hours": {
            "Tens": {"X": C.CLOCK_X[0], "Y": C.CLOCK_Y,
                     "ImageIndex": C.HOUR_FIRST_INDEX, "ImagesCount": 10},
            "Ones": {"X": C.CLOCK_X[1], "Y": C.CLOCK_Y,
                     "ImageIndex": C.HOUR_FIRST_INDEX, "ImagesCount": 10},
        },
        "Minutes": {
            "Tens": {"X": C.CLOCK_X[2], "Y": C.CLOCK_Y,
                     "ImageIndex": C.MIN_FIRST_INDEX, "ImagesCount": 10},
            "Ones": {"X": C.CLOCK_X[3], "Y": C.CLOCK_Y,
                     "ImageIndex": C.MIN_FIRST_INDEX, "ImagesCount": 10},
        },
    },
}


def _battery_block() -> dict:
    """نسبة الشحن داخل الشعار المفرّغ — عنصر حيّ لا صورة مطبوعة."""
    x0, y0, x1, y1 = C.BAT_BOX
    return {
        "Battery": {
            "BatteryText": {
                "Coordinates": {
                    "TopLeftX": x0, "TopLeftY": y0,
                    "BottomRightX": x1, "BottomRightY": y1,
                    "Alignment": "TopCenter",
                    "SpacingX": 0, "SpacingY": 0,
                    "ImageIndex": C.BAT_FIRST_INDEX, "ImagesCount": 10,
                },
                **({"SuffixImageIndex": C.BAT_SUFFIX_INDEX} if C.BAT_SUFFIX else {}),
            },
            **({"BatteryIcon": {
                "X": C.BATWARN_X, "Y": C.BATWARN_Y,
                "ImageIndex": C.BATWARN_INDEX, "ImagesCount": 10,
            }} if C.BATWARN_ON else {}),
        }
    }


# الصيغة الصحيحة — مستخرجة من واجهات Band 5 حقيقية (المعرّفات 5177، 5163، 5158).
# الأنيميشن ليس عنصراً في أعلى المستوى بل مُعشَّش داخل "Other" كمصفوفة.
# Speed هنا بالملّي ثانية لكل إطار، لا القيمة 5 الإلزامية في Band 4.
def _animation_block() -> dict:
    return {
        "Other": {
            "Animation": [
                {
                    "AnimationImages": {
                        "X": C.ANIM_X,
                        "Y": C.ANIM_Y,
                        "ImageIndex": C.ANIM_FIRST_INDEX,
                        "ImagesCount": C.ANIM_FRAMES,
                    },
                    "Speed": C.ANIM_SPEED,
                    "RepeatCount": C.ANIM_REPEAT,
                    "UnknownTF4": 0,
                }
            ]
        }
    }


def _animation_variants() -> list[dict]:
    return [_animation_block()]


def _date_block() -> dict:
    """
    التاريخ ويوم الأسبوع — عنصران حيّان يحدّثهما السوار يومياً بنفسه،
    فلا تحتاج الواجهة إعادة بناء عند تغيّر اليوم.
    الشهر واليوم مجموعتا صور منفصلتان، فيمكن تلوين كلٍّ على حدة.
    """
    mx0, my0, mx1, my1 = C.MONTH_BOX
    dx0, dy0, dx1, dy1 = C.DAY_BOX
    block: dict = {
        "Date": {
            "MonthAndDayAndYear": {
                "Separate": {
                    "Month": {
                        "TopLeftX": mx0, "TopLeftY": my0,
                        "BottomRightX": mx1, "BottomRightY": my1,
                        "Alignment": "TopCenter", "SpacingX": 0, "SpacingY": 0,
                        "ImageIndex": C.MONTH_INDEX, "ImagesCount": 10,
                    },
                    "Day": {
                        "TopLeftX": dx0, "TopLeftY": dy0,
                        "BottomRightX": dx1, "BottomRightY": dy1,
                        "Alignment": "TopCenter", "SpacingX": 0, "SpacingY": 0,
                        "ImageIndex": C.DAY_INDEX, "ImagesCount": 10,
                    },
                },
                "TwoDigitsMonth": True,
                "TwoDigitsDay": True,
            }
        }
    }
    if C.WEEKDAY_ON:
        block["Date"]["ENWeekDays"] = {
            "X": C.WEEKDAY_X, "Y": C.WEEKDAY_Y,
            "ImageIndex": C.WEEKDAY_INDEX, "ImagesCount": 7,
        }
    return block


def write_template(path: Path | None = None, animation: dict | None = None) -> Path:
    path = path or C.WF_JSON
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dict(WATCHFACE_TEMPLATE)
    if animation:
        data.update(animation)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def build(with_animation: bool = True) -> tuple[Path, str]:
    """
    يكتب القالب ويحزم. إن كان الأنيميشن مطلوباً جُرِّبت صيغه بالترتيب،
    وإن رفضها المُغلِّف كلها رجع إلى واجهة بلا أنيميشن بدل أن يفشل.
    يعيد: (مسار الـ bin، وصف الصيغة المستخدمة)
    """
    extra: dict = {}
    if C.BAT_ON:
        extra.update(_battery_block())
    if C.DATE_ON:
        extra.update(_date_block())

    if with_animation and C.ANIM_ON:
        for i, variant in enumerate(_animation_variants(), start=1):
            merged = dict(extra)
            merged.update(variant)
            write_template(animation=merged)
            try:
                return pack(), f"animation+battery variant {i}"
            except RuntimeError:
                continue
        print("  [pack] رفض المُغلِّف صيغة الأنيميشن — بناء بلا شعار")

    write_template(animation=extra or None)
    return pack(), "battery only" if extra else "plain"


def pack(json_path: Path | None = None) -> Path:
    """يشغّل المُغلِّف ويعيد مسار ملف .bin الناتج."""
    json_path = json_path or C.WF_JSON
    if not C.PACKER.exists():
        raise RuntimeError(f"المُغلِّف غير موجود: {C.PACKER}")
    if not json_path.exists():
        raise RuntimeError(f"ملف القالب غير موجود: {json_path}")

    expected = json_path.with_name(json_path.stem + "_packed.bin")
    if expected.exists():
        expected.unlink()

    if platform.system() == "Windows":
        proc = subprocess.run(
            [str(C.PACKER), str(json_path)],
            cwd=str(json_path.parent),
            capture_output=True,
            text=True,
            errors="replace",
        )
    else:
        # لينكس: المُغلِّف .NET يُشغَّل عبر wine، ويلزمه طرفية حقيقية
        # (يضبط عنوان الطرفية عند البدء) فنغلّفه بـ script لتوفير pty.
        inner = 'cd "%s" && wine "%s" "%s"' % (
            json_path.parent, C.PACKER, json_path.name)
        proc = subprocess.run(
            ["script", "-qec", inner, "/tmp/pack.log"],
            capture_output=True,
            text=True,
            errors="replace",
        )

    if not expected.exists():
        tail = (proc.stdout or "")[-1500:] + (proc.stderr or "")[-1500:]
        raise RuntimeError(f"فشل الحزم (رمز {proc.returncode}):\n{tail}")

    size = expected.stat().st_size
    if size < 5_000:
        raise RuntimeError(f"الملف الناتج صغير بشكل مريب ({size} بايت) — حزم فاشل")

    return expected


if __name__ == "__main__":
    write_template()
    out = pack()
    print(f"نجح الحزم: {out}  ({out.stat().st_size:,} بايت)")
