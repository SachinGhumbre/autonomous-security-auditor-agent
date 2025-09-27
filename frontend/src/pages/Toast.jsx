import React from 'react';

function Toast({ message, type = 'success' }) {
  const bgColor =
    type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';

  return (
    <div className={`fixed top-4 right-4 z-50 px-4 py-2 text-white rounded shadow-lg ${bgColor}`}>
      {message}
    </div>
  );
}

export default Toast;