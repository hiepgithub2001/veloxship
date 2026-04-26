FROM python:3.11-slim

# WeasyPrint native dependencies + Vietnamese font
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    fonts-noto-cjk \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Be Vietnam Pro font for diacritic-faithful PDFs
RUN mkdir -p /usr/share/fonts/truetype/be-vietnam-pro && \
    wget -q -O /tmp/be-vietnam-pro.zip "https://fonts.google.com/download?family=Be+Vietnam+Pro" && \
    (cd /tmp && unzip -o be-vietnam-pro.zip -d /usr/share/fonts/truetype/be-vietnam-pro 2>/dev/null || true) && \
    fc-cache -fv && \
    rm -f /tmp/be-vietnam-pro.zip

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
