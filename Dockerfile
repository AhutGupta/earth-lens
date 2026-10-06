FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cached unless pyproject.toml/uv.lock change).
# The project itself is installed after the source is copied.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project

COPY . .
RUN uv sync --frozen --no-cache

CMD ["uv", "run", "earth-lens"]
