# Watch-face packer (third-party, not included)

Packing images + `watchface.json` into a Mi Band 5 `.bin` is done by a
third-party Windows **.NET** watch-face tool. It is **not redistributed here**
for licensing reasons.

Place the packer's files in this folder so the layout is:

```
tools/WatchFace/WatchFace.exe
tools/WatchFace/<its supporting .dll / .config / .json files>
```

`config.py` expects the executable at `tools/WatchFace/WatchFace.exe`
(`PACKER` setting). Any Mi Band 5 compatible packer that accepts a
`watchface.json` on the command line will do — community tools are commonly
named *MiBandWFTool* or *WatchFace* editors. Adjust `PACKER` in `config.py`
if your tool's entry point differs.

### Running it on Linux

The packer is a Windows .NET program, so on Linux it runs under **Wine** with
**real .NET Framework 4.8** (not Wine-Mono). See `deploy/README.md`. It also
needs a real pseudo-terminal, so `src/pack.py` wraps it in `script -qec` on
Linux (the tool sets `Console.Title` at startup and throws without a tty).
