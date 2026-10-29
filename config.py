# -*- coding: utf-8 -*-
"""
عقدة الإعدادات المركزية.
كل متغيّر في المشروع يُعرَّف هنا وحده — لا قيم مبعثرة في الوحدات.
"""
import os
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IS_WINDOWS = platform.system() == "Windows"

# ── الجهاز ───────────────────────────────────────────────────────────
DEVICE   = "miband5"
SCREEN_W = 127          # القياس الفعلي المستخرج من واجهة Band 5 أساس
SCREEN_H = 294

# ── الموقع وطريقة الحساب ─────────────────────────────────────────────
CITY      = "Istanbul"
LATITUDE  = 41.0082
LONGITUDE = 28.9784
TIMEZONE  = "Europe/Istanbul"
METHOD_ID = 13          # Aladhan: Diyanet Isleri Baskanligi (ديانيت التركية)
SCHOOL    = 0           # 0 = العصر القياسي (ما تعتمده ديانيت)

# ── الدورية ──────────────────────────────────────────────────────────
CADENCE_DAYS = 7        # 1 = يومي، 7 = أسبوعي
OFFSET_DAYS  = 3        # اليوم المُعتمد داخل الدورة (منتصفها) لتقليل الانحراف

# ── الخطوط ───────────────────────────────────────────────────────────
# Tahoma Bold أوضح خطّ عربي في الأحجام الصغيرة جداً
FONT_LABEL = (r"C:\Windows\Fonts\tahomabd.ttf" if IS_WINDOWS else str(ROOT/"fonts"/"tahomabd.ttf"))
FONT_TIME  = (r"C:\Windows\Fonts\segoeuib.ttf" if IS_WINDOWS else str(ROOT/"fonts"/"segoeuib.ttf"))
FONT_DIGIT = (r"C:\Windows\Fonts\segoeuib.ttf" if IS_WINDOWS else str(ROOT/"fonts"/"segoeuib.ttf"))
SIZE_LABEL = 15
SIZE_TIME  = 22
SIZE_DIGIT = 34

# ── الألوان ──────────────────────────────────────────────────────────
COLOR_BG    = (0, 0, 0)
COLOR_TIME  = (255, 255, 255)
COLOR_RULE  = (38, 38, 38)

# ── هوية أيقونات البوتات: emerald green ← turquoise ← electric blue ──
# أسماء الصلوات تتدرّج على هذا التدرّج: الفجر أخضر والعشاء أزرق.
BRAND_START = (0, 214, 120)    # emerald green
BRAND_MID   = (0, 205, 215)    # turquoise
BRAND_END   = (70, 135, 255)   # electric blue

# الساعة الحية: الساعات خضراء والدقائق بيضاء،
# والنقطتان بينهما: العليا خضراء والسفلى بيضاء
COLOR_HOUR      = (0, 210, 95)
COLOR_MINUTE    = (255, 255, 255)
COLOR_COLON_TOP = (0, 210, 95)
COLOR_COLON_BOT = (255, 255, 255)
COLOR_BATTERY   = (255, 255, 255)

# ── الصلوات (مفاتيح Aladhan ← التسمية المعروضة) ──────────────────────
# اللغة: "ar" عربية أو "en" إنجليزية. التبديل بكلمة واحدة.
# العربية ممكنة لأن الأسماء تُرسم كصورة لا كنصّ — فلا قيد ترميز على السوار.
LANG = "ar"

# بلا أداة تعريف — توفيراً لعرض الشاشة الضيّق (127 بكسل)
_NAMES = {
    "Fajr":    ("Fajr",    "فجر"),
    "Dhuhr":   ("Dhuhr",   "ظهر"),
    "Asr":     ("Asr",     "عصر"),
    "Maghrib": ("Maghrib", "مغرب"),
    "Isha":    ("Isha",    "عشاء"),
}
PRAYERS = [(k, v[1] if LANG == "ar" else v[0]) for k, v in _NAMES.items()]

# في العربية: الاسم يميناً والوقت يساراً — الترتيب الطبيعي للقراءة
RTL = (LANG == "ar")

# ── تخطيط الشاشة (127×294) ───────────────────────────────────────────
DIGIT_W  = 22           # عرض صورة الرقم الواحد
DIGIT_H  = 38           # ارتفاعها
CLOCK_Y  = 8            # أعلى أرقام الساعة الحية
CLOCK_X  = [18, 41, 70, 93]   # عشرات الساعة، آحادها، عشرات الدقيقة، آحادها
COLON_X  = 64
COLON_Y  = 18

LIST_TOP = 58           # أعلى أول سطر صلاة
ROW_H    = 40           # ارتفاع السطر الواحد
PAD_X    = 8            # هامش جانبي

# الخطوط الفاصلة بين الأسطر — اختيارية.
# موضعها الصحيح منتصف الفراغ بين نهاية الوقت (y+34) وبداية السطر التالي (y+40).
ROW_LINES   = False     # True لإعادتها
ROW_LINE_Y  = 37        # إزاحة من أعلى السطر
TOP_RULE    = False     # الخط تحت الساعة — مطفأ كذلك

# ── الشعار المتحرّك: قبّة مسجد تتحوّل إلى هلال وتعود ──────────────────
# مرسوم **مفرّغاً** (خطوط فقط) ليبقى جوفه فارغاً تظهر فيه نسبة الشحن.
# الأسود يبقى سائداً حفاظاً على البطارية — AMOLED يُطفئ البكسل الأسود.
ANIM_ON     = True
ANIM_W      = 26
ANIM_H      = 26
ANIM_X      = 3                          # الزاوية السفلى اليسرى
ANIM_Y      = 264                        # 264 + 26 = 290 ≤ 294
ANIM_FRAMES = 16        # 8 للتحوّل و8 للعودة
ANIM_SPEED  = 260       # ملّي ثانية لكل إطار — أُبطئت لتقليل عدد التحديثات
ANIM_REPEAT = 255       # تكرار دائم
ANIM_STROKE = 2         # سماكة الخط المفرّغ
COLOR_ANIM  = (0, 210, 95)

