import { useState, useEffect } from 'react';
import { FlowEditor } from './FlowEditor';
import { Node, Edge } from 'reactflow';
import axios from 'axios';

const API_BASE_URL = '/api/flows';

function App() {
  const [flows, setFlows] = useState<any[]>([]);
  const [currentFlowId, setCurrentFlowId] = useState<string | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(false);

  // Load flows list
  useEffect(() => {
    loadFlows();
  }, []);

  const loadFlows = async () => {
    try {
      const response = await axios.get(API_BASE_URL);
      setFlows(response.data.flows || []);
    } catch (error) {
      console.error('Error loading flows:', error);
    }
  };

  const loadFlow = async (flowId: string) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/${flowId}`);
      const flow = response.data.flow;
      setNodes(flow.nodes || []);
      setEdges(flow.edges || []);
      setCurrentFlowId(flowId);
    } catch (error) {
      console.error('Error loading flow:', error);
    } finally {
      setLoading(false);
    }
  };

  const createNewFlow = async () => {
    const name = prompt('Enter flow name:');
    if (!name) return;

    try {
      const response = await axios.post(API_BASE_URL, {
        name,
        description: 'Created from visual editor',
      });
      const flow = response.data.flow;
      setFlows([...flows, { id: flow.id, name: flow.name }]);
      loadFlow(flow.id);
    } catch (error) {
      console.error('Error creating flow:', error);
    }
  };

  const saveFlow = async (updatedNodes: Node[], updatedEdges: Edge[]) => {
    if (!currentFlowId) return;

    try {
      const currentFlow = flows.find((f) => f.id === currentFlowId);
      await axios.put(`${API_BASE_URL}/${currentFlowId}`, {
        id: currentFlowId,
        name: currentFlow?.name || 'Untitled Flow',
        nodes: updatedNodes,
        edges: updatedEdges,
      });
      alert('Flow saved successfully!');
    } catch (error) {
      console.error('Error saving flow:', error);
      alert('Error saving flow');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <div
        style={{
          width: '250px',
          background: '#f3f4f6',
          padding: '20px',
          borderRight: '1px solid #d1d5db',
          overflowY: 'auto',
        }}
      >
        <h2 style={{ marginTop: 0 }}>Rasa Flow Editor</h2>
        <button
          onClick={createNewFlow}
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '20px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
          }}
        >
          + New Flow
        </button>
        <h3>Flows</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {flows.map((flow) => (
            <li
              key={flow.id}
              onClick={() => loadFlow(flow.id)}
              style={{
                padding: '10px',
                marginBottom: '5px',
                background: currentFlowId === flow.id ? '#dbeafe' : 'white',
                borderRadius: '5px',
                cursor: 'pointer',
                border: '1px solid #e5e7eb',
              }}
            >
              {flow.name}
            </li>
          ))}
        </ul>
      </div>

      {/* Main Editor */}
      <div style={{ flex: 1 }}>
        {loading ? (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}
          >
            Loading...
          </div>
        ) : currentFlowId ? (
          <FlowEditor
            flowId={currentFlowId}
            initialNodes={nodes}
            initialEdges={edges}
            onSave={saveFlow}
          />
        ) : (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
              color: '#6b7280',
            }}
          >
            Select a flow or create a new one to get started
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
