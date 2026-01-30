import React, { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MiniMap,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { IntentNode } from './nodes/IntentNode';
import { ActionNode } from './nodes/ActionNode';
import { ConditionNode } from './nodes/ConditionNode';
import { StartNode } from './nodes/StartNode';
import { EndNode } from './nodes/EndNode';

const nodeTypes = {
  intent: IntentNode,
  action: ActionNode,
  condition: ConditionNode,
  start: StartNode,
  end: EndNode,
};

interface FlowEditorProps {
  flowId?: string;
  initialNodes?: Node[];
  initialEdges?: Edge[];
  onSave?: (nodes: Node[], edges: Edge[]) => void;
}

export const FlowEditor: React.FC<FlowEditorProps> = ({
  initialNodes = [],
  initialEdges = [],
  onSave,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleSave = useCallback(() => {
    if (onSave) {
      onSave(nodes, edges);
    }
  }, [nodes, edges, onSave]);

  const addNode = useCallback(
    (type: string) => {
      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position: { x: 250, y: 250 },
        data: { label: `New ${type}` },
      };
      setNodes((nds) => [...nds, newNode]);
    },
    [setNodes]
  );

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Panel position="top-left">
          <div style={{ 
            background: 'white', 
            padding: '10px', 
            borderRadius: '5px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ margin: '0 0 10px 0' }}>Add Nodes</h3>
            <button onClick={() => addNode('intent')} style={{ margin: '5px' }}>
              + Intent
            </button>
            <button onClick={() => addNode('action')} style={{ margin: '5px' }}>
              + Action
            </button>
            <button onClick={() => addNode('condition')} style={{ margin: '5px' }}>
              + Condition
            </button>
            <button onClick={handleSave} style={{ margin: '5px', marginLeft: '20px' }}>
              💾 Save Flow
            </button>
          </div>
        </Panel>
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    </div>
  );
};
