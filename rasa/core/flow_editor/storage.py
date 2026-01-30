"""Storage layer for conversation flows."""
from typing import Any, Dict, List, Optional, Text
import json
import logging
from pathlib import Path
import os

from rasa.core.flow_editor.models import ConversationFlow

logger = logging.getLogger(__name__)


class FlowStorage:
    """Handles persistence of conversation flows to disk."""
    
    def __init__(self, storage_path: Optional[Text] = None) -> None:
        """Initialize flow storage.
        
        Args:
            storage_path: Directory to store flow files. 
                         Defaults to ./flows in current directory.
        """
        if storage_path is None:
            storage_path = os.path.join(os.getcwd(), "flows")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Flow storage initialized at: {self.storage_path}")
    
    def _get_flow_file_path(self, flow_id: Text) -> Path:
        """Get file path for a flow.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            Path to flow file
        """
        return self.storage_path / f"{flow_id}.json"
    
    def save_flow(self, flow: ConversationFlow) -> None:
        """Save a conversation flow to disk.
        
        Args:
            flow: Flow to save
        """
        file_path = self._get_flow_file_path(flow.id)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(flow.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved flow {flow.id} to {file_path}")
        except Exception as e:
            logger.error(f"Error saving flow {flow.id}: {e}")
            raise
    
    def load_flow(self, flow_id: Text) -> Optional[ConversationFlow]:
        """Load a conversation flow from disk.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            Loaded flow or None if not found
        """
        file_path = self._get_flow_file_path(flow_id)
        
        if not file_path.exists():
            logger.warning(f"Flow {flow_id} not found at {file_path}")
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            flow = ConversationFlow.from_dict(data)
            logger.debug(f"Loaded flow {flow_id} from {file_path}")
            return flow
        except Exception as e:
            logger.error(f"Error loading flow {flow_id}: {e}")
            raise
    
    def delete_flow(self, flow_id: Text) -> bool:
        """Delete a conversation flow from disk.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_flow_file_path(flow_id)
        
        if not file_path.exists():
            logger.warning(f"Flow {flow_id} not found for deletion")
            return False
        
        try:
            file_path.unlink()
            logger.info(f"Deleted flow {flow_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting flow {flow_id}: {e}")
            raise
    
    def list_flows(self) -> List[Dict[Text, Any]]:
        """List all conversation flows.
        
        Returns:
            List of flow metadata (id, name, description)
        """
        flows = []
        
        try:
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    flows.append({
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "metadata": data.get("metadata", {}),
                    })
                except Exception as e:
                    logger.error(f"Error reading flow file {file_path}: {e}")
                    continue
            
            logger.debug(f"Listed {len(flows)} flows")
            return flows
        except Exception as e:
            logger.error(f"Error listing flows: {e}")
            raise
    
    def flow_exists(self, flow_id: Text) -> bool:
        """Check if a flow exists.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            True if flow exists, False otherwise
        """
        return self._get_flow_file_path(flow_id).exists()
