# Rasa Flow Editor - Frontend

React-based visual flow editor using React Flow for designing Rasa conversation flows.

## Features

- Visual node-based flow editor
- Drag-and-drop interface
- Multiple node types: Intent, Action, Condition, Start, End
- Real-time flow editing
- Integration with Rasa backend API
- Flow validation
- Export to Rasa story format

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Node Types

- **Start Node**: Entry point of the conversation flow
- **End Node**: Exit point of the conversation flow
- **Intent Node**: User intent trigger
- **Action Node**: Bot action execution
- **Condition Node**: Conditional branching logic

## API Integration

The frontend communicates with the Rasa backend through REST API endpoints at `/api/flows`.
