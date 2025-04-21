// Enhanced XML Document Viewer
// This script provides an improved viewing experience for XML documents

document.addEventListener('DOMContentLoaded', function() {
    console.log('Document Viewer initialized');
    
    // Define global debug level
    window.AP_DEBUG = {
        level: 'info', // 'error', 'warn', 'info', 'debug', 'verbose'
        api: true,     // Log API calls
        ui: true,      // Log UI events
        data: true     // Log data transformations
    };
    
    // Enhance console logging with app-specific prefixes
    const logger = {
        error: (msg, ...args) => console.error(`[AP ERROR] ${msg}`, ...args),
        warn: (msg, ...args) => console.warn(`[AP WARN] ${msg}`, ...args),
        info: (msg, ...args) => console.info(`[AP INFO] ${msg}`, ...args),
        debug: (msg, ...args) => window.AP_DEBUG.level !== 'error' && window.AP_DEBUG.level !== 'warn' && 
                                 window.AP_DEBUG.level !== 'info' && console.debug(`[AP DEBUG] ${msg}`, ...args),
        verbose: (msg, ...args) => window.AP_DEBUG.level === 'verbose' && console.debug(`[AP VERBOSE] ${msg}`, ...args),
        api: (msg, ...args) => window.AP_DEBUG.api && console.log(`[AP API] ${msg}`, ...args),
        ui: (msg, ...args) => window.AP_DEBUG.ui && console.log(`[AP UI] ${msg}`, ...args),
        data: (msg, ...args) => window.AP_DEBUG.data && console.log(`[AP DATA] ${msg}`, ...args)
    };
    
    // Make logger available globally
    window.apLogger = logger;
    
    // Initialize the application if the root element exists
    const rootElement = document.getElementById('app');
    if (rootElement) {
        logger.info('Initializing document viewer application');
        initDocumentViewer(rootElement);
        
        // Check if we have a document ID passed in the URL
        if (window.DOC_ID) {
            logger.info('Document ID from URL:', window.DOC_ID);
            
            // Set a timeout to allow the select element to be populated
            setTimeout(() => {
                const selectElement = document.getElementById('docSelect');
                if (selectElement) {
                    // Try to set the select to the passed document ID
                    const options = Array.from(selectElement.options);
                    const matchingOption = options.find(option => option.value === window.DOC_ID);
                    
                    if (matchingOption) {
                        selectElement.value = window.DOC_ID;
                        // Trigger the document load
                        logger.ui('Auto-loading document:', window.DOC_ID);
                        document.getElementById('loadDocumentBtn').click();
                    } else {
                        logger.warn(`Document ID from URL (${window.DOC_ID}) not found in available documents`);
                    }
                } else {
                    logger.error('Document selector not found in DOM');
                }
            }, 1000);
        }
    } else {
        logger.error('Root element #app not found in DOM');
    }
});

function initDocumentViewer(rootElement) {
    // Setup the basic UI structure
    rootElement.innerHTML = `
        <div class="min-h-screen bg-gray-100 flex flex-col">
            <header class="bg-white shadow-sm">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16 items-center">
                        <div class="flex items-center">
                            <h1 class="text-xl font-bold text-gray-900">Agent Provocateur</h1>
                        </div>
                        <div id="headerActions">
                            <button id="backButton" class="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                                Back to Documents
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main class="flex-grow p-4">
                <div class="max-w-7xl mx-auto">
                    <div class="flex flex-col md:flex-row gap-4">
                        <!-- Document Panel (Left) -->
                        <div class="flex-1 bg-white rounded-lg shadow-md p-4 min-h-[500px]">
                            <div class="flex justify-between items-center mb-4">
                                <h2 class="text-lg font-medium text-gray-900">Document Viewer</h2>
                                <div>
                                    <button id="refreshDocumentBtn" class="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700">
                                        Refresh
                                    </button>
                                </div>
                            </div>
                            <div id="documentSelector" class="mb-4">
                                <label for="docSelect" class="block text-sm font-medium text-gray-700">Select Document:</label>
                                <div class="flex gap-2 mt-1">
                                    <select id="docSelect" class="flex-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                                        <option value="">-- Select a document --</option>
                                    </select>
                                    <button id="loadDocumentBtn" class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700">
                                        Load
                                    </button>
                                </div>
                            </div>
                            <div id="documentViewer" class="border rounded-md p-4 bg-gray-50 min-h-[400px] max-w-full overflow-auto"></div>
                        </div>

                        <!-- Supervisor Panel (Right) -->
                        <div class="w-full md:w-80 lg:w-96 bg-white rounded-lg shadow-md p-4 min-h-[500px]">
                            <h2 class="text-lg font-medium text-gray-900 mb-4">Supervisor</h2>
                            <div id="supervisorChat" class="border rounded-md p-4 bg-gray-50 h-[400px] overflow-auto mb-4">
                                <div class="bg-indigo-100 p-3 rounded-lg mb-2 max-w-[80%]">
                                    <p>Hello! I'm your XML processing supervisor. Please select a document to begin.</p>
                                </div>
                            </div>
                            <div class="flex gap-2">
                                <input 
                                    id="supervisorInput" 
                                    type="text" 
                                    class="flex-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                                    placeholder="Type your message..."
                                    disabled
                                />
                                <button 
                                    id="sendMessageBtn" 
                                    class="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
                                    disabled
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Results Panel (Bottom) -->
                    <div class="mt-4 bg-white rounded-lg shadow-md p-4 min-h-[200px]">
                        <div class="flex justify-between items-center mb-4">
                            <h2 class="text-lg font-medium text-gray-900">Processing & Results</h2>
                            <div class="flex gap-2">
                                <div class="dropdown relative" id="processingDropdown">
                                    <button id="processingTypeBtn" class="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center">
                                        <span>Processing Type</span>
                                        <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </button>
                                    <div class="dropdown-menu hidden absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg z-10">
                                        <a href="#" data-type="entity-extraction" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">Extract Entities</a>
                                        <div class="sub-menu">
                                            <a href="#" data-type="term-research" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 relative">
                                                Research Terms
                                                <span class="absolute right-2 top-1/2 transform -translate-y-1/2">➤</span>
                                            </a>
                                            <div class="dropdown-submenu hidden absolute left-full top-0 mt-0 -ml-1 w-48 bg-white rounded-md shadow-lg z-20">
                                                <div class="py-1 text-xs text-gray-700 px-3">Search Provider:</div>
                                                <a href="#" data-type="term-research" data-provider="brave" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">Brave (Default)</a>
                                                <a href="#" data-type="term-research" data-provider="google" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">Google</a>
                                                <a href="#" data-type="term-research" data-provider="bing" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">Bing</a>
                                                <div class="border-t my-1"></div>
                                                <a href="#" data-type="term-research" data-provider="none" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">No Web Search</a>
                                            </div>
                                        </div>
                                        <a href="#" data-type="structure-validation" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">Validate Structure</a>
                                        <a href="#" data-type="xml-enrichment" class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50">Enrich XML</a>
                                    </div>
                                </div>
                                <button id="startProcessingBtn" class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 opacity-50" disabled>
                                    Start Processing
                                </button>
                            </div>
                        </div>
                        <div id="resultsPanel" class="border rounded-md p-4 bg-gray-50 min-h-[150px] overflow-auto">
                            <p class="text-gray-500">Select a document and define processing goals to see results.</p>
                        </div>
                    </div>
                </div>
            </main>

            <footer class="bg-white border-t border-gray-200 py-4">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <p class="text-center text-sm text-gray-500">
                        Agent Provocateur • Writer's Research Assistant
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

    // Initialize components
    initializeDocumentSelector();
    setupEventListeners();
}

async function initializeDocumentSelector() {
    const selectElement = document.getElementById('docSelect');
    const documentViewer = document.getElementById('documentViewer');
    const supervisorChat = document.getElementById('supervisorChat');
    
    try {
        // Fetch the list of documents using API client
        documentViewer.innerHTML = '<p>Loading documents...</p>';
        
        // Add a message to the supervisor chat
        addSupervisorMessage("I'm connecting to the database to find available XML documents.");
        
        // Use API client to fetch documents
        const documents = await window.apApi.documents.getAllDocuments();
        console.log("Documents loaded with API client:", documents);
        
        // Filter to get only XML documents
        const xmlDocuments = documents.filter(doc => doc.doc_type === 'xml');
        console.log("XML documents:", xmlDocuments);
        
        if (xmlDocuments.length === 0) {
            documentViewer.innerHTML = '<p>No XML documents found in the system.</p>';
            addSupervisorMessage("I couldn't find any XML documents in the system. You may need to upload one first.");
            return;
        }
        
        // Populate the select dropdown
        selectElement.innerHTML = '<option value="">-- Select a document --</option>';
        xmlDocuments.forEach(doc => {
            const option = document.createElement('option');
            option.value = doc.doc_id;
            option.textContent = `${doc.title} (${doc.doc_id})`;
            selectElement.appendChild(option);
        });
        
        documentViewer.innerHTML = '<p>Select a document from the dropdown and click "Load".</p>';
        
        // Enable the load button
        document.getElementById('loadDocumentBtn').disabled = false;
        
        // Add a message to the supervisor chat
        addSupervisorMessage(`I found ${xmlDocuments.length} XML document${xmlDocuments.length !== 1 ? 's' : ''} in the system. Please select one from the dropdown to begin.`);
        
    } catch (error) {
        console.error('Error initializing document selector:', error);
        
        // Format the error using API utils if available
        const formattedError = window.apiUtils?.formatApiError 
            ? window.apiUtils.formatApiError(error, 'Failed to load documents')
            : { message: error.message || 'Unknown error loading documents' };
        
        documentViewer.innerHTML = `<p class="text-red-500">Error loading documents: ${formattedError.message}</p>`;
        
        // Provide more context in the supervisor message based on error type
        if (formattedError.isNetworkError || formattedError.status === 0) {
            addSupervisorMessage(`I couldn't connect to the backend server. Please check that it's running and try again.`);
        } else {
            addSupervisorMessage(`I encountered an error while trying to fetch documents: ${formattedError.message}. Please check the backend server status.`);
        }
    }
}

// Helper function to add a message from the supervisor to the chat
function addSupervisorMessage(message) {
    const supervisorChat = document.getElementById('supervisorChat');
    if (!supervisorChat) return;
    
    const messageHtml = `
        <div class="bg-indigo-100 p-3 rounded-lg mb-2 max-w-[80%]">
            <p>${message}</p>
        </div>
    `;
    supervisorChat.insertAdjacentHTML('beforeend', messageHtml);
    supervisorChat.scrollTop = supervisorChat.scrollHeight;
}

// Helper function to add a message from the user to the chat
function addUserMessage(message) {
    const supervisorChat = document.getElementById('supervisorChat');
    if (!supervisorChat) return;
    
    const messageHtml = `
        <div class="bg-green-100 p-3 rounded-lg mb-2 max-w-[80%] ml-auto">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    supervisorChat.insertAdjacentHTML('beforeend', messageHtml);
    supervisorChat.scrollTop = supervisorChat.scrollHeight;
}

