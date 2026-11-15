#!/bin/bash

# Generate Verification Report
# Creates an HTML report of all verification tests

set -e

# Configuration
SERVER_IP=${1:-localhost}
API_PORT=${2:-8000}
OUTPUT_FILE=${3:-verification_report.html}
BASE_URL="http://$SERVER_IP:$API_PORT"

# Create report
cat > "$OUTPUT_FILE" << 'EOFHTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Request System - API Verification Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        
        .header p {
            margin: 5px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.5em;
        }
        
        .summary-card .value {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .status {
            margin-bottom: 40px;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid;
        }
        
        .status.success {
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        
        .status.error {
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }
        
        .status h2 {
            margin: 0 0 10px 0;
        }
        
        .tests {
            margin-top: 40px;
        }
        
        .test {
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .test-header {
            padding: 15px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .test-header:hover {
            background: #e9ecef;
        }
        
        .test-header h3 {
            margin: 0;
            flex: 1;
        }
        
        .test-status {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .test-status.pass {
            background: #d4edda;
            color: #155724;
        }
        
        .test-status.fail {
            background: #f8d7da;
            color: #721c24;
        }
        
        .test-body {
            padding: 20px;
            background: white;
            display: none;
            border-top: 1px solid #ddd;
        }
        
        .test-body.show {
            display: block;
        }
        
        .test-info {
            margin-bottom: 15px;
        }
        
        .test-label {
            font-weight: bold;
            color: #667eea;
            margin-right: 10px;
        }
        
        .response {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        
        .response code {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            color: #333;
        }
        
        .endpoints {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 40px;
        }
        
        .endpoints h2 {
            margin-top: 0;
        }
        
        .endpoints-list {
            display: grid;
            gap: 10px;
        }
        
        .endpoint-link {
            padding: 10px 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            text-decoration: none;
            color: #667eea;
            font-weight: 500;
        }
        
        .endpoint-link:hover {
            background: #e9ecef;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }
        
        .timestamp {
            font-size: 0.9em;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Request System API</h1>
            <p>Remote Verification Report</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <div class="summary-card">
                    <h3>Server</h3>
                    <div class="value" id="server-ip">Loading...</div>
                </div>
                <div class="summary-card">
                    <h3>Tests Run</h3>
                    <div class="value" id="total-tests">0</div>
                </div>
                <div class="summary-card">
                    <h3>Passed</h3>
                    <div class="value" id="passed-tests" style="color: #4ade80;">0</div>
                </div>
                <div class="summary-card">
                    <h3>Failed</h3>
                    <div class="value" id="failed-tests" style="color: #f87171;">0</div>
                </div>
            </div>
            
            <div id="status-container">
                <!-- Status will be inserted here -->
            </div>
            
            <div class="tests" id="tests-container">
                <!-- Tests will be inserted here -->
            </div>
            
            <div class="endpoints">
                <h2>📚 API Endpoints</h2>
                <div class="endpoints-list">
                    <a href="#" class="endpoint-link" id="swagger-link">📖 Swagger UI (Interactive Documentation)</a>
                    <a href="#" class="endpoint-link" id="redoc-link">📚 ReDoc (API Reference)</a>
                    <a href="#" class="endpoint-link" id="openapi-link">⚙️ OpenAPI Schema (openapi.json)</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Request System - Production Ready API</p>
            <p class="timestamp" id="timestamp">Generated: </p>
        </div>
    </div>
    
    <script>
        // Set timestamp
        document.getElementById('timestamp').textContent = 'Generated: ' + new Date().toLocaleString();
        
        // Set server IP
        const urlParams = new URLSearchParams(window.location.search);
        const serverIp = urlParams.get('server') || 'localhost:8000';
        document.getElementById('server-ip').textContent = serverIp;
        
        // Update links
        const baseUrl = 'http://' + serverIp;
        document.getElementById('swagger-link').href = baseUrl + '/docs';
        document.getElementById('redoc-link').href = baseUrl + '/redoc';
        document.getElementById('openapi-link').href = baseUrl + '/openapi.json';
        
        // Test data (would be inserted by script)
        const tests = TESTS_DATA_HERE;
        const passed = tests.filter(t => t.pass).length;
        const failed = tests.filter(t => !t.pass).length;
        
        // Update summary
        document.getElementById('total-tests').textContent = tests.length;
        document.getElementById('passed-tests').textContent = passed;
        document.getElementById('failed-tests').textContent = failed;
        
        // Render status
        const statusHtml = failed === 0 
            ? '<div class="status success"><h2>✅ All Tests Passed</h2><p>Application is running correctly and all endpoints are functional.</p></div>'
            : '<div class="status error"><h2>❌ Some Tests Failed</h2><p>Please review the failed tests below.</p></div>';
        document.getElementById('status-container').innerHTML = statusHtml;
        
        // Render tests
        const testsHtml = tests.map((test, idx) => `
            <div class="test">
                <div class="test-header" onclick="this.nextElementSibling.classList.toggle('show')">
                    <h3>${idx + 1}. ${test.name}</h3>
                    <span class="test-status ${test.pass ? 'pass' : 'fail'}">
                        ${test.pass ? '✅ PASS' : '❌ FAIL'}
                    </span>
                </div>
                <div class="test-body">
                    <div class="test-info">
                        <span class="test-label">Method:</span> ${test.method}
                    </div>
                    <div class="test-info">
                        <span class="test-label">Endpoint:</span> ${test.endpoint}
                    </div>
                    <div class="test-info">
                        <span class="test-label">Status Code:</span> ${test.statusCode}
                    </div>
                    <div class="test-info">
                        <span class="test-label">Response:</span>
                        <div class="response"><code>${escapeHtml(test.response)}</code></div>
                    </div>
                </div>
            </div>
        `).join('');
        
        document.getElementById('tests-container').innerHTML = testsHtml;
        
        // Helper function to escape HTML
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
    </script>
</body>
</html>
EOFHTML

echo -e "Report generated: ${GREEN}$OUTPUT_FILE${NC}"
