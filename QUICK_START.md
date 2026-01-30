# Quick Start Guide - Rasa Flow Editor

Get up and running with the Rasa Flow Editor in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+
- Rasa installed

## Installation

### 1. Clone/Update Rasa

```bash
# If you already have Rasa, pull the latest changes
cd rasa
git pull origin copilot/analyze-rasa-architecture

# Or clone fresh
git clone https://github.com/herbiel/rasa.git
cd rasa
git checkout copilot/analyze-rasa-architecture
```

### 2. Install Frontend Dependencies

```bash
cd rasa/core/flow_editor/frontend
npm install
```

## Running the Flow Editor

### Option 1: Development Mode (Recommended for testing)

**Terminal 1 - Start Rasa Server:**
```bash
# From project root
cd rasa
python -m rasa run --enable-api --port 5005
```

**Terminal 2 - Start Frontend Dev Server:**
```bash
# From frontend directory
cd rasa/core/flow_editor/frontend
npm run dev
```

Open browser to: `http://localhost:5173`

### Option 2: Production Mode

**Build Frontend:**
```bash
cd rasa/core/flow_editor/frontend
npm run build
```

**Start Rasa with Frontend:**
```bash
# Configure Rasa to serve the built frontend
# Then start Rasa server
python -m rasa run --enable-api
```

## Your First Flow

### Using the UI

1. **Open the Flow Editor**: Navigate to `http://localhost:5173`

2. **Create a New Flow**:
   - Click "New Flow" button
   - Enter name: "Greeting Flow"
   - Click OK

3. **Add Nodes**:
   - Click "+ Intent" button
   - A blue intent node appears on canvas
   - Click the node to edit properties
   - Set intent name: "greet"
   
   - Click "+ Action" button
   - A green action node appears
   - Set action name: "utter_greet"

4. **Connect Nodes**:
   - Drag from the bottom handle of START node
   - Connect to top of Intent node
   - Connect Intent to Action
   - Connect Action to END

5. **Save**:
   - Click "💾 Save Flow" button
   - Flow is saved to `./flows` directory

### Using the API

```bash
# 1. Create a flow
curl -X POST http://localhost:5005/api/flows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Flow",
    "description": "A simple greeting flow"
  }'
# Save the returned flow ID

# 2. Add an intent node
curl -X POST http://localhost:5005/api/flows/{FLOW_ID}/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "type": "intent",
    "data": {
      "intent": "greet",
      "label": "User says hello",
      "text": "/greet"
    },
    "position": {"x": 250, "y": 100}
  }'
# Save the returned node ID

# 3. Add an action node
curl -X POST http://localhost:5005/api/flows/{FLOW_ID}/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "data": {
      "action": "utter_greet",
      "label": "Bot responds"
    },
    "position": {"x": 250, "y": 200}
  }'

# 4. Connect the nodes
curl -X POST http://localhost:5005/api/flows/{FLOW_ID}/edges \
  -H "Content-Type: application/json" \
  -d '{
    "source": "{START_NODE_ID}",
    "target": "{INTENT_NODE_ID}"
  }'

# 5. Export to stories
curl http://localhost:5005/api/flows/{FLOW_ID}/export/stories
```

### Using Python

```python
from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge
from rasa.core.flow_editor.storage import FlowStorage

# 1. Create a flow
flow = ConversationFlow.create(
    name="Quick Start Flow",
    description="My first flow"
)

# 2. Add nodes
start_node = flow.nodes[0]  # Default start node
end_node = flow.nodes[1]    # Default end node

intent_node = FlowNode.create(
    node_type="intent",
    data={"intent": "greet", "text": "/greet"},
    position={"x": 250, "y": 100}
)
flow.add_node(intent_node)

action_node = FlowNode.create(
    node_type="action",
    data={"action": "utter_greet"},
    position={"x": 250, "y": 200}
)
flow.add_node(action_node)

# 3. Connect nodes
flow.add_edge(FlowEdge.create(start_node.id, intent_node.id))
flow.add_edge(FlowEdge.create(intent_node.id, action_node.id))
flow.add_edge(FlowEdge.create(action_node.id, end_node.id))

# 4. Save
storage = FlowStorage()
storage.save_flow(flow)

print(f"Flow created with ID: {flow.id}")
print(f"Saved to: ./flows/{flow.id}.json")
```

## Common Tasks

### View All Flows

