# Integration Guide - Rasa Flow Editor

This guide explains how to integrate the React Flow visual editor into your Rasa installation.

## Prerequisites

- Rasa 3.x installed
- Python 3.8+
- Node.js 16+ (for frontend)
- npm or yarn

## Backend Integration

### 1. Register the Flow Editor Blueprint

Edit your Rasa server file (usually `rasa/server.py` or your custom server script):

```python
from sanic import Sanic
from rasa.core.flow_editor.endpoints import flow_editor_bp

# In your server setup function
def create_app():
    app = Sanic("rasa_server")
    
    # ... existing setup ...
    
    # Register the flow editor blueprint
    app.blueprint(flow_editor_bp)
    
    return app
```

### 2. Configure Flow Storage

By default, flows are stored in `./flows` directory. To customize:

```python
from rasa.core.flow_editor.endpoints import get_flow_storage

# Set custom storage path before starting server
storage = get_flow_storage("/path/to/your/flows")
```

### 3. Start the Server

```bash
rasa run --enable-api
```

The Flow Editor API will be available at `http://localhost:5005/api/flows`

## Frontend Integration

### 1. Install Dependencies

```bash
cd rasa/core/flow_editor/frontend
npm install
```

### 2. Development Mode

```bash
npm run dev
```

This starts the development server at `http://localhost:5173` with hot reload.

### 3. Production Build

```bash
npm run build
```

Built files will be in the `dist` directory.

### 4. Serve Frontend with Rasa

To serve the frontend from Rasa server:

```python
from sanic import Sanic
from sanic.response import file

app = Sanic("rasa_server")

# Serve the frontend build
@app.route("/flow-editor")
async def flow_editor_ui(request):
    return await file("rasa/core/flow_editor/frontend/dist/index.html")

# Serve static assets
app.static("/flow-editor/assets", "rasa/core/flow_editor/frontend/dist/assets")
```

## API Usage Examples

### Create a New Flow

```bash
curl -X POST http://localhost:5005/api/flows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Flow",
    "description": "A simple greeting flow"
  }'
```

Response:
```json
{
  "flow": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "My First Flow",
    "description": "A simple greeting flow",
    "nodes": [
      {
        "id": "start-node",
        "type": "start",
        "data": {"label": "START"},
        "position": {"x": 250, "y": 0}
      },
      {
        "id": "end-node",
        "type": "end",
        "data": {"label": "END"},
        "position": {"x": 250, "y": 500}
      }
    ],
    "edges": [],
    "metadata": {
      "created_at": null,
      "updated_at": null,
      "version": "1.0"
    }
  }
}
```

### List All Flows

```bash
curl http://localhost:5005/api/flows
```

### Get Flow Details

```bash
curl http://localhost:5005/api/flows/{flow_id}
```

### Add a Node to Flow

```bash
curl -X POST http://localhost:5005/api/flows/{flow_id}/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "type": "intent",
    "data": {
      "intent": "greet",
      "label": "User says hello"
    },
    "position": {"x": 250, "y": 100}
  }'
```

### Add an Edge

```bash
curl -X POST http://localhost:5005/api/flows/{flow_id}/edges \
  -H "Content-Type: application/json" \
  -d '{
    "source": "node1-id",
    "target": "node2-id",
    "label": "Optional label"
  }'
```

### Export Flow to Stories

```bash
curl http://localhost:5005/api/flows/{flow_id}/export/stories
```

### Validate Flow

```bash
curl -X POST http://localhost:5005/api/flows/{flow_id}/validate
```

Response:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Node 'action_node_xyz' is not connected"
  ]
}
```

## Programmatic Usage

### Python Example

```python
from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge
from rasa.core.flow_editor.storage import FlowStorage
from rasa.core.flow_editor.converter import FlowConverter

# Create a flow
flow = ConversationFlow.create(
    name="Greeting Flow",
    description="Simple greeting"
)

