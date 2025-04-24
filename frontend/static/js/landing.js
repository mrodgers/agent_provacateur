// Landing page script
document.addEventListener('DOMContentLoaded', function() {
    console.log('Landing page initialized');
    
    // Initialize the application if the root element exists
    const rootElement = document.getElementById('app');
    if (rootElement) {
        initLandingPage(rootElement);
    }
});

async function initLandingPage(rootElement) {
    rootElement.innerHTML = `
        <div class="min-h-screen bg-gray-100 flex flex-col">
            <header class="bg-white shadow-sm">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16 items-center">
                        <div class="flex items-center">
                            <h1 class="text-xl font-bold text-gray-900">Agent Provocateur</h1>
                        </div>
                    </div>
                </div>
            </header>

            <main class="flex-grow py-10">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="text-center mb-12">
                        <h2 class="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                            Writer's Research Assistant
                        </h2>
                        <p class="mt-4 text-xl text-gray-500">
                            Researchd ocuments with intelligent agent supervision
                        </p>
                    </div>

                    <div class="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                        <!-- Document Viewer Card -->
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="px-4 py-5 sm:p-6">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                    </div>
                                    <div class="ml-5">
                                        <h3 class="text-lg font-medium text-gray-900">Document Processing</h3>
                                        <p class="mt-2 text-sm text-gray-500">
                                            Upload, view, and process XML documents
                                        </p>
                                    </div>
                                </div>
                                <div class="mt-6">
                                    <a href="/document-viewer" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                        Open Document Viewer
                                    </a>
                                </div>
                            </div>
                        </div>

                        <!-- Technical Research Card -->
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="px-4 py-5 sm:p-6">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                                        </svg>
                                    </div>
                                    <div class="ml-5">
                                        <h3 class="text-lg font-medium text-gray-900">Technical Research</h3>
                                        <p class="mt-2 text-sm text-gray-500">
                                            Research entities and concepts in XML documents
                                        </p>
                                    </div>
                                </div>
                                <div class="mt-6">
                                    <button id="xmlResearchBtn" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                                        Coming Soon
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Admin Console Card -->
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="px-4 py-5 sm:p-6">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
                                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                    </div>
                                    <div class="ml-5">
                                        <h3 class="text-lg font-medium text-gray-900">Agent Management</h3>
                                        <p class="mt-2 text-sm text-gray-500">
                                            Configure and monitor agent performance
                                        </p>
                                    </div>
                                </div>
                                <div class="mt-6">
                                    <a href="/agent-management" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
                                        Open Agent Management
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Document List -->
                    <!-- Document Upload Section -->
                    <div class="mt-12 bg-white shadow rounded-lg overflow-hidden">
                        <div class="px-4 py-5 sm:px-6 bg-gray-50">
                            <h3 class="text-lg font-medium text-gray-900">Upload XML Document</h3>
                            <p class="mt-1 text-sm text-gray-500">Add a new XML document for processing</p>
                        </div>
                        <div class="px-4 py-5 sm:p-6">
                            <form id="uploadForm" class="space-y-4">
                                <div>
                                    <label for="documentTitle" class="block text-sm font-medium text-gray-700">Document Title</label>
                                    <!-- Changed name to match the FastAPI endpoint's expected field name 'title' -->
                                    <input type="text" name="title" id="documentTitle" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" placeholder="Enter document title">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Upload XML File</label>
                                    <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                                        <div class="space-y-1 text-center">
                                            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                                                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H8m36-24h-4m-8-4v12m0 0l-8-8m8 8l8-8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                            </svg>
                                            <div class="flex text-sm text-gray-600">
                                                <label for="file-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                                                    <span>Upload a file</span>
                                                    <!-- Changed name to match the FastAPI endpoint's expected field name -->
                                                    <input id="file-upload" name="file" type="file" accept=".xml" class="sr-only">
                                                </label>
                                                <p class="pl-1">or drag and drop</p>
                                            </div>
                                            <p class="text-xs text-gray-500">XML up to 10MB</p>
                                        </div>
                                    </div>
                                    <div id="filePreview" class="mt-2 hidden">
                                        <div class="bg-gray-50 p-2 rounded flex items-center justify-between">
                                            <div class="flex items-center space-x-2">
                                                <svg class="h-5 w-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                </svg>
                                                <span id="fileName" class="text-sm text-gray-700"></span>
                                            </div>
                                            <button type="button" id="removeFileBtn" class="text-red-500 hover:text-red-700">
                                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <button type="submit" id="uploadBtn" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                        Upload Document
                                    </button>
                                    <span id="uploadStatus" class="ml-3 text-sm text-gray-500"></span>
                                </div>
                            </form>
                        </div>
                    </div>

                    <!-- Document List Section -->
                    <div class="mt-8 bg-white shadow rounded-lg overflow-hidden">
                        <div class="px-4 py-5 sm:px-6 bg-gray-50">
                            <h3 class="text-lg font-medium text-gray-900">Available Documents</h3>
                            <p class="mt-1 text-sm text-gray-500">XML documents available for processing</p>
                        </div>
                        <div class="px-4 py-5 sm:p-6">
                            <div id="documentList" class="overflow-x-auto">
                                <table class="min-w-full divide-y divide-gray-200">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="documentTableBody" class="bg-white divide-y divide-gray-200">
                                        <tr>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center" colspan="4">
                                                Loading documents...
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
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
                            <span id="build-number" class="font-mono text-amber-400" title="Build identifier">Build: loading...</span>
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

    // Set up event listeners
    setupLandingPageListeners();
    
    // Load documents
    loadDocuments();
}

function setupLandingPageListeners() {
    // Redirect to document viewer
    document.querySelector('a[href="/document-viewer"]').addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/document-viewer';
    });
    
    // Handle "Coming Soon" buttons
    document.getElementById('xmlResearchBtn').addEventListener('click', function() {
        alert('This feature is coming soon!');
    });
    
    // Setup file upload handling
    setupFileUpload();
    
    // Setup port checker button
    document.getElementById('check-ports-btn').addEventListener('click', function() {
        checkSystemPorts();
    });
    
    // Fetch system info to display build number and version
    fetchSystemInfo();
}

// Function to fetch system info including build number
async function fetchSystemInfo() {
    try {
        // Get system info
        const systemInfo = await window.apApi.getSystemInfo();
        
        // Update version information
        if (systemInfo.version) {
            document.getElementById('version-info').textContent = `Version: ${systemInfo.version}`;
        }
        
        // Update build number with highlighting
        if (systemInfo.build_number) {
            const buildElement = document.getElementById('build-number');
            buildElement.textContent = `Build: ${systemInfo.build_number}`;
            buildElement.classList.add('text-amber-400', 'font-mono');
            
            // Add tooltip with timestamp info
            const timestamp = systemInfo.build_number.split('.')[0];
            if (timestamp && timestamp.length === 8) {
                const year = timestamp.substring(0, 4);
                const month = timestamp.substring(4, 6);
                const day = timestamp.substring(6, 8);
                const formattedDate = `${year}-${month}-${day}`;
                buildElement.title = `Build from ${formattedDate}`;
            }
        }
    } catch (error) {
        console.error('Error fetching system info:', error);
        document.getElementById('build-number').textContent = 'Build: unknown';
    }
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
        
        // Fetch port status information from our API endpoint
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
                    
                    <div class="flex flex-col border-b pb-3">
                        <div class="flex justify-between items-center">
                            <span class="font-medium">Build Number</span>
                            <span class="bg-amber-100 text-amber-800 px-2 py-1 rounded text-xs font-mono">
                                ${systemInfo.build_number || 'unknown'}
                            </span>
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                            UI build identifier (format: YYYYMMDD.n)
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

function setupFileUpload() {
    const fileUploadInput = document.getElementById('file-upload');
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const uploadForm = document.getElementById('uploadForm');
    const uploadStatus = document.getElementById('uploadStatus');
    
    // Setup drag and drop
    const dropZone = fileUploadInput.closest('div.flex.justify-center');
    
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('border-indigo-300', 'bg-indigo-50');
    });
    
    dropZone.addEventListener('dragleave', function() {
        dropZone.classList.remove('border-indigo-300', 'bg-indigo-50');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('border-indigo-300', 'bg-indigo-50');
        
        if (e.dataTransfer.files.length) {
            fileUploadInput.files = e.dataTransfer.files;
            updateFilePreview();
        }
    });
    
    // Handle file selection
    fileUploadInput.addEventListener('change', updateFilePreview);
    
    function updateFilePreview() {
        if (fileUploadInput.files.length) {
            const file = fileUploadInput.files[0];
            
            // Check if it's an XML file
            if (!file.name.toLowerCase().endsWith('.xml')) {
                alert('Only XML files are allowed.');
                fileUploadInput.value = '';
                return;
            }
            
            // Display the selected file
            fileName.textContent = file.name;
            filePreview.classList.remove('hidden');
            
            // Auto-fill the title field if it's empty
            const titleInput = document.getElementById('documentTitle');
            if (!titleInput.value) {
                titleInput.value = file.name.replace(/\.xml$/i, '');
            }
        } else {
            filePreview.classList.add('hidden');
        }
    }
    
    // Handle file removal
    removeFileBtn.addEventListener('click', function() {
        fileUploadInput.value = '';
        filePreview.classList.add('hidden');
    });
    
    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const titleInput = document.getElementById('documentTitle');
        const title = titleInput.value.trim();
        
        // Validate input
        if (!title) {
            alert('Please enter a document title.');
            titleInput.focus();
            return;
        }
        
        if (!fileUploadInput.files.length) {
            alert('Please select an XML file to upload.');
            return;
        }
        
        // Get the selected file
        const file = fileUploadInput.files[0];
        
        console.log('Preparing to upload document with title:', title, 'and file:', file.name);
        
        // Disable form and show uploading status
        const uploadBtn = document.getElementById('uploadBtn');
        uploadBtn.disabled = true;
        uploadBtn.classList.add('opacity-50');
        uploadStatus.textContent = 'Uploading...';
        
        try {
            // Use the API client to upload the document
            console.log('Using API client to upload document');
            
            // Call the document API's upload method
            const result = await window.apApi.documents.uploadDocument({
                title: title,
                file: file
            });
            
            console.log('Upload result from API client:', result);
            
            // Handle response based on result
            if (result.error) {
                // Error case - show the error message
                uploadStatus.textContent = result.message || result.error;
                uploadStatus.classList.add('text-red-500');
                uploadStatus.classList.remove('text-gray-500', 'text-green-500', 'text-yellow-500');
                
                // If it's a backend unavailable error but file was saved locally
                if (result.local_only) {
                    uploadStatus.textContent = 'Document saved locally but backend processing unavailable. Will process when backend is up.';
                    uploadStatus.classList.add('text-yellow-500');
                    uploadStatus.classList.remove('text-gray-500', 'text-green-500', 'text-red-500');
                }
            } else {
                // Success case
                uploadStatus.textContent = 'Upload successful!';
                uploadStatus.classList.add('text-green-500');
                uploadStatus.classList.remove('text-gray-500', 'text-red-500', 'text-yellow-500');
            }
            
            // Reset form
            titleInput.value = '';
            fileUploadInput.value = '';
            filePreview.classList.add('hidden');
            
            // Reload document list
            setTimeout(() => {
                loadDocuments();
                uploadStatus.textContent = '';
                uploadStatus.classList.remove('text-green-500');
                uploadStatus.classList.add('text-gray-500');
            }, 2000);
            
        } catch (error) {
            console.error('Error uploading document:', error);
            
            // Format the error using API utils if available
            const formattedError = window.apiUtils?.formatApiError 
                ? window.apiUtils.formatApiError(error, 'Failed to upload document')
                : { message: error.message || 'Unknown error uploading document' };
            
            // Show more detailed error information
            let errorMessage = formattedError.message;
            
            // Display error in UI
            uploadStatus.textContent = errorMessage;
            uploadStatus.classList.add('text-red-500');
            uploadStatus.classList.remove('text-gray-500');
            
            // If this appears to be a network or backend error, provide additional context
            if (formattedError.isNetworkError || formattedError.status === 0) {
                uploadStatus.textContent += ' (Backend server appears to be unavailable)';
            }
            
            console.log('Upload error details:', {
                title: title,
                fileName: file.name,
                errorType: formattedError.status || 'unknown'
            });
            
        } finally {
            // Re-enable form
            uploadBtn.disabled = false;
            uploadBtn.classList.remove('opacity-50');
        }
    });
}

async function loadDocuments() {
    const tableBody = document.getElementById('documentTableBody');
    const docTable = document.getElementById('documentList');
    
    try {
        console.log('Fetching documents using API client');
        
        // Show loading state
        tableBody.innerHTML = `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center" colspan="4">
                    <div class="flex items-center justify-center">
                        <svg class="animate-spin h-5 w-5 mr-3 text-indigo-500" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Loading documents...
                    </div>
                </td>
            </tr>
        `;
        
        // Use API client to fetch documents
        try {
            // Get documents using the API client
            const documents = await window.apApi.documents.getAllDocuments();
            console.log('Documents loaded from API client:', documents);
            
            // Filter for XML documents
            const xmlDocuments = documents.filter(doc => doc.doc_type === 'xml');
            
            if (xmlDocuments.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center" colspan="4">
                            No XML documents found in the system.
                        </td>
                    </tr>
                `;
                return;
            }
            
            // Populate the table
            tableBody.innerHTML = '';
            xmlDocuments.forEach(doc => {
                // Add a local indicator for documents that haven't been synchronized to backend
                const isLocalOnly = doc.local_only === true;
                const syncStatus = isLocalOnly ? 
                    `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        Local Only
                    </span>` : '';
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-gray-900">${doc.title}</div>
                        ${syncStatus}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-500">${doc.doc_id}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-500">${new Date(doc.created_at).toLocaleString()}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-indigo-600">
                        <a href="/document-viewer?doc=${doc.doc_id}" class="text-indigo-600 hover:text-indigo-900">
                            ${isLocalOnly ? 'View (limited)' : 'View'}
                        </a>
                    </td>
                `;
                tableBody.appendChild(row);
            });
            
            // Add event listeners to the view links
            document.querySelectorAll('a[href^="/document-viewer"]').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const url = new URL(this.href);
                    const docId = url.searchParams.get('doc');
                    window.location.href = `/document-viewer?doc=${docId}`;
                });
            });
            
        } catch (apiError) {
            // Handle API client errors
            console.error('API client error:', apiError);
            
            // Format the error using API utils if available
            const formattedError = window.apiUtils?.formatApiError 
                ? window.apiUtils.formatApiError(apiError, 'Failed to load documents')
                : { message: apiError.message || 'Unknown error loading documents' };
            
            const errorMessage = formattedError.message;
            
            // Display user-friendly error message
            tableBody.innerHTML = `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-center" colspan="4">
                        <div class="bg-red-50 border border-red-200 rounded-md p-4">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                                    </svg>
                                </div>
                                <div class="ml-3">
                                    <h3 class="text-sm font-medium text-red-800">Error Loading Documents</h3>
                                    <div class="mt-2 text-sm text-red-700">
                                        <p>${errorMessage}</p>
                                    </div>
                                    <div class="mt-4">
                                        <button type="button" id="retry-load-docs" class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none">
                                            Retry
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            `;
            
            // Check if we have backend status information
            if (formattedError.isNetworkError || formattedError.status === 0) {
                // Add a warning banner above the table indicating backend unavailability
                const warningBanner = document.createElement('div');
                warningBanner.className = 'bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4';
                warningBanner.innerHTML = `
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-yellow-700">
                                Backend server appears to be unavailable. Check your connection or try again later.
                                <button id="refresh-docs" class="font-medium underline text-yellow-700 hover:text-yellow-600">
                                    Refresh
                                </button>
                            </p>
                        </div>
                    </div>
                `;
                
                docTable.parentNode.insertBefore(warningBanner, docTable);
                
                // Add refresh button handler
                document.getElementById('refresh-docs')?.addEventListener('click', () => {
                    // Remove the warning banner
                    warningBanner.remove();
                    // Reload documents
                    loadDocuments();
                });
            }
            
            // Add retry button handler
            document.getElementById('retry-load-docs')?.addEventListener('click', () => loadDocuments());
        }
        
    } catch (error) {
        console.error('Unexpected error loading documents:', error);
        tableBody.innerHTML = `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-center" colspan="4">
                    <div class="bg-red-50 border border-red-200 rounded-md p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                                </svg>
                            </div>
                            <div class="ml-3">
                                <h3 class="text-sm font-medium text-red-800">Error Loading Documents</h3>
                                <div class="mt-2 text-sm text-red-700">
                                    <p>${error.message || 'Unknown error'}</p>
                                </div>
                                <div class="mt-4">
                                    <button type="button" id="retry-load-docs" class="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none">
                                        Retry
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        `;
        
        // Add retry button handler
        document.getElementById('retry-load-docs')?.addEventListener('click', () => loadDocuments());
    }
}