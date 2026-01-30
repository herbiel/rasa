# Rasa Flow Editor

A complete visual flow editor system for Rasa, enabling React Flow-style visual editing of conversation flows.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)             │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ Flow Editor│  │ Node Types │  │  React Flow Library  │  │
│  │  Component │  │            │  │                      │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JSON)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Backend (Python + Sanic)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ API Endpoints│  │ Flow Models  │  │  Flow Storage    │  │
│  │              │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Converter   │  │    Rasa      │  │  Story Format    │  │
│  │ Flow ↔ Story │  │    Core      │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Features

### 1. Visual Flow Editor
- **Drag-and-drop interface**: Intuitive node-based visual editor
- **Multiple node types**: 
  - Start/End nodes for flow boundaries
  - Intent nodes for user inputs
  - Action nodes for bot responses
  - Condition nodes for branching logic
- **Real-time editing**: Instant visual feedback
- **Minimap & controls**: Navigation aids for complex flows

### 2. Backend API
- **RESTful endpoints**: Complete CRUD operations for flows
- **Flow storage**: JSON-based persistence
- **Validation**: Automatic flow validation
- **Export/Import**: Convert between visual flows and Rasa stories

### 3. Data Models
- **FlowNode**: Represents conversation nodes
- **FlowEdge**: Represents connections between nodes
- **ConversationFlow**: Complete flow with metadata

### 4. Flow Conversion
- **Flow → Stories**: Converts visual flows to Rasa story format
- **Stories → Flow**: Imports existing stories as visual flows
- **Path traversal**: Intelligent graph traversal algorithm

## API Endpoints

### Flow Management

```
GET    /api/flows              # List all flows
POST   /api/flows              # Create new flow
GET    /api/flows/<id>         # Get flow details
PUT    /api/flows/<id>         # Update flow
DELETE /api/flows/<id>         # Delete flow
```

### Node Operations

```
POST   /api/flows/<id>/nodes           # Add node to flow
DELETE /api/flows/<id>/nodes/<node_id> # Remove node
```

### Edge Operations

```
POST   /api/flows/<id>/edges           # Add edge to flow
DELETE /api/flows/<id>/edges/<edge_id> # Remove edge
```

### Utilities

```
GET  /api/flows/<id>/export/stories    # Export to stories format
POST /api/flows/<id>/validate          # Validate flow
```

## Data Models

### FlowNode

```python
{
  "id": "uuid",
  "type": "intent|action|condition|start|end",
  "data": {
    "label": "Node Label",
    "intent": "greet",          # For intent nodes
    "action": "utter_greet",    # For action nodes
    "condition": "slot_filled"   # For condition nodes
  },
  "position": {"x": 0, "y": 0}
}
```

### FlowEdge

```python
{
  "id": "source-target-uuid",
  "source": "source_node_id",
  "target": "target_node_id",
  "label": "Optional label",
  "data": {}
}
```

### ConversationFlow

```python
{
  "id": "flow_uuid",
  "name": "Flow Name",
  "description": "Optional description",
  "nodes": [FlowNode, ...],
  "edges": [FlowEdge, ...],
  "metadata": {
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "version": "1.0"
  }
}
```

## Installation & Setup

### Backend Setup

1. The flow editor module is already integrated into Rasa
2. Flow data is stored in the `./flows` directory by default
3. API endpoints are available at `/api/flows`

### Frontend Setup

```bash
cd rasa/core/flow_editor/frontend

# Install dependencies
npm install

# Development mode
npm run dev

# Production build
npm run build
```

### Integration with Rasa Server

The flow editor can be integrated with existing Rasa server by registering the blueprint:

```python
from rasa.core.flow_editor.endpoints import flow_editor_bp

# In your server setup
app.blueprint(flow_editor_bp)
```

## Usage Examples

### Creating a Flow Programmatically

```python
from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge

# Create a new flow
flow = ConversationFlow.create(
    name="Greeting Flow",
    description="Simple greeting conversation"
)

# Add intent node
intent_node = FlowNode.create(
    node_type="intent",
    data={"intent": "greet", "label": "User says hello"},
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
edge1 = FlowEdge.create(start_node.id, intent_node.id)
edge2 = FlowEdge.create(intent_node.id, action_node.id)
flow.add_edge(edge1)
flow.add_edge(edge2)

# Save flow
from rasa.core.flow_editor.storage import FlowStorage
storage = FlowStorage()
storage.save_flow(flow)
```

### Converting Flow to Stories

```python
from rasa.core.flow_editor.converter import FlowConverter
from rasa.core.flow_editor.storage import FlowStorage

# Load flow
storage = FlowStorage()
flow = storage.load_flow("flow_id")

# Convert to stories
stories = FlowConverter.flow_to_stories(flow)

# Use stories for training
for story in stories:
    print(f"Story: {story.block_name}")
    for event in story.events:
        print(f"  - {event}")
```

## Multi-Bot Support

The system supports managing multiple conversation flows:

1. **Flow Isolation**: Each flow is independent
2. **Shared Resources**: Flows can reference same intents/actions
3. **Flow Management**: List, create, update, delete flows via API
4. **Metadata**: Track flow versions, creation dates, etc.

## Development Workflow

### Adding New Node Types

1. Create node component in `frontend/src/nodes/`
2. Register in `nodeTypes` object in `FlowEditor.tsx`
3. Update converter logic if needed for story export

### Extending API

1. Add endpoint to `endpoints.py`
2. Register route with blueprint
3. Update frontend API client

## Testing

### Backend Tests

```python
# Test flow creation
def test_flow_creation():
    flow = ConversationFlow.create(name="Test Flow")
    assert flow.id is not None
    assert len(flow.nodes) == 2  # start and end

# Test flow conversion
def test_flow_to_stories():
    flow = create_test_flow()
    stories = FlowConverter.flow_to_stories(flow)
    assert len(stories) > 0
```

### Frontend Tests

```typescript
// Test node creation
test('creates intent node', () => {
  const node = createIntentNode('greet');
  expect(node.type).toBe('intent');
  expect(node.data.intent).toBe('greet');
});
```

## Performance Considerations

- **Flow Storage**: JSON files for quick read/write
- **Graph Traversal**: Optimized path finding algorithm
- **Frontend**: React Flow handles rendering performance
- **API**: Async endpoints for non-blocking operations

## Security Considerations

- **Input Validation**: All API inputs validated
- **Path Traversal Protection**: Flow IDs validated
- **File System Safety**: Flows stored in designated directory only
- **CORS**: Configure appropriately for production

## Future Enhancements

1. **Real-time Collaboration**: Multiple users editing same flow
2. **Version Control**: Git-style flow versioning
3. **Templates**: Pre-built flow templates
4. **Advanced Validation**: Semantic flow validation
5. **Testing Integration**: Test flows within editor
6. **Import/Export**: Support for other formats (XML, BPMN)
7. **AI Suggestions**: ML-based flow suggestions
8. **Analytics**: Flow execution analytics

## Troubleshooting

### Flow Not Saving

- Check `./flows` directory exists and is writable
- Verify flow data is valid JSON
- Check server logs for errors

### Frontend Not Connecting

- Verify backend server is running
- Check API proxy configuration in `vite.config.ts`
- Inspect browser console for CORS errors

### Flow Export Failing

- Ensure flow has valid start node
- Check for disconnected nodes
- Validate node data completeness

## Contributing

When contributing to the flow editor:

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Test both backend and frontend changes

## License

This is part of the Rasa framework and follows the same Apache 2.0 license.
