
import React, { useEffect, useMemo, useState } from 'react';

function Dashboard() {
  const [audits, setAudits] = useState([]);
  const [message, setMessage] = useState('');
  const [report, setReport] = useState(null);

  useEffect(() => {
    const fetchAudits = async () => {
      try {
        // Mock API call for audits
        const mockAudits = [
          { id: 1, status: 'Completed', date: '2023-10-26' },
          { id: 2, status: 'Pending', date: '2023-10-25' },
        ];
        setAudits(mockAudits);
      } catch (error) {
        console.error('Error fetching audits:', error);
      }
    };
    fetchAudits();
  }, []);

  const handleIngestEmbeddings = async () => {
    setMessage('');
    setReport(null); // Hide report when ingesting embeddings
    try {
      // Mock API call for embedding
      const response = await fetch('https://api.example.com/ingest-embeddings', { method: 'POST' });
      if (response.ok) {
        setMessage('Embeddings ingested successfully!');
      } else {
        setMessage('Failed to ingest embeddings.');
      }
    } catch (error) {
      console.error('Error ingesting embeddings:', error);
      setMessage('Error ingesting embeddings.');
    }
  };

  const handleStartAuditor = async () => {
    setMessage('');
    setReport(null);
    // The report will be set to data.report if the API call is successful, making it visible.
    try {
      // Mock API call for auditor
      const response = await fetch('https://httpbin.org/post', { method: 'POST' });
      if (response.ok) {
        // Mock data for the report
        const data = {
          report: [
            {
              srNo: 1, apiServiceName: 'User Service', pluginsUsed: 'jwt, rate-limiting', securityPolicy: 'Authentication, Authorization', complianceStatus: 'compliant', recommendation: 'None',
            },
            {
              srNo: 2, apiServiceName: 'Product Service', pluginsUsed: 'oauth2', securityPolicy: 'Authentication', complianceStatus: 'non-compliant', recommendation: 'Add Authorization Policy',
            },
            {
              srNo: 3, apiServiceName: 'Order Service', pluginsUsed: 'acl', securityPolicy: 'Rate Limiting', complianceStatus: 'compliant', recommendation: 'None',
            },
            {
              srNo: 4, apiServiceName: 'Payment Service', pluginsUsed: 'ssl', securityPolicy: 'Encryption', complianceStatus: 'compliant', recommendation: 'None',
            },
            {
              srNo: 5, apiServiceName: 'Shipping Service', pluginsUsed: 'cors', securityPolicy: 'Authentication', complianceStatus: 'non-compliant', recommendation: 'Implement OAuth',
            },
            {
              srNo: 6, apiServiceName: 'Inventory Service', pluginsUsed: 'ip-restriction', securityPolicy: 'Access Control', complianceStatus: 'compliant', recommendation: 'None',
            },
          ],
        };
        setReport(data.report);
        setMessage('Auditor started successfully!');
      } else {
        setMessage('Failed to start auditor.');
      }
    } catch (error) {
      console.error('Error starting auditor:', error);
      setMessage('Error starting auditor.');
    }
  };

  const handleGenerateExcel = () => {
    alert('Generating Excel report...');
    // Logic to generate Excel file
  };

  const handleSendEmail = () => {
    alert('Sending report via email...');
    // Logic to send email
  };

  const getStatusRowClass = (status) => {
    switch (status.toLowerCase()) {
      case 'compliant':
        return 'bg-green-100';
      case 'non-compliant':
        return 'bg-red-100';
      default:
        return '';
    }
  };

  const sortedReport = useMemo(() => {
    if (!report) {
      return null;
    }
    // Create a new array to avoid mutating state directly
    return [...report].sort((a, b) => {
      if (a.status === b.status) return 0; // Keep original order for same status
      return a.complianceStatus.toLowerCase() === 'non-compliant' ? -1 : 1;
    });
  }, [report]);

  const handleReset = () => {
    setAudits([]);
    setMessage('');
    setReport(null);
  };


  return (
    <div className="container mx-auto p-4">
      <div className="flex space-x-4 mb-4">
        <button
          onClick={handleIngestEmbeddings}
          className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded"
        >
          Ingest Embeddings
        </button>
        <button
          onClick={handleStartAuditor}
          className="bg-blue-900 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Start Autonomous Auditor
        </button>
        <button
          onClick={handleReset}
          className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
        >
          Reset
        </button>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded ${message.includes('successfully') ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
          {message}
        </div>
      )}

      {sortedReport && (
        <div className="mb-8">
          <h3 className="text-xl mb-3">Audit Report</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-200">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b">Sr. No.</th>
                  <th className="py-2 px-4 border-b">API Service Name</th>
                  <th className="py-2 px-4 border-b">Plugins Used</th>
                  <th className="py-2 px-4 border-b">Security Policy</th>
                  <th className="py-2 px-4 border-b">Compliance Status</th>
                  <th className="py-2 px-4 border-b">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {sortedReport.map((item, index) => (
                  <tr key={index} className={getStatusRowClass(item.complianceStatus)}>
                    <td className="py-2 px-4 border-b">{item.srNo}</td>
                    <td className="py-2 px-4 border-b">{item.apiServiceName}</td>
                    <td className="py-2 px-4 border-b">{item.pluginsUsed}</td>
                    <td className="py-2 px-4 border-b">{item.securityPolicy}</td>
                    <td className="py-2 px-4 border-b">{item.complianceStatus}</td>
                    <td className="py-2 px-4 border-b">{item.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex space-x-4 mt-4">
            <button
              onClick={handleGenerateExcel}
              className="bg-blue-900 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Generate Excel Report
            </button>
            <button
              onClick={handleSendEmail}
              className="bg-blue-900 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Send Report in Email
            </button>
          </div>
        </div>
      )}

      {!report && (
        <div className="mt-8 p-6 bg-gray-100 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Welcome to the Autonomous Security Auditor Agent</h2>
          <p className="text-gray-700 mb-4">
            This tool is designed to automate the security auditing process for your services.
            By leveraging advanced AI capabilities, it can identify potential security vulnerabilities
            and compliance issues within your configurations and policies.
          </p>
          <p className="text-gray-700">
            It can be used by Enterprise Security Auditors, compliance teams, and DevSecOps professionals to ensure regulatory compliance and security best practices.
            The agent will analyze your API configurations and provide a detailed report with
            actionable recommendations to enhance your security posture.
          </p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
