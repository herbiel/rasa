import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const EndNode: React.FC<NodeProps> = ({ isConnectable }) => {
  return (
    <div
      style={{
        padding: '10px 20px',
        borderRadius: '50%',
        border: '3px solid #ef4444',
        background: '#fca5a5',
        minWidth: '80px',
        minHeight: '80px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        color: '#7f1d1d',
      }}
    >
      END
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
    </div>
  );
};