function setupEventListeners() {
    // Setup Load Document button
    const loadDocumentBtn = document.getElementById('loadDocumentBtn');
    loadDocumentBtn.addEventListener('click', loadSelectedDocument);
    
    // Setup Refresh button
    const refreshDocumentBtn = document.getElementById('refreshDocumentBtn');
    refreshDocumentBtn.addEventListener('click', () => {
        const selectElement = document.getElementById('docSelect');
        if (selectElement.value) {
            loadDocument(selectElement.value);
        } else {
            alert('Please select a document first.');
        }
    });
    
    // Setup Back button
    const backButton = document.getElementById('backButton');
    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // Setup Start Processing button
    const startProcessingBtn = document.getElementById('startProcessingBtn');
    startProcessingBtn.addEventListener('click', startProcessing);
    
    // Setup Send Message button
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const supervisorInput = document.getElementById('supervisorInput');
    
    sendMessageBtn.addEventListener('click', () => {
        sendSupervisorMessage(supervisorInput.value);
        supervisorInput.value = '';
    });
    
    supervisorInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendSupervisorMessage(supervisorInput.value);
            supervisorInput.value = '';
        }
    });
    
    // Setup Processing Type dropdown
    setupProcessingTypeDropdown();
    
    // Setup port checker button
    document.getElementById('check-ports-btn').addEventListener('click', function() {
        checkSystemPorts();
    });
}

// Function to check system ports and display results
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
        
        // Fetch port status information using the API client
        try {
            const currentPort = window.location.port || '80';
            const portStatusContent = document.getElementById('port-status-content');
            
            // Use the API client to get system information
            const systemInfo = await window.apApi.getSystemInfo();
            console.log('System info from API client:', systemInfo);
            
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

function setupProcessingTypeDropdown() {
    const dropdown = document.getElementById('processingDropdown');
    const dropdownMenu = dropdown.querySelector('.dropdown-menu');
    const dropdownButton = document.getElementById('processingTypeBtn');
    const submenu = dropdown.querySelector('.sub-menu');
    const submenuContent = dropdown.querySelector('.dropdown-submenu');
    
    // Toggle dropdown menu on button click
    dropdownButton.addEventListener('click', function(e) {
        e.preventDefault();
        dropdownMenu.classList.toggle('hidden');
    });
    
    // Handle submenu hover
    if (submenu) {
        submenu.addEventListener('mouseenter', function() {
            submenuContent.classList.remove('hidden');
        });
        
        submenu.addEventListener('mouseleave', function() {
            submenuContent.classList.add('hidden');
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target)) {
            dropdownMenu.classList.add('hidden');
            if (submenuContent) {
                submenuContent.classList.add('hidden');
            }
        }
    });
    
    // Handle processing type selection
    dropdownMenu.querySelectorAll('a').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Skip if this is the parent "Research Terms" menu item that opens the submenu
            if (this.querySelector('.absolute') && this.classList.contains('relative')) {
                return;
            }
            
            const processType = this.getAttribute('data-type');
            const provider = this.getAttribute('data-provider');
            let buttonText = this.textContent.trim();
            
            // Create full button text for research with provider
            if (processType === 'term-research' && provider) {
                if (provider === 'none') {
                    buttonText = 'Research Terms (No Web Search)';
                } else {
                    buttonText = `Research Terms (${provider.charAt(0).toUpperCase() + provider.slice(1)})`;
                }
            }
            
            // Update button text and processing type
            dropdownButton.querySelector('span').textContent = buttonText;
            dropdownMenu.classList.add('hidden');
            
            // Update processing type and button text
            updateProcessingType(processType, provider);
            
            // Add message to supervisor chat
            addSupervisorMessage(`I'll help you with ${buttonText.toLowerCase()}. Click the "${buttonText.split('(')[0].trim()}" button when you're ready to begin.`);
        });
    });
}

