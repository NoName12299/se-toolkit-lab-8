FROM python:3.14-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем все пакеты из workspace
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol ./nanobot-websocket-channel/nanobot-channel-protocol
COPY --from=workspace nanobot-websocket-channel/mcp-webchat ./nanobot-websocket-channel/mcp-webchat
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat ./nanobot-websocket-channel/nanobot-webchat
COPY --from=workspace mcp/mcp-lms ./mcp/mcp-lms
COPY --from=workspace mcp/mcp-obs ./mcp/mcp-obs

# Удаляем tool.uv.sources из pyproject.toml чтобы uv мог собрать пакеты
RUN sed -i '/\[tool\.uv\.sources\]/,/^\[.*\]/d' ./nanobot-websocket-channel/mcp-webchat/pyproject.toml && \
    sed -i '/\[tool\.uv\.sources\]/,/^\[.*\]/d' ./nanobot-websocket-channel/nanobot-webchat/pyproject.toml && \
    sed -i '/\[tool\.uv\.sources\]/,/^\[.*\]/d' ./mcp/mcp-obs/pyproject.toml

# Устанавливаем зависимости в правильном порядке
# 1. Сначала nanobot-channel-protocol (нет зависимостей от workspace)
RUN uv pip install --system ./nanobot-websocket-channel/nanobot-channel-protocol

# 2. Затем mcp-lms
RUN uv pip install --system ./mcp/mcp-lms

# 3. mcp-obs (observability tools)
RUN uv pip install --system ./mcp/mcp-obs

# 4. mcp-webchat (зависит от nanobot-channel-protocol, уже установлен)
RUN uv pip install --system ./nanobot-websocket-channel/mcp-webchat

# 5. nanobot-webchat (зависит от nanobot-channel-protocol и nanobot-ai)
RUN uv pip install --system ./nanobot-websocket-channel/nanobot-webchat

# Копируем nanobot код из текущего context
COPY . ./nanobot/

ENV PATH="/usr/local/bin:$PATH"

CMD ["python", "/app/nanobot/entrypoint.py"]
