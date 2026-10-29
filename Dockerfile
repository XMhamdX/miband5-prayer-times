# Headless Linux build: runs the Windows .NET packer under Wine.
# The real .NET 4.8 lives in a persistent volume mounted at /home/wineuser/.wine
# (see deploy/README.md), not in this image.
FROM scottyhardy/docker-wine:latest
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pil python3-requests libraqm0 util-linux \
    && rm -rf /var/lib/apt/lists/*
# Supply fonts/ (.ttf) and tools/WatchFace/ (the packer) locally before building.
COPY . /app/
RUN mkdir -p /app/out /app/cache /app/watchface \
    && chmod -R 777 /app
CMD ["python3","/app/src/main.py"]
