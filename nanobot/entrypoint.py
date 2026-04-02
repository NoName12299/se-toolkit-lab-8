#!/usr/bin/env python3
import json
import os
import sys

CONFIG_PATH = "/app/nanobot/config.json"
RESOLVED_PATH = "/app/nanobot/config.resolved.json"

def main():
    # Читаем конфиг
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

        # Подставляем переменные из окружения
    # Пробуем получить ключ из QWEN_CODE_API_KEY, если LLM_API_KEY не задан
    api_key = os.getenv("LLM_API_KEY") or os.getenv("QWEN_CODE_API_KEY")
    if api_key:
        config.setdefault("providers", {}).setdefault("custom", {})["apiKey"] = api_key
    
    api_base = os.getenv("LLM_API_BASE_URL")
    if not api_base:
        # Собираем из переменных или используем значение по умолчанию
        port = os.getenv("QWEN_CODE_API_CONTAINER_PORT", "8080")
        api_base = f"http://qwen-code-api:{port}/v1"
    if api_base:
        config.setdefault("providers", {}).setdefault("custom", {})["apiBase"] = api_base
    
    model = os.getenv("LLM_API_MODEL") or "coder-model"
    if model:
        config.setdefault("agents", {}).setdefault("defaults", {})["model"] = model
    # Gateway
    if os.getenv("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
        config.setdefault("gateway", {})["host"] = os.getenv("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    if os.getenv("NANOBOT_GATEWAY_CONTAINER_PORT"):
        config.setdefault("gateway", {})["port"] = int(os.getenv("NANOBOT_GATEWAY_CONTAINER_PORT"))

    # WebSocket channel
    if os.getenv("NANOBOT_WEBCHAT_CONTAINER_ADDRESS") and os.getenv("NANOBOT_WEBCHAT_CONTAINER_PORT"):
        config.setdefault("channels", {}).setdefault("webchat", {})["enabled"] = True
        config["channels"]["webchat"]["host"] = os.getenv("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
        config["channels"]["webchat"]["port"] = int(os.getenv("NANOBOT_WEBCHAT_CONTAINER_PORT"))
        config["channels"]["webchat"]["allowFrom"] = ["*"]

    # MCP servers
    mcp_servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
    
    if os.getenv("NANOBOT_LMS_BACKEND_URL") and os.getenv("NANOBOT_LMS_API_KEY"):
        mcp_servers["lms"] = {
            "command": "python",
            "args": ["-m", "mcp_lms"],
            "env": {
                "NANOBOT_LMS_BACKEND_URL": os.getenv("NANOBOT_LMS_BACKEND_URL"),
                "NANOBOT_LMS_API_KEY": os.getenv("NANOBOT_LMS_API_KEY")
            }
        }

    # Сохраняем
    with open(RESOLVED_PATH, "w") as f:
        json.dump(config, f, indent=2)

    # Запускаем
    os.execvp("nanobot", ["nanobot", "gateway", "--config", RESOLVED_PATH, "--workspace", "/app/nanobot/workspace"])

if __name__ == "__main__":
    main()
