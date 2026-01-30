import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const ActionNode: React.FC<NodeProps> = ({ data, isConnectable }) => {
  return (
    <div
      style={{
        padding: '10px 20px',
        borderRadius: '8px',
        border: '2px solid #10b981',
        background: '#d1fae5',
        minWidth: '150px',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div style={{ fontWeight: 'bold', color: '#065f46' }}>
        ⚡ Action
      </div>
      <div style={{ marginTop: '5px', fontSize: '14px' }}>
        {data.label || data.action || 'New Action'}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </div>
  );
};
