# Linux / Docker deployment (always-on + cron)

The packer is a Windows .NET program, so the container runs it under **Wine**
with **real .NET Framework 4.8** installed into a persistent prefix volume.

### 1. Build the image

Put your fonts in `fonts/` and the packer in `tools/WatchFace/` first (they are
not in the repo), then:

```bash
docker build -t miband-prayer:local .
```

### 2. One-time: install .NET 4.8 into a persistent Wine prefix

This creates a named volume `mbwine32` holding a 32-bit Wine prefix with real
.NET 4.8. It takes ~10–20 minutes (it downloads and runs the Microsoft
installer under Wine). Run it once:

```bash
# make the volume writable by the wine user (uid 1010 in scottyhardy/docker-wine)
docker run --rm --user root -v mbwine32:/home/wineuser/.wine \
  --entrypoint /bin/bash miband-prayer:local \
  -lc "mkdir -p /home/wineuser/.wine && chown -R 1010:1010 /home/wineuser/.wine && chmod 777 /home/wineuser/.wine"

# install .NET 4.8 into the prefix
docker run --rm --security-opt seccomp=unconfined \
  -e USE_XVFB=yes -e WINEARCH=win32 -e WINEDLLOVERRIDES=mscoree=n -e WINEDEBUG=-all \
  -v mbwine32:/home/wineuser/.wine \
  miband-prayer:local winetricks -q dotnet48
```

Verify: `.../Microsoft.NET/Framework/v4.0.30319/mscorlib.dll` should exist in the volume.

### 3. Run

```bash
export DISPATCH_URL=...  DISPATCH_SECRET=...   # or TG_BOT_TOKEN / TG_CHAT_ID
IMAGE=miband-prayer:local WINE_VOLUME=mbwine32 ./deploy/run.sh
```

### 4. Schedule weekly with cron

```cron
# Saturday 20:00 UTC  (example; adjust to your timezone/cadence)
0 20 * * 6 DISPATCH_URL=... DISPATCH_SECRET=... /path/to/deploy/run.sh >> /path/to/run.log 2>&1
```

### Mandatory `docker run` flags (why)

- `--security-opt seccomp=unconfined` — avoids `socket: Function not implemented`.
- `-e USE_XVFB=yes` — provides a virtual DISPLAY the installer/packer needs.
- `-e WINEDLLOVERRIDES=mscoree=n` — forces real .NET over Wine-Mono.
- `-e WINEARCH=win32` — matches the 32-bit prefix dotnet48 was installed into.

### Gotchas

- The prefix volume is the valuable part — **don't let `docker image/volume prune`
  remove it.** If it vanishes, repeat step 2.
- `src/pack.py` wraps the packer in `script -qec` on Linux (it needs a real tty
  because the tool sets `Console.Title` at startup).
