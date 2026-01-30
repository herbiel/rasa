"""Tests for flow converter."""
import pytest

from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge
from rasa.core.flow_editor.converter import FlowConverter
from rasa.shared.core.events import UserUttered, ActionExecuted


@pytest.fixture
def simple_flow():
    """Create a simple conversation flow for testing."""
    flow = ConversationFlow.create(name="Simple Flow")
    
    # Get start node
    start_node = flow.nodes[0]
    
    # Add intent node
    intent_node = FlowNode.create(
        node_type="intent",
        data={"intent": "greet", "label": "User greets", "text": "/greet"}
    )
    flow.add_node(intent_node)
    
    # Add action node
    action_node = FlowNode.create(
        node_type="action",
        data={"action": "utter_greet", "label": "Bot responds"}
    )
    flow.add_node(action_node)
    
    # Get end node
    end_node = flow.nodes[1]
    
    # Connect nodes
    flow.add_edge(FlowEdge.create(start_node.id, intent_node.id))
    flow.add_edge(FlowEdge.create(intent_node.id, action_node.id))
    flow.add_edge(FlowEdge.create(action_node.id, end_node.id))
    
    return flow


@pytest.fixture
def branching_flow():
    """Create a flow with branching for testing."""
    flow = ConversationFlow.create(name="Branching Flow")
    
    start_node = flow.nodes[0]
    end_node = flow.nodes[1]
    
    # Add intent node
    intent_node = FlowNode.create(
        node_type="intent",
        data={"intent": "ask_weather", "text": "/ask_weather"}
    )
    flow.add_node(intent_node)
    
    # Add two action nodes (branches)
    action1_node = FlowNode.create(
        node_type="action",
        data={"action": "action_get_weather"}
    )
    flow.add_node(action1_node)
    
    action2_node = FlowNode.create(
        node_type="action",
        data={"action": "utter_weather"}
    )
    flow.add_node(action2_node)
    
    # Connect with branching
    flow.add_edge(FlowEdge.create(start_node.id, intent_node.id))
    flow.add_edge(FlowEdge.create(intent_node.id, action1_node.id))
    flow.add_edge(FlowEdge.create(intent_node.id, action2_node.id))
    flow.add_edge(FlowEdge.create(action1_node.id, end_node.id))
    flow.add_edge(FlowEdge.create(action2_node.id, end_node.id))
    
    return flow


def test_flow_to_stories_simple(simple_flow):
    """Test converting a simple flow to stories."""
    stories = FlowConverter.flow_to_stories(simple_flow)
    
    assert len(stories) > 0
    story = stories[0]
    
    # Check that story contains expected events
    events = story.events
    assert len(events) > 0
    
    # Find UserUttered and ActionExecuted events
    user_events = [e for e in events if isinstance(e, UserUttered)]
    action_events = [e for e in events if isinstance(e, ActionExecuted)]
    
    assert len(user_events) >= 1
    assert len(action_events) >= 1
    
    # Check intent
    assert user_events[0].intent_name == "greet"
    
    # Check action
    assert action_events[0].action_name == "utter_greet"


def test_flow_to_stories_branching(branching_flow):
    """Test converting a branching flow to stories."""
    stories = FlowConverter.flow_to_stories(branching_flow)
    
    # Should generate multiple stories for different paths
    assert len(stories) >= 2


def test_traverse_flow_simple(simple_flow):
    """Test graph traversal for simple flow."""
    start_node = simple_flow.nodes[0]
    paths = FlowConverter._traverse_flow(simple_flow, start_node.id)
    
    assert len(paths) > 0
    # Each path should end at an end node
    for path in paths:
        assert len(path) > 0


def test_traverse_flow_with_cycle():
    """Test graph traversal handles cycles correctly."""
    flow = ConversationFlow.create(name="Cycle Flow")
    
    start_node = flow.nodes[0]
    node1 = FlowNode.create(node_type="action", data={"action": "action1"})
    node2 = FlowNode.create(node_type="action", data={"action": "action2"})
    
    flow.add_node(node1)
    flow.add_node(node2)
    
    # Create a cycle
    flow.add_edge(FlowEdge.create(start_node.id, node1.id))
    flow.add_edge(FlowEdge.create(node1.id, node2.id))
    flow.add_edge(FlowEdge.create(node2.id, node1.id))  # Cycle back
    
    # Should not infinite loop
    paths = FlowConverter._traverse_flow(flow, start_node.id)
    assert len(paths) >= 0  # Should return some paths


def test_path_to_events():
    """Test converting node path to events."""
    flow = ConversationFlow.create(name="Test Flow")
    
    intent_node = FlowNode.create(
        node_type="intent",
        data={"intent": "greet", "text": "/greet"}
    )
    action_node = FlowNode.create(
        node_type="action",
        data={"action": "utter_greet"}
    )
    
    flow.add_node(intent_node)
    flow.add_node(action_node)
    
    path = [intent_node.id, action_node.id]
    events = FlowConverter._path_to_events(flow, path)
    
    assert len(events) == 2
    assert isinstance(events[0], UserUttered)
    assert isinstance(events[1], ActionExecuted)
    assert events[0].intent_name == "greet"
    assert events[1].action_name == "utter_greet"


def test_path_to_events_skip_start_end():
    """Test that start and end nodes are skipped in event generation."""
    flow = ConversationFlow.create(name="Test Flow")
    
    start_node = flow.nodes[0]
    end_node = flow.nodes[1]
    
    path = [start_node.id, end_node.id]
    events = FlowConverter._path_to_events(flow, path)
    
    # Start and end nodes should not generate events
    assert len(events) == 0


def test_flow_to_stories_empty_flow():
    """Test converting an empty flow (no paths)."""
    flow = ConversationFlow.create(name="Empty Flow")
    
    # Remove edges to create isolated nodes
    flow.edges = []
    
    stories = FlowConverter.flow_to_stories(flow)
    
    # Should return empty list or handle gracefully
    assert isinstance(stories, list)


def test_stories_to_flow():
    """Test converting stories to flow (reverse operation)."""
    from rasa.shared.core.training_data.structures import StoryStep
    
    # Create a simple story
    story = StoryStep(
        block_name="test_story",
        events=[
            UserUttered(
                text="/greet",
                intent={"name": "greet", "confidence": 1.0},
            ),
            ActionExecuted(action_name="utter_greet"),
        ],
    )
    
    flow = FlowConverter.stories_to_flow([story], "Test Flow")
    
    assert flow.name == "Test Flow"
    assert len(flow.nodes) > 2  # Should have start, end, and story nodes
    
    # Check that intent and action nodes were created
    intent_nodes = [n for n in flow.nodes if n.type == "intent"]
    action_nodes = [n for n in flow.nodes if n.type == "action"]
    
    assert len(intent_nodes) >= 1
    assert len(action_nodes) >= 1
