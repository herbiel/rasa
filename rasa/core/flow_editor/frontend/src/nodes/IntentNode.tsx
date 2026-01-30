import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const IntentNode: React.FC<NodeProps> = ({ data, isConnectable }) => {
  return (
    <div
      style={{
        padding: '10px 20px',
        borderRadius: '8px',
        border: '2px solid #3b82f6',
        background: '#eff6ff',
        minWidth: '150px',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div style={{ fontWeight: 'bold', color: '#1e40af' }}>
        💬 Intent
      </div>
      <div style={{ marginTop: '5px', fontSize: '14px' }}>
        {data.label || data.intent || 'New Intent'}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </div>
  );
};
