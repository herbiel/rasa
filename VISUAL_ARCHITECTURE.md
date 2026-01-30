# Rasa Flow Editor - Visual Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              React Flow Visual Editor (Browser)                 │ │
│  │                                                                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │ │
│  │  │ Sidebar  │  │  Canvas  │  │ Controls │  │ Property │       │ │
│  │  │   List   │  │  Editor  │  │  Panel   │  │  Panel   │       │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │ │
│  │                                                                  │ │
│  │  Custom Nodes:                                                  │ │
│  │  [🟦 Intent] [🟩 Action] [🟧 Condition] [🟢 Start] [🔴 End]  │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ REST API (JSON)
                                │ /api/flows/*
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                      Backend API Layer (Python)                      │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Sanic REST API Blueprint                           │ │
│  │                                                                  │ │
│  │  Endpoints:                                                     │ │
│  │  • GET    /api/flows           → List all flows                │ │
│  │  • POST   /api/flows           → Create flow                   │ │
│  │  • GET    /api/flows/{id}      → Get flow                      │ │
│  │  • PUT    /api/flows/{id}      → Update flow                   │ │
│  │  • DELETE /api/flows/{id}      → Delete flow                   │ │
│  │  • POST   /api/flows/{id}/nodes         → Add node             │ │
│  │  • DELETE /api/flows/{id}/nodes/{nid}   → Remove node          │ │
│  │  • POST   /api/flows/{id}/edges         → Add edge             │ │
│  │  • DELETE /api/flows/{id}/edges/{eid}   → Remove edge          │ │
│  │  • GET    /api/flows/{id}/export/stories → Export              │ │
│  │  • POST   /api/flows/{id}/validate      → Validate             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                    Business Logic Layer (Python)                     │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Flow Models    │  │  Flow Converter  │  │  Flow Validator  │  │
│  │                  │  │                  │  │                  │  │
│  │  • FlowNode      │  │  • Flow→Story    │  │  • Completeness  │  │
│  │  • FlowEdge      │  │  • Story→Flow    │  │  • Connectivity  │  │
│  │  • ConvFlow      │  │  • Graph Traverse│  │  • Logic Check   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                       Storage Layer (Python)                         │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Flow Storage Manager                         │ │
│  │                                                                  │ │
│  │  • save_flow()    • load_flow()                                │ │
│  │  • delete_flow()  • list_flows()                               │ │
│  │  • flow_exists()                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Storage Backends                             │ │
│  │                                                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │ │
│  │  │  JSON Files  │  │  PostgreSQL  │  │    Redis     │         │ │
│  │  │   (Default)  │  │   (Future)   │  │  (Future)    │         │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                     Rasa Core Integration                            │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  Story Graph & Domain                           │ │
│  │                                                                  │ │
│  │  • StoryStep → Training data                                   │ │
│  │  • Events → UserUttered, ActionExecuted                        │ │
│  │  • Domain → Intents, Actions, Slots                            │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Dialogue Management                           │ │
│  │                                                                  │ │
│  │  • Policies → TEDPolicy, RulePolicy                            │ │
│  │  • Tracker → DialogueStateTracker                              │ │
│  │  • NLU Pipeline → Intent Classification                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Flow Creation Workflow

```
User Action                Frontend                 Backend                  Storage
    │                         │                        │                        │
    │ Click "New Flow"        │                        │                        │
    ├────────────────────────>│                        │                        │
    │                         │ POST /api/flows        │                        │
    │                         ├───────────────────────>│                        │
    │                         │                        │ Create ConversationFlow│
    │                         │                        │ with default nodes     │
    │                         │                        ├───────────────────────>│
    │                         │                        │                   Save JSON
    │                         │                        │<───────────────────────┤
    │                         │<───────────────────────┤                        │
    │                         │ Return Flow JSON       │                        │
    │<────────────────────────┤                        │                        │
    │ Display Flow            │                        │                        │
```

### Node Addition Workflow

```
User Action                Frontend                 Backend                  Storage
    │                         │                        │                        │
    │ Drag & Drop Node        │                        │                        │
    ├────────────────────────>│                        │                        │
    │                         │ POST /api/flows/{id}/nodes                     │
    │                         ├───────────────────────>│                        │
    │                         │                        │ Create FlowNode        │
    │                         │                        │ Add to flow.nodes      │
    │                         │                        ├───────────────────────>│
    │                         │                        │                   Update JSON
    │                         │                        │<───────────────────────┤
    │                         │<───────────────────────┤                        │
    │                         │ Return Node JSON       │                        │
    │<────────────────────────┤                        │                        │
    │ Render Node on Canvas   │                        │                        │
```

### Export to Stories Workflow

```
User Action                Frontend                 Backend                  Rasa Core
    │                         │                        │                        │
    │ Click "Export"          │                        │                        │
    ├────────────────────────>│                        │                        │
    │                         │ GET /api/flows/{id}/export/stories             │
    │                         ├───────────────────────>│                        │
    │                         │                        │ Load flow              │
    │                         │                        │ Traverse graph         │
    │                         │                        │ Generate paths         │
    │                         │                        │ Convert to StorySteps  │
    │                         │                        ├───────────────────────>│
    │                         │                        │ Validate with Domain   │
    │                         │                        │<───────────────────────┤
    │                         │<───────────────────────┤                        │
    │                         │ Return Stories YAML    │                        │
    │<────────────────────────┤                        │                        │
    │ Download/Save Stories   │                        │                        │
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                          FlowEditor                              │
│                                                                   │
│  1. User creates/edits flow visually                            │
│  2. Changes synced to backend via API                           │
│  3. Backend validates and stores                                │
│  4. Flow can be exported to Rasa stories                        │
│  5. Stories train dialogue policies                             │
│  6. Bot uses trained model for conversations                    │
└─────────────────────────────────────────────────────────────────┘

      ↓ Creates                ↓ Converts to            ↓ Trains
      
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Flow JSON  │    →    │ Story YAML   │    →    │Trained Model │
│  (Visual)    │         │  (Text)      │         │              │
└──────────────┘         └──────────────┘         └──────────────┘

      ↑ Loads                  ↑ Imports               ↑ Uses
      
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Storage    │    ←    │  Converter   │    ←    │ Rasa Agent   │
│  (Files/DB)  │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
```

## Multi-Bot Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Flow Editor UI                              │
│                                                                   │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│  │   Bot A    │    │   Bot B    │    │   Bot C    │            │
│  │  Workspace │    │  Workspace │    │  Workspace │            │
│  │            │    │            │    │            │            │
│  │ • Flow 1   │    │ • Flow 1   │    │ • Flow 1   │            │
│  │ • Flow 2   │    │ • Flow 2   │    │ • Flow 2   │            │
│  │ • Flow 3   │    │            │    │ • Flow 3   │            │
│  └────────────┘    └────────────┘    └────────────┘            │
└─────────────────────────────────────────────────────────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
│                                                                   │
│  ./flows/                                                        │
│    ├── bot_a/                                                    │
│    │   ├── flow1.json                                           │
│    │   ├── flow2.json                                           │
│    │   └── flow3.json                                           │
│    ├── bot_b/                                                    │
│    │   ├── flow1.json                                           │
│    │   └── flow2.json                                           │
│    └── bot_c/                                                    │
│        ├── flow1.json                                           │
│        ├── flow2.json                                           │
│        └── flow3.json                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack Layers

```
┌────────────────────────────────────────────────────────────────┐
│ Presentation Layer                                              │
│ • React 18 • TypeScript • React Flow • Vite                    │
└────────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────────────────────────────────────────────────┐
│ API Layer                                                       │
│ • Sanic • REST • JSON • CORS • Authentication (future)         │
└────────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────────────────────────────────────────────────┐
│ Business Logic Layer                                            │
│ • Flow Models • Converter • Validator • Graph Algorithms        │
└────────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────────────────────────────────────────────────┐
│ Persistence Layer                                               │
│ • File System (JSON) • Database (future) • Cache (future)      │
└────────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────────────────────────────────────────────────┐
│ Rasa Integration Layer                                          │
│ • Story Graph • Domain • Policies • NLU • Dialogue Tracker     │
└────────────────────────────────────────────────────────────────┘
```

This visual architecture provides a comprehensive overview of how all components interact in the Rasa Flow Editor system.
