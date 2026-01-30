import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const ConditionNode: React.FC<NodeProps> = ({ data, isConnectable }) => {
  return (
    <div
      style={{
        padding: '10px 20px',
        borderRadius: '8px',
        border: '2px solid #f59e0b',
        background: '#fef3c7',
        minWidth: '150px',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div style={{ fontWeight: 'bold', color: '#92400e' }}>
        🔀 Condition
      </div>
      <div style={{ marginTop: '5px', fontSize: '14px' }}>
        {data.label || data.condition || 'New Condition'}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        id="true"
        isConnectable={isConnectable}
        style={{ left: '30%' }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        isConnectable={isConnectable}
        style={{ left: '70%' }}
      />
    </div>
  );
};
