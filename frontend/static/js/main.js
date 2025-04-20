// Simple script for testing static file serving
console.log('Main.js loaded successfully');

// Add a simple message to the page
document.addEventListener('DOMContentLoaded', function() {
    const rootElement = document.getElementById('root');
    if (rootElement) {
        rootElement.innerHTML = `
            <div style="padding: 20px; max-width: 800px; margin: 0 auto;">
                <h1 style="color: #4b5563;">Agent Provocateur</h1>
                <div style="background-color: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h2 style="color: #1f2937;">Static File Test</h2>
                    <p>If you can see this message, the static file server is working correctly.</p>
                    <p>Backend URL: ${window.BACKEND_URL || 'Not defined'}</p>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <button id="testBackendBtn" style="background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                            Test Backend Connection
                        </button>
                        <button id="testXmlBtn" style="background-color: #10b981; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                            Test XML Documents
                        </button>
                    </div>
                    <div id="backendResult" style="margin-top: 20px; background-color: #f9fafb; padding: 10px; border-radius: 4px; max-height: 400px; overflow-y: auto;"></div>
                </div>
            </div>
        `;

        // Add event listeners for the buttons
        const testButton = document.getElementById('testBackendBtn');
        if (testButton) {
            testButton.addEventListener('click', async function() {
                const resultElement = document.getElementById('backendResult');
                resultElement.innerHTML = '<p>Testing connection...</p>';

                try {
                    const response = await fetch(`${window.BACKEND_URL}/documents`);
                    if (response.ok) {
                        const data = await response.json();
                        resultElement.innerHTML = `
                            <p style="color: green;">Connection successful!</p>
                            <p>Found ${data.length} documents.</p>
                            <pre style="background-color: #f3f4f6; padding: 10px; overflow: auto;">${JSON.stringify(data, null, 2)}</pre>
                        `;
                    } else {
                        resultElement.innerHTML = `
                            <p style="color: red;">Connection failed: ${response.status} ${response.statusText}</p>
                        `;
                    }
                } catch (error) {
                    resultElement.innerHTML = `
                        <p style="color: red;">Error: ${error.message}</p>
                        <p>Make sure the backend server is running at ${window.BACKEND_URL}</p>
                    `;
                }
            });
        }

        // Add listener for XML documents button
        const xmlButton = document.getElementById('testXmlBtn');
        if (xmlButton) {
            xmlButton.addEventListener('click', async function() {
                const resultElement = document.getElementById('backendResult');
                resultElement.innerHTML = '<p>Loading XML documents...</p>';

                try {
                    // Log request for debugging
                    console.log(`Fetching from: ${window.BACKEND_URL}/documents`);
                    resultElement.innerHTML += `<p>Fetching from: ${window.BACKEND_URL}/documents</p>`;
                    
                    // First try just listing all documents
                    const allDocsResponse = await fetch(`${window.BACKEND_URL}/documents`);
                    if (!allDocsResponse.ok) {
                        throw new Error(`Failed to fetch all documents: ${allDocsResponse.status} ${allDocsResponse.statusText}`);
                    }
                    
                    const allDocs = await allDocsResponse.json();
                    console.log(`Received ${allDocs.length} documents of all types`);
                    resultElement.innerHTML += `<p>Received ${allDocs.length} documents of all types</p>`;
                    
                    // Extract XML documents by filtering on client side
                    const xmlDocs = allDocs.filter(doc => doc.doc_type === 'xml');
                    console.log(`Found ${xmlDocs.length} XML documents`);
                    resultElement.innerHTML += `<p>Found ${xmlDocs.length} XML documents by filtering</p>`;
                    
                    if (xmlDocs.length === 0) {
                        resultElement.innerHTML = `
                            <p>No XML documents found. Sample XML documents should be available in the default setup.</p>
                            <p>Please check that your backend server contains the sample XML documents.</p>
                        `;
                        
                        // Show all document types to help with troubleshooting
                        if (allDocs.length > 0) {
                            resultElement.innerHTML += `
                                <h4>All Available Document Types:</h4>
                                <ul>
                                    ${Array.from(new Set(allDocs.map(doc => doc.doc_type))).map(type => 
                                        `<li>${type}: ${allDocs.filter(doc => doc.doc_type === type).length} documents</li>`
                                    ).join('')}
                                </ul>
                            `;
                        }
                        
                        return;
                    }
                    
                    // Display XML document list
                    let html = `
                        <h3 style="margin-top: 0;">XML Documents (${xmlDocs.length})</h3>
                        <div style="display: grid; gap: 10px;">
                    `;
                    
                    for (const doc of xmlDocs) {
                        html += `
                            <div style="border: 1px solid #e5e7eb; padding: 10px; border-radius: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                    <strong>${doc.title}</strong>
                                    <span style="font-size: 0.8em; color: #6b7280;">ID: ${doc.doc_id}</span>
                                </div>
                                <div style="display: flex; gap: 5px; margin-top: 5px;">
                                    <button class="view-content-btn" data-id="${doc.doc_id}" style="background-color: #6366f1; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; cursor: pointer;">
                                        View Content
                                    </button>
                                    <button class="view-nodes-btn" data-id="${doc.doc_id}" style="background-color: #8b5cf6; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; cursor: pointer;">
                                        View Nodes
                                    </button>
                                    <button class="simulate-research-btn" data-id="${doc.doc_id}" style="background-color: #ec4899; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; cursor: pointer;">
                                        Simulate Research
                                    </button>
                                </div>
                            </div>
                        `;
                    }
                    
                    html += `</div>`;
                    resultElement.innerHTML = html;
                    
                    // Add event listeners for document buttons
                    document.querySelectorAll('.view-content-btn').forEach(button => {
                        button.addEventListener('click', async function() {
                            const docId = this.dataset.id;
                            resultElement.innerHTML += `<p>Loading content for ${docId}...</p>`;
                            
                            try {
                                console.log(`Fetching XML content from: ${window.BACKEND_URL}/documents/${docId}/xml/content`);
                                resultElement.innerHTML += `<p>Fetching XML content from: ${window.BACKEND_URL}/documents/${docId}/xml/content</p>`;
                                
                                const response = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/content`);
                                console.log(`XML content response status: ${response.status}`);
                                resultElement.innerHTML += `<p>XML content response status: ${response.status}</p>`;
                                
                                if (!response.ok) {
                                    throw new Error(`Failed to fetch content: ${response.status}`);
                                }
                                
                                const content = await response.text();
                                resultElement.innerHTML = `
                                    <h3>XML Content for ${docId}</h3>
                                    <button id="back-to-list" style="background-color: #4b5563; color: white; border: none; padding: 4px 8px; border-radius: 4px; margin-bottom: 10px; cursor: pointer;">
                                        Back to Documents
                                    </button>
                                    <pre style="background-color: #f3f4f6; padding: 10px; overflow: auto; max-height: 300px;">${escapeHtml(content)}</pre>
                                `;
                                
                                document.getElementById('back-to-list').addEventListener('click', function() {
                                    xmlButton.click();
                                });
                            } catch (error) {
                                resultElement.innerHTML += `
                                    <p style="color: red;">Error: ${error.message}</p>
                                `;
                            }
                        });
                    });
                    
                    document.querySelectorAll('.view-nodes-btn').forEach(button => {
                        button.addEventListener('click', async function() {
                            const docId = this.dataset.id;
                            resultElement.innerHTML += `<p>Loading nodes for ${docId}...</p>`;
                            
                            try {
                                console.log(`Fetching XML nodes from: ${window.BACKEND_URL}/documents/${docId}/xml/nodes`);
                                resultElement.innerHTML += `<p>Fetching XML nodes from: ${window.BACKEND_URL}/documents/${docId}/xml/nodes</p>`;
                                
                                const response = await fetch(`${window.BACKEND_URL}/documents/${docId}/xml/nodes`);
                                console.log(`XML nodes response status: ${response.status}`);
                                resultElement.innerHTML += `<p>XML nodes response status: ${response.status}</p>`;
                                
                                if (!response.ok) {
                                    throw new Error(`Failed to fetch nodes: ${response.status}`);
                                }
                                
                                const nodes = await response.json();
                                let nodesHtml = `
                                    <h3>Researchable Nodes for ${docId}</h3>
                                    <button id="back-to-list" style="background-color: #4b5563; color: white; border: none; padding: 4px 8px; border-radius: 4px; margin-bottom: 10px; cursor: pointer;">
                                        Back to Documents
                                    </button>
                                `;
                                
                                if (nodes.length === 0) {
                                    nodesHtml += `<p>No researchable nodes found.</p>`;
                                } else {
                                    nodesHtml += `
                                        <table style="width: 100%; border-collapse: collapse;">
                                            <thead>
                                                <tr style="background-color: #f3f4f6;">
                                                    <th style="text-align: left; padding: 8px; border: 1px solid #e5e7eb;">Element</th>
                                                    <th style="text-align: left; padding: 8px; border: 1px solid #e5e7eb;">XPath</th>
                                                    <th style="text-align: left; padding: 8px; border: 1px solid #e5e7eb;">Content</th>
                                                    <th style="text-align: left; padding: 8px; border: 1px solid #e5e7eb;">Status</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                    `;
                                    
                                    for (const node of nodes) {
                                        nodesHtml += `
                                            <tr>
                                                <td style="padding: 8px; border: 1px solid #e5e7eb;">${node.element_name || 'N/A'}</td>
                                                <td style="padding: 8px; border: 1px solid #e5e7eb; font-family: monospace; font-size: 0.8em;">${node.xpath || 'N/A'}</td>
                                                <td style="padding: 8px; border: 1px solid #e5e7eb;">${node.content || 'N/A'}</td>
                                                <td style="padding: 8px; border: 1px solid #e5e7eb;">
                                                    <span style="display: inline-block; padding: 2px 6px; border-radius: 9999px; font-size: 0.75em; 
                                                        background-color: ${node.verification_status === 'verified' ? '#d1fae5' : '#fef3c7'}; 
                                                        color: ${node.verification_status === 'verified' ? '#065f46' : '#92400e'};">
                                                        ${node.verification_status || 'unknown'}
                                                    </span>
                                                </td>
                                            </tr>
                                        `;
                                    }
                                    
                                    nodesHtml += `
                                            </tbody>
                                        </table>
                                    `;
                                }
                                
                                resultElement.innerHTML = nodesHtml;
                                
                                document.getElementById('back-to-list').addEventListener('click', function() {
                                    xmlButton.click();
                                });
                            } catch (error) {
                                resultElement.innerHTML += `
                                    <p style="color: red;">Error: ${error.message}</p>
                                `;
                            }
                        });
                    });
                    
                    document.querySelectorAll('.simulate-research-btn').forEach(button => {
                        button.addEventListener('click', function() {
                            const docId = this.dataset.id;
                            
                            // Create simulated research results
                            const results = {
                                doc_id: docId,
                                workflow_id: `research_${docId}_${Date.now()}`,
                                summary: "Research completed successfully",
                                entity_count: 5,
                                research_count: 3,
                                enriched_xml: `<?xml version="1.0"?>\n<research-document>\n  <original-content>\n    <!-- Original XML would be here -->\n  </original-content>\n  <research-results>\n    <entity-research entity="Machine Learning" confidence="0.92">\n      <definition>Machine Learning is a subfield of artificial intelligence that focuses on computer algorithms that learn from data.</definition>\n      <sources>\n        <source type="web" url="https://example.com/ml">Machine Learning - Wikipedia</source>\n      </sources>\n    </entity-research>\n    <!-- More entities would be here -->\n  </research-results>\n</research-document>`,
                                research_results: [
                                    {
                                        entity: "Machine Learning",
                                        definition: "Machine Learning is a subfield of artificial intelligence that focuses on computer algorithms that learn from data.",
                                        confidence: 0.92,
                                        sources: [
                                            { type: "web", title: "Machine Learning - Wikipedia", url: "https://example.com/ml" }
                                        ],
                                        original_xpath: "//*[contains(text(), 'machine learning')]"
                                    },
                                    {
                                        entity: "Natural Language Processing",
                                        definition: "Natural Language Processing (NLP) is a field of AI enabling computers to understand and process human language.",
                                        confidence: 0.88,
                                        sources: [
                                            { type: "document", title: "AI Reference Guide", doc_id: "doc1" }
                                        ],
                                        original_xpath: "//*[contains(text(), 'NLP')]"
                                    },
                                    {
                                        entity: "Neural Networks",
                                        definition: "Neural networks are computing systems inspired by the biological neural networks in human brains, designed to recognize patterns.",
                                        confidence: 0.85,
                                        sources: [
                                            { type: "web", title: "Neural Networks Explained", url: "https://example.com/nn" }
                                        ],
                                        original_xpath: "//p[3]"
                                    }
                                ],
                                validation: {
                                    valid: true,
                                    errors: [],
                                    warnings: ["Basic validation only"]
                                }
                            };
                            
                            // Display simulated research results
                            let html = `
                                <h3>Research Results for ${docId}</h3>
                                <button id="back-to-list" style="background-color: #4b5563; color: white; border: none; padding: 4px 8px; border-radius: 4px; margin-bottom: 10px; cursor: pointer;">
                                    Back to Documents
                                </button>
                                
                                <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                    <h4 style="margin-top: 0;">Overview</h4>
                                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                        <div>
                                            <p style="margin: 5px 0; color: #6b7280;">Workflow ID</p>
                                            <p style="margin: 5px 0; font-weight: 500;">${results.workflow_id}</p>
                                        </div>
                                        <div>
                                            <p style="margin: 5px 0; color: #6b7280;">Summary</p>
                                            <p style="margin: 5px 0; font-weight: 500;">${results.summary}</p>
                                        </div>
                                        <div>
                                            <p style="margin: 5px 0; color: #6b7280;">Entities Found</p>
                                            <p style="margin: 5px 0; font-weight: 500;">${results.entity_count}</p>
                                        </div>
                                        <div>
                                            <p style="margin: 5px 0; color: #6b7280;">Entities Researched</p>
                                            <p style="margin: 5px 0; font-weight: 500;">${results.research_count}</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <h4>Research Results</h4>
                                <div style="display: grid; gap: 10px;">
                            `;
                            
                            for (const result of results.research_results) {
                                html += `
                                    <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <h5 style="margin: 0 0 10px 0;">${result.entity}</h5>
                                            <span style="background-color: #ddd6fe; color: #5b21b6; padding: 2px 8px; border-radius: 9999px; font-size: 0.75em;">
                                                ${Math.round(result.confidence * 100)}% confidence
                                            </span>
                                        </div>
                                        <p style="margin: 10px 0;">${result.definition}</p>
                                        
                                        <div style="margin-top: 10px;">
                                            <p style="margin: 5px 0; font-size: 0.85em; color: #6b7280;">Sources:</p>
                                            <ul style="margin: 5px 0; padding-left: 20px; font-size: 0.85em;">
                                                ${result.sources.map(source => `
                                                    <li>${source.type === 'web' 
                                                        ? `<a href="${source.url}" style="color: #4f46e5;">${source.title}</a>` 
                                                        : `${source.title} (${source.type})`
                                                    }</li>
                                                `).join('')}
                                            </ul>
                                        </div>
                                    </div>
                                `;
                            }
                            
                            html += `
                                </div>
                                
                                <h4>Enriched XML</h4>
                                <pre style="background-color: #f3f4f6; padding: 10px; overflow: auto; max-height: 200px; font-size: 0.85em;">${escapeHtml(results.enriched_xml)}</pre>
                            `;
                            
                            resultElement.innerHTML = html;
                            
                            document.getElementById('back-to-list').addEventListener('click', function() {
                                xmlButton.click();
                            });
                        });
                    });
                } catch (error) {
                    resultElement.innerHTML = `
                        <p style="color: red;">Error: ${error.message}</p>
                        <p>Make sure the backend server is running at ${window.BACKEND_URL}</p>
                    `;
                }
            });
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
    }
});