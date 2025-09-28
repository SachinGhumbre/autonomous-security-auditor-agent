import React from 'react';

function Header({ onLogout }) {
  return (
    <header className="bg-gradient-to-r from-blue-800 to-blue-900 text-white py-4 px-6 flex justify-between items-center shadow-md">
      <h1 className="text-xl font-bold tracking-wide">
        Autonomous Security Auditor Agents
      </h1>
    </header>
  );
}

export default Header;