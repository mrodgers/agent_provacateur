// Main application component
const App = () => {
  const [page, setPage] = React.useState('dashboard');
  const [documents, setDocuments] = React.useState([]);
  const [agents, setAgents] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [activeDocument, setActiveDocument] = React.useState(null);
  const [researchResults, setResearchResults] = React.useState(null);

  // Navigation handler
  const navigate = (newPage) => {
    setPage(newPage);
  };

  // Fetch documents from API
  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${window.BACKEND_URL}/documents`);
      setDocuments(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch active agents
  const fetchAgents = async () => {
    // This is a mock function until we implement agent status in the backend
    setAgents([
      { id: 'research_supervisor', status: 'active', type: 'supervisor' },
      { id: 'xml_agent', status: 'active', type: 'xml' },
      { id: 'doc_agent', status: 'active', type: 'document' },
      { id: 'search_agent', status: 'inactive', type: 'search' },
      { id: 'synthesis_agent', status: 'active', type: 'synthesis' },
    ]);
  };

  // View document details
  const viewDocument = async (docId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${window.BACKEND_URL}/documents/${docId}`);
      setActiveDocument(response.data);
      setPage('document-view');
      setError(null);
    } catch (err) {
      console.error('Error fetching document:', err);
      setError('Failed to load document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Run research on a document
  const runResearch = async (docId, options = {}) => {
    setLoading(true);
    try {
      // In a real implementation, this would call the backend API
      // For demo purposes, we're creating mock data
      setResearchResults({
        doc_id: docId,
        workflow_id: `research_${docId}_${Date.now()}`,
        entity_count: 5,
        research_count: 3,
        summary: "Research completed successfully",
        research_results: [
          {
            entity: "Artificial Intelligence",
            definition: "AI refers to computer systems capable of performing tasks that typically require human intelligence.",
            confidence: 0.95,
            sources: [
              { type: "web", title: "AI Definition", url: "https://example.com/ai" }
            ]
          },
          {
            entity: "Machine Learning",
            definition: "A subset of AI focused on systems that can learn from data without explicit programming.",
            confidence: 0.9,
            sources: [
              { type: "document", title: "ML Basics", doc_id: "doc2" }
            ]
          },
          {
            entity: "Natural Language Processing",
            definition: "NLP enables computers to understand and process human language.",
            confidence: 0.85,
            sources: [
              { type: "web", title: "NLP Guide", url: "https://example.com/nlp" }
            ]
          }
        ],
        enriched_xml: `<?xml version="1.0"?>\n<research-document>\n  <entity name="Artificial Intelligence" confidence="0.95">\n    <definition>AI refers to computer systems capable of performing tasks that typically require human intelligence.</definition>\n  </entity>\n</research-document>`
      });
      setPage('research-results');
    } catch (err) {
      console.error('Error running research:', err);
      setError('Failed to run research. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Initialize - fetch data on component mount
  React.useEffect(() => {
    fetchDocuments();
    fetchAgents();
  }, []);

  // Render appropriate page based on state
  const renderPage = () => {
    switch (page) {
      case 'dashboard':
        return <Dashboard agents={agents} documents={documents} navigate={navigate} />;
      case 'documents':
        return <DocumentsList documents={documents} viewDocument={viewDocument} />;
      case 'document-view':
        return <DocumentView document={activeDocument} runResearch={runResearch} />;
      case 'research-results':
        return <ResearchResults results={researchResults} />;
      case 'agents':
        return <AgentsList agents={agents} />;
      default:
        return <Dashboard agents={agents} documents={documents} navigate={navigate} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header navigate={navigate} activePage={page} />
      
      {/* Main content */}
      <main className="flex-grow p-6">
        {loading && <LoadingSpinner />}
        {error && <ErrorAlert message={error} />}
        {!loading && !error && renderPage()}
      </main>
      
      <Footer />
    </div>
  );
};

// Dashboard component
const Dashboard = ({ agents, documents, navigate }) => {
  const activeAgentCount = agents.filter(agent => agent.status === 'active').length;
  const xmlDocCount = documents.filter(doc => doc.doc_type === 'xml').length;
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Agent Status Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-2">Agent Status</h2>
          <p className="text-3xl font-bold text-blue-600">{activeAgentCount} / {agents.length}</p>
          <p className="text-gray-600">Agents Active</p>
          <button 
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={() => navigate('agents')}
          >
            View Agents
          </button>
        </div>
        
        {/* Document Stats Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-2">Documents</h2>
          <p className="text-3xl font-bold text-green-600">{documents.length}</p>
          <p className="text-gray-600">Total Documents</p>
          <p className="mt-2">{xmlDocCount} XML Documents</p>
          <button 
            className="mt-4 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            onClick={() => navigate('documents')}
          >
            View Documents
          </button>
        </div>
        
        {/* Quick Actions Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-2">Quick Actions</h2>
          <div className="space-y-2">
            <button 
              className="w-full px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
              onClick={() => navigate('documents')}
            >
              Start Research
            </button>
            <button className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
              Upload XML Document
            </button>
          </div>
        </div>
      </div>
      
      {/* Recent Documents */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Recent Documents</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.slice(0, 5).map((doc) => (
                <tr key={doc.doc_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.doc_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.doc_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button 
                      className="text-blue-600 hover:text-blue-900"
                      onClick={() => navigate('document-view', doc.doc_id)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Documents List component
const DocumentsList = ({ documents, viewDocument }) => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Documents</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">All Documents</h2>
          <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Upload New
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.doc_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.doc_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{doc.doc_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm flex space-x-2">
                    <button 
                      className="text-blue-600 hover:text-blue-900"
                      onClick={() => viewDocument(doc.doc_id)}
                    >
                      View
                    </button>
                    {doc.doc_type === 'xml' && (
                      <button className="text-green-600 hover:text-green-900">
                        Research
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Document View component
const DocumentView = ({ document, runResearch }) => {
  if (!document) return <p>No document selected</p>;
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{document.title}</h1>
      
      <div className="mb-6 flex justify-between items-center">
        <div>
          <span className="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">
            {document.doc_type}
          </span>
          <span className="text-gray-600">ID: {document.doc_id}</span>
        </div>
        
        {document.doc_type === 'xml' && (
          <button 
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            onClick={() => runResearch(document.doc_id)}
          >
            Start Research
          </button>
        )}
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Document Content</h2>
        
        {/* Render content based on document type */}
        {document.doc_type === 'text' && (
          <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: document.html }}></div>
        )}
        
        {document.doc_type === 'xml' && (
          <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-sm">
            {document.content}
          </pre>
        )}
        
        {document.doc_type === 'pdf' && (
          <div>
            <p className="mb-2">PDF URL: <a href={document.url} className="text-blue-600 hover:underline">{document.url}</a></p>
            <div className="space-y-4">
              {document.pages.map((page, index) => (
                <div key={index} className="border p-4 rounded">
                  <h3 className="font-semibold mb-2">Page {page.page_number}</h3>
                  <p>{page.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {document.doc_type === 'code' && (
          <div>
            <p className="mb-2">Language: {document.language} • {document.line_count} lines</p>
            <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-sm">
              {document.content}
            </pre>
          </div>
        )}
      </div>
      
      {/* Display XML-specific information */}
      {document.doc_type === 'xml' && document.researchable_nodes && document.researchable_nodes.length > 0 && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-4">Researchable Nodes</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Element</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">XPath</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {document.researchable_nodes.map((node, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{node.element_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">{node.xpath}</td>
                    <td className="px-6 py-4 text-sm">{node.content || "[Empty]"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        node.verification_status === 'verified' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {node.verification_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Research Results component
const ResearchResults = ({ results }) => {
  if (!results) return <p>No research results available</p>;
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Research Results</h1>
      
      <div className="mb-6 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-gray-600">Document ID</p>
            <p className="font-semibold">{results.doc_id}</p>
          </div>
          <div>
            <p className="text-gray-600">Workflow ID</p>
            <p className="font-semibold">{results.workflow_id}</p>
          </div>
          <div>
            <p className="text-gray-600">Summary</p>
            <p className="font-semibold">{results.summary}</p>
          </div>
          <div>
            <p className="text-gray-600">Entities Found</p>
            <p className="font-semibold">{results.entity_count}</p>
          </div>
          <div>
            <p className="text-gray-600">Entities Researched</p>
            <p className="font-semibold">{results.research_count}</p>
          </div>
        </div>
      </div>
      
      <div className="mb-6 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Research Results</h2>
        <div className="space-y-4">
          {results.research_results.map((result, index) => (
            <div key={index} className="border p-4 rounded">
              <div className="flex justify-between">
                <h3 className="font-semibold text-lg">{result.entity}</h3>
                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                  Confidence: {(result.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="my-2">{result.definition}</p>
              
              {result.sources && result.sources.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm text-gray-600 font-semibold">Sources:</p>
                  <ul className="list-disc pl-5 text-sm">
                    {result.sources.map((source, idx) => (
                      <li key={idx}>
                        {source.type === 'web' ? (
                          <a href={source.url} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
                            {source.title}
                          </a>
                        ) : (
                          <span>{source.title} ({source.type})</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {results.enriched_xml && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-4">Enriched XML</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-sm whitespace-pre-wrap">
            {results.enriched_xml}
          </pre>
        </div>
      )}
    </div>
  );
};

// Agents List component
const AgentsList = ({ agents }) => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Agents</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Agent Status</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agents.map((agent) => (
                <tr key={agent.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{agent.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{agent.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {agent.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {agent.status === 'active' ? (
                      <button className="text-red-600 hover:text-red-900">Stop</button>
                    ) : (
                      <button className="text-green-600 hover:text-green-900">Start</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Header component
const Header = ({ navigate, activePage }) => {
  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Agent Provocateur</h1>
            </div>
            <nav className="ml-6 flex space-x-8">
              <button 
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  activePage === 'dashboard' 
                    ? 'border-indigo-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
                onClick={() => navigate('dashboard')}
              >
                Dashboard
              </button>
              <button 
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  activePage === 'documents' || activePage === 'document-view' 
                    ? 'border-indigo-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
                onClick={() => navigate('documents')}
              >
                Documents
              </button>
              <button 
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  activePage === 'agents' 
                    ? 'border-indigo-500 text-gray-900' 
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
                onClick={() => navigate('agents')}
              >
                Agents
              </button>
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
};

// Footer component
const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 py-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-sm text-gray-500">
          Agent Provocateur • Multi-Agent Research System
        </p>
      </div>
    </footer>
  );
};

// Loading spinner component
const LoadingSpinner = () => {
  return (
    <div className="flex justify-center mt-8">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );
};

// Error alert component
const ErrorAlert = ({ message }) => {
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4" role="alert">
      <strong className="font-bold">Error!</strong>
      <span className="block sm:inline"> {message}</span>
    </div>
  );
};

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
  try {
    console.log("Initializing App...");
    
    // Check if we have the newer createRoot API (React 18+)
    if (ReactDOM.createRoot) {
      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(React.createElement(App));
    } else {
      // Fallback for older React versions
      ReactDOM.render(
        React.createElement(App), 
        document.getElementById('root')
      );
    }
    
    console.log("App initialized successfully");
  } catch (error) {
    console.error("Error initializing app:", error);
    
    // Display error message
    document.getElementById('error-container').innerHTML = `
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
        <strong class="font-bold">Error initializing app:</strong>
        <span class="block sm:inline"> ${error.message}</span>
        <pre class="mt-2 text-xs overflow-auto">${error.stack || 'No stack trace available'}</pre>
      </div>
    `;
  }
});