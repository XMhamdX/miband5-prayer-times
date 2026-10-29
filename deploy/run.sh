#!/bin/bash
# Weekly runner for the Linux/Docker deployment (schedule with cron).
# Hardened: detects a docker/generation failure and alerts via the dispatcher,
# so a silently broken job can't let the band drift unnoticed.
#
# Pass delivery creds to the container as environment variables (see .env.example).
IMAGE="${IMAGE:-miband-prayer:local}"
WINE_VOLUME="${WINE_VOLUME:-mbwine32}"
LOGTMP="$(mktemp)"

echo "===== $(date -u) UTC ====="

docker run --rm --security-opt seccomp=unconfined \
  -e USE_XVFB=yes -e WINEARCH=win32 -e WINEDLLOVERRIDES=mscoree=n -e WINEDEBUG=-all \
  -e DISPATCH_URL -e DISPATCH_SECRET -e TG_BOT_TOKEN -e TG_CHAT_ID \
  -v "${WINE_VOLUME}:/home/wineuser/.wine" \
  "$IMAGE" > "$LOGTMP" 2>&1
RC=$?

# Show useful output, drop Wine noise
grep -vaE "err:|fixme:|warn:|^[0-9a-f]{4}:|^[[:space:]]*[0-9a-f]{8}" "$LOGTMP"

# Success only if docker exited 0 AND main.py printed its done marker ("تمّ:")
if [ "$RC" -ne 0 ] || ! grep -qa "تمّ:" "$LOGTMP"; then
  echo "!!!! generation failed (rc=$RC) — sending alert"
  TAIL="$(tail -n 3 "$LOGTMP" | tr '\n' ' ' | cut -c1-300)"
  if [ -n "$DISPATCH_URL" ] && [ -n "$DISPATCH_SECRET" ]; then
    curl -s --max-time 25 -X POST "$DISPATCH_URL" \
      --data-urlencode "secret=$DISPATCH_SECRET" \
      --data-urlencode "caption=⚠️ Prayer-times watch face generation FAILED on the server (rc=$RC). Last log: $TAIL" >/dev/null
  fi
  rm -f "$LOGTMP"
  exit 1
fi

rm -f "$LOGTMP"
