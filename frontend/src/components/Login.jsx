import React, { useState } from 'react';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTimeout(() => {
      if (username === 'kong_champion' && password === 'Kong@123') {
        onLogin();
      } else {
        setError('Invalid credentials');
      }
      setLoading(false);
    }, 1000); // Simulate API delay
  };

  return (
    <div className="flex-grow flex items-center justify-center">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded shadow-md w-full max-w-md"
      >
        <h2 className="text-2xl font-bold text-center text-blue-900 mb-6">
          Login
        </h2>

        {error && (
          <div className="mb-4 text-red-600 text-sm text-center font-medium animate-pulse">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-semibold mb-2">
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter username"
          />
        </div>

        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-semibold mb-2">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter password"
          />
        </div>

        <div className="flex items-center justify-center">
          <button
            type="submit"
            disabled={loading}
            className={`bg-blue-900 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition duration-200 shadow-md ${loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </div>

        {loading && (
          <div className="absolute top-2 right-2">
            <div className="w-5 h-5 border-4 border-blue-300 border-t-white rounded-full animate-spin"></div>
          </div>
        )}
      </form>
    </div>
  );
}

export default Login;