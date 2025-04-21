// Agent Management Console
document.addEventListener('DOMContentLoaded', function() {
    console.log('Agent Management Console initialized');
    
    // Initialize the application if the root element exists
    const rootElement = document.getElementById('app');
    if (rootElement) {
        initAgentManagement(rootElement);
    }
});

async function initAgentManagement(rootElement) {
    rootElement.innerHTML = `
        <div class="min-h-screen bg-gray-100 flex flex-col">
            <header class="bg-white shadow-sm">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16 items-center">
                        <div class="flex items-center">
                            <h1 class="text-xl font-bold text-gray-900">Agent Provocateur</h1>
                            <span class="ml-2 px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-md">
                                Agent Management
                            </span>
                        </div>
                        <div id="headerActions">
                            <button id="backButton" class="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                                Back to Home
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main class="flex-grow p-4">
                <div class="max-w-7xl mx-auto">
                    <div class="mb-8">
                        <h2 class="text-2xl font-bold text-gray-900 mb-4">Agent Management Console</h2>
                        <p class="text-gray-600">
                            Monitor, configure, and manage your Agent Provocateur agents from a central location.
                        </p>
                    </div>
                    
                    <!-- Agent Dashboard -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <!-- Total Agents Card -->
                        <div class="bg-white rounded-lg shadow p-6 flex items-center">
                            <div class="rounded-full bg-blue-100 p-3 mr-4">
                                <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Total Agents</p>
                                <p class="text-3xl font-bold text-gray-900" id="totalAgentsCount">--</p>
                            </div>
                        </div>

                        <!-- Active Agents Card -->
                        <div class="bg-white rounded-lg shadow p-6 flex items-center">
                            <div class="rounded-full bg-green-100 p-3 mr-4">
                                <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Active Agents</p>
                                <p class="text-3xl font-bold text-gray-900" id="activeAgentsCount">--</p>
                            </div>
                        </div>

                        <!-- Tasks Processed Card -->
                        <div class="bg-white rounded-lg shadow p-6 flex items-center">
                            <div class="rounded-full bg-indigo-100 p-3 mr-4">
                                <svg class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Tasks Processed</p>
                                <p class="text-3xl font-bold text-gray-900" id="tasksCount">--</p>
                            </div>
                        </div>
                    </div>

                    <!-- Agent List -->
                    <div class="bg-white rounded-lg shadow mb-8">
                        <div class="px-4 py-5 border-b border-gray-200 sm:px-6 flex justify-between items-center">
                            <h3 class="text-lg leading-6 font-medium text-gray-900">
                                Registered Agents
                            </h3>
                            <div>
                                <button id="refreshAgentsBtn" class="px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 text-sm flex items-center">
                                    <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    Refresh
                                </button>
                            </div>
                        </div>
                        <div class="p-4 overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tasks</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="agentsList" class="bg-white divide-y divide-gray-200">
                                    <tr>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center" colspan="5">
                                            Loading agents...
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Agent Configuration -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <!-- Plugin Management -->
                        <div class="bg-white rounded-lg shadow">
                            <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">
                                    Agent Plugins
                                </h3>
                                <p class="mt-1 text-sm text-gray-500">
                                    Enable or disable agent plugins and modules
                                </p>
                            </div>
                            <div class="p-4">
                                <ul class="divide-y divide-gray-200">
                                    <li class="py-4 flex justify-between items-center">
                                        <div class="flex items-center">
                                            <div class="bg-blue-100 rounded-md p-2 mr-3">
                                                <svg class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                                </svg>
                                            </div>
                                            <div>
                                                <p class="text-sm font-medium text-gray-900">Web Search MCP</p>
                                                <p class="text-xs text-gray-500">External search capabilities</p>
                                            </div>
                                        </div>
                                        <label class="switch">
                                            <input type="checkbox" id="webSearchToggle" checked>
                                            <span class="slider round"></span>
                                        </label>
                                    </li>
                                    <li class="py-4 flex justify-between items-center">
                                        <div class="flex items-center">
                                            <div class="bg-green-100 rounded-md p-2 mr-3">
                                                <svg class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                                </svg>
                                            </div>
                                            <div>
                                                <p class="text-sm font-medium text-gray-900">Entity Detector</p>
                                                <p class="text-xs text-gray-500">Named entity recognition</p>
                                            </div>
                                        </div>
                                        <label class="switch">
                                            <input type="checkbox" id="entityDetectorToggle" checked>
                                            <span class="slider round"></span>
                                        </label>
                                    </li>
                                    <li class="py-4 flex justify-between items-center">
                                        <div class="flex items-center">
                                            <div class="bg-purple-100 rounded-md p-2 mr-3">
                                                <svg class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                                </svg>
                                            </div>
                                            <div>
                                                <p class="text-sm font-medium text-gray-900">Source Attribution</p>
                                                <p class="text-xs text-gray-500">Reference and citation management</p>
                                            </div>
                                        </div>
                                        <label class="switch">
                                            <input type="checkbox" id="sourceAttributionToggle" checked>
                                            <span class="slider round"></span>
                                        </label>
                                    </li>
                                </ul>
                                <div class="mt-4">
                                    <button id="savePluginSettingsBtn" class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm">
                                        Save Settings
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- System Monitoring -->
                        <div class="bg-white rounded-lg shadow">
                            <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">
                                    System Monitoring
                                </h3>
                                <p class="mt-1 text-sm text-gray-500">
                                    Real-time system metrics and performance
                                </p>
                            </div>
                            <div class="p-4">
                                <div class="mb-4">
                                    <p class="text-sm font-medium text-gray-700 mb-2">System Health</p>
                                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                                        <div class="bg-green-600 h-2.5 rounded-full" style="width: 90%"></div>
                                    </div>
                                    <div class="flex justify-between text-xs text-gray-500 mt-1">
                                        <span>CPU: 10%</span>
                                        <span>Memory: 35%</span>
                                        <span>Disk: 20%</span>
                                    </div>
                                </div>
                                
                                <div class="mb-4">
                                    <p class="text-sm font-medium text-gray-700 mb-2">Agent Response Time</p>
                                    <div class="flex items-center">
                                        <div class="w-full bg-gray-200 rounded-full h-2.5 mr-2">
                                            <div class="bg-blue-600 h-2.5 rounded-full" style="width: 65%"></div>
                                        </div>
                                        <span class="text-xs text-gray-500">1.2s</span>
                                    </div>
                                </div>
                                
                                <div class="mb-4">
                                    <p class="text-sm font-medium text-gray-700 mb-2">Message Queue</p>
                                    <div class="flex items-center">
                                        <div class="w-full bg-gray-200 rounded-full h-2.5 mr-2">
                                            <div class="bg-indigo-600 h-2.5 rounded-full" style="width: 15%"></div>
                                        </div>
                                        <span class="text-xs text-gray-500">3/20</span>
                                    </div>
                                </div>
                                
                                <div class="mt-6">
                                    <a href="http://localhost:3000" target="_blank" class="text-sm text-indigo-600 hover:text-indigo-800 flex items-center">
                                        <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                        Open Grafana Dashboard
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <footer class="bg-white border-t border-gray-200 py-4 mt-8">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <p class="text-center text-sm text-gray-500">
                        Agent Provocateur • Agent Management Console
                    </p>
                    <div class="flex justify-center mt-2">
                        <div id="system-info" class="text-xs text-gray-400 flex items-center space-x-4">
                            <span id="version-info">Version: 0.1.0</span>
                            <span class="text-gray-300">|</span>
                            <span id="ui-port">UI Port: <span class="font-mono">${window.location.port || '80'}</span></span>
                            <span class="text-gray-300">|</span>
                            <span id="backend-url">API: <span class="font-mono">${window.BACKEND_URL}</span></span>
                            <span class="text-gray-300">|</span>
                            <button id="check-ports-btn" class="text-indigo-400 hover:text-indigo-600 transition">Check Ports</button>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    `;

    // Add CSS for toggle switches
    addToggleStyles();

    // Set up event listeners
    setupEventListeners();
    
    // Load agent data
    loadAgentData();
}

