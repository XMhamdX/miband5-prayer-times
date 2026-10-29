# -*- coding: utf-8 -*-
"""
معاينة تركيبية للواجهة — بما فيها الشعار المتحرّك.

يركّب الخلفية وأرقام الساعة وإطارات الشعار في GIF متحرّك.
هذه محاكاة لما ستبدو عليه الشاشة، لا الواجهة الفعلية —
الشعار غير مُدرَج في ملف .bin لأن مُخطَّط Band 5 لا يقبل عنصر Animation.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C


def compose(clock: str = "12:45", scale: int = 3) -> tuple[Path, Path]:
    wf = C.WF_DIR
    bg = Image.open(wf / "0000.png").convert("RGB")

    # أرقام الساعة الثابتة للمعاينة
    digits = clock.replace(":", "")
    for i, ch in enumerate(digits):
        d = Image.open(wf / f"{int(ch) + 1:04d}.png").convert("RGB")
        bg.paste(d, (C.CLOCK_X[i], C.CLOCK_Y))

    frames: list[Image.Image] = []
    for i in range(C.ANIM_FRAMES):
        p = wf / f"{C.ANIM_FIRST_INDEX + i:04d}.png"
        if not p.exists():
            continue
        frame = bg.copy()
        frame.paste(Image.open(p).convert("RGB"), (C.ANIM_X, C.ANIM_Y))
        frames.append(frame.resize((C.SCREEN_W * scale, C.SCREEN_H * scale), Image.NEAREST))

    if not frames:
        raise RuntimeError("لا توجد إطارات شعار — شغّل render أولاً مع ANIM_ON=True")

    C.OUT_DIR.mkdir(parents=True, exist_ok=True)
    gif = C.OUT_DIR / "preview-animated.gif"
    png = C.OUT_DIR / "preview-still.png"

    frames[0].save(
        gif, save_all=True, append_images=frames[1:],
        duration=120, loop=0, optimize=False,
    )
    frames[0].save(png)
    return gif, png


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from times import get_times
    from render import render_all

    render_all(get_times()["times"])
    g, p = compose()
    print(f"GIF: {g}")
    print(f"PNG: {p}")
