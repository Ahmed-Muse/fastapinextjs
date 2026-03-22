// components/Button.tsx
import React from 'react';

export default function Button({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button 
      style={{ padding: '10px 20px', borderRadius: '5px', cursor: 'pointer' }} 
      {...props}
    >
      {/* Whatever is passed inside the <Button> tags gets injected here */}
      {children}
    </button>
  );
}