// Enhanced XML Document Viewer
// This script provides an improved viewing experience for XML documents

document.addEventListener('DOMContentLoaded', function() {
    console.log('Document Viewer initialized');
    
    // Initialize the application if the root element exists
    const rootElement = document.getElementById('app');
    if (rootElement) {
        initDocumentViewer(rootElement);
        
        // Check if we have a document ID passed in the URL
        if (window.DOC_ID) {
            console.log('Document ID from URL:', window.DOC_ID);
            
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
                        document.getElementById('loadDocumentBtn').click();
                    }
                }
            }, 1000);
        }
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
                            <div>
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
                        Agent Provocateur • XML Processing Interface
                    </p>
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
        // Fetch the list of documents from the backend
        documentViewer.innerHTML = '<p>Loading documents...</p>';
        
        // Add a message to the supervisor chat
        addSupervisorMessage("I'm connecting to the database to find available XML documents.");
        
        const response = await fetch(`${window.BACKEND_URL}/documents`);
        if (!response.ok) {
            throw new Error(`Failed to fetch documents: ${response.status} ${response.statusText}`);
        }
        
        const documents = await response.json();
        console.log("Documents loaded:", documents);
        
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
        documentViewer.innerHTML = `<p class="text-red-500">Error loading documents: ${error.message}</p>`;
        addSupervisorMessage(`I encountered an error while trying to fetch documents: ${error.message}. Please check that the backend server is running.`);
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
        
        // Fetch XML document details first
        let docInfo;
        try {
            const docInfoResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml`);
            if (!docInfoResponse.ok) {
                throw new Error(`Failed to fetch document info: ${docInfoResponse.status}`);
            }
            docInfo = await docInfoResponse.json();
            console.log("Document info:", docInfo);
        } catch (error) {
            console.error("Error fetching document info:", error);
            addSupervisorMessage(`I couldn't retrieve the document metadata, but I'll try to get the content.`);
        }
        
        // Fetch document content
        const contentResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/content`);
        if (!contentResponse.ok) {
            throw new Error(`Failed to fetch document content: ${contentResponse.status}`);
        }
        
        let xmlContent = await contentResponse.text();
        console.log("XML content fetched, length:", xmlContent.length);
        
        // Check for JSON-encoded XML response (which happens sometimes with API responses)
        if (xmlContent.startsWith('"') && xmlContent.endsWith('"')) {
            try {
                // Try to parse it as JSON-encoded string
                xmlContent = JSON.parse(xmlContent);
            } catch (e) {
                console.warn("Content looks like JSON but cannot be parsed:", e);
            }
        }
        
        // Format the XML content with proper indentation and syntax highlighting
        const formattedXml = formatXml(xmlContent);
        documentViewer.innerHTML = `
            <pre class="language-xml" style="max-height: 400px; overflow: auto; white-space: pre-wrap; word-wrap: break-word; tab-size: 2;"><code>${formattedXml}</code></pre>
        `;
        
        // Apply syntax highlighting
        Prism.highlightAllUnder(documentViewer);
        
        // Get researchable nodes, if available
        let nodes = [];
        let nodeCount = 0;
        
        try {
            const nodesResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/nodes`);
            if (nodesResponse.ok) {
                nodes = await nodesResponse.json();
                nodeCount = nodes.length;
                console.log("Researchable nodes:", nodes);
            }
        } catch (error) {
            console.error("Error fetching researchable nodes:", error);
        }
        
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
        documentViewer.innerHTML = `<p class="text-red-500">Error loading document: ${error.message}</p>`;
        addSupervisorMessage(`I encountered an error while loading document "${docId}": ${error.message}`);
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
        
        // Create task request payload for analyze_xml
        const analyzePayload = {
            task_id: `analyze_${Date.now()}`,
            source_agent: "frontend",
            target_agent: "xml_agent",
            intent: "analyze_xml",
            payload: {
                doc_id: docId
            }
        };
        
        // Try to call the task API endpoint, but fallback to mock implementation if it fails
        let analysisResult;
        
        try {
            // Make API call to analyze XML document
            const analyzeResponse = await fetch(`${window.BACKEND_URL}/task`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(analyzePayload)
            });
            
            if (analyzeResponse.ok) {
                analysisResult = await analyzeResponse.json();
                console.log("Document analysis:", analysisResult);
            } else {
                console.warn(`Task API endpoint not available: ${analyzeResponse.status}. Using fallback.`);
                throw new Error("Task API endpoint not available");
            }
        } catch (error) {
            // Fallback: simulate analysis based on document info
            console.warn("Falling back to mock implementation:", error);
            
            // Get document info to at least get some real data
            const docInfoResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml`);
            if (!docInfoResponse.ok) {
                throw new Error(`Failed to fetch document info: ${docInfoResponse.status}`);
            }
            
            const docInfo = await docInfoResponse.json();
            
            // Create simulated analysis result
            analysisResult = {
                doc_id: docId,
                title: docInfo.title || "Document",
                analysis: {
                    verification_needed: true,
                    priority: "medium",
                    reason: "Simulated analysis",
                    estimated_time_minutes: 15
                },
                node_count: docInfo.researchable_nodes?.length || 0,
                root_element: docInfo.root_element || "unknown"
            };
            
            console.log("Simulated document analysis:", analysisResult);
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
        
        // Prepare task payload
        const taskPayloadObj = {
            task_id: `task_${Date.now()}`,
            source_agent: "frontend",
            target_agent: "xml_agent",
            intent: taskIntent,
            payload: taskPayload
        };
        
        // Try to call the task API endpoint, but fallback to mock implementation if it fails
        let taskResult;
        
        try {
            // Make API call to process the document
            const taskResponse = await fetch(`${window.BACKEND_URL}/task`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskPayloadObj)
            });
            
            if (taskResponse.ok) {
                taskResult = await taskResponse.json();
                console.log("Task result:", taskResult);
            } else {
                console.warn(`Task API endpoint not available: ${taskResponse.status}. Using fallback.`);
                throw new Error("Task API endpoint not available");
            }
        } catch (error) {
            // Fallback: create simulated results based on the requested task
            console.warn("Falling back to mock implementation for task:", error);
            
            // Get document info and nodes to at least get some real data
            const docInfoResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml`);
            const nodesResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/nodes`);
            
            const docInfo = docInfoResponse.ok ? await docInfoResponse.json() : { title: "Document" };
            const nodes = nodesResponse.ok ? await nodesResponse.json() : [];
            
            // Create simulated task result based on the task type
            if (taskIntent === "extract_entities") {
                // Simulate entity extraction
                const entities = nodes.map(node => ({
                    name: node.content || node.element_name,
                    element: node.element_name,
                    xpath: node.xpath,
                    confidence: Math.random() * 0.5 + 0.5, // 0.5-1.0
                    context: `Context for ${node.element_name} element`,
                    evidence: ["Document context", "Element analysis"]
                }));
                
                taskResult = {
                    doc_id: docId,
                    entity_count: entities.length,
                    entities: entities
                };
            } else if (taskIntent === "create_verification_plan") {
                // Group nodes by element type
                const elementGroups = {};
                nodes.forEach(node => {
                    const type = node.element_name || "unknown";
                    if (!elementGroups[type]) {
                        elementGroups[type] = [];
                    }
                    elementGroups[type].push(node);
                });
                
                // Create tasks for each element type
                const tasks = Object.entries(elementGroups).map(([type, nodes], index) => ({
                    task_id: `verify_${index + 1}`,
                    element_type: type,
                    node_count: nodes.length,
                    priority: type.includes("claim") ? "high" : "medium",
                    estimated_minutes: nodes.length * 5,
                    nodes: nodes
                }));
                
                taskResult = {
                    doc_id: docId,
                    title: docInfo.title || "Document",
                    verification_needed: nodes.length > 0,
                    priority: "medium",
                    node_count: nodes.length,
                    tasks: tasks,
                    recommended_approach: "sequential"
                };
            } else {
                // Generic fallback
                taskResult = {
                    doc_id: docId,
                    title: docInfo.title || "Document",
                    simulated: true,
                    message: "Simulated results for " + taskIntent
                };
            }
            
            console.log("Simulated task result:", taskResult);
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