# ── ترتيب الصور داخل الواجهة ─────────────────────────────────────────
HOUR_FIRST_INDEX = 1     # 0001..0010  أرقام الساعات (خضراء)  22×38
MIN_FIRST_INDEX  = 11    # 0011..0020  أرقام الدقائق (بيضاء)  22×38
BAT_FIRST_INDEX  = 21    # 0021..0030  أرقام البطارية الصغيرة
BAT_SUFFIX_INDEX = 31    # 0031        علامة %
ANIM_FIRST_INDEX = 32    # 0032..      إطارات الشعار

# ── نسبة الشحن داخل الشعار ───────────────────────────────────────────
# الصندوق يجب أن يتّسع لثلاثة عناصر: رقمان + علامة %.
# كان 30 بكسل وهو أضيق من 33 التي يحتاجها، فتخطّى السوار العنصر صامتاً.
BAT_ON       = True
BAT_SUFFIX   = False    # بلا علامة % — توفيراً للعرض
BAT_W        = 8
BAT_H        = 12
SIZE_BAT     = 11
# النسبة داخل الشعار في الزاوية
BAT_BOX      = (ANIM_X + 2, ANIM_Y + 8, ANIM_X + ANIM_W - 2, ANIM_Y + 22)

# إطارات الشعار تُحفظ بشفافية لا بخلفية سوداء، وإلا طمست الرقم تحتها
# لأن الأنيميشن يُرسم فوق بقية العناصر.
ANIM_TRANSPARENT = True

# تحذير الشحن المنخفض: BatteryIcon يتغيّر بحسب المستوى (عشر شرائح 10%).
# الشريحتان 0 و1 (أي 0–19%) تعرضان علامة حمراء، والبقية سوداء غير مرئية.
# لا يمكن تلوين الأرقام نفسها — الصيغة تربطها بمجموعة صور واحدة.
BATWARN_ON     = True
BATWARN_LEVELS = 2          # عدد الشرائح المُحذِّرة من الأسفل
BATWARN_W      = 12
BATWARN_H      = 12
BATWARN_X      = 9
BATWARN_Y      = 269
BATWARN_INDEX  = 48         # 0048..0057
COLOR_WARN     = (255, 60, 60)

# ── التاريخ ويوم الأسبوع — عنصران حيّان يحدّثهما السوار يومياً ────────
# لا يحتاجان إعادة بناء الواجهة إطلاقاً.
DATE_ON        = True
DATE_W         = 11         # عرض رقم التاريخ
DATE_H         = 15
SIZE_DATE      = 13
COLOR_MONTH    = COLOR_HOUR      # الشهر بلون الساعات — أخضر
COLOR_DAY      = COLOR_MINUTE    # اليوم أبيض
MONTH_INDEX    = 58         # 0058..0067  أرقام الشهر (خضراء)
DAY_INDEX      = 68         # 0068..0077  أرقام اليوم (بيضاء)
DATE_Y         = 268
MONTH_BOX      = (48, DATE_Y, 72, DATE_Y + DATE_H)
DAY_BOX        = (74, DATE_Y, 98, DATE_Y + DATE_H)

# يوم الأسبوع في الزاوية الأخرى — سبع صور يختار السوار منها
WEEKDAY_ON     = True
WEEKDAY_INDEX  = 78         # 0078..0084
WEEKDAY_W      = 22
WEEKDAY_H      = 14
WEEKDAY_X      = 103
WEEKDAY_Y      = 269
SIZE_WEEKDAY   = 12
COLOR_WEEKDAY  = (170, 175, 185)   # فضّي
# ترتيب ENWeekDays غير موثّق — يبدأ بالاثنين على الأرجح.
# إن ظهر يوم خاطئ على السوار فأزح القائمة خطوة واحدة.
WEEKDAY_NAMES  = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

# ── التوصيل عبر الموزّع (n8n) ────────────────────────────────────────
# لا رمز بوت هنا إطلاقاً — الموزّع في n8n يحمل الرمز وحده.
# المشروع يدفع الملف للويبهوك بالسرّ المشترك، والموزّع يرسله للبوت.
DISPATCH_URL    = os.getenv("DISPATCH_URL", "")
DISPATCH_SECRET = os.getenv("DISPATCH_SECRET", "")
TG_CHAT_ID      = int(os.getenv("TG_CHAT_ID", "0")) or None

# طريق مباشر احتياطي إن سقط الموزّع (يُترك فارغاً عادة)
TG_BOT_TOKEN    = os.getenv("TG_BOT_TOKEN", "")

# ── المسارات ─────────────────────────────────────────────────────────
PACKER    = ROOT / "tools" / "WatchFace" / "WatchFace.exe"
WF_DIR    = ROOT / "watchface"
WF_JSON   = WF_DIR / "watchface.json"
WF_BIN    = WF_DIR / "watchface_packed.bin"
OUT_DIR   = ROOT / "out"
CACHE_DIR = ROOT / "cache"

# ── مصدر الأوقات ─────────────────────────────────────────────────────
ALADHAN_URL = "https://api.aladhan.com/v1/calendar"
HTTP_TIMEOUT = 20