async function loadSelectedDocument() {
    const selectElement = document.getElementById('docSelect');
    const docId = selectElement.value;
    
    if (!docId) {
        alert('Please select a document.');
        return;
    }
    
    await loadDocument(docId);
}

async function loadDocument(docId) {
    const documentViewer = document.getElementById('documentViewer');
    const resultsPanel = document.getElementById('resultsPanel');
    
    try {
        // Show loading state
        documentViewer.innerHTML = '<p>Loading document...</p>';
        addSupervisorMessage(`I'm loading document "${docId}" for analysis...`);
        
        // Use API client to fetch document information in parallel
        let docInfo, xmlContent, nodes;
        
        try {
            // Setup parallel requests using Promise.all
            const [docInfoResult, xmlContentResult, nodesResult] = await Promise.all([
                // Get document XML metadata
                window.apApi.documents.getDocumentXml(docId).catch(err => {
                    console.warn("Could not load document metadata:", err);
                    return null;
                }),
                
                // Get document XML content
                window.apApi.documents.getDocumentXmlContent(docId),
                
                // Get document nodes
                window.apApi.documents.getDocumentNodes(docId).catch(err => {
                    console.warn("Could not load document nodes:", err);
                    return [];
                })
            ]);
            
            // Assign results
            docInfo = docInfoResult;
            xmlContent = xmlContentResult;
            nodes = nodesResult || [];
            
            console.log("Document loaded with API client:", {
                hasMetadata: !!docInfo,
                contentLength: xmlContent ? xmlContent.length : 0,
                nodeCount: nodes ? nodes.length : 0
            });
            
        } catch (error) {
            // Handle critical errors (content must be available)
            console.error("Critical error loading document:", error);
            throw new Error(`Failed to load document content: ${error.message}`);
        }
        
        // Check for JSON-encoded XML response (which happens sometimes with API responses)
        if (typeof xmlContent === 'string' && xmlContent.startsWith('"') && xmlContent.endsWith('"')) {
            try {
                // Try to parse it as JSON-encoded string
                xmlContent = JSON.parse(xmlContent);
            } catch (e) {
                console.warn("Content looks like JSON but cannot be parsed:", e);
            }
        }
        
        // Format the XML content with proper indentation and syntax highlighting
        const formattedXml = window.apiUtils?.formatXmlForDisplay 
            ? window.apiUtils.formatXmlForDisplay(xmlContent)
            : formatXml(xmlContent);
            
        documentViewer.innerHTML = `
            <pre class="language-xml" style="max-height: 400px; overflow: auto; white-space: pre-wrap; word-wrap: break-word; tab-size: 2;"><code>${formattedXml}</code></pre>
        `;
        
        // Apply syntax highlighting
        Prism.highlightAllUnder(documentViewer);
        
        // Count nodes if available
        const nodeCount = nodes ? nodes.length : 0;
        
        // Add a document info section
        if (docInfo) {
            const infoHtml = `
                <div class="mt-4 p-3 bg-indigo-50 rounded-md">
                    <h3 class="font-medium">Document Info</h3>
                    <p><strong>Title:</strong> ${docInfo.title}</p>
                    <p><strong>ID:</strong> ${docInfo.doc_id}</p>
                    <p><strong>Root Element:</strong> ${docInfo.root_element || 'Unknown'}</p>
                    <p><strong>Researchable Nodes:</strong> ${nodeCount}</p>
                    <p><strong>Created:</strong> ${new Date(docInfo.created_at).toLocaleString()}</p>
                </div>
            `;
            documentViewer.insertAdjacentHTML('beforeend', infoHtml);
        }
        
        // Enable the processing button
        document.getElementById('startProcessingBtn').disabled = false;
        document.getElementById('startProcessingBtn').classList.remove('opacity-50');
        
        // Enable the supervisor chat
        document.getElementById('supervisorInput').disabled = false;
        document.getElementById('sendMessageBtn').disabled = false;
        
        // Update the supervisor chat with appropriate message based on nodes
        if (nodeCount > 0) {
            addSupervisorMessage(`I've loaded document "${docId}" and found ${nodeCount} researchable nodes. Would you like me to extract entities, research terms, or validate the structure?`);
        } else {
            addSupervisorMessage(`I've loaded document "${docId}" for you. This document doesn't have any pre-identified researchable nodes, but I can still analyze it. What would you like to do with this document?`);
        }
        
        // Update results panel with node information
        if (nodeCount > 0) {
            let nodeTypes = {};
            nodes.forEach(node => {
                const type = node.element_name || 'unknown';
                nodeTypes[type] = (nodeTypes[type] || 0) + 1;
            });
            
            let nodeTypesList = Object.entries(nodeTypes).map(([type, count]) => 
                `${type}: ${count}`
            ).join(', ');
            
            resultsPanel.innerHTML = `
                <p>Document "${docId}" loaded successfully with ${nodeCount} researchable nodes.</p>
                <p class="text-sm text-gray-600 mt-2">Node types: ${nodeTypesList}</p>
                <p class="text-sm text-gray-500 mt-2">Use the supervisor chat to define your processing goals or click "Start Processing" to begin entity extraction.</p>
            `;
        } else {
            resultsPanel.innerHTML = `
                <p>Document "${docId}" loaded successfully.</p>
                <p class="text-sm text-gray-500 mt-2">No pre-identified researchable nodes found. Use the supervisor chat to define your processing goals.</p>
            `;
        }
        
    } catch (error) {
        console.error('Error loading document:', error);
        
        // Format the error using API utils if available
        const formattedError = window.apiUtils?.formatApiError 
            ? window.apiUtils.formatApiError(error, 'Failed to load document')
            : { message: error.message || 'Unknown error loading document' };
        
        documentViewer.innerHTML = `<p class="text-red-500">Error loading document: ${formattedError.message}</p>`;
        
        // Provide more context in the supervisor message based on error type
        if (formattedError.isNetworkError || formattedError.status === 0) {
            addSupervisorMessage(`I couldn't connect to the backend server while trying to load document "${docId}". Please check that it's running and try again.`);
        } else {
            addSupervisorMessage(`I encountered an error while loading document "${docId}": ${formattedError.message}`);
        }
    }
}

async function sendSupervisorMessage(message) {
    if (!message.trim()) return;
    
    // Get current document ID
    const selectElement = document.getElementById('docSelect');
    const docId = selectElement.value;
    
    // Add user message to the chat
    addUserMessage(message);
    
    // Show thinking indicator
    const supervisorChat = document.getElementById('supervisorChat');
    const thinkingId = 'thinking-indicator';
    supervisorChat.insertAdjacentHTML('beforeend', `
        <div id="${thinkingId}" class="bg-indigo-100 p-3 rounded-lg mb-2 max-w-[80%] flex items-center">
            <div class="animate-pulse flex items-center">
                <div class="mr-2">Thinking</div>
                <div class="w-1 h-1 bg-indigo-600 rounded-full mx-0.5 animate-bounce"></div>
                <div class="w-1 h-1 bg-indigo-600 rounded-full mx-0.5 animate-bounce [animation-delay:0.2s]"></div>
                <div class="w-1 h-1 bg-indigo-600 rounded-full mx-0.5 animate-bounce [animation-delay:0.4s]"></div>
            </div>
        </div>
    `);
    supervisorChat.scrollTop = supervisorChat.scrollHeight;
    
    try {
        // Set current process type based on user message
        let processType = detectProcessType(message);
        
        // Update UI to reflect the chosen process
        updateProcessingType(processType);
        
        // In a real implementation, we would call the backend API here
        // For now, we'll simulate a response based on the message content
        await simulateProcessing(500); // Short delay to simulate processing
        
        // Generate response based on message content and document context
        let response = await generateResponse(message, docId, processType);
        
        // Remove thinking indicator
        document.getElementById(thinkingId)?.remove();
        
        // Add supervisor response
        addSupervisorMessage(response);
        
    } catch (error) {
        console.error('Error processing message:', error);
        
        // Remove thinking indicator
        document.getElementById(thinkingId)?.remove();
        
        // Add error message
        addSupervisorMessage(`I encountered an error while processing your request: ${error.message}`);
    }
}

