
import React from 'react';

function Sidebar({ setActivePage }) {
  return (
    <div className="w-64 bg-blue-800 text-white p-4">
      <h2 className="text-xl mb-4">Menu</h2>
      <ul>
        <li className="mb-2 cursor-pointer hover:underline" onClick={() => setActivePage('dashboard')}>Audit Dashboard</li>
      </ul>
    </div>
  );
}

export default Sidebar;