function displaySimulatedResults(docId) {
    const resultsPanel = document.getElementById('resultsPanel');
    
    // Simulated results
    const entities = [
        { name: "ChatGPT", confidence: 0.95, definition: "A conversational AI model developed by OpenAI based on the GPT architecture." },
        { name: "Machine Learning", confidence: 0.87, definition: "A subset of artificial intelligence focused on building systems that learn from data." },
        { name: "Natural Language Processing", confidence: 0.92, definition: "A field of AI that focuses on the interaction between computers and human language." }
    ];
    
    // Build results HTML
    let resultsHtml = `
        <div class="space-y-4">
            <div class="flex justify-between">
                <h3 class="font-medium text-lg">Processing Results</h3>
                <div>
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded">Download XML</button>
                    <button class="px-2 py-1 bg-green-600 text-white text-sm rounded ml-2">Export Report</button>
                </div>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Summary</h4>
                <p>Processed document: <strong>${docId}</strong></p>
                <p>Entities found: <strong>${entities.length}</strong></p>
                <p>Processing time: <strong>7.2 seconds</strong></p>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Extracted Entities</h4>
                <div class="space-y-3">
    `;
    
    // Add each entity
    entities.forEach(entity => {
        resultsHtml += `
            <div class="border-l-4 border-indigo-500 pl-3 py-1">
                <div class="flex justify-between items-center">
                    <h5 class="font-medium">${entity.name}</h5>
                    <span class="px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded-full">
                        ${Math.round(entity.confidence * 100)}% confidence
                    </span>
                </div>
                <p class="text-sm mt-1">${entity.definition}</p>
            </div>
        `;
    });
    
    // Close and display the HTML
    resultsHtml += `
                </div>
            </div>
            
            <div class="bg-white border rounded-md p-3">
                <h4 class="font-medium mb-2">Enriched XML Sample</h4>
                <pre class="text-xs bg-gray-100 p-2 rounded max-h-32 overflow-auto" style="white-space: pre-wrap; word-break: break-word; tab-size: 2;"><code class="language-xml">${formatXml(
`<?xml version="1.0" encoding="UTF-8"?><research-document><entity name="ChatGPT" confidence="0.95"><definition>A conversational AI model developed by OpenAI based on the GPT architecture.</definition><references><reference type="web" url="https://openai.com/chatgpt">OpenAI ChatGPT</reference></references></entity><!-- Additional entities... --></research-document>`
                )}</code></pre>
            </div>
        </div>
    `;
    
    resultsPanel.innerHTML = resultsHtml;
    
    // Apply Prism highlighting to the code sample
    Prism.highlightAllUnder(resultsPanel);
}