function addToggleStyles() {
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        /* Toggle Switch Styles */
        .switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }
        
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #e2e8f0;
            -webkit-transition: .4s;
            transition: .4s;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            -webkit-transition: .4s;
            transition: .4s;
        }
        
        input:checked + .slider {
            background-color: #6366f1;
        }
        
        input:focus + .slider {
            box-shadow: 0 0 1px #6366f1;
        }
        
        input:checked + .slider:before {
            -webkit-transform: translateX(20px);
            -ms-transform: translateX(20px);
            transform: translateX(20px);
        }
        
        /* Rounded sliders */
        .slider.round {
            border-radius: 34px;
        }
        
        .slider.round:before {
            border-radius: 50%;
        }
    `;
    document.head.appendChild(styleEl);
}

function setupEventListeners() {
    // Back button
    document.getElementById('backButton').addEventListener('click', function() {
        window.location.href = '/';
    });
    
    // Refresh agents button
    document.getElementById('refreshAgentsBtn').addEventListener('click', function() {
        this.classList.add('animate-spin');
        loadAgentData().finally(() => {
            this.classList.remove('animate-spin');
        });
    });
    
    // Save plugin settings button
    document.getElementById('savePluginSettingsBtn').addEventListener('click', function() {
        savePluginSettings();
    });
    
    // Setup port checker button
    document.getElementById('check-ports-btn').addEventListener('click', function() {
        checkSystemPorts();
    });
}

// Function to check system ports (shared with landing.js)
async function checkSystemPorts() {
    try {
        // Create a modal to display port information
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center';
        modal.innerHTML = `
            <div class="absolute inset-0 bg-black bg-opacity-30" id="port-modal-backdrop"></div>
            <div class="bg-white rounded-lg shadow-xl p-6 max-w-xl w-full relative z-10 m-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium">System Port Status</h3>
                    <button id="port-modal-close" class="text-gray-400 hover:text-gray-500">
                        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div id="port-status-content" class="mb-4">
                    <p class="text-gray-500">Checking port status...</p>
                </div>
                <div class="mt-4 text-xs text-gray-500">
                    <p>Common ports used by Agent Provocateur:</p>
                    <ul class="list-disc pl-5 mt-1 space-y-1">
                        <li>3000: Grafana dashboard (monitoring)</li>
                        <li>3001: Frontend UI server</li>
                        <li>8000: MCP Server API</li>
                        <li>8080: Web Search MCP</li>
                        <li>8081: Entity Detector MCP</li>
                        <li>9090: Prometheus metrics</li>
                        <li>9091: Pushgateway</li>
                        <li>6379: Redis</li>
                    </ul>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Add event listeners for closing the modal
        document.getElementById('port-modal-backdrop').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        document.getElementById('port-modal-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        // Fetch port status information from our API endpoint
        try {
            const currentPort = window.location.port || '80';
            const portStatusContent = document.getElementById('port-status-content');
            
            // Use the system info API to get comprehensive information
            const infoResponse = await fetch(`${window.location.origin}/api/info`);
            if (!infoResponse.ok) {
                throw new Error(`Failed to fetch system info: ${infoResponse.status}`);
            }
            
            const systemInfo = await infoResponse.json();
            console.log('System info:', systemInfo);
            
            // Build the status display
            let portsHtml = '';
            if (systemInfo.ports) {
                // Sort the ports to display in order
                const sortedPorts = Object.entries(systemInfo.ports).sort((a, b) => a[0] - b[0]);
                
                portsHtml = `
                    <div class="mt-4 border rounded p-3 bg-gray-50 text-sm">
                        <h4 class="font-medium mb-2">Port Status</h4>
                        <div class="grid grid-cols-3 gap-2">
                            ${sortedPorts.map(([port, info]) => `
                                <div class="flex items-center space-x-2">
                                    <span class="w-2 h-2 rounded-full ${info.in_use ? 'bg-green-500' : 'bg-gray-300'}"></span>
                                    <span class="font-mono">${port}</span>
                                    <span class="text-gray-600">${info.service}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            // Update the content
            portStatusContent.innerHTML = `
                <div class="space-y-3">
                    <div class="flex flex-col border-b pb-3">
                        <div class="flex justify-between items-center">
                            <span class="font-medium">Version</span>
                            <span class="bg-gray-100 px-2 py-1 rounded text-xs font-mono">
                                ${systemInfo.version || '0.1.0'}
                            </span>
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                            Agent Provocateur system version
                        </div>
                    </div>
                
                    <div class="flex items-center justify-between border-b pb-2">
                        <span class="font-medium">Frontend UI</span>
                        <span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            Connected (Port ${currentPort})
                        </span>
                    </div>
                    
                    <div class="flex items-center justify-between border-b pb-2">
                        <span class="font-medium">Backend API</span>
                        <span class="bg-${systemInfo.backend_status === 'available' ? 'green' : 'red'}-100 
                               text-${systemInfo.backend_status === 'available' ? 'green' : 'red'}-800 px-2 py-1 rounded text-xs">
                            ${systemInfo.backend_status === 'available' ? 'Available' : 'Unavailable'}
                        </span>
                    </div>
                    
                    ${portsHtml}
                    
                    <div class="mt-4">
                        <p class="text-sm">If you're experiencing connection issues:</p>
                        <ol class="list-decimal pl-5 mt-2 text-sm space-y-1">
                            <li>Ensure the backend server is running (port 8000)</li>
                            <li>Check for port conflicts with Grafana (port 3000)</li>
                            <li>Use explicit port URLs in the browser: http://localhost:3001</li>
                            <li>See <code class="bg-gray-100 px-1 py-0.5 rounded">docs/development/DEVELOPMENT.md</code> for more troubleshooting</li>
                        </ol>
                    </div>
                </div>
            `;
            
        } catch (error) {
            const portStatusContent = document.getElementById('port-status-content');
            portStatusContent.innerHTML = `
                <div class="text-red-500">
                    Error checking port status: ${error.message}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error showing port information:', error);
    }
}

// Load agent data from the backend
async function loadAgentData() {
    try {
        // Fetch the agent data from the backend
        // In a real implementation, we would call a backend API
        // For now, let's simulate the data
        const simulatedData = await simulateAgentData();
        
        // Update dashboard stats
        updateDashboardStats(simulatedData);
        
        // Populate agent list
        populateAgentList(simulatedData.agents);
        
    } catch (error) {
        console.error('Error loading agent data:', error);
        // Show error in the agent list
        document.getElementById('agentsList').innerHTML = `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-red-500 text-center" colspan="5">
                    Error loading agent data: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Simulate agent data retrieval (to be replaced with real API calls)
async function simulateAgentData() {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
        totalAgents: 5,
        activeAgents: 3,
        tasksProcessed: 124,
        agents: [
            {
                id: 'xml_agent_1',
                name: 'XML Agent',
                type: 'document_processor',
                status: 'active',
                tasks: 47,
                description: 'Processes XML documents and extracts structured data'
            },
            {
                id: 'web_search_agent_1',
                name: 'Web Search Agent',
                type: 'research',
                status: 'active',
                tasks: 62,
                description: 'Searches the web for information to enrich documents'
            },
            {
                id: 'research_supervisor_1',
                name: 'Research Supervisor',
                type: 'supervisor',
                status: 'active',
                tasks: 15,
                description: 'Coordinates research tasks and manages agent workflow'
            },
            {
                id: 'entity_detector_1',
                name: 'Entity Detector MCP',
                type: 'service',
                status: 'inactive',
                tasks: 0,
                description: 'Detects and extracts named entities from text'
            },
            {
                id: 'verification_agent_1',
                name: 'Verification Agent',
                type: 'auditor',
                status: 'inactive',
                tasks: 0,
                description: 'Verifies claims and statements in documents'
            }
        ]
    };
}

// Update dashboard statistics
function updateDashboardStats(data) {
    document.getElementById('totalAgentsCount').textContent = data.totalAgents;
    document.getElementById('activeAgentsCount').textContent = data.activeAgents;
    document.getElementById('tasksCount').textContent = data.tasksProcessed;
}

// Populate agent list table
function populateAgentList(agents) {
    const tableBody = document.getElementById('agentsList');
    
    if (!agents || agents.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center" colspan="5">
                    No agents found in the system.
                </td>
            </tr>
        `;
        return;
    }
    
    // Clear table
    tableBody.innerHTML = '';
    
    // Add each agent row
    agents.forEach(agent => {
        const row = document.createElement('tr');
        
        // Get status color based on agent status
        const statusColor = agent.status === 'active' ? 'green' : 'gray';
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-indigo-100 rounded-full">
                        ${getAgentIcon(agent.type)}
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${agent.name}</div>
                        <div class="text-xs text-gray-500">${agent.id}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${formatAgentType(agent.type)}</div>
                <div class="text-xs text-gray-500">${agent.description}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${statusColor}-100 text-${statusColor}-800">
                    ${agent.status}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${agent.tasks}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex space-x-2">
                    ${agent.status === 'active' 
                        ? `<button data-agent-id="${agent.id}" class="stop-agent-btn text-red-600 hover:text-red-900" title="Stop Agent">
                            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>`
                        : `<button data-agent-id="${agent.id}" class="start-agent-btn text-green-600 hover:text-green-900" title="Start Agent">
                            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>`
                    }
                    <button data-agent-id="${agent.id}" class="configure-agent-btn text-indigo-600 hover:text-indigo-900" title="Configure Agent">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </button>
                    <button data-agent-id="${agent.id}" class="logs-agent-btn text-gray-600 hover:text-gray-900" title="View Logs">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                        </svg>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners to action buttons
    setupAgentActionButtons();
}

// Get appropriate icon for agent type
function getAgentIcon(agentType) {
    switch (agentType) {
        case 'document_processor':
            return `<svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>`;
        case 'research':
            return `<svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>`;
        case 'supervisor':
            return `<svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>`;
        case 'service':
            return `<svg class="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                    </svg>`;
        case 'auditor':
            return `<svg class="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>`;
        default:
            return `<svg class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>`;
    }
}

// Format agent type for display
function formatAgentType(type) {
    return type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Set up agent action buttons
function setupAgentActionButtons() {
    // Start agent buttons
    document.querySelectorAll('.start-agent-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            startAgent(agentId);
        });
    });
    
    // Stop agent buttons
    document.querySelectorAll('.stop-agent-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            stopAgent(agentId);
        });
    });
    
    // Configure agent buttons
    document.querySelectorAll('.configure-agent-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            configureAgent(agentId);
        });
    });
    
    // View logs buttons
    document.querySelectorAll('.logs-agent-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agentId = this.getAttribute('data-agent-id');
            viewAgentLogs(agentId);
        });
    });
}

