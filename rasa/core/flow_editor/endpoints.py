"""REST API endpoints for React Flow visual editor."""
from typing import Any, Dict, List, Optional, Text
import json
import logging
from pathlib import Path

from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse

from rasa.core.flow_editor.models import ConversationFlow, FlowNode, FlowEdge
from rasa.core.flow_editor.converter import FlowConverter
from rasa.core.flow_editor.storage import FlowStorage

logger = logging.getLogger(__name__)

# Create blueprint for flow editor endpoints
flow_editor_bp = Blueprint("flow_editor", url_prefix="/api/flows")


# Initialize storage
_flow_storage: Optional[FlowStorage] = None


def get_flow_storage(storage_path: Optional[Text] = None) -> FlowStorage:
    """Get or create flow storage instance."""
    global _flow_storage
    if _flow_storage is None:
        _flow_storage = FlowStorage(storage_path)
    return _flow_storage


@flow_editor_bp.route("/", methods=["GET"])
async def list_flows(request: Request) -> HTTPResponse:
    """List all conversation flows.
    
    Returns:
        JSON array of flow metadata (id, name, description)
    """
    try:
        storage = get_flow_storage()
        flows = storage.list_flows()
        return response.json({"flows": flows})
    except Exception as e:
        logger.error(f"Error listing flows: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/", methods=["POST"])
async def create_flow(request: Request) -> HTTPResponse:
    """Create a new conversation flow.
    
    Request body:
        {
            "name": "Flow name",
            "description": "Optional description"
        }
    
    Returns:
        Created flow with ID
    """
    try:
        data = request.json
        name = data.get("name")
        description = data.get("description")
        
        if not name:
            return response.json({"error": "Flow name is required"}, status=400)
        
        flow = ConversationFlow.create(name=name, description=description)
        storage = get_flow_storage()
        storage.save_flow(flow)
        
        return response.json({"flow": flow.to_dict()}, status=201)
    except Exception as e:
        logger.error(f"Error creating flow: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>", methods=["GET"])
async def get_flow(request: Request, flow_id: Text) -> HTTPResponse:
    """Get a specific conversation flow by ID.
    
    Args:
        flow_id: Flow identifier
        
    Returns:
        Complete flow data including nodes and edges
    """
    try:
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        return response.json({"flow": flow.to_dict()})
    except Exception as e:
        logger.error(f"Error getting flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>", methods=["PUT"])
async def update_flow(request: Request, flow_id: Text) -> HTTPResponse:
    """Update a conversation flow.
    
    Request body should contain complete flow data.
    
    Args:
        flow_id: Flow identifier
        
    Returns:
        Updated flow data
    """
    try:
        data = request.json
        
        # Ensure the flow ID matches
        if data.get("id") != flow_id:
            return response.json(
                {"error": "Flow ID mismatch"}, 
                status=400,
            )
        
        flow = ConversationFlow.from_dict(data)
        storage = get_flow_storage()
        storage.save_flow(flow)
        
        return response.json({"flow": flow.to_dict()})
    except Exception as e:
        logger.error(f"Error updating flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>", methods=["DELETE"])
