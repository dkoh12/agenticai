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