"""Converter between React Flow format and Rasa story format."""
from typing import Any, Dict, List, Optional, Text

from rasa.shared.core.training_data.structures import StoryStep, RuleStep
from rasa.shared.core.events import UserUttered, ActionExecuted
from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge


class FlowConverter:
    """Converts between React Flow visual format and Rasa story format."""
    
    @staticmethod
    def flow_to_stories(flow: ConversationFlow) -> List[StoryStep]:
        """Convert a React Flow to Rasa story steps.
        
        This traverses the flow graph and generates story steps representing
        possible conversation paths.
        
        Args:
            flow: The conversation flow to convert
            
        Returns:
            List of story steps representing the flow
        """
        stories = []
        
        # Find start node
        start_nodes = [n for n in flow.nodes if n.type == "start"]
        if not start_nodes:
            return []
        
        start_node = start_nodes[0]
        
        # Traverse the graph from start node
        paths = FlowConverter._traverse_flow(flow, start_node.id)
        
        # Convert each path to a story
        for idx, path in enumerate(paths):
            story_name = f"{flow.name}_path_{idx + 1}"
            events = FlowConverter._path_to_events(flow, path)
            
            if events:
                story = StoryStep(
                    block_name=story_name,
                    events=events,
                )
                stories.append(story)
        
        return stories
    
    @staticmethod
    def _traverse_flow(
        flow: ConversationFlow, 
        current_node_id: Text,
        visited: Optional[set] = None,
        current_path: Optional[List[Text]] = None,
    ) -> List[List[Text]]:
        """Traverse flow graph and return all paths from current node to end nodes.
        
        Args:
            flow: The conversation flow
            current_node_id: Current node being visited
            visited: Set of visited nodes (to detect cycles)
            current_path: Current path being built
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        if visited is None:
            visited = set()
        if current_path is None:
            current_path = []
        
        # Avoid infinite loops
        if current_node_id in visited:
            return []
        
        visited = visited.copy()
        visited.add(current_node_id)
        current_path = current_path + [current_node_id]
        
        current_node = flow.get_node(current_node_id)
        if not current_node:
            return []
        
        # If this is an end node, return the current path
        if current_node.type == "end":
            return [current_path]
        
        # Find all outgoing edges
        outgoing_edges = [e for e in flow.edges if e.source == current_node_id]
        
        if not outgoing_edges:
            # Dead end - return current path
            return [current_path]
        
        # Recursively traverse all branches
        all_paths = []
        for edge in outgoing_edges:
            sub_paths = FlowConverter._traverse_flow(
                flow, edge.target, visited, current_path
            )
            all_paths.extend(sub_paths)
        
        return all_paths
    
    @staticmethod
    def _path_to_events(
        flow: ConversationFlow, 
        path: List[Text],
    ) -> List:
        """Convert a path of node IDs to Rasa events.
        
        Args:
            flow: The conversation flow
            path: List of node IDs representing a path through the flow
            
        Returns:
            List of Rasa events (UserUttered, ActionExecuted)
        """
        events = []
        
        for node_id in path:
            node = flow.get_node(node_id)
            if not node:
                continue
            
            if node.type == "intent":
                # Create UserUttered event
                intent_name = node.data.get("intent", "unknown")
                text = node.data.get("text", f"/{intent_name}")
                
                event = UserUttered(
                    text=text,
                    intent={"name": intent_name, "confidence": 1.0},
                    parse_data={
                        "intent": {"name": intent_name, "confidence": 1.0},
                        "entities": node.data.get("entities", []),
                    },
                )
                events.append(event)
            
            elif node.type == "action":
                # Create ActionExecuted event
                action_name = node.data.get("action", "action_default_fallback")
                event = ActionExecuted(action_name=action_name)
                events.append(event)
        
        return events
    
    @staticmethod
    def stories_to_flow(
        stories: List[StoryStep], 
        flow_name: Text,
    ) -> ConversationFlow:
        """Convert Rasa story steps to a React Flow.
        
        This is the reverse operation - takes existing stories and creates
        a visual flow representation.
        
        Args:
            stories: List of story steps to convert
            flow_name: Name for the generated flow
            
        Returns:
            A conversation flow representing the stories
        """
        flow = ConversationFlow.create(
            name=flow_name,
            description=f"Generated from {len(stories)} stories",
        )
        
        # Track nodes by their content to avoid duplicates
        node_cache: Dict[str, FlowNode] = {}
        
        # Get start node
        start_node = flow.nodes[0]
        
        # Process each story
        y_offset = 100
        for story_idx, story in enumerate(stories):
            x_offset = 100 + (story_idx * 300)
            previous_node = start_node
            
            for event in story.events:
                node = None
                cache_key = None
                
                if isinstance(event, UserUttered):
                    # Create intent node
                    cache_key = f"intent:{event.intent_name}"
                    if cache_key in node_cache:
                        node = node_cache[cache_key]
                    else:
                        node = FlowNode.create(
                            node_type="intent",
                            data={
                                "label": event.intent_name or "unknown",
                                "intent": event.intent_name,
                                "text": event.text,
                            },
                            position={"x": x_offset, "y": y_offset},
                        )
                        flow.add_node(node)
                        node_cache[cache_key] = node
                        y_offset += 100
                
                elif isinstance(event, ActionExecuted):
                    # Create action node
                    cache_key = f"action:{event.action_name}"
                    if cache_key in node_cache:
                        node = node_cache[cache_key]
                    else:
                        node = FlowNode.create(
                            node_type="action",
                            data={
                                "label": event.action_name,
                                "action": event.action_name,
                            },
                            position={"x": x_offset, "y": y_offset},
                        )
                        flow.add_node(node)
                        node_cache[cache_key] = node
                        y_offset += 100
                
                # Create edge from previous node to current node
                if node and previous_node:
                    # Check if edge already exists
                    edge_exists = any(
                        e.source == previous_node.id and e.target == node.id
                        for e in flow.edges
                    )
                    if not edge_exists:
                        edge = FlowEdge.create(
                            source=previous_node.id,
                            target=node.id,
                        )
                        flow.add_edge(edge)
                
                if node:
                    previous_node = node
        
        return flow