# Add intent node
intent_node = FlowNode.create(
    node_type="intent",
    data={"intent": "greet", "label": "User greets"},
    position={"x": 250, "y": 100}
)
flow.add_node(intent_node)

# Add action node
action_node = FlowNode.create(
    node_type="action",
    data={"action": "utter_greet", "label": "Bot responds"},
    position={"x": 250, "y": 200}
)
flow.add_node(action_node)

# Connect nodes
start_node = flow.nodes[0]  # Default start node
end_node = flow.nodes[1]    # Default end node

flow.add_edge(FlowEdge.create(start_node.id, intent_node.id))
flow.add_edge(FlowEdge.create(intent_node.id, action_node.id))
flow.add_edge(FlowEdge.create(action_node.id, end_node.id))

# Save flow
storage = FlowStorage()
storage.save_flow(flow)

# Convert to stories
stories = FlowConverter.flow_to_stories(flow)
for story in stories:
    print(f"Story: {story.block_name}")
    for event in story.events:
        print(f"  {event}")
```

### JavaScript/TypeScript Example

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:5005/api/flows';

// Create a flow
const createFlow = async () => {
  const response = await axios.post(API_BASE, {
    name: 'My Flow',
    description: 'Example flow'
  });
  return response.data.flow;
};

// Add node
const addNode = async (flowId: string) => {
  const response = await axios.post(`${API_BASE}/${flowId}/nodes`, {
    type: 'intent',
    data: {
      intent: 'greet',
      label: 'Greeting'
    },
    position: { x: 250, y: 100 }
  });
  return response.data.node;
};

// Update flow
const updateFlow = async (flow: any) => {
  const response = await axios.put(`${API_BASE}/${flow.id}`, flow);
  return response.data.flow;
};
```

## Multi-Bot Support

To support multiple bots, organize flows by bot ID:

```python
# Store flows per bot
bot_storage = FlowStorage(f"./flows/{bot_id}")

# In your API, filter by bot
@flow_editor_bp.route("/bots/<bot_id:str>/flows")
async def list_bot_flows(request, bot_id):
    storage = FlowStorage(f"./flows/{bot_id}")
    flows = storage.list_flows()
    return response.json({"flows": flows})
```

## Deployment Considerations

### Security

1. **Authentication**: Add authentication middleware to protect API endpoints
2. **Authorization**: Implement RBAC for flow access control
3. **Input Validation**: Always validate flow data on the server side

```python
from functools import wraps
from sanic.response import json

def require_auth(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not validate_token(token):
            return json({'error': 'Unauthorized'}, status=401)
        return await f(request, *args, **kwargs)
    return decorated_function

@flow_editor_bp.route("/flows", methods=["POST"])
@require_auth
async def create_flow(request):
    # ... implementation ...
```

### Performance

1. **Caching**: Use Redis for flow caching
2. **Pagination**: Implement pagination for large flow lists
3. **Lazy Loading**: Load flow details on demand

### Monitoring

1. **Logging**: Log all flow operations
2. **Metrics**: Track flow creation, updates, validation errors
3. **Alerts**: Monitor for suspicious activity

## Troubleshooting

### Issue: "Flow not found"

**Solution**: Check that the flow ID is correct and the flow file exists in the storage directory.

### Issue: "Cannot connect to backend"

**Solution**: Ensure Rasa server is running and CORS is properly configured:

```python
from sanic_cors import CORS

app = Sanic("rasa_server")
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Issue: "Flow validation errors"

**Solution**: Check that all required node fields are filled and connections are valid.

## Next Steps

1. Explore the [Architecture Design Document](../ARCHITECTURE_DESIGN.md) for system details
2. Review the [README](../rasa/core/flow_editor/README.md) for feature documentation
3. Check out example flows in `examples/flow_editor_example.py`
4. Customize node types for your specific use case
5. Implement custom validation rules

## Support

For issues and questions:
- GitHub Issues: https://github.com/rasahq/rasa/issues
- Documentation: https://rasa.com/docs
- Community Forum: https://forum.rasa.com
