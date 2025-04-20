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
                            <div id="documentViewer" class="border rounded-md p-4 bg-gray-50 min-h-[400px] overflow-auto"></div>
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
    
    try {
        // Fetch the list of documents from the backend
        documentViewer.innerHTML = '<p>Loading documents...</p>';
        
        const response = await fetch(`${window.BACKEND_URL}/documents`);
        if (!response.ok) {
            throw new Error(`Failed to fetch documents: ${response.status}`);
        }
        
        const documents = await response.json();
        const xmlDocuments = documents.filter(doc => doc.doc_type === 'xml');
        
        if (xmlDocuments.length === 0) {
            documentViewer.innerHTML = '<p>No XML documents found in the system.</p>';
            return;
        }
        
        // Populate the select dropdown
        xmlDocuments.forEach(doc => {
            const option = document.createElement('option');
            option.value = doc.doc_id;
            option.textContent = `${doc.title} (${doc.doc_id})`;
            selectElement.appendChild(option);
        });
        
        documentViewer.innerHTML = '<p>Select a document from the dropdown and click "Load".</p>';
        
        // Enable the load button
        document.getElementById('loadDocumentBtn').disabled = false;
        
    } catch (error) {
        console.error('Error initializing document selector:', error);
        documentViewer.innerHTML = `<p class="text-red-500">Error loading documents: ${error.message}</p>`;
    }
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
    const supervisorChat = document.getElementById('supervisorChat');
    const resultsPanel = document.getElementById('resultsPanel');
    
    try {
        // Show loading state
        documentViewer.innerHTML = '<p>Loading document...</p>';
        
        // Fetch document content
        const response = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/content`);
        if (!response.ok) {
            throw new Error(`Failed to fetch document: ${response.status}`);
        }
        
        const xmlContent = await response.text();
        
        // Format the XML content with syntax highlighting using Prism.js
        documentViewer.innerHTML = `
            <pre class="language-xml" style="max-height: 400px; overflow: auto;"><code>${escapeHtml(xmlContent)}</code></pre>
        `;
        
        // Apply syntax highlighting
        Prism.highlightAllUnder(documentViewer);
        
        // Add a document info section
        const docInfoResponse = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml`);
        if (docInfoResponse.ok) {
            const docInfo = await docInfoResponse.json();
            const nodeCount = docInfo.researchable_nodes ? docInfo.researchable_nodes.length : 0;
            
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
        
        // Update the supervisor chat
        const newMessage = `
            <div class="bg-indigo-100 p-3 rounded-lg mb-2 max-w-[80%]">
                <p>I've loaded document "${docId}" for you. What would you like to do with this document?</p>
                <p class="text-sm text-indigo-800 mt-1">Options: extract entities, research terms, validate structure</p>
            </div>
        `;
        supervisorChat.insertAdjacentHTML('beforeend', newMessage);
        supervisorChat.scrollTop = supervisorChat.scrollHeight;
        
        // Update results panel
        resultsPanel.innerHTML = `
            <p>Document "${docId}" loaded successfully.</p>
            <p class="text-sm text-gray-500 mt-2">Use the supervisor chat to define your processing goals or click "Start Processing" to use default settings.</p>
        `;
        
    } catch (error) {
        console.error('Error loading document:', error);
        documentViewer.innerHTML = `<p class="text-red-500">Error loading document: ${error.message}</p>`;
    }
}

function sendSupervisorMessage(message) {
    if (!message.trim()) return;
    
    const supervisorChat = document.getElementById('supervisorChat');
    
    // Add user message
    const userMessage = `
        <div class="bg-green-100 p-3 rounded-lg mb-2 max-w-[80%] ml-auto">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    supervisorChat.insertAdjacentHTML('beforeend', userMessage);
    
    // Simulate supervisor response
    setTimeout(() => {
        let response = "I'm processing your request...";
        
        // Simple keyword-based responses
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('extract') && lowerMessage.includes('entit')) {
            response = "I'll help you extract entities from this document. To start the extraction process, click the 'Start Processing' button at the bottom.";
        } else if (lowerMessage.includes('research') || lowerMessage.includes('term')) {
            response = "Research on terms involves identifying key concepts and finding definitions. I'll set that up for you. Ready to begin when you click 'Start Processing'.";
        } else if (lowerMessage.includes('valid') || lowerMessage.includes('structur')) {
            response = "I'll help validate the document structure against schema requirements. This will check for any structural issues or inconsistencies.";
        } else if (lowerMessage.includes('help') || lowerMessage.includes('what') || lowerMessage.includes('how')) {
            response = "I can help you process this XML document in several ways: extracting entities, researching terms, or validating structure. What would you like to do?";
        }
        
        const supervisorResponse = `
            <div class="bg-indigo-100 p-3 rounded-lg mb-2 max-w-[80%]">
                <p>${response}</p>
            </div>
        `;
        supervisorChat.insertAdjacentHTML('beforeend', supervisorResponse);
        supervisorChat.scrollTop = supervisorChat.scrollHeight;
    }, 1000);
}

function startProcessing() {
    const documentViewer = document.getElementById('documentViewer');
    const resultsPanel = document.getElementById('resultsPanel');
    const supervisorChat = document.getElementById('supervisorChat');
    const startBtn = document.getElementById('startProcessingBtn');
    
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
    
    // Simulate processing steps with delays
    const processingSteps = document.getElementById('processingSteps');
    
    setTimeout(() => {
        processingSteps.innerHTML += `<p>✓ Initialized processing</p>`;
        processingSteps.innerHTML += `<p>◽ Analyzing XML structure...</p>`;
    }, 1000);
    
    setTimeout(() => {
        processingSteps.innerHTML += `<p>✓ XML structure analyzed</p>`;
        processingSteps.innerHTML += `<p>◽ Extracting entities...</p>`;
    }, 2500);
    
    setTimeout(() => {
        processingSteps.innerHTML += `<p>✓ Entities extracted</p>`;
        processingSteps.innerHTML += `<p>◽ Conducting research...</p>`;
    }, 4000);
    
    setTimeout(() => {
        processingSteps.innerHTML += `<p>✓ Research completed</p>`;
        processingSteps.innerHTML += `<p>◽ Generating results...</p>`;
    }, 6000);
    
    // Finalize after all steps
    setTimeout(() => {
        processingSteps.innerHTML += `<p>✓ Results generated</p>`;
        
        // Show example results
        displaySimulatedResults(docId);
        
        // Add supervisor message
        const supervisorResponse = `
            <div class="bg-indigo-100 p-3 rounded-lg mb-2 max-w-[80%]">
                <p>I've completed processing the document. You can see the results below. Is there anything specific you'd like me to explain about the findings?</p>
            </div>
        `;
        supervisorChat.insertAdjacentHTML('beforeend', supervisorResponse);
        supervisorChat.scrollTop = supervisorChat.scrollHeight;
        
        // Re-enable the button
        startBtn.disabled = false;
        startBtn.classList.remove('opacity-50');
    }, 7500);
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
                <pre class="text-xs bg-gray-100 p-2 rounded max-h-32 overflow-auto"><code class="language-xml">&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;research-document&gt;
  &lt;entity name="ChatGPT" confidence="0.95"&gt;
    &lt;definition&gt;A conversational AI model developed by OpenAI based on the GPT architecture.&lt;/definition&gt;
    &lt;references&gt;
      &lt;reference type="web" url="https://openai.com/chatgpt"&gt;OpenAI ChatGPT&lt;/reference&gt;
    &lt;/references&gt;
  &lt;/entity&gt;
  &lt;!-- Additional entities... --&gt;
&lt;/research-document&gt;</code></pre>
            </div>
        </div>
    `;
    
    resultsPanel.innerHTML = resultsHtml;
    
    // Apply Prism highlighting to the code sample
    Prism.highlightAllUnder(resultsPanel);
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