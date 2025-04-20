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
                            XML Processing Interface
                        </h2>
                        <p class="mt-4 text-xl text-gray-500">
                            Process XML documents with intelligent agent supervision
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

                        <!-- XML Research Card -->
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="px-4 py-5 sm:p-6">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                                        </svg>
                                    </div>
                                    <div class="ml-5">
                                        <h3 class="text-lg font-medium text-gray-900">XML Research</h3>
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
                                    <button id="adminConsoleBtn" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
                                        Coming Soon
                                    </button>
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
                        Agent Provocateur • XML Processing Interface
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
    
    document.getElementById('adminConsoleBtn').addEventListener('click', function() {
        alert('This feature is coming soon!');
    });
    
    // Setup file upload handling
    setupFileUpload();
    
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
        
        // Prepare form data with the field names expected by the server
        const formData = new FormData();
        formData.append('title', title); // The server expects 'title'
        formData.append('file', fileUploadInput.files[0]); // The server expects 'file'
        
        console.log('Sending upload with title:', title, 'and file:', fileUploadInput.files[0].name);
        
        // Disable form and show uploading status
        const uploadBtn = document.getElementById('uploadBtn');
        uploadBtn.disabled = true;
        uploadBtn.classList.add('opacity-50');
        uploadStatus.textContent = 'Uploading...';
        
        try {
            console.log('Sending upload request to /documents/upload');
            console.log('Form data:', {
                title: formData.get('title'),
                file: formData.get('file').name
            });
            
            // Send the upload request to the test endpoint first to debug
            console.log('Testing upload with explicit port 3001');
            const testResponse = await fetch('http://localhost:3001/test-upload', {
                method: 'POST',
                body: formData
            });
            
            if (testResponse.ok) {
                const testResult = await testResponse.json();
                console.log('Test upload successful:', testResult);
            } else {
                console.error('Test upload failed:', testResponse.status, testResponse.statusText);
            }
            
            // Now try the real upload endpoint with explicit port 3001
            console.log('Now trying the real endpoint on port 3001');
            // Use absolute URL with port 3001 to avoid connecting to the wrong server
            const response = await fetch('http://localhost:3001/documents/upload', {
                method: 'POST',
                body: formData
            });
            
            console.log('Upload response status:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Show success message
            uploadStatus.textContent = result.simulated ? 
                'Upload successful (simulated - backend may be unavailable)' : 
                'Upload successful!';
            uploadStatus.classList.add('text-green-500');
            uploadStatus.classList.remove('text-gray-500');
            
            console.log('Upload result:', result);
            
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
            
            // Show more detailed error information
            let errorMessage = `Error: ${error.message}`;
            
            // Show additional details about the request
            errorMessage += `\nEndpoint: /documents/upload\nMethod: POST`;
            console.log('Form data being sent:', {
                title: titleInput.value.trim(),
                file: fileUploadInput.files[0] ? fileUploadInput.files[0].name : 'No file'
            });
            
            // Display error in UI
            uploadStatus.textContent = errorMessage;
            uploadStatus.classList.add('text-red-500');
            uploadStatus.classList.remove('text-gray-500');
            
            // Show an alert for better visibility during debugging
            alert(`Upload failed: ${error.message}`);
        } finally {
            // Re-enable form
            uploadBtn.disabled = false;
            uploadBtn.classList.remove('opacity-50');
        }
    });
}

async function loadDocuments() {
    const tableBody = document.getElementById('documentTableBody');
    
    try {
        console.log('Fetching documents with explicit port 3001');
        // Fetch documents from the backend through local server on port 3001
        const response = await fetch(`http://localhost:3001/api/documents`);
        console.log('Documents response status:', response.status);
        if (!response.ok) {
            throw new Error(`Failed to fetch documents: ${response.status}`);
        }
        
        const documents = await response.json();
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
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${doc.title}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${doc.doc_id}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${new Date(doc.created_at).toLocaleString()}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-indigo-600">
                    <a href="/document-viewer?doc=${doc.doc_id}" class="text-indigo-600 hover:text-indigo-900">View</a>
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
        
    } catch (error) {
        console.error('Error loading documents:', error);
        tableBody.innerHTML = `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-red-500 text-center" colspan="4">
                    Error loading documents: ${error.message}
                </td>
            </tr>
        `;
    }
}