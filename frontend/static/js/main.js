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
                    <div>
                        <button id="testBackendBtn" style="background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                            Test Backend Connection
                        </button>
                    </div>
                    <div id="backendResult" style="margin-top: 20px;"></div>
                </div>
            </div>
        `;

        // Add event listener for the button
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
    }
});