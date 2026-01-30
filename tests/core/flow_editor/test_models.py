"""Tests for flow editor models."""
import pytest
from rasa.core.flow_editor.models import FlowNode, FlowEdge, ConversationFlow


def test_flow_node_create():
    """Test creating a flow node."""
    node = FlowNode.create(
        node_type="intent",
        data={"intent": "greet", "label": "Greeting"},
        position={"x": 100, "y": 200},
    )
    
    assert node.id is not None
    assert node.type == "intent"
    assert node.data["intent"] == "greet"
    assert node.position["x"] == 100
    assert node.position["y"] == 200


def test_flow_node_to_dict():
    """Test converting flow node to dictionary."""
    node = FlowNode(
        id="test-id",
        type="action",
        data={"action": "utter_greet"},
        position={"x": 0, "y": 0},
    )
    
    node_dict = node.to_dict()
    
    assert node_dict["id"] == "test-id"
    assert node_dict["type"] == "action"
    assert node_dict["data"]["action"] == "utter_greet"


def test_flow_node_from_dict():
    """Test creating flow node from dictionary."""
    data = {
        "id": "test-id",
        "type": "intent",
        "data": {"intent": "greet"},
        "position": {"x": 50, "y": 100},
    }
    
    node = FlowNode.from_dict(data)
    
    assert node.id == "test-id"
    assert node.type == "intent"
    assert node.data["intent"] == "greet"


def test_flow_edge_create():
    """Test creating a flow edge."""
    edge = FlowEdge.create(
        source="node1",
        target="node2",
        label="connect",
    )
    
    assert edge.id is not None
    assert edge.source == "node1"
    assert edge.target == "node2"
    assert edge.label == "connect"


def test_flow_edge_to_dict():
    """Test converting flow edge to dictionary."""
    edge = FlowEdge(
        id="edge-id",
        source="node1",
        target="node2",
        label="test",
    )
    
    edge_dict = edge.to_dict()
    
    assert edge_dict["id"] == "edge-id"
    assert edge_dict["source"] == "node1"
    assert edge_dict["target"] == "node2"
    assert edge_dict["label"] == "test"


def test_conversation_flow_create():
    """Test creating a conversation flow."""
    flow = ConversationFlow.create(
        name="Test Flow",
        description="A test flow",
    )
    
    assert flow.id is not None
    assert flow.name == "Test Flow"
    assert flow.description == "A test flow"
    assert len(flow.nodes) == 2  # start and end nodes
    assert len(flow.edges) == 0


def test_conversation_flow_add_node():
    """Test adding a node to a flow."""
    flow = ConversationFlow.create(name="Test Flow")
    
    node = FlowNode.create(
        node_type="intent",
        data={"intent": "greet"},
    )
    
    initial_count = len(flow.nodes)
    flow.add_node(node)
    
    assert len(flow.nodes) == initial_count + 1
    assert node in flow.nodes


def test_conversation_flow_add_edge():
    """Test adding an edge to a flow."""
    flow = ConversationFlow.create(name="Test Flow")
    
    node1 = FlowNode.create(node_type="intent", data={"intent": "greet"})
    node2 = FlowNode.create(node_type="action", data={"action": "utter_greet"})
    flow.add_node(node1)
    flow.add_node(node2)
    
    edge = FlowEdge.create(source=node1.id, target=node2.id)
    flow.add_edge(edge)
    
    assert len(flow.edges) == 1
    assert edge in flow.edges


def test_conversation_flow_remove_node():
    """Test removing a node from a flow."""
    flow = ConversationFlow.create(name="Test Flow")
    
    node = FlowNode.create(node_type="intent", data={"intent": "greet"})
    flow.add_node(node)
    
    initial_count = len(flow.nodes)
    flow.remove_node(node.id)
    
    assert len(flow.nodes) == initial_count - 1
    assert node not in flow.nodes


def test_conversation_flow_remove_node_with_edges():
    """Test that removing a node also removes connected edges."""
    flow = ConversationFlow.create(name="Test Flow")
    
    node1 = FlowNode.create(node_type="intent", data={"intent": "greet"})
    node2 = FlowNode.create(node_type="action", data={"action": "utter_greet"})
    flow.add_node(node1)
    flow.add_node(node2)
    
    edge = FlowEdge.create(source=node1.id, target=node2.id)
    flow.add_edge(edge)
    
    flow.remove_node(node1.id)
    
    # Edge should be removed as well
    assert len(flow.edges) == 0


def test_conversation_flow_get_node():
    """Test getting a node by ID."""
    flow = ConversationFlow.create(name="Test Flow")
    
    node = FlowNode.create(node_type="intent", data={"intent": "greet"})
    flow.add_node(node)
    
    retrieved_node = flow.get_node(node.id)
    
    assert retrieved_node is not None
    assert retrieved_node.id == node.id


def test_conversation_flow_to_dict():
    """Test converting flow to dictionary."""
    flow = ConversationFlow.create(name="Test Flow")
    
    flow_dict = flow.to_dict()
    
    assert flow_dict["name"] == "Test Flow"
    assert "nodes" in flow_dict
    assert "edges" in flow_dict
    assert "metadata" in flow_dict


def test_conversation_flow_from_dict():
    """Test creating flow from dictionary."""
    data = {
        "id": "flow-id",
        "name": "Test Flow",
        "description": "Test",
        "nodes": [
            {
                "id": "node1",
                "type": "start",
                "data": {"label": "START"},
                "position": {"x": 0, "y": 0},
            }
        ],
        "edges": [],
        "metadata": {},
    }
    
    flow = ConversationFlow.from_dict(data)
    
    assert flow.id == "flow-id"
    assert flow.name == "Test Flow"
    assert len(flow.nodes) == 1