// Start an agent
function startAgent(agentId) {
    // In a real implementation, we would call a backend API
    // For now, let's just show an alert
    alert(`Starting agent ${agentId}...`);
    console.log(`Starting agent ${agentId}`);
    
    // Refresh agent data after a short delay to simulate the agent starting
    setTimeout(() => {
        loadAgentData();
    }, 1000);
}

// Stop an agent
function stopAgent(agentId) {
    // In a real implementation, we would call a backend API
    // For now, let's just show an alert
    alert(`Stopping agent ${agentId}...`);
    console.log(`Stopping agent ${agentId}`);
    
    // Refresh agent data after a short delay to simulate the agent stopping
    setTimeout(() => {
        loadAgentData();
    }, 1000);
}

// Configure an agent
function configureAgent(agentId) {
    // In a real implementation, we would show a configuration modal
    // For now, let's just show an alert
    alert(`Configure agent ${agentId} (coming soon)`);
    console.log(`Configure agent ${agentId}`);
}

// View agent logs
function viewAgentLogs(agentId) {
    // Create a modal to show the logs
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center';
    modal.innerHTML = `
        <div class="absolute inset-0 bg-black bg-opacity-30" id="logs-modal-backdrop"></div>
        <div class="bg-white rounded-lg shadow-xl p-6 max-w-3xl w-full max-h-3/4 relative z-10 m-4 flex flex-col">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-medium">Logs for ${agentId}</h3>
                <button id="logs-modal-close" class="text-gray-400 hover:text-gray-500">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="overflow-y-auto flex-grow">
                <pre class="bg-gray-100 p-3 rounded text-xs font-mono h-96 overflow-auto">${generateDummyLogs(agentId)}</pre>
            </div>
            <div class="mt-4 flex justify-end">
                <button id="download-logs-btn" class="px-3 py-1 bg-indigo-600 text-white rounded text-sm">Download Logs</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Add event listeners for closing the modal
    document.getElementById('logs-modal-backdrop').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    document.getElementById('logs-modal-close').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    // Add event listener for downloading logs
    document.getElementById('download-logs-btn').addEventListener('click', () => {
        downloadLogs(agentId, generateDummyLogs(agentId));
    });
}

// Generate dummy logs for demo purposes
function generateDummyLogs(agentId) {
    const logEntries = [
        `[2025-04-20 08:00:01] INFO: ${agentId} started`,
        `[2025-04-20 08:00:02] INFO: Agent registered with supervisor`,
        `[2025-04-20 08:00:05] INFO: Waiting for task assignment`,
        `[2025-04-20 08:01:10] INFO: Received task: process_document`,
        `[2025-04-20 08:01:11] DEBUG: Task parameters: {"doc_id": "doc_12345", "mode": "full_analysis"}`,
        `[2025-04-20 08:01:12] INFO: Processing document doc_12345`,
        `[2025-04-20 08:01:15] DEBUG: Found 15 nodes in document`,
        `[2025-04-20 08:01:20] INFO: Extracting entities from document`,
        `[2025-04-20 08:01:25] DEBUG: Extracted 8 entities`,
        `[2025-04-20 08:01:30] INFO: Researching entities with Web Search MCP`,
        `[2025-04-20 08:01:35] DEBUG: Received search results for 6/8 entities`,
        `[2025-04-20 08:01:40] WARN: No search results for 2 entities`,
        `[2025-04-20 08:01:45] INFO: Compiling entity information`,
        `[2025-04-20 08:01:50] INFO: Task completed successfully`,
        `[2025-04-20 08:01:55] INFO: Results reported to supervisor`,
        `[2025-04-20 08:02:00] INFO: Waiting for next task`,
        `[2025-04-20 08:15:10] INFO: Received task: process_document`,
        `[2025-04-20 08:15:11] DEBUG: Task parameters: {"doc_id": "doc_67890", "mode": "entity_extraction"}`,
        `[2025-04-20 08:15:12] INFO: Processing document doc_67890`,
        `[2025-04-20 08:15:15] DEBUG: Found 22 nodes in document`,
        `[2025-04-20 08:15:20] INFO: Extracting entities from document`,
        `[2025-04-20 08:15:25] DEBUG: Extracted 12 entities`,
        `[2025-04-20 08:15:30] INFO: Task completed successfully`,
        `[2025-04-20 08:15:35] INFO: Results reported to supervisor`,
        `[2025-04-20 08:15:40] INFO: Waiting for next task`
    ];
    
    return logEntries.join('\n');
}

// Download logs as a text file
function downloadLogs(agentId, logsContent) {
    const blob = new Blob([logsContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${agentId}_logs_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

// Save plugin settings
function savePluginSettings() {
    // Get toggle states
    const webSearchEnabled = document.getElementById('webSearchToggle').checked;
    const entityDetectorEnabled = document.getElementById('entityDetectorToggle').checked;
    const sourceAttributionEnabled = document.getElementById('sourceAttributionToggle').checked;
    
    // In a real implementation, we would send this to the backend
    console.log('Saving plugin settings:', {
        webSearchEnabled,
        entityDetectorEnabled,
        sourceAttributionEnabled
    });
    
    // Show a success message
    alert('Plugin settings saved successfully!');
}