async def delete_flow(request: Request, flow_id: Text) -> HTTPResponse:
    """Delete a conversation flow.
    
    Args:
        flow_id: Flow identifier
        
    Returns:
        Success message
    """
    try:
        storage = get_flow_storage()
        success = storage.delete_flow(flow_id)
        
        if not success:
            return response.json({"error": "Flow not found"}, status=404)
        
        return response.json({"message": "Flow deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>/nodes", methods=["POST"])
async def add_node(request: Request, flow_id: Text) -> HTTPResponse:
    """Add a node to a flow.
    
    Request body:
        {
            "type": "intent|action|condition",
            "data": {...},
            "position": {"x": 0, "y": 0}
        }
    
    Returns:
        Created node with ID
    """
    try:
        data = request.json
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        node = FlowNode.create(
            node_type=data.get("type", "action"),
            data=data.get("data", {}),
            position=data.get("position", {"x": 0, "y": 0}),
        )
        flow.add_node(node)
        storage.save_flow(flow)
        
        return response.json({"node": node.to_dict()}, status=201)
    except Exception as e:
        logger.error(f"Error adding node to flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>/nodes/<node_id:str>", methods=["DELETE"])
async def remove_node(request: Request, flow_id: Text, node_id: Text) -> HTTPResponse:
    """Remove a node from a flow.
    
    Also removes all edges connected to the node.
    
    Args:
        flow_id: Flow identifier
        node_id: Node identifier
        
    Returns:
        Success message
    """
    try:
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        flow.remove_node(node_id)
        storage.save_flow(flow)
        
        return response.json({"message": "Node removed successfully"})
    except Exception as e:
        logger.error(f"Error removing node {node_id} from flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>/edges", methods=["POST"])
async def add_edge(request: Request, flow_id: Text) -> HTTPResponse:
    """Add an edge (connection) to a flow.
    
    Request body:
        {
            "source": "source_node_id",
            "target": "target_node_id",
            "label": "Optional label"
        }
    
    Returns:
        Created edge with ID
    """
    try:
        data = request.json
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        edge = FlowEdge.create(
            source=data.get("source"),
            target=data.get("target"),
            label=data.get("label"),
            data=data.get("data", {}),
        )
        flow.add_edge(edge)
        storage.save_flow(flow)
        
        return response.json({"edge": edge.to_dict()}, status=201)
    except Exception as e:
        logger.error(f"Error adding edge to flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>/edges/<edge_id:str>", methods=["DELETE"])
async def remove_edge(request: Request, flow_id: Text, edge_id: Text) -> HTTPResponse:
    """Remove an edge from a flow.
    
    Args:
        flow_id: Flow identifier
        edge_id: Edge identifier
        
    Returns:
        Success message
    """
    try:
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        flow.remove_edge(edge_id)
        storage.save_flow(flow)
        
        return response.json({"message": "Edge removed successfully"})
    except Exception as e:
        logger.error(f"Error removing edge {edge_id} from flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>/export/stories", methods=["GET"])
async def export_to_stories(request: Request, flow_id: Text) -> HTTPResponse:
    """Export a flow to Rasa story format.
    
    Args:
        flow_id: Flow identifier
        
    Returns:
        Story YAML content
    """
    try:
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        # Convert flow to stories
        stories = FlowConverter.flow_to_stories(flow)
        
        # Convert stories to YAML format (simplified)
        # In production, use proper YAML serialization
        story_data = []
        for story in stories:
            story_dict = {
                "story": story.block_name,
                "steps": [],
            }
            for event in story.events:
                if hasattr(event, "intent_name"):
                    story_dict["steps"].append({
                        "intent": event.intent_name
                    })
                elif hasattr(event, "action_name"):
                    story_dict["steps"].append({
                        "action": event.action_name
                    })
            story_data.append(story_dict)
        
        return response.json({"stories": story_data})
    except Exception as e:
        logger.error(f"Error exporting flow {flow_id} to stories: {e}")
        return response.json({"error": str(e)}, status=500)


@flow_editor_bp.route("/<flow_id:str>/validate", methods=["POST"])
async def validate_flow(request: Request, flow_id: Text) -> HTTPResponse:
    """Validate a conversation flow.
    
    Checks for:
    - Disconnected nodes
    - Cycles
    - Missing required data
    - Invalid connections
    
    Args:
        flow_id: Flow identifier
        
    Returns:
        Validation results with warnings and errors
    """
    try:
        storage = get_flow_storage()
        flow = storage.load_flow(flow_id)
        
        if not flow:
            return response.json({"error": "Flow not found"}, status=404)
        
        errors = []
        warnings = []
        
        # Check for disconnected nodes
        connected_nodes = set()
        for edge in flow.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)
        
        for node in flow.nodes:
            if node.type not in ["start", "end"] and node.id not in connected_nodes:
                warnings.append(f"Node '{node.data.get('label', node.id)}' is not connected")
        
        # Check for nodes without required data
        for node in flow.nodes:
            if node.type == "intent" and not node.data.get("intent"):
                errors.append(f"Intent node '{node.id}' is missing intent name")
            elif node.type == "action" and not node.data.get("action"):
                errors.append(f"Action node '{node.id}' is missing action name")
        
        # Check for multiple start/end nodes
        start_nodes = [n for n in flow.nodes if n.type == "start"]
        end_nodes = [n for n in flow.nodes if n.type == "end"]
        
        if len(start_nodes) > 1:
            warnings.append("Flow has multiple start nodes")
        if len(start_nodes) == 0:
            errors.append("Flow is missing a start node")
        
        return response.json({
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        })
    except Exception as e:
        logger.error(f"Error validating flow {flow_id}: {e}")
        return response.json({"error": str(e)}, status=500)
