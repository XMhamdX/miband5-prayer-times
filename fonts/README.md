# Fonts

The fonts are **not included** — Tahoma and Segoe UI are proprietary Microsoft
fonts and cannot be redistributed here.

The defaults (see `config.py`) are:

- `tahomabd.ttf` — Tahoma Bold (used for prayer labels; clearest Arabic at tiny sizes)
- `segoeuib.ttf` — Segoe UI Bold (used for the time/digits)

On Windows these already exist in `C:\Windows\Fonts\`, and `config.py` points
there automatically. For Linux/Docker, copy those two `.ttf` files into this
folder, **or** substitute any readable TrueType fonts and update the
`FONT_LABEL` / `FONT_TIME` / `FONT_DIGIT` paths in `config.py`.

For Arabic, make sure Pillow is built with **raqm** so letters shape and join
correctly.