```bash
curl http://localhost:5005/api/flows
```

### Load a Flow

```bash
curl http://localhost:5005/api/flows/{FLOW_ID}
```

### Update a Flow

```bash
curl -X PUT http://localhost:5005/api/flows/{FLOW_ID} \
  -H "Content-Type: application/json" \
  -d @flow.json
```

### Delete a Flow

```bash
curl -X DELETE http://localhost:5005/api/flows/{FLOW_ID}
```

### Validate a Flow

```bash
curl -X POST http://localhost:5005/api/flows/{FLOW_ID}/validate
```

## Node Types Reference

### Intent Node 🟦
Represents a user intent trigger.

```json
{
  "type": "intent",
  "data": {
    "intent": "greet",
    "label": "User greeting",
    "text": "/greet",
    "entities": []
  }
}
```

### Action Node 🟩
Represents a bot action.

```json
{
  "type": "action",
  "data": {
    "action": "utter_greet",
    "label": "Bot greeting response"
  }
}
```

### Condition Node 🟧
Represents conditional branching.

```json
{
  "type": "condition",
  "data": {
    "condition": "slot_filled",
    "label": "Check if slot is filled"
  }
}
```

### Start Node 🟢
Flow entry point (automatically created).

```json
{
  "type": "start",
  "data": {"label": "START"}
}
```

### End Node 🔴
Flow exit point (automatically created).

```json
{
  "type": "end",
  "data": {"label": "END"}
}
```

## Example Flows

### Simple Greeting Flow

```
START → Intent(greet) → Action(utter_greet) → END
```

### FAQ Flow with Branching

```
START → Intent(ask_question) → Condition(known_answer?)
                                      ↓                ↓
                                   [Yes]            [No]
                                      ↓                ↓
                              Action(answer)    Action(fallback)
                                      ↓                ↓
                                     END              END
```

### Multi-step Booking Flow

```
START → Intent(book) → Action(ask_date) → Intent(provide_date)
                                                    ↓
                                           Action(ask_time)
                                                    ↓
                                           Intent(provide_time)
                                                    ↓
                                           Action(confirm)
                                                    ↓
                                                   END
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Zoom In | `Ctrl/Cmd + +` |
| Zoom Out | `Ctrl/Cmd + -` |
| Fit View | `Ctrl/Cmd + 0` |
| Delete Selected | `Delete` or `Backspace` |
| Select All | `Ctrl/Cmd + A` |
| Copy | `Ctrl/Cmd + C` |
| Paste | `Ctrl/Cmd + V` |

## Troubleshooting

### "Cannot connect to backend"

**Check:**
1. Rasa server is running: `curl http://localhost:5005/`
2. CORS is enabled in Rasa config
3. Firewall allows port 5005

**Fix:**
```bash
# Restart Rasa with API enabled
python -m rasa run --enable-api --cors "*"
```

### "Flow not found"

**Check:**
1. Flow ID is correct
2. Flow file exists in `./flows` directory

**Fix:**
```bash
# List all flows to find correct ID
curl http://localhost:5005/api/flows
```

### "Frontend not loading"

**Check:**
1. Node modules installed: `npm install`
2. Port 5173 is not in use

**Fix:**
```bash
cd rasa/core/flow_editor/frontend
npm install
npm run dev -- --port 3000  # Use different port
```

### "Node types not rendering"

**Check:**
1. Browser console for errors
2. React Flow CSS loaded

**Fix:**
```bash
# Rebuild frontend
npm run build
```

## Next Steps

1. **Explore Advanced Features**:
   - Read [Integration Guide](INTEGRATION_GUIDE.md)
   - Study [Architecture Design](ARCHITECTURE_DESIGN.md)

2. **Customize**:
   - Add custom node types
   - Implement validation rules
   - Create flow templates

3. **Integrate**:
   - Connect to your Rasa bot
   - Export flows to stories
   - Train your model

4. **Share**:
   - Export flows as JSON
   - Share with team members
   - Version control flows

## Resources

- **Documentation**: `/rasa/core/flow_editor/README.md`
- **API Reference**: `INTEGRATION_GUIDE.md`
- **Examples**: `/examples/flow_editor_example.py`
- **Tests**: `/tests/core/flow_editor/`

## Getting Help

- Check the documentation
- Review example scripts
- Open an issue on GitHub
- Ask on Rasa forum

Happy flow editing! 🚀