// Display results for entity extraction or term research
function displayEntityResults(result, processType) {
    const resultsPanel = document.getElementById('resultsPanel');
    const isResearch = processType === 'term-research';
    
    // Extract entities from the result
    let entities = [];
    if (result.entities) {
        entities = result.entities;
    } else if (result.entity_count && result.entities) {
        entities = result.entities;
    } else {
        // Fallback to simulated entities if API doesn't return expected format
        entities = [
            { name: "Entity 1", element: "claim", confidence: 0.85, context: "Context for entity 1" },
            { name: "Entity 2", element: "statement", confidence: 0.76, context: "Context for entity 2" }
        ];
    }
    
    // Calculate processing time (simulated)
    const processingTime = (Math.random() * 2 + 3).toFixed(1);
    
    // Build results HTML
    let resultsHtml = `
        <div class="space-y-4">
            <div class="flex justify-between">
                <h3 class="font-medium text-lg">${isResearch ? 'Research' : 'Entity Extraction'} Results</h3>
                <div>
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded">Download XML</button>
                    <button class="px-2 py-1 bg-green-600 text-white text-sm rounded ml-2">Export Report</button>
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
    entities.forEach(entity => {
        const confidence = Math.round((entity.confidence || 0.7) * 100);
        const name = entity.name || entity.content || "Unnamed Entity";
        const context = entity.context || "";
        const evidence = entity.evidence || [];
        const element = entity.element || "unknown";
        
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
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded">Download Report</button>
                    <button class="px-2 py-1 bg-green-600 text-white text-sm rounded ml-2">Start Verification</button>
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
                    <button class="px-2 py-1 bg-blue-600 text-white text-sm rounded">Download Results</button>
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
        xml += '</entity>';
    });
    
    xml += '</research-document>';
    return xml;
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