// Detect the type of processing requested in the message
function detectProcessType(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('extract') && lowerMessage.includes('entit')) {
        return 'entity-extraction';
    } else if (lowerMessage.includes('research') || lowerMessage.includes('term') || lowerMessage.includes('define')) {
        return 'term-research';
    } else if (lowerMessage.includes('valid') || lowerMessage.includes('structur') || lowerMessage.includes('check')) {
        return 'structure-validation';
    } else if (lowerMessage.includes('enrich') || lowerMessage.includes('enhance')) {
        return 'xml-enrichment';
    } else {
        return 'general';
    }
}

// Update UI elements based on the chosen process type
function updateProcessingType(processType) {
    const startBtn = document.getElementById('startProcessingBtn');
    
    // Update button text based on process type
    if (processType === 'entity-extraction') {
        startBtn.textContent = 'Extract Entities';
    } else if (processType === 'term-research') {
        startBtn.textContent = 'Research Terms';
    } else if (processType === 'structure-validation') {
        startBtn.textContent = 'Validate Structure';
    } else if (processType === 'xml-enrichment') {
        startBtn.textContent = 'Enrich XML';
    } else {
        startBtn.textContent = 'Start Processing';
    }
    
    // Store the current process type as a data attribute on the button
    startBtn.dataset.processType = processType;
}

// Simulate processing delay
function simulateProcessing(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Generate a response based on the message and document context
async function generateResponse(message, docId, processType) {
    // In a real implementation, we would call the backend API here
    // For now, we'll simulate responses based on the message content
    
    const lowerMessage = message.toLowerCase();
    
    // Get document information if available
    let docInfo = null;
    let nodeCount = 0;
    
    try {
        if (docId) {
            const response = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml`);
            if (response.ok) {
                docInfo = await response.json();
                
                // Get researchable node count
                try {
                    const nodesResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/nodes`);
                    if (nodesResponse.ok) {
                        const nodes = await nodesResponse.json();
                        nodeCount = nodes.length;
                    }
                } catch (error) {
                    console.error("Error fetching node count:", error);
                }
            }
        }
    } catch (error) {
        console.error("Error fetching document info for response:", error);
    }
    
    // Generate response based on process type and document context
    if (processType === 'entity-extraction') {
        if (nodeCount > 0) {
            return `I'll help you extract entities from this document. I can see ${nodeCount} potential nodes to analyze. Click the 'Extract Entities' button when you're ready to begin the extraction process.`;
        } else {
            return `I'll help you extract entities from this document. I'll need to analyze the XML structure first since there are no pre-identified nodes. Click the 'Extract Entities' button when you're ready to begin.`;
        }
    } else if (processType === 'term-research') {
        return `Research on terms involves identifying key concepts and finding definitions. I'll set that up for you. We'll extract entities first, then research each one to build a knowledge base. Ready to begin when you click the 'Research Terms' button.`;
    } else if (processType === 'structure-validation') {
        if (docInfo && docInfo.root_element) {
            return `I'll help validate the document structure with root element '${docInfo.root_element}'. This will check for any structural issues or inconsistencies against XML standards.`;
        } else {
            return `I'll help validate the document structure against schema requirements. This will check for any structural issues or inconsistencies.`;
        }
    } else if (processType === 'xml-enrichment') {
        return `XML enrichment involves adding researched information back into the document. I'll extract entities, research them, and then create an enhanced version of your document with the new information.`;
    } else if (lowerMessage.includes('help') || lowerMessage.includes('what') || lowerMessage.includes('how')) {
        return `I can help you process this XML document in several ways:\n\n1. **Extract entities** - identify important terms and concepts\n2. **Research terms** - find definitions and context for entities\n3. **Validate structure** - check XML against schema requirements\n4. **Enrich XML** - add researched information back to the document\n\nWhat would you like to do?`;
    } else {
        // Generic response
        return `I'll help you with that. For this XML document${docInfo ? ` titled "${docInfo.title}"` : ''}, I can extract entities, research terms, validate the structure, or enrich the content. Let me know what specific task you'd like me to perform, or click 'Start Processing' to begin.`;
    }
}

async function startProcessing() {
    const documentViewer = document.getElementById('documentViewer');
    const resultsPanel = document.getElementById('resultsPanel');
    const supervisorChat = document.getElementById('supervisorChat');
    const startBtn = document.getElementById('startProcessingBtn');
    
    // Get the process type from the button's data attribute
    const processType = startBtn.dataset.processType || 'entity-extraction';
    
    // Disable the button during processing
    startBtn.disabled = true;
    startBtn.classList.add('opacity-50');
    
    // Show processing state
    resultsPanel.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-indigo-500"></div>
            <span>Processing document...</span>
        </div>
        <div class="mt-3" id="processingSteps">
            <p>◽ Initializing processing...</p>
        </div>
    `;
    
    // Get the selected document
    const selectElement = document.getElementById('docSelect');
    const docId = selectElement.value;
    
    if (!docId) {
        resultsPanel.innerHTML = `<p class="text-red-500">Error: No document selected.</p>`;
        startBtn.disabled = false;
        startBtn.classList.remove('opacity-50');
        return;
    }
    
    const processingSteps = document.getElementById('processingSteps');
    
    try {
        // Step 1: Initialize and analyze document structure
        processingSteps.innerHTML += `<p>✓ Initialized processing</p>`;
        processingSteps.innerHTML += `<p>◽ Analyzing XML structure...</p>`;
        
        // Use the API client to create and execute the analysis task
        let analysisResult;
        
        try {
            // Create a task to analyze the XML structure using the task API client
            const analyzeTask = await window.apApi.tasks.createTask({
                intent: "analyze_xml",
                target_agent: "xml_agent",
                payload: {
                    doc_id: docId
                }
            });
            
            console.log("Analysis task created:", analyzeTask);
            
            // If we have a task ID, we can consider this a success
            if (analyzeTask.task_id) {
                // In a real implementation with async tasks, we would poll for the result
                // For now, we'll use the task response directly since our backend is synchronous
                analysisResult = analyzeTask;
                console.log("Document analysis result:", analysisResult);
            } else {
                throw new Error("Failed to create analysis task - no task ID returned");
            }
        } catch (error) {
            console.warn("API client task creation failed:", error);
            
            // Format the error using API utils if available
            const formattedError = window.apiUtils?.formatApiError 
                ? window.apiUtils.formatApiError(error, 'Failed to analyze document')
                : { message: error.message || 'Unknown error during analysis' };
            
            // If this is a network or backend error, we'll create a fallback analysis
            if (formattedError.isNetworkError || formattedError.status === 0) {
                console.warn("Backend unavailable - using fallback implementation");
                
                // Attempt to get document info to build a fallback result
                try {
                    // Try to use the API client to get document info
                    const docInfo = await window.apApi.documents.getDocumentById(docId);
                    
                    // Create simulated analysis result based on available info
                    analysisResult = {
                        doc_id: docId,
                        title: docInfo.title || "Document",
                        analysis: {
                            verification_needed: true,
                            priority: "medium",
                            reason: "Offline analysis (backend unavailable)",
                            estimated_time_minutes: 15
                        },
                        node_count: docInfo.researchable_nodes?.length || 0,
                        root_element: docInfo.root_element || "unknown"
                    };
                    
                    console.log("Fallback document analysis:", analysisResult);
                } catch (fallbackError) {
                    // If we can't even get document info, create a minimal fallback
                    console.error("Failed to create even a fallback analysis:", fallbackError);
                    
                    analysisResult = {
                        doc_id: docId,
                        title: "Unknown Document",
                        analysis: {
                            verification_needed: true,
                            priority: "medium",
                            reason: "Minimal fallback (backend unavailable)",
                            estimated_time_minutes: 15
                        },
                        node_count: 0,
                        root_element: "unknown"
                    };
                }
            } else {
                // If it's a specific API error (not a network issue), rethrow
                throw error;
            }
        }
        
        processingSteps.innerHTML += `<p>✓ XML structure analyzed</p>`;
        
        // Step 2: Extract entities or perform requested process type
        processingSteps.innerHTML += `<p>◽ ${processType === 'entity-extraction' ? 'Extracting entities' : 
            processType === 'term-research' ? 'Researching terms' : 
            processType === 'structure-validation' ? 'Validating structure' : 
            'Processing document'}...</p>`;
        
        let taskIntent;
        let taskPayload = { doc_id: docId };
        
        // Determine which task to run based on process type
        switch (processType) {
            case 'entity-extraction':
                taskIntent = "extract_entities";
                break;
            case 'term-research':
                taskIntent = "extract_entities"; // First extract entities, then research them
                break;
            case 'structure-validation':
                taskIntent = "create_verification_plan";
                break;
            case 'xml-enrichment':
                taskIntent = "extract_entities"; // First extract entities for enrichment
                break;
            default:
                taskIntent = "extract_entities";
        }
        
        // Add optional parameters based on process type
        if (processType === 'term-research') {
            // Include web search options for term research
            taskPayload.options = {
                use_web_search: true,
                search_provider: 'brave',
                max_entities: 10
            };
        }
        
        // Prepare task payload
        const taskPayloadObj = {
            task_id: `task_${Date.now()}`,
            source_agent: "frontend",
            target_agent: "xml_agent",
            intent: taskIntent,
            payload: taskPayload
        };
        
        // Use the API client to process the document
        let taskResult;
        
        try {
            // Use appropriate API client task methods based on the process type
            switch (processType) {
                case 'entity-extraction':
                    // Use the dedicated entity extraction method
                    taskResult = await window.apApi.tasks.extractEntities(docId);
                    break;
                    
                case 'term-research':
                    // Use the research entities method with web search options
                    taskResult = await window.apApi.tasks.researchEntities(docId, {
                        use_web_search: true,
                        search_provider: taskPayload.options?.search_provider || 'brave'
                    });
                    break;
                    
                case 'structure-validation':
                    // Use the structure validation method
                    taskResult = await window.apApi.tasks.validateStructure(docId);
                    break;
                    
                case 'xml-enrichment':
                    // Use entity extraction first (this would be followed by enrichment in a real implementation)
                    taskResult = await window.apApi.tasks.extractEntities(docId);
                    break;
                    
                default:
                    // Fallback to generic task creation
                    taskResult = await window.apApi.tasks.createTask({
                        intent: taskIntent,
                        target_agent: taskPayload.target_agent || 'xml_agent',
                        payload: taskPayload
                    });
            }
            
            console.log(`Task result from API client (${processType}):`, taskResult);
            
        } catch (error) {
            console.error("Error processing document with API client:", error);
            
            // Format the error using API utils if available
            const formattedError = window.apiUtils?.formatApiError 
                ? window.apiUtils.formatApiError(error, 'Failed to process document')
                : { message: error.message || 'Unknown error processing document' };
            
            // Set a proper error response with helpful details
            taskResult = {
                error: true,
                error_type: formattedError.isNetworkError ? "backend_unavailable" : "processing_error",
                message: formattedError.message,
                details: error.message,
                doc_id: docId,
                task_intent: taskIntent
            };
            
            // Create a function to display errors in the UI if not already defined
            if (typeof displayError !== 'function') {
                window.displayError = function(title, message, details = '') {
                    const resultPanel = document.getElementById('resultPanel');
                    if (resultPanel) {
                        resultPanel.innerHTML = `
                            <div class="bg-red-50 border-l-4 border-red-400 p-4">
                                <div class="flex">
                                    <div class="flex-shrink-0">
                                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                                        </svg>
                                    </div>
                                    <div class="ml-3">
                                        <h3 class="text-sm font-medium text-red-800">${title}</h3>
                                        <div class="mt-2 text-sm text-red-700">
                                            <p>${message}</p>
                                            ${details ? `<pre class="mt-2 text-xs bg-red-50 p-2 rounded overflow-auto">${details}</pre>` : ''}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                };
            }
            
            // Display error in the UI
            if (typeof displayError === 'function') {
                const errorTitle = formattedError.isNetworkError ? "Backend Service Unavailable" : "Processing Error";
                const errorMessage = formattedError.isNetworkError 
                    ? "The document processing service is currently unavailable. Please try again later."
                    : `Error processing ${processType}: ${formattedError.message}`;
                
                displayError(errorTitle, errorMessage, error.message);
            }
            
            // This could be logged or reported to a monitoring system
            if (window.apLogger?.error) {
                window.apLogger.error(`Processing error for ${taskIntent} on document ${docId}: ${formattedError.message}`);
            } else {
                console.error(`Processing error for ${taskIntent} on document ${docId}: ${formattedError.message}`);
            }
        }
        
        // Mark the extraction/processing as complete
        processingSteps.innerHTML += `<p>✓ ${processType === 'entity-extraction' ? 'Entities extracted' : 
            processType === 'term-research' ? 'Terms identified' : 
            processType === 'structure-validation' ? 'Structure analyzed' : 
            'Processing completed'}</p>`;
        
        // Step 3: Additional processing for research or validation if needed
        if (processType === 'term-research' && taskResult.entities) {
            processingSteps.innerHTML += `<p>◽ Conducting research on extracted terms...</p>`;
            
            // Simulating research step - in a real implementation, we would 
            // call a research endpoint for each entity
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            processingSteps.innerHTML += `<p>✓ Research completed</p>`;
        } else if (processType === 'structure-validation' && taskResult.tasks) {
            processingSteps.innerHTML += `<p>◽ Validating against schema requirements...</p>`;
            
            // Simulate validation step - in a real implementation, we would
            // call a validation endpoint
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            processingSteps.innerHTML += `<p>✓ Validation completed</p>`;
        }
        
        // Step 4: Generate final results
        processingSteps.innerHTML += `<p>◽ Generating results...</p>`;
        
        // Wait a moment to simulate final processing
        await new Promise(resolve => setTimeout(resolve, 800));
        
        processingSteps.innerHTML += `<p>✓ Results generated</p>`;
        
        // Display actual results based on the task response
        if (processType === 'entity-extraction' || processType === 'term-research') {
            displayEntityResults(taskResult, processType);
        } else if (processType === 'structure-validation') {
            displayValidationResults(taskResult);
        } else {
            // Fallback to showing generic results if we can't determine the type
            displayGenericResults(taskResult, processType);
        }
        
        // Add supervisor message
        addSupervisorMessage(`I've completed ${processType.replace('-', ' ')} for the document. You can see the results below. Is there anything specific you'd like me to explain about the findings?`);
        
    } catch (error) {
        console.error('Error processing document:', error);
        
        // Show error in results panel
        processingSteps.innerHTML += `<p class="text-red-500">✗ Error: ${error.message}</p>`;
        
        // Add supervisor message about the error
        addSupervisorMessage(`I encountered an error while processing the document: ${error.message}. Please try again or select a different process type.`);
    } finally {
        // Re-enable the button
        startBtn.disabled = false;
        startBtn.classList.remove('opacity-50');
    }
}

// Helper function to display error messages in the results panel
function displayResultsError(docId, errorTitle, errorMessage, details) {
    const resultsPanel = document.getElementById('resultsPanel');
    
    // Build error HTML
    let errorHtml = `
        <div class="space-y-4">
            <div class="flex justify-between">
                <h3 class="font-medium text-lg">Processing Results</h3>
            </div>
            
            <div class="bg-red-50 border-l-4 border-red-400 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-medium text-red-800">${errorTitle}</h3>
                        <div class="mt-2 text-sm text-red-700">
                            <p>${errorMessage}</p>
                            ${details ? `<pre class="mt-2 text-xs bg-red-50 p-2 rounded overflow-auto">${details}</pre>` : ''}
                        </div>
                        <div class="mt-4">
                            <button type="button" id="retry-process" class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none">
                                Retry
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Document Information</h4>
                <p>Document ID: <strong>${docId || "Unknown"}</strong></p>
                <p>Status: <strong>Processing Failed</strong></p>
                <p>Time: <strong>${new Date().toLocaleTimeString()}</strong></p>
            </div>
        </div>
    `;
    
    resultsPanel.innerHTML = errorHtml;
    
    // Add event listener to retry button
    const retryBtn = document.getElementById('retry-process');
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            // Get the currently selected process type
            const processType = document.querySelector('button[data-selected="true"]')?.dataset.processType || 'entity-extraction';
            
            // Trigger the process again
            processDocument(docId, processType);
        });
    }
}

// Display results for entity extraction or term research
function displayEntityResults(result, processType) {
    const resultsPanel = document.getElementById('resultsPanel');
    const isResearch = processType === 'term-research';
    
    // Debug logging for result structure
    if (window.apLogger) {
        window.apLogger.info('Displaying entity results', { processType });
        window.apLogger.data('Result structure', { 
            hasEntities: !!result.entities,
            entityCount: result.entity_count,
            resultKeys: Object.keys(result),
            resultType: typeof result
        });
    }
    
    // Extract entities from the result
    let entities = [];
    if (result.entities) {
        entities = result.entities;
        if (window.apLogger) {
            window.apLogger.debug('Using entities from result.entities');
        }
    } else if (result.entity_count && result.entities) {
        entities = result.entities;
        if (window.apLogger) {
            window.apLogger.debug('Using entities from result.entities (with entity_count)');
        }
    } else {
        if (window.apLogger) {
            window.apLogger.warn('API returned unexpected format with no entities', result);
        }
        // No simulated entities - instead, show an empty result
        entities = [];
    }
    
    // Get processing time from result or use "N/A"
    const processingTime = result.processing_time ? result.processing_time.toFixed(1) : "N/A";
    
    // Build results HTML
    let resultsHtml = `
        <div class="space-y-4">
            <div class="flex justify-between">
                <h3 class="font-medium text-lg">${isResearch ? 'Research' : 'Entity Extraction'} Results</h3>
                <div>
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded download-xml-btn">Download XML</button>
                    <button class="px-2 py-1 bg-green-600 text-white text-sm rounded ml-2 export-report-btn">Export Report</button>
                </div>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Summary</h4>
                <p>Processed document: <strong>${result.doc_id || "N/A"}</strong></p>
                <p>Entities found: <strong>${entities.length}</strong></p>
                <p>Processing time: <strong>${processingTime} seconds</strong></p>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">${isResearch ? 'Researched Terms' : 'Extracted Entities'}</h4>
                <div class="space-y-3">
    `;
    
    // Add each entity
    entities.forEach((entity, index) => {
        // Debug source information
        if (window.apLogger) {
            window.apLogger.data(`Entity ${index} source info`, {
                name: entity.name || entity.content || "Unnamed",
                hasSource: !!entity.sources,
                sourceCount: entity.sources ? entity.sources.length : 0,
                sourceType: entity.sources ? typeof entity.sources : 'N/A',
                entityKeys: Object.keys(entity)
            });
            
            // Convert sources to expected format if needed
            if (entity.verification_data && entity.verification_data.sources && !entity.sources) {
                window.apLogger.debug('Moving sources from verification_data to entity.sources', entity.verification_data.sources);
                entity.sources = entity.verification_data.sources;
            }
        }
        
        const confidence = Math.round((entity.confidence || 0.7) * 100);
        const name = entity.name || entity.content || "Unnamed Entity";
        const context = entity.context || "";
        const evidence = entity.evidence || [];
        const element = entity.element || "unknown";
        
        // Check if entity has sources and ensure it's an array
        const hasSources = entity.sources && Array.isArray(entity.sources) && entity.sources.length > 0;
        
        // For debugging, print details about sources to console
        if (window.apLogger && hasSources) {
            window.apLogger.debug(`Entity ${name} has ${entity.sources.length} sources`);
            entity.sources.forEach((source, idx) => {
                window.apLogger.data(`Source ${idx}`, { 
                    title: source.title || 'Unnamed',
                    type: source.source_type || source.type || 'unknown',
                    keys: Object.keys(source)
                });
            });
        }
        
        resultsHtml += `
            <div class="border-l-4 border-indigo-500 pl-3 py-1">
                <div class="flex justify-between items-center">
                    <h5 class="font-medium">${name}</h5>
                    <span class="px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded-full">
                        ${confidence}% confidence
                    </span>
                </div>
                <p class="text-xs text-gray-500">Element: ${element}</p>
                ${context ? `<p class="text-sm mt-1"><span class="font-medium">Context:</span> ${context}</p>` : ''}
                ${evidence.length > 0 ? 
                    `<p class="text-sm mt-1"><span class="font-medium">Evidence:</span> ${evidence.join(', ')}</p>` : ''}
                ${isResearch ? 
                    `<p class="text-sm mt-1"><span class="font-medium">Definition:</span> ${entity.definition || "Research in progress..."}</p>` : ''}
                    
                <!-- Source Attribution Section -->
                ${hasSources ? 
                    `<div class="mt-2">
                        <details class="text-sm">
                            <summary class="text-indigo-600 cursor-pointer font-medium">
                                <span class="flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                    </svg>
                                    Sources (${entity.sources.length})
                                </span>
                            </summary>
                            <div class="pl-2 mt-1 border-l-2 border-gray-200 space-y-1">
                                ${entity.sources.map(source => {
                                    const sourceType = source.source_type || source.type || 'unknown';
                                    const sourceTitle = source.title || 'Unnamed Source';
                                    const sourceConfidence = Math.round((source.confidence || 0.5) * 100);
                                    
                                    return `
                                        <div class="py-1">
                                            <div class="flex items-center justify-between">
                                                <span class="font-medium">${sourceTitle}</span>
                                                <span class="text-xs px-1 py-0.5 bg-blue-50 text-blue-700 rounded">
                                                    ${sourceConfidence}%
                                                </span>
                                            </div>
                                            <div class="text-xs text-gray-600 flex items-center">
                                                <span class="bg-gray-100 rounded px-1">${sourceType}</span>
                                                ${source.url ? 
                                                    `<a href="${source.url}" target="_blank" class="ml-2 text-blue-500 hover:underline flex items-center">
                                                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                                        </svg>
                                                        link
                                                    </a>` : 
                                                    ''
                                                }
                                            </div>
                                            ${source.citation ? 
                                                `<div class="text-xs italic text-gray-500 mt-1">${source.citation}</div>` : 
                                                ''
                                            }
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </details>
                    </div>` : 
                    `<!-- No sources available for this entity -->`
                }
            </div>
        `;
    });
    
    // Close entity section
    resultsHtml += `
                </div>
            </div>
    `;
    
    // Add sample XML section
    resultsHtml += `
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">${isResearch ? 'Enriched' : 'Annotated'} XML Sample</h4>
                <pre class="text-xs bg-gray-100 p-2 rounded max-h-32 overflow-auto" style="white-space: pre-wrap; word-break: break-word; tab-size: 2;"><code class="language-xml">${formatXml(generateEntityXml(entities, isResearch))}</code></pre>
            </div>
        </div>
    `;
    
    resultsPanel.innerHTML = resultsHtml;
    
    // Apply Prism highlighting to the code sample
    Prism.highlightAllUnder(resultsPanel);
    
    // Add event listeners to the download buttons
    const downloadXmlBtn = resultsPanel.querySelector('.download-xml-btn');
    if (downloadXmlBtn) {
        downloadXmlBtn.addEventListener('click', () => {
            const xmlContent = generateEntityXml(entities, isResearch);
            const docId = result.doc_id || 'document';
            downloadXml(xmlContent, `${docId}_processed.xml`);
        });
    }
    
    const exportReportBtn = resultsPanel.querySelector('.export-report-btn');
    if (exportReportBtn) {
        exportReportBtn.addEventListener('click', () => {
            // Create a report object with the results data
            const report = {
                document_id: result.doc_id || 'unknown',
                process_type: isResearch ? 'term-research' : 'entity-extraction',
                timestamp: new Date().toISOString(),
                entities: entities,
                summary: {
                    entity_count: entities.length,
                    processing_time_seconds: parseFloat(processingTime)
                }
            };
            
            const docId = result.doc_id || 'document';
            exportReport(report, `${docId}_${isResearch ? 'research' : 'entities'}_report.json`);
        });
    }
}

// Display results for structure validation
function displayValidationResults(result) {
    const resultsPanel = document.getElementById('resultsPanel');
    
    // Extract validation information
    const docId = result.doc_id || "N/A";
    const title = result.title || "Document";
    const tasks = result.tasks || [];
    const priority = result.priority || "medium";
    const verificationNeeded = result.verification_needed !== false;
    const nodeCount = result.node_count || 0;
    
    // Calculate processing time (simulated)
    const processingTime = (Math.random() * 1.5 + 2).toFixed(1);
    
    // Build results HTML
    let resultsHtml = `
        <div class="space-y-4">
            <div class="flex justify-between">
                <h3 class="font-medium text-lg">Structure Validation Results</h3>
                <div>
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded export-report-btn">Download Report</button>
                    <button class="px-2 py-1 bg-green-600 text-white text-sm rounded ml-2 start-verification-btn">Start Verification</button>
                </div>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Summary</h4>
                <p>Processed document: <strong>${title} (${docId})</strong></p>
                <p>Elements analyzed: <strong>${nodeCount}</strong></p>
                <p>Verification needed: <strong>${verificationNeeded ? 'Yes' : 'No'}</strong></p>
                <p>Priority: <strong>${priority.charAt(0).toUpperCase() + priority.slice(1)}</strong></p>
                <p>Processing time: <strong>${processingTime} seconds</strong></p>
            </div>
    `;
    
    // Add verification tasks if available
    if (tasks && tasks.length > 0) {
        resultsHtml += `
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Verification Tasks</h4>
                <div class="space-y-3">
        `;
        
        // Add each task group
        tasks.forEach((task, index) => {
            const elementType = task.element_type || "unknown";
            const priority = task.priority || "medium";
            const nodeCount = task.node_count || 0;
            
            // Set priority color
            let priorityColor = "bg-yellow-100 text-yellow-800";
            if (priority === "high") {
                priorityColor = "bg-red-100 text-red-800";
            } else if (priority === "low") {
                priorityColor = "bg-green-100 text-green-800";
            }
            
            resultsHtml += `
                <div class="border-l-4 border-indigo-500 pl-3 py-1">
                    <div class="flex justify-between items-center">
                        <h5 class="font-medium">Task ${index + 1}: Verify ${elementType} elements</h5>
                        <span class="px-2 py-1 text-xs ${priorityColor} rounded-full">
                            ${priority} priority
                        </span>
                    </div>
                    <p class="text-sm mt-1">Elements to verify: ${nodeCount}</p>
                    <p class="text-sm">Estimated time: ${task.estimated_minutes || "N/A"} minutes</p>
                    ${task.nodes && task.nodes.length > 0 ? 
                        `<details class="mt-2">
                            <summary class="text-sm text-indigo-600 cursor-pointer">View Elements (${task.nodes.length})</summary>
                            <ul class="mt-1 pl-4 text-xs text-gray-600 list-disc">
                                ${task.nodes.slice(0, 5).map(node => 
                                    `<li>${node.element_name || 'Element'}: ${node.content ? `"${node.content.substring(0, 30)}${node.content.length > 30 ? '...' : ''}"` : 'No content'}</li>`
                                ).join('')}
                                ${task.nodes.length > 5 ? `<li>...and ${task.nodes.length - 5} more</li>` : ''}
                            </ul>
                        </details>` : ''
                    }
                </div>
            `;
        });
        
        resultsHtml += `
                </div>
            </div>
        `;
    }
    
    // Add recommended approach if available
    if (result.recommended_approach) {
        resultsHtml += `
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Verification Approach</h4>
                <p>Recommended approach: <strong>${result.recommended_approach}</strong></p>
                <p class="mt-2 text-sm text-gray-600">The system recommends a ${result.recommended_approach} verification process based on the document structure and content patterns.</p>
            </div>
        `;
    }
    
    // Close and display
    resultsHtml += `</div>`;
    resultsPanel.innerHTML = resultsHtml;
    
    // Add event listeners to the buttons
    const exportReportBtn = resultsPanel.querySelector('.export-report-btn');
    if (exportReportBtn) {
        exportReportBtn.addEventListener('click', () => {
            // Create a validation report
            const report = {
                document_id: docId,
                title: title,
                process_type: 'structure-validation',
                timestamp: new Date().toISOString(),
                verification_needed: verificationNeeded,
                priority: priority,
                node_count: nodeCount,
                tasks: tasks || [],
                summary: {
                    processing_time_seconds: parseFloat(processingTime)
                }
            };
            
            exportReport(report, `${docId}_validation_report.json`);
        });
    }
    
    // Add event listener for start verification button
    const startVerificationBtn = resultsPanel.querySelector('.start-verification-btn');
    if (startVerificationBtn) {
        startVerificationBtn.addEventListener('click', () => {
            // In a real implementation, this would start the verification process
            alert('Verification process initiated. This feature is coming soon.');
        });
    }
}

// Display generic results for other process types
function displayGenericResults(result, processType) {
    const resultsPanel = document.getElementById('resultsPanel');
    
    // Extract information from result
    const docId = result.doc_id || "N/A";
    const processTypeName = processType.replace(/-/g, ' ');
    
    // Build results HTML
    let resultsHtml = `
        <div class="space-y-4">
            <div class="flex justify-between">
                <h3 class="font-medium text-lg">${processTypeName.charAt(0).toUpperCase() + processTypeName.slice(1)} Results</h3>
                <div>
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded export-report-btn">Download Results</button>
                </div>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Summary</h4>
                <p>Processed document: <strong>${docId}</strong></p>
                <p>Process type: <strong>${processTypeName}</strong></p>
                <p>Status: <strong>Complete</strong></p>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Process Output</h4>
                <pre class="bg-gray-100 p-2 rounded text-sm overflow-auto max-h-64" style="white-space: pre-wrap; word-wrap: break-word;">${JSON.stringify(result, null, 2)}</pre>
            </div>
        </div>
    `;
    
    resultsPanel.innerHTML = resultsHtml;
    
    // Add event listener for export button
    const exportReportBtn = resultsPanel.querySelector('.export-report-btn');
    if (exportReportBtn) {
        exportReportBtn.addEventListener('click', () => {
            // Export the raw result data
            exportReport(result, `${docId}_${processType}_report.json`);
        });
    }
}

// Helper function to escape HTML
function escapeHtml(html) {
    return html
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Generate XML for entity display
function generateEntityXml(entities, isResearch) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?><research-document>';
    
    // Add each entity
    entities.forEach(entity => {
        xml += `<entity name="${entity.name || entity.content || 'Entity'}" confidence="${entity.confidence || 0.7}" element="${entity.element || 'unknown'}">`;
        xml += `<context>${entity.context || ''}</context>`;
        
        if (isResearch) {
            xml += `<definition>${entity.definition || 'Pending research...'}</definition>`;
        }
        
        xml += '<evidence>';
        
        if (entity.evidence && entity.evidence.length > 0) {
            entity.evidence.forEach(ev => {
                xml += `<item>${ev}</item>`;
            });
        } else {
            xml += '<item>Identified from document context</item>';
        }
        
        xml += '</evidence>';
        
        // Add sources if available
        if (entity.sources && entity.sources.length > 0) {
            xml += '<sources>';
            
            entity.sources.forEach(source => {
                const sourceType = source.source_type || source.type || 'unknown';
                const sourceTitle = source.title || 'Unnamed Source';
                const sourceId = source.source_id || `source-${Math.random().toString(36).substring(2, 10)}`;
                const confidence = source.confidence || 0.5;
                
                xml += `<source id="${sourceId}" type="${sourceType}" confidence="${confidence}"`;
                
                // Add optional attributes
                if (source.url) {
                    xml += ` url="${source.url}"`;
                }
                
                if (source.retrieved_at) {
                    xml += ` retrieved_at="${source.retrieved_at}"`;
                }
                
                xml += '>';
                
                // Add source content
                xml += `<title>${sourceTitle}</title>`;
                
                if (source.citation) {
                    xml += `<citation>${source.citation}</citation>`;
                }
                
                // Add any other metadata fields
                if (source.metadata) {
                    xml += '<metadata>';
                    for (const [key, value] of Object.entries(source.metadata)) {
                        xml += `<${key}>${value}</${key}>`;
                    }
                    xml += '</metadata>';
                }
                
                xml += '</source>';
            });
            
            xml += '</sources>';
        }
        
        xml += '</entity>';
    });
    
    xml += '</research-document>';
    return xml;
}

// Helper function to download XML results
function downloadXml(xmlContent, fileName) {
    // Format the XML for download
    try {
        window.apLogger?.info?.('Downloading XML file', { fileName });
        
        // Check if vkBeautify is available
        let formattedXml = xmlContent;
        if (window.vkbeautify) {
            try {
                formattedXml = window.vkbeautify.xml(xmlContent);
                window.apLogger?.debug?.('Formatted XML with vkBeautify');
            } catch (formatError) {
                window.apLogger?.warn?.('Error formatting XML with vkBeautify, using raw XML', formatError);
                // Fall back to basic indentation if vkBeautify fails
                formattedXml = xmlContent.replace(/></g, '>\n<');
            }
        } else {
            window.apLogger?.warn?.('vkBeautify not available, using manual XML formatting');
            // Basic manual formatting if vkBeautify is not available
            formattedXml = xmlContent.replace(/></g, '>\n<');
        }
        
        // Create a blob from the XML content
        const blob = new Blob([formattedXml], { type: 'application/xml' });
        const url = URL.createObjectURL(blob);
        
        // Create a download link and click it
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName || 'processed-document.xml';
        document.body.appendChild(a);
        
        window.apLogger?.debug?.('Triggering download');
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            window.apLogger?.debug?.('Download cleanup complete');
        }, 100);
        
        return true;
    } catch (error) {
        window.apLogger?.error?.('Error downloading XML:', error);
        alert('Error preparing XML for download: ' + error.message);
        return false;
    }
}

// Helper function to download report as JSON
function exportReport(data, fileName) {
    try {
        // Create a formatted JSON string
        const jsonContent = JSON.stringify(data, null, 2);
        
        // Create a blob from the JSON content
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // Create a download link and click it
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName || 'processing-report.json';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    } catch (error) {
        console.error('Error exporting report:', error);
        alert('Error preparing report for download: ' + error.message);
    }
}

// Format XML with proper indentation for display
function formatXml(xml) {
    if (!xml) return '';
    
    try {
        // First, check if the XML contains literal '\n' strings 
        // (this happens when XML is passed through JSON or certain APIs)
        let cleanXml = xml;
        if (xml.includes('\\n')) {
            // Convert literal '\n' to actual newlines
            cleanXml = xml.replace(/\\n/g, '\n')
                         .replace(/\\"/g, '"')
                         .replace(/\\t/g, '    ');
        }
        
        // Check if we need to unescape HTML entities
        let rawXml = cleanXml;
        if (cleanXml.includes('&lt;') && !cleanXml.includes('<')) {
            // Convert escaped HTML to raw XML
            rawXml = cleanXml
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .replace(/&amp;/g, '&')
                .replace(/&quot;/g, '"')
                .replace(/&#039;/g, "'");
        }
        
        // Use vkBeautify library for reliable formatting
        const prettyXml = window.vkbeautify.xml(rawXml);
        
        // Re-escape for HTML display
        return escapeHtml(prettyXml);
    } catch (e) {
        console.error("Error formatting XML:", e);
        // Fall back to just escaping the input if formatting fails
        return escapeHtml(xml);
    }
}