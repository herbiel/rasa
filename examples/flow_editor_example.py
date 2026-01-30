#!/usr/bin/env python3
"""
Example script demonstrating the Rasa Flow Editor functionality.

This script shows how to:
1. Create a conversation flow programmatically
2. Add nodes and edges
3. Save the flow
4. Convert flow to stories
5. Load and display flows
"""

from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge
from rasa.core.flow_editor.storage import FlowStorage
from rasa.core.flow_editor.converter import FlowConverter


def create_greeting_flow():
    """Create a simple greeting conversation flow."""
    print("\n=== Creating Greeting Flow ===")
    
    # Create a new flow
    flow = ConversationFlow.create(
        name="Greeting Flow",
        description="A simple greeting conversation flow"
    )
    print(f"Created flow: {flow.name} (ID: {flow.id})")
    
    # Get the default start and end nodes
    start_node = flow.nodes[0]
    end_node = flow.nodes[1]
    print(f"Default nodes: Start ({start_node.id}), End ({end_node.id})")
    
    # Add an intent node
    intent_node = FlowNode.create(
        node_type="intent",
        data={
            "intent": "greet",
            "label": "User says hello",
            "text": "/greet"
        },
        position={"x": 250, "y": 100}
    )
    flow.add_node(intent_node)
    print(f"Added intent node: greet ({intent_node.id})")
    
    # Add an action node
    action_node = FlowNode.create(
        node_type="action",
        data={
            "action": "utter_greet",
            "label": "Bot responds with greeting"
        },
        position={"x": 250, "y": 200}
    )
    flow.add_node(action_node)
    print(f"Added action node: utter_greet ({action_node.id})")
    
    # Connect the nodes
    edge1 = FlowEdge.create(
        source=start_node.id,
        target=intent_node.id,
        label="start"
    )
    flow.add_edge(edge1)
    
    edge2 = FlowEdge.create(
        source=intent_node.id,
        target=action_node.id
    )
    flow.add_edge(edge2)
    
    edge3 = FlowEdge.create(
        source=action_node.id,
        target=end_node.id
    )
    flow.add_edge(edge3)
    
    print(f"Connected nodes with {len(flow.edges)} edges")
    
    return flow


def create_weather_flow():
    """Create a more complex weather inquiry flow."""
    print("\n=== Creating Weather Flow ===")
    
    flow = ConversationFlow.create(
        name="Weather Inquiry Flow",
        description="Handle weather-related questions"
    )
    print(f"Created flow: {flow.name} (ID: {flow.id})")
    
    start_node = flow.nodes[0]
    end_node = flow.nodes[1]
    
    # Intent: ask_weather
    intent_node = FlowNode.create(
        node_type="intent",
        data={
            "intent": "ask_weather",
            "label": "User asks about weather",
            "text": "/ask_weather"
        },
        position={"x": 250, "y": 100}
    )
    flow.add_node(intent_node)
    
    # Action: get_weather
    get_weather_node = FlowNode.create(
        node_type="action",
        data={
            "action": "action_get_weather",
            "label": "Fetch weather data"
        },
        position={"x": 250, "y": 200}
    )
    flow.add_node(get_weather_node)
    
    # Condition: check if location available
    condition_node = FlowNode.create(
        node_type="condition",
        data={
            "condition": "slot_location_filled",
            "label": "Location available?"
        },
        position={"x": 250, "y": 300}
    )
    flow.add_node(condition_node)
    
    # Action: ask_location
    ask_location_node = FlowNode.create(
        node_type="action",
        data={
            "action": "utter_ask_location",
            "label": "Ask for location"
        },
        position={"x": 100, "y": 400}
    )
    flow.add_node(ask_location_node)
    
    # Action: provide_weather
    provide_weather_node = FlowNode.create(
        node_type="action",
        data={
            "action": "utter_weather",
            "label": "Provide weather info"
        },
        position={"x": 400, "y": 400}
    )
    flow.add_node(provide_weather_node)
    
    # Connect nodes
    flow.add_edge(FlowEdge.create(start_node.id, intent_node.id))
    flow.add_edge(FlowEdge.create(intent_node.id, get_weather_node.id))
    flow.add_edge(FlowEdge.create(get_weather_node.id, condition_node.id))
    flow.add_edge(FlowEdge.create(condition_node.id, ask_location_node.id, label="False"))
    flow.add_edge(FlowEdge.create(condition_node.id, provide_weather_node.id, label="True"))
    flow.add_edge(FlowEdge.create(ask_location_node.id, end_node.id))
    flow.add_edge(FlowEdge.create(provide_weather_node.id, end_node.id))
    
    print(f"Created complex flow with {len(flow.nodes)} nodes and {len(flow.edges)} edges")
    
    return flow


def save_and_load_flow(flow):
    """Save a flow and load it back."""
    print(f"\n=== Saving and Loading Flow: {flow.name} ===")
    
    # Create storage
    storage = FlowStorage("./example_flows")
    
    # Save flow
    storage.save_flow(flow)
    print(f"Saved flow to: ./example_flows/{flow.id}.json")
    
    # Load flow
    loaded_flow = storage.load_flow(flow.id)
    print(f"Loaded flow: {loaded_flow.name}")
    print(f"  - Nodes: {len(loaded_flow.nodes)}")
    print(f"  - Edges: {len(loaded_flow.edges)}")
    
    return loaded_flow


def convert_to_stories(flow):
    """Convert a flow to Rasa stories."""
    print(f"\n=== Converting Flow to Stories: {flow.name} ===")
    
    stories = FlowConverter.flow_to_stories(flow)
    print(f"Generated {len(stories)} story path(s)")
    
    for idx, story in enumerate(stories):
        print(f"\nStory {idx + 1}: {story.block_name}")
        for event in story.events:
            if hasattr(event, 'intent_name'):
                print(f"  - intent: {event.intent_name}")
            elif hasattr(event, 'action_name'):
                print(f"  - action: {event.action_name}")
    
    return stories


def list_all_flows():
    """List all saved flows."""
    print("\n=== Listing All Flows ===")
    
    storage = FlowStorage("./example_flows")
    flows = storage.list_flows()
    
    print(f"Found {len(flows)} flow(s):")
    for flow_meta in flows:
        print(f"  - {flow_meta['name']} (ID: {flow_meta['id']})")
        if flow_meta.get('description'):
            print(f"    Description: {flow_meta['description']}")


def display_flow_structure(flow):
    """Display the structure of a flow."""
    print(f"\n=== Flow Structure: {flow.name} ===")
    print(f"Description: {flow.description}")
    print(f"\nNodes ({len(flow.nodes)}):")
    for node in flow.nodes:
        node_label = node.data.get('label', node.data.get('intent', node.data.get('action', 'Unknown')))
        print(f"  - [{node.type}] {node_label} (ID: {node.id[:8]}...)")
    
    print(f"\nEdges ({len(flow.edges)}):")
    for edge in flow.edges:
        source = flow.get_node(edge.source)
        target = flow.get_node(edge.target)
        source_label = source.data.get('label', source.type) if source else "Unknown"
        target_label = target.data.get('label', target.type) if target else "Unknown"
        edge_label = f" [{edge.label}]" if edge.label else ""
        print(f"  - {source_label} -> {target_label}{edge_label}")


def main():
    """Main example function."""
    print("=" * 60)
    print("Rasa Flow Editor - Example Usage")
    print("=" * 60)
    
    # Create flows
    greeting_flow = create_greeting_flow()
    weather_flow = create_weather_flow()
    
    # Display flow structures
    display_flow_structure(greeting_flow)
    display_flow_structure(weather_flow)
    
    # Save and load
    greeting_flow = save_and_load_flow(greeting_flow)
    weather_flow = save_and_load_flow(weather_flow)
    
    # Convert to stories
    convert_to_stories(greeting_flow)
    convert_to_stories(weather_flow)
    
    # List all flows
    list_all_flows()
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Check the './example_flows' directory for saved flows")
    print("2. Start the Rasa server and access the Flow Editor UI")
    print("3. Use the REST API at /api/flows to manage flows")
    print("=" * 60)


if __name__ == "__main__":
    main()
