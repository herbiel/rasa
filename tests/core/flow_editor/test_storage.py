"""Tests for flow storage."""
import pytest
import tempfile
import json
from pathlib import Path

from rasa.core.flow_editor.models import ConversationFlow, FlowNode
from rasa.core.flow_editor.storage import FlowStorage


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for flow storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def storage(temp_storage_dir):
    """Create a flow storage instance."""
    return FlowStorage(temp_storage_dir)


@pytest.fixture
def sample_flow():
    """Create a sample conversation flow."""
    flow = ConversationFlow.create(
        name="Test Flow",
        description="A test flow"
    )
    node = FlowNode.create(
        node_type="intent",
        data={"intent": "greet"}
    )
    flow.add_node(node)
    return flow


def test_storage_initialization(temp_storage_dir):
    """Test storage initialization creates directory."""
    storage_path = Path(temp_storage_dir) / "flows"
    storage = FlowStorage(str(storage_path))
    
    assert storage.storage_path.exists()
    assert storage.storage_path.is_dir()


def test_save_flow(storage, sample_flow):
    """Test saving a flow to storage."""
    storage.save_flow(sample_flow)
    
    file_path = storage._get_flow_file_path(sample_flow.id)
    assert file_path.exists()
    
    # Verify content
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data["id"] == sample_flow.id
    assert data["name"] == sample_flow.name


def test_load_flow(storage, sample_flow):
    """Test loading a flow from storage."""
    storage.save_flow(sample_flow)
    
    loaded_flow = storage.load_flow(sample_flow.id)
    
    assert loaded_flow is not None
    assert loaded_flow.id == sample_flow.id
    assert loaded_flow.name == sample_flow.name
    assert len(loaded_flow.nodes) == len(sample_flow.nodes)


def test_load_nonexistent_flow(storage):
    """Test loading a non-existent flow returns None."""
    loaded_flow = storage.load_flow("nonexistent-id")
    assert loaded_flow is None


def test_delete_flow(storage, sample_flow):
    """Test deleting a flow from storage."""
    storage.save_flow(sample_flow)
    
    result = storage.delete_flow(sample_flow.id)
    assert result is True
    
    # Verify file is deleted
    file_path = storage._get_flow_file_path(sample_flow.id)
    assert not file_path.exists()


def test_delete_nonexistent_flow(storage):
    """Test deleting a non-existent flow returns False."""
    result = storage.delete_flow("nonexistent-id")
    assert result is False


def test_list_flows_empty(storage):
    """Test listing flows when storage is empty."""
    flows = storage.list_flows()
    assert flows == []


def test_list_flows(storage, sample_flow):
    """Test listing flows."""
    # Create multiple flows
    flow1 = sample_flow
    flow2 = ConversationFlow.create(name="Flow 2")
    
    storage.save_flow(flow1)
    storage.save_flow(flow2)
    
    flows = storage.list_flows()
    
    assert len(flows) == 2
    flow_ids = [f["id"] for f in flows]
    assert flow1.id in flow_ids
    assert flow2.id in flow_ids


def test_flow_exists(storage, sample_flow):
    """Test checking if a flow exists."""
    assert not storage.flow_exists(sample_flow.id)
    
    storage.save_flow(sample_flow)
    assert storage.flow_exists(sample_flow.id)
    
    storage.delete_flow(sample_flow.id)
    assert not storage.flow_exists(sample_flow.id)
