# 🎨 Rasa Flow Editor - Visual Conversation Design

> **New Feature**: A complete visual flow editor system for Rasa, enabling intuitive drag-and-drop conversation design with React Flow.

[![React Flow](https://img.shields.io/badge/React_Flow-11.x-blue)](https://reactflow.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-37_passing-brightgreen)](#testing)

---

## 🌟 Overview

The Rasa Flow Editor transforms conversation design from text-based story files into an intuitive visual interface. Design complex conversation flows with drag-and-drop nodes, visualize conversation paths in real-time, and seamlessly integrate with Rasa's core training pipeline.

### Key Highlights

- 🎨 **Visual Editor**: Drag-and-drop interface powered by React Flow
- 🔄 **Bidirectional Conversion**: Flow ↔ Story format
- 🏗️ **5 Node Types**: Intent, Action, Condition, Start, End
- 🌐 **REST API**: 11 endpoints for complete flow management
- 🤖 **Multi-Bot Support**: Manage multiple bots with isolated flows
- 📦 **Production Ready**: Comprehensive tests and documentation

---

## 🚀 Quick Start

Get started in 5 minutes! See **[QUICK_START.md](QUICK_START.md)** for detailed instructions.

### 1. Start Backend

```bash
python -m rasa run --enable-api --port 5005
```

### 2. Start Frontend

```bash
cd rasa/core/flow_editor/frontend
npm install
npm run dev
```

### 3. Open Browser

Navigate to `http://localhost:5173` and start designing!

---

## 📸 Screenshots

### Flow Editor Interface

```
┌─────────────────────────────────────────────────────────────────┐
│ Rasa Flow Editor                                     [Save Flow] │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                        │
│ Flows    │                    ┌──────────┐                      │
│          │                    │  START   │                      │
│ • Flow 1 │                    └────┬─────┘                      │
│ • Flow 2 │                         │                            │
│ • Flow 3 │                         ▼                            │
│          │                  ┌─────────────┐                     │
│          │                  │ 💬 Intent   │                     │
│          │                  │   greet     │                     │
│          │                  └──────┬──────┘                     │
│          │                         │                            │
│          │                         ▼                            │
│          │                  ┌─────────────┐                     │
│          │                  │ ⚡ Action   │                     │
│          │                  │ utter_greet │                     │
│          │                  └──────┬──────┘                     │
│          │                         │                            │
│          │                         ▼                            │
│          │                    ┌──────────┐                      │
│          │                    │   END    │                      │
│          │                    └──────────┘                      │
│          │                                                        │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## 📚 Documentation

### Getting Started
- 📖 **[Quick Start Guide](QUICK_START.md)** - Get running in 5 minutes
- 🔧 **[Integration Guide](INTEGRATION_GUIDE.md)** - Integrate with your Rasa bot
- 📝 **[Flow Editor README](rasa/core/flow_editor/README.md)** - Module documentation

### Architecture & Design
- 🏛️ **[Architecture Design](ARCHITECTURE_DESIGN.md)** - Complete system design (Chinese)
- 📊 **[Visual Architecture](VISUAL_ARCHITECTURE.md)** - Architecture diagrams
- 📄 **[Project Summary](PROJECT_SUMMARY.md)** - Project overview

### Examples
- 💡 **[Example Script](examples/flow_editor_example.py)** - Working Python examples
- 🧪 **[Tests](tests/core/flow_editor/)** - 37 comprehensive test cases

---

## 🎯 Features

### Visual Editor

- **Drag & Drop**: Intuitive node placement
- **Real-time Updates**: See changes immediately
- **Zoom & Pan**: Navigate large flows easily
- **Mini-map**: Overview of entire flow
- **Auto-layout**: Automatic node positioning

### Node Types

| Node | Icon | Purpose | Example |
|------|------|---------|---------|
| **Intent** | 🟦 | User input trigger | `greet`, `ask_weather` |
| **Action** | 🟩 | Bot response | `utter_greet`, `action_weather` |
| **Condition** | 🟧 | Branching logic | `slot_filled?`, `confidence > 0.8` |
| **Start** | 🟢 | Flow entry point | - |
| **End** | 🔴 | Flow exit point | - |

### Backend API

```
REST API Endpoints:
  GET    /api/flows              # List all flows
  POST   /api/flows              # Create flow
  GET    /api/flows/{id}         # Get flow
  PUT    /api/flows/{id}         # Update flow
  DELETE /api/flows/{id}         # Delete flow
  POST   /api/flows/{id}/nodes   # Add node
  DELETE /api/flows/{id}/nodes/{node_id}   # Remove node
  POST   /api/flows/{id}/edges   # Add edge
  DELETE /api/flows/{id}/edges/{edge_id}   # Remove edge
  GET    /api/flows/{id}/export/stories    # Export to Rasa
  POST   /api/flows/{id}/validate          # Validate flow
```

### Data Flow

```
Visual Flow (JSON) → Flow Converter → Rasa Stories (YAML) → Training
```

---

## 💻 Usage Examples

### Python Example

```python
from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge
from rasa.core.flow_editor.storage import FlowStorage
from rasa.core.flow_editor.converter import FlowConverter

# Create a flow
flow = ConversationFlow.create(name="Greeting Flow")

# Add nodes
intent = FlowNode.create("intent", data={"intent": "greet"})
action = FlowNode.create("action", data={"action": "utter_greet"})
flow.add_node(intent)
flow.add_node(action)

# Connect nodes
flow.add_edge(FlowEdge.create(intent.id, action.id))

# Save flow
storage = FlowStorage()
storage.save_flow(flow)

# Convert to stories
stories = FlowConverter.flow_to_stories(flow)
```

### JavaScript/TypeScript Example

```typescript
import axios from 'axios';

// Create flow
const { data } = await axios.post('/api/flows', {
  name: 'My Flow',
  description: 'Example flow'
});

// Add node
await axios.post(`/api/flows/${data.flow.id}/nodes`, {
  type: 'intent',
  data: { intent: 'greet' },
  position: { x: 250, y: 100 }
});
```

### cURL Example

```bash
# Create flow
curl -X POST http://localhost:5005/api/flows \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Flow"}'

# Export to stories
curl http://localhost:5005/api/flows/{flow_id}/export/stories
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all flow editor tests
pytest tests/core/flow_editor/

# Run specific test file
pytest tests/core/flow_editor/test_models.py

# Run with coverage
pytest tests/core/flow_editor/ --cov=rasa.core.flow_editor
```

**Test Coverage**: 37 tests covering models, storage, and conversion logic.

---

## 🏗️ Architecture

### System Components

```
┌────────────────────────────────────┐
│      React Flow Frontend           │
│  (TypeScript + React + Vite)       │
└─────────────┬──────────────────────┘
              │ REST API
┌─────────────▼──────────────────────┐
│      Sanic Backend API             │
│  (Python + Flow Models)            │
└─────────────┬──────────────────────┘
              │
┌─────────────▼──────────────────────┐
│      Storage Layer                 │
│  (JSON Files / Database)           │
└─────────────┬──────────────────────┘
              │
┌─────────────▼──────────────────────┐
│      Rasa Core                     │
│  (Stories + Domain + Policies)     │
└────────────────────────────────────┘
```

See **[VISUAL_ARCHITECTURE.md](VISUAL_ARCHITECTURE.md)** for detailed diagrams.

---

## 🤝 Multi-Bot Support

Organize flows by bot for multi-bot deployments:

```
./flows/
  ├── bot_a/
  │   ├── greeting_flow.json
  │   └── faq_flow.json
  ├── bot_b/
  │   └── booking_flow.json
  └── bot_c/
      └── support_flow.json
```

---

## 🔧 Configuration

### Backend Configuration

```python
from rasa.core.flow_editor.endpoints import flow_editor_bp, get_flow_storage

# Configure storage path
storage = get_flow_storage("/custom/path/to/flows")

# Register blueprint in Rasa server
app.blueprint(flow_editor_bp)
```

### Frontend Configuration

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5005',
        changeOrigin: true,
      },
    },
  },
});
```

---

## 🚧 Roadmap

### ✅ Completed (v1.0)

- [x] Core data models
- [x] REST API endpoints
- [x] React Flow integration
- [x] 5 node types
- [x] Flow-to-story conversion
- [x] JSON storage
- [x] Comprehensive documentation

### 🔜 Planned (v2.0)

- [ ] Real-time collaboration (WebSocket)
- [ ] Version control system
- [ ] Flow templates library
- [ ] Advanced validation
- [ ] Database backend
- [ ] Authentication/Authorization
- [ ] Flow analytics dashboard
- [ ] Import from other formats

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Read the documentation
2. Follow existing code style
3. Add tests for new features
4. Update documentation
5. Submit a pull request

---

## 📝 License

This is part of the Rasa framework and follows the same Apache 2.0 license.

---

## 🆘 Support

- 📖 **Documentation**: See files in the root directory
- 💬 **Community**: [Rasa Forum](https://forum.rasa.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/rasahq/rasa/issues)
- 📧 **Contact**: Check Rasa documentation

---

## 🎉 Acknowledgments

Built with:
- [React Flow](https://reactflow.dev/) - Visual node editor
- [React](https://react.dev/) - UI framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Vite](https://vitejs.dev/) - Build tool
- [Sanic](https://sanic.dev/) - Python web framework
- [Rasa](https://rasa.com/) - Conversation AI framework

---

<div align="center">
  <p>Made with ❤️ for the Rasa Community</p>
  <p>
    <a href="QUICK_START.md">Quick Start</a> •
    <a href="INTEGRATION_GUIDE.md">Integration Guide</a> •
    <a href="rasa/core/flow_editor/README.md">Full Documentation</a>
  </p>
</div>
