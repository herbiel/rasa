"""Data models for React Flow visual editor."""
from typing import Any, Dict, List, Optional, Text
from dataclasses import dataclass, field
import uuid


@dataclass
class FlowNode:
    """Represents a node in the visual flow editor.
    
    Node types:
    - intent: User intent node (entry point)
    - action: Bot action node
    - condition: Conditional branching node
    - start: Flow start node
    - end: Flow end node
    """
    
    id: Text
    type: Text  # intent, action, condition, start, end
    data: Dict[Text, Any] = field(default_factory=dict)
    position: Dict[Text, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    
    @classmethod
    def create(
        cls,
        node_type: Text,
        data: Optional[Dict[Text, Any]] = None,
        position: Optional[Dict[Text, float]] = None,
    ) -> "FlowNode":
        """Create a new flow node with auto-generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            type=node_type,
            data=data or {},
            position=position or {"x": 0, "y": 0},
        )
    
    def to_dict(self) -> Dict[Text, Any]:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "position": self.position,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> "FlowNode":
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            type=data["type"],
            data=data.get("data", {}),
            position=data.get("position", {"x": 0, "y": 0}),
        )


@dataclass
class FlowEdge:
    """Represents an edge (connection) between nodes in the visual flow editor."""
    
    id: Text
    source: Text  # Source node ID
    target: Text  # Target node ID
    label: Optional[Text] = None
    data: Dict[Text, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        source: Text,
        target: Text,
        label: Optional[Text] = None,
        data: Optional[Dict[Text, Any]] = None,
    ) -> "FlowEdge":
        """Create a new flow edge with auto-generated ID."""
        return cls(
            id=f"{source}-{target}-{uuid.uuid4()}",
            source=source,
            target=target,
            label=label,
            data=data or {},
        )
    
    def to_dict(self) -> Dict[Text, Any]:
        """Convert edge to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "data": self.data,
        }
        if self.label:
            result["label"] = self.label
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> "FlowEdge":
        """Create edge from dictionary."""
        return cls(
            id=data["id"],
            source=data["source"],
            target=data["target"],
            label=data.get("label"),
            data=data.get("data", {}),
        )


@dataclass
class ConversationFlow:
    """Represents a complete conversation flow for visual editing."""
    
    id: Text
    name: Text
    description: Optional[Text] = None
    nodes: List[FlowNode] = field(default_factory=list)
    edges: List[FlowEdge] = field(default_factory=list)
    metadata: Dict[Text, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        name: Text,
        description: Optional[Text] = None,
    ) -> "ConversationFlow":
        """Create a new conversation flow with auto-generated ID."""
        flow_id = str(uuid.uuid4())
        
        # Create default start and end nodes
        start_node = FlowNode.create(
            node_type="start",
            data={"label": "START"},
            position={"x": 250, "y": 0},
        )
        end_node = FlowNode.create(
            node_type="end",
            data={"label": "END"},
            position={"x": 250, "y": 500},
        )
        
        return cls(
            id=flow_id,
            name=name,
            description=description,
            nodes=[start_node, end_node],
            edges=[],
            metadata={
                "created_at": None,
                "updated_at": None,
                "version": "1.0",
            },
        )
    
    def add_node(self, node: FlowNode) -> None:
        """Add a node to the flow."""
        self.nodes.append(node)
    
    def add_edge(self, edge: FlowEdge) -> None:
        """Add an edge to the flow."""
        self.edges.append(edge)
    
    def remove_node(self, node_id: Text) -> None:
        """Remove a node and all connected edges."""
        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.edges = [
            e for e in self.edges if e.source != node_id and e.target != node_id
        ]
    
    def remove_edge(self, edge_id: Text) -> None:
        """Remove an edge from the flow."""
        self.edges = [e for e in self.edges if e.id != edge_id]
    
    def get_node(self, node_id: Text) -> Optional[FlowNode]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def to_dict(self) -> Dict[Text, Any]:
        """Convert flow to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> "ConversationFlow":
        """Create flow from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            nodes=[FlowNode.from_dict(n) for n in data.get("nodes", [])],
            edges=[FlowEdge.from_dict(e) for e in data.get("edges", [])],
            metadata=data.get("metadata", {}),
        )
