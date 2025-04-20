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
                    <div class="mt-12 bg-white shadow rounded-lg overflow-hidden">
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
}

async function loadDocuments() {
    const tableBody = document.getElementById('documentTableBody');
    
    try {
        // Fetch documents from the backend
        const response = await fetch(`${window.BACKEND_URL}/documents`);
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