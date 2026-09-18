FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_RL_NETWORK_ENABLED=0

WORKDIR /lab
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY mcp_servers ./mcp_servers
COPY tasks ./tasks
COPY fixtures ./fixtures
COPY schemas ./schemas
RUN python -m pip install --no-cache-dir pip==26.2.1 \
    && python -m pip install --no-cache-dir .

USER 65532:65532
ENTRYPOINT ["mcp-rl-lab"]
CMD ["catalogue"]
