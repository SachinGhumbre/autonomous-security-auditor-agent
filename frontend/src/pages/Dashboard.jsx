
import React, { useEffect, useMemo, useState } from 'react';
import Toast from './Toast';

function Dashboard() {
  const [auditsReport, setAuditsReport] = useState([]);
  const [ingestedData, setIngestedData] = useState([]);
  const [message, setMessage] = useState('');
  const [report, setReport] = useState(null);
  const [remediationData, setRemediationData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeButton, setActiveButton] = useState('');
  const [selectedStandards, setSelectedStandards] = useState([]);

  const securityStandardsList = [
    "GDPR", "HIPAA", "PCI-DSS", "ISO 27001", "OWASP API Top 10",
    "PSD2/SCA", "PIPEDA", "NIST", "SOC 2", "All Security Standards"
  ];

const toggleStandard = (standard) => {
  if (standard === "All Security Standards") {
    if (selectedStandards.includes("All Security Standards")) {
      // Deselect all
      setSelectedStandards([]);
    } else {
      // Select all
      setSelectedStandards([...securityStandardsList]);
    }
  } else {
    setSelectedStandards(prev => {
      const updated = prev.includes(standard)
        ? prev.filter(s => s !== standard)
        : [...prev, standard];

      // If all individual standards are selected, include "All Security Standards"
      const allExceptAll = securityStandardsList.filter(s => s !== "All Security Standards");
      const allSelected = allExceptAll.every(s => updated.includes(s));

      if (allSelected && !updated.includes("All Security Standards")) {
        return [...updated, "All Security Standards"];
      }

      // If deselecting any individual standard, remove "All Security Standards"
      if (!allSelected && updated.includes("All Security Standards")) {
        return updated.filter(s => s !== "All Security Standards");
      }

      return updated;
    });
  }
};

  const handleGenerateAuditReport = () => {
    if (!auditsReport || auditsReport.length === 0) {
      setMessage('❌ No audit report available to download.');
      return;
    }
    const blob = new Blob([auditsReport], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'audit_report.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const handleIngestEmbeddings = async () => {
    setLoading(true);
    setActiveButton('ingest');
    setError(null);
    setMessage('');
    setReport(null);
    try {
      const response = await fetch('http://localhost:5001/api/v1/knowledge/ingest', {
        method: 'POST',
        body: JSON.stringify({}),
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        setMessage('✅ All Security Policies Ingested successfully!');
        setIngestedData([data]);
      } else {
        setMessage('❌ Failed to ingest Security Policies.');
      }
    } catch (error) {
      console.error('Error ingesting Security Policies:', error);
      setMessage('❌ Error ingesting Security Policies.');
    } finally {
      setLoading(false);
      setActiveButton('');
    }
  };

  const handleStartAuditor = async () => {
    setLoading(true);
    setActiveButton('audit');
    setError(null);
    setMessage('');
    setReport(null);
    setAuditsReport([]);
    setIngestedData([]);

    //alert("selectedStandards: "+selectedStandards)
    try {
      const response = await fetch('http://localhost:5000/api/v1/ai-agents/audit', {
      //const response = await fetch('https://httpbin.org/post', {
        method: 'POST',
        body: JSON.stringify({
          selected_standards: selectedStandards
        }),
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        if (data && data.audit_report) {
          setAuditsReport(JSON.stringify({ audit_report: data.audit_report }));
          const reportArr = Object.entries(data.audit_report).map(([key, value]) => {
            const policies = value.policies || value.results || [];
            const policy_checks = policies.map(p => ({
              ...p,
              comply: typeof p.comply === 'string' ? p.comply.toLowerCase() === 'comply' : !!p.comply,
              missing_plugins: p.missing_plugins || [],
              policy_name: p.policy_name,
              required_for: p.required_for || p.policy_name,
              details: p.details || ''
            }));
            return {
              serviceName: value.serviceName,
              policy_checks
            };
          });
          setReport(reportArr);
        }
        setMessage('✅ Audit Completed successfully!');
      } else {
        setMessage('❌ Failed to start auditor.');
      }
    } catch (error) {
      console.error('Error starting auditor:', error);
      setMessage('❌ Error starting auditor.');
    } finally {
      setLoading(false);
      setActiveButton('');
    }
  };

  const fetchRemediationPlan = async () => {
    setMessage('');
    setIngestedData([]);
    setLoading(true);
    setActiveButton('remediate');
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/v1/ai-agents/remediate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audit_report: JSON.parse(auditsReport).audit_report
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();
      setRemediationData(data);
    } catch (err) {
      console.error('Error fetching remediation plan:', err);
      setError('❌ Failed to fetch remediation plan.');
    } finally {
      setLoading(false);
      setActiveButton('');
    }
  };

  const sortedReport = useMemo(() => {
    if (!report) return null;
    const flat = [];
    report.forEach(serviceObj => {
      serviceObj.policy_checks.forEach(policy => {
        flat.push({ ...policy, serviceName: serviceObj.serviceName });
      });
    });
    flat.sort((a, b) => (a.comply === b.comply ? 0 : a.comply ? 1 : -1));
    return flat;
  }, [report]);

  const handleReset = () => {
    setAuditsReport([]);
    setMessage('');
    setReport(null);
    setIngestedData([]);
    setRemediationData([]);
    setError(null);
    setSelectedStandards([]);
  };

  return (
    <div className="container mx-auto p-6 bg-gray-50 rounded-lg shadow-lg">
      {error && (
        <p className="text-red-600 text-sm font-medium">{error}</p>
      )}

      {message && (
        <Toast message={message} type={message.includes('success') ? 'success' : 'error'} />
      )}

{/* Security Standards Selection */}
<div className="mb-6">
  <h1 className="text-lg font-semibold text-gray-700 mb-4 text-center">
    Select Security Standards
  </h1>
  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    {securityStandardsList.map((standard) => {
      const isSelected = selectedStandards.includes(standard);
      return (
        <div
          key={standard}
          onClick={() => toggleStandard(standard)}
          className={`cursor-pointer p-3 rounded-lg shadow-md border transition duration-300 ease-in-out flex items-center justify-between
            ${isSelected ? 'bg-blue-900 text-white border-blue-700' : 'bg-gradient-to-r from-blue-100 via-blue-200 to-blue-300 text-gray-800 hover:from-blue-200 hover:via-blue-300 hover:to-blue-400 border-gray-300'}`}
        >
          <span className="text-sm font-medium">{standard}</span>
          <div className="relative inline-block w-10 h-5 align-middle select-none transition duration-200 ease-in">
            <div className={`w-10 h-5 rounded-full shadow-inner ${isSelected ? 'bg-green-500' : 'bg-gray-300'}`}>
              <div className={`absolute top-0.5 left-0.5 w-3.5 h-3.5 bg-white rounded-full transition transform ${isSelected ? 'translate-x-5' : ''}`}></div>
            </div>
          </div>
        </div>
      );
    })}
  </div>
</div>
      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center mb-6">
        <button
          onClick={handleIngestEmbeddings}
          disabled={loading && activeButton === 'ingest'}
          className={`px-5 py-2 rounded font-semibold shadow-md transition duration-200 ${activeButton === 'ingest' && loading
            ? 'bg-orange-300 cursor-not-allowed'
            : 'bg-orange-500 hover:bg-orange-600 text-white'
            }`}
        >
          {activeButton === 'ingest' && loading ? 'Processing...' : 'Ingest Security Policies'}
        </button>

        <button
          onClick={handleStartAuditor}
          disabled={loading && activeButton === 'audit'}
          className={`px-5 py-2 rounded font-semibold shadow-md transition duration-200 ${activeButton === 'audit' && loading
            ? 'bg-blue-300 cursor-not-allowed'
            : 'bg-blue-900 hover:bg-blue-700 text-white'
            }`}
        >
          {activeButton === 'audit' && loading
            ? 'Running Audit...'
            : 'Start Security Audit and Generate Report'}
        </button>

        <button
          onClick={handleReset}
          className="bg-gray-600 hover:bg-gray-700 text-white font-semibold px-5 py-2 rounded shadow-md transition duration-200"
        >
          Reset
        </button>
      </div>

      {/* Status Messages */}
      <div className="mb-4 text-center">
        {loading && (
          <p className="text-blue-700 text-sm animate-pulse">
            Auditor Process in progress...
          </p>
        )}


        {/* Security Policy Table */}
        {ingestedData.length > 0 && (
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-center text-white bg-gradient-to-r from-indigo-700 to-indigo-900 py-3 rounded shadow-md mb-6">
              Security Policies Ingested Report
            </h3>
            <div className="w-full overflow-x-auto rounded-lg shadow-lg">
              <table className="min-w-[1000px] bg-white border border-gray-300 rounded-lg">
                <thead className="bg-indigo-100 sticky top-0 z-10">
                  <tr>
                    {["Index Name", "Chunk ID", "Content", "Metadata"].map((header, idx) => (
                      <th
                        key={idx}
                        className="py-3 px-4 border-b text-left text-sm font-semibold text-indigo-900 whitespace-nowrap"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ingestedData.map((item, idx) =>
                    Array.isArray(item.chunks)
                      ? item.chunks.map((chunk, cidx) => (
                        <tr
                          key={`${idx}-${cidx}`}
                          className={cidx % 2 === 0 ? "bg-white" : "bg-gray-50 hover:bg-indigo-50"}
                        >
                          <td className="py-2 px-4 border-b whitespace-nowrap">{item.index_name}</td>
                          <td className="py-2 px-4 border-b whitespace-nowrap">{chunk.chunk_id}</td>
                          <td className="py-2 px-4 border-b">
                            <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded text-gray-800">
                              {chunk.content}
                            </pre>
                          </td>
                          <td className="py-2 px-4 border-b">
                            <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded text-gray-800">
                              {chunk.metadata}
                            </pre>
                          </td>
                        </tr>
                      ))
                      : null
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Audit Report Table */}
        {sortedReport && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-center text-white bg-gradient-to-r from-blue-700 to-blue-900 py-3 rounded shadow-md mb-6">
              Security Audit Report
            </h2>
            <div className="w-full max-w-full overflow-x-auto rounded-lg shadow-lg scrollbar-thin scrollbar-thumb-blue-500 scrollbar-track-blue-100">
              <table className="min-w-[1200px] bg-white border border-gray-300 rounded-lg">
                <thead className="bg-blue-100 sticky top-0 z-10">
                  <tr>
                    {[
                      "Sr. No.",
                      "Service Name",
                      "Security Policy Name",
                      "Compliance Status",
                      "Missing Plugins",
                      "Details"
                    ].map((header, idx) => (
                      <th
                        key={idx}
                        className="py-3 px-4 border-b text-left text-sm font-semibold text-blue-900 whitespace-nowrap"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sortedReport.map((policy, idx) => (
                    <tr
                      key={idx}
                      className={
                        policy.comply
                          ? "bg-green-50 hover:bg-green-100"
                          : "bg-red-50 hover:bg-red-100"
                      }
                    >
                      <td className="py-2 px-4 border-b whitespace-nowrap">{idx + 1}</td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">{policy.serviceName}</td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">{policy.policy_name}</td>
                      <td className="py-2 px-4 border-b font-semibold whitespace-nowrap">
                        {policy.comply ? (
                          <span className="text-green-700">Compliant</span>
                        ) : (
                          <span className="text-red-700">Non-Compliant</span>
                        )}
                      </td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">
                        {!policy.comply && policy.missing_plugins?.length > 0
                          ? policy.missing_plugins.map((mp, mpIdx) => (
                            <div key={mpIdx} className="text-sm text-gray-800">
                              <span className="font-semibold">
                                {mp.plugin || mp.name || JSON.stringify(mp)}
                              </span>
                              {mp.required_for && (
                                <span className="text-xs text-gray-600">
                                  {" "}
                                  (Required for: {mp.required_for})
                                </span>
                              )}
                            </div>
                          ))
                          : "-"}
                      </td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">
                        {policy.details ? (
                          <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded text-gray-800">
                            {policy.details}
                          </pre>
                        ) : (
                          "-"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Audit Actions */}
            <div className="flex flex-wrap gap-4 mt-6 justify-center">
              <button
                onClick={handleGenerateAuditReport}
                className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700 transition duration-200 shadow-md"
              >
                Download Audit Report
              </button>
              <button
                onClick={fetchRemediationPlan}
                disabled={loading && activeButton === 'remediate'}
                className={`px-5 py-2 rounded font-semibold shadow-md transition duration-200 ${activeButton === 'remediate' && loading
                  ? 'bg-blue-300 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
              >
                {activeButton === 'remediate' && loading
                  ? 'Generating Remediation Plan...'
                  : 'Run Remediation Plan'}
              </button>

              {loading && activeButton === 'remediate' && (
                <p className="mt-4 text-blue-600 text-sm animate-pulse">
                  Loading remediation plan...
                </p>
              )}
              {error && (
                <p className="mt-4 text-red-600 text-sm font-medium">{error}</p>
              )}
            </div>
          </div>
        )}

        {/* Remediation Plan Table */}
        {remediationData.length > 0 && (
          <div className="w-full overflow-x-auto">
            <h3 className="text-2xl font-bold text-center text-white bg-gradient-to-r from-blue-700 to-blue-900 py-3 rounded shadow-md mb-6">
              Remediation Plan
            </h3>
            <div className="min-w-[1600px] inline-block align-middle">
              <table className="w-full bg-white border border-gray-300 rounded-lg">
                <thead className="bg-blue-100 sticky top-0 z-10">
                  <tr>
                    {[
                      "Service Name",
                      "Policy Name",
                      "Issue",
                      "Missing Plugin(s)",
                      "Recommended Action",
                      "Severity",
                      "Owner",
                      "Estimated Effort",
                      "Impact",
                      "Security Standard Reference"
                    ].map((header, idx) => (
                      <th
                        key={idx}
                        className="py-3 px-4 border-b text-left text-sm font-semibold text-blue-900 whitespace-nowrap"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {remediationData.map((item, idx) => (
                    <tr
                      key={idx}
                      className={idx % 2 === 0 ? "bg-white" : "bg-gray-50 hover:bg-blue-50"}
                    >
                      <td className="py-2 px-4 border-b whitespace-nowrap">{item.serviceName}</td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">{item.policyName}</td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">
                        <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded text-gray-800">
                          {item.issue}
                        </pre>
                      </td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">
                        {Array.isArray(item.missingPlugin)
                          ? item.missingPlugin.join(', ')
                          : item.missingPlugin}
                      </td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">
                        <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded text-gray-800">
                          {item.recommendedAction}
                        </pre>
                      </td>
                      <td className="py-2 px-4 border-b font-semibold text-red-600 whitespace-nowrap">
                        {item.severity}
                      </td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">{item.owner}</td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">{item.estimatedEffort}</td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">
                        <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded text-gray-800">
                          {item.impact}
                        </pre>
                      </td>
                      <td className="py-2 px-4 border-b whitespace-nowrap">{item.securityStandardReference}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Welcome Section */}
        {!report && ingestedData.length === 0 && (
          <div className="mt-8 p-6 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-center text-gray-800 mb-4">
              Welcome to the Autonomous Security Auditor Agents
            </h2>
            <p className="text-gray-700 mb-4 leading-relaxed text-justify">
              The <strong>Autonomous Security Auditor Agentic AI</strong> is an advanced application designed to automate the auditing and remediation of API configurations for organizations using Kong API Gateway and Kong AI Gateway. Leveraging AI, large language models (LLMs), and agentic workflows, this tool enables organizations to continuously validate API configurations against enterprise security and compliance policies, identify risks, and remediate issues with minimal manual intervention.
            </p>
            <p className="text-gray-700 leading-relaxed text-justify">
              The Autonomous Security Auditor Agentic AI bridges these gaps by automatically auditing API proxy configurations in Kong against organizational security policies. It generates actionable audit reports and enables one-click remediation, ensuring every API adheres to mandatory security standards. This tool empowers <strong>developers, DevSecOps engineers, reviewers, auditors, and architects</strong> to maintain compliance and security without deep expertise in every policy, reducing risk and streamlining the review process.
            </p>
          </div>
        )}


      </div>
    </div>
  );
}

export default Dashboard;
