import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const StartNode: React.FC<NodeProps> = ({ data, isConnectable }) => {
  return (
    <div
      style={{
        padding: '10px 20px',
        borderRadius: '50%',
        border: '3px solid #22c55e',
        background: '#86efac',
        minWidth: '80px',
        minHeight: '80px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        color: '#14532d',
      }}
    >
      START
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </div>
  );
};
