# PM Agentic AI Platform

A Cursor-like platform for Product Managers that uses agentic AI to help make data-driven product decisions.

## Features

- 🤖 **Agentic AI**: LangGraph-powered agent for complex multi-step reasoning
- 🔗 **MCP Integration**: Connects to PM tools via Model Context Protocol
- 📊 **Analytics Tools**: Mixpanel, PostHog integration
- 💬 **Support Tools**: Zendesk, Intercom integration
- 💼 **Sales Tools**: Salesforce integration
- 📋 **Project Management**: Jira, Confluence integration
- 📄 **Document Processing**: Upload and analyze customer interviews (PDF/DOCX)
- 🎯 **Feature Recommendations**: Data-driven feature suggestions
- ✨ **UI Proposals**: Automated UI/workflow change proposals
- 📝 **Task Breakdown**: Generate development task lists

## Architecture

```
User Query → LangGraph Agent → MCP Tools → Data Processors → Analyzers → Generators → Output
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Verify Installation

```bash
python -c "from src.agent.graph import create_agent"
```

## Usage

### CLI Interface

```bash
# Upload customer interview
python main.py upload interview.pdf

# Ask strategic questions
python main.py ask "What should we build next?"

# Analyze uploaded data
python main.py analyze

# Start web UI
python main.py serve
```

### Web UI

```bash
python app.py
# Open browser to http://localhost:8000
```

## Project Structure

```
squash/
├── main.py                    # CLI entry point
├── app.py                     # Web UI entry point
├── config/                    # Configuration files
├── src/
│   ├── agent/                # LangGraph agent
│   ├── mcp/                  # MCP integration layer
│   ├── tools/                # Tool connectors
│   ├── processors/           # Data processors
│   ├── analyzers/            # Feature analyzers
│   ├── generators/           # Output generators
│   ├── utils/                # Utilities
│   └── web/                  # Web UI
├── data/                     # Data storage
└── tests/                    # Tests
```

## Development

### Running Tests

```bash
pytest tests/
```

### Mock vs Real MCP Servers

This prototype uses mock MCP servers with realistic sample data. To use real MCP servers:

1. Set `USE_MOCK_MCP=false` in `.env`
2. Configure real MCP server endpoints in `config/mcp_servers.json`
3. Add authentication credentials to `.env`

## Contributing

This is a prototype. Contributions welcome!

## License

MIT
