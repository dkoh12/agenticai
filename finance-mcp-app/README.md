┌─────────────────────────────────────────────┐
│  React TypeScript Frontend (Port 5173)     │
│  ├── Dashboard                              │
│  ├── Transactions                           │
│  ├── Budgets                               │
│  └── AI Chat                               │
└─────────────────┬───────────────────────────┘
                  │ HTTP/API Calls
┌─────────────────▼───────────────────────────┐
│  Flask API Server (Port 5003)              │
│  ├── /api/financial_summary                │
│  ├── /api/transactions                     │
│  ├── /api/budgets                          │
│  ├── /api/chat                             │
│  └── /api/add_transaction                  │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────────┐
│  Finance MCP Server + Ollama LLM           │
│  ├── Transaction Tools                     │
│  ├── Budget Tools                          │
│  ├── Summary Tools                         │
│  └── AI Assistant                          │
└─────────────────────────────────────────────┘

# Start React Frontend

React server is on localhost:5173
```
cd agenticai/finance-mcp-app/frontend
npm run dev
```

# Start Flask Backend

Flask backend server is on localhost:5003
```
source .venv/bin/activate
cd finance-mcp-app
python finance_web_mcp.py
```

# Single Server Production (Optional)

To run everything from one server:

1. Build React app:
```
cd frontend
npm run build
```

2. Modify Flask to serve static files (would need code changes)
3. Access everything at http://localhost:5003

**Note:** Currently requires code modifications to Flask server to serve the built React files.
