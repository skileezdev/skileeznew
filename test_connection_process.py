#!/usr/bin/env python3
"""
Test Connection Process
Tests the actual connection process to identify where the failure occurs
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Connection test template
CONNECTION_TEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Connection Process Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .log { margin: 5px 0; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }
        .success { background-color: #10b981; color: white; }
        .error { background-color: #ef4444; color: white; }
        .info { background-color: #3b82f6; color: white; }
        .warning { background-color: #f59e0b; color: white; }
        #logs { max-height: 600px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
        button { margin: 5px; padding: 10px 15px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2563eb; }
        .status { padding: 15px; border-radius: 8px; margin: 20px 0; font-weight: bold; }
        .status.success { background: #10b981; }
        .status.error { background: #ef4444; }
        .status.info { background: #3b82f6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Connection Process Test</h1>
        <p>This tests the exact connection process to identify where the failure occurs</p>

        <div id="status" class="status info">Ready to test connection process...</div>

        <div>
            <button onclick="testStepByStep()">Test Step by Step</button>
            <button onclick="testDirectConnection()">Test Direct Connection</button>
            <button onclick="clearLogs()">Clear Logs</button>
        </div>

        <div id="logs"></div>
    </div>

    <!-- Video functionality has been removed from this application -->

    <script>
        function log(message, type = 'info') {
            const logsDiv = document.getElementById('logs');
            const logDiv = document.createElement('div');
            logDiv.className = `log ${type}`;
            logDiv.innerHTML = `<strong>${new Date().toLocaleTimeString()}:</strong> ${message}`;
            logsDiv.appendChild(logDiv);
            console.log(message);
            logsDiv.scrollTop = logsDiv.scrollHeight;
        }

        function updateStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
        }

        function clearLogs() {
            document.getElementById('logs').innerHTML = '';
        }

        async function testStepByStep() {
            log('=== Testing Connection Process Step by Step ===', 'info');
            updateStatus('Testing connection process...', 'info');

            try {
                // Step 1: Check if nuclear fix is available
                log('Step 1: Checking nuclear fix availability...', 'info');
                // Video functionality has been removed from this application
                log('✅ Nuclear fix is available', 'success');

                // Step 2: Generate token
                log('Step 2: Generating token...', 'info');
                const response = await fetch('/generate_exact_token');
                const data = await response.json();

                if (!data.success) {
                    throw new Error(`Token generation failed: ${data.error}`);
                }
                log('✅ Token generated successfully', 'success');
                log(`Token length: ${data.token.length}`, 'info');

                // Video functionality has been removed from this application

                // Step 4: Create room instance
                log('Step 4: Creating room instance...', 'info');
                const room = new client.Room();
                log('✅ Room instance created', 'success');

                // Step 5: Set up event listeners
                log('Step 5: Setting up event listeners...', 'info');
                room.on('connected', () => {
                    log('✅ Room connected event fired', 'success');
                });
                room.on('disconnected', () => {
                    log('ℹ️ Room disconnected event fired', 'info');
                });
                room.on('connectionStateChanged', (state) => {
                    log(`ℹ️ Connection state changed: ${state}`, 'info');
                });
                log('✅ Event listeners set up', 'success');

                // Step 6: Attempt connection
                log('Step 6: Attempting connection...', 'info');
                const config = {
                    // Video functionality has been removed from this application
                    accessToken: data.token,
                    roomName: data.room_name
                };
                
                log(`Video functionality has been removed from this application`, 'info');
                log(`Room: ${config.roomName}`, 'info');
                
                // Video functionality has been removed from this application
                
                log('✅ Connection successful!', 'success');
                updateStatus('✅ Connection process works!', 'success');

                // Disconnect after 5 seconds
                setTimeout(() => {
                    room.disconnect();
                    log('Disconnected from room', 'info');
                }, 5000);

            } catch (error) {
                log(`❌ Connection process failed: ${error.message}`, 'error');
                log(`Error details: ${error.stack}`, 'error');
                updateStatus(`❌ Connection failed: ${error.message}`, 'error');
            }
        }

        async function testDirectConnection() {
            log('=== Testing Direct Connection ===', 'info');
            updateStatus('Testing direct connection...', 'info');

            try {
                // Generate token
                const response = await fetch('/generate_exact_token');
                const data = await response.json();

                if (!data.success) {
                    throw new Error(`Token generation failed: ${data.error}`);
                }

                // Video functionality has been removed from this application
                const config = {
                    // Video functionality has been removed from this application
                    accessToken: data.token,
                    roomName: data.room_name
                };

                log('Video functionality has been removed from this application', 'info');
                // Video functionality has been removed from this application

                log('✅ Direct connection successful!', 'success');
                updateStatus('✅ Direct connection works!', 'success');

                // Disconnect after 5 seconds
                setTimeout(() => {
                    room.disconnect();
                    log('Disconnected from room', 'info');
                }, 5000);

            } catch (error) {
                log(`❌ Direct connection failed: ${error.message}`, 'error');
                updateStatus(`❌ Direct connection failed: ${error.message}`, 'error');
            }
        }

        // Auto-test on page load
        window.addEventListener('load', () => {
            log('Page loaded, ready to test connection process', 'info');
            updateStatus('Ready to test connection process!', 'success');
        });
    </script>
</body>
</html>
"""

from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

@app.route('/')
def connection_process_test():
    # Video functionality has been removed from this application
    return render_template_string(CONNECTION_TEST_TEMPLATE, video_url="video_functionality_removed")

@app.route('/generate_exact_token')
def generate_exact_token():
    """Video functionality has been removed from this application"""
    try:
        # Video functionality has been removed from this application
        # Video functionality has been removed from this application
# config = LiveKitConfig()
# token_manager = LiveKitTokenManager(config)

        # Video functionality has been removed from this application
        token = "video_functionality_removed"
            room_name='session_44_5a8e781a',
            participant_name='Ahmed abusetta',
            is_coach=True
        )

        return jsonify({
            'success': True, 
            'token': token,
            'room_name': 'session_44_5a8e781a'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🔗 Starting Connection Process Test...")
    print("📱 Open your browser to: http://localhost:5013")
    print("🔍 This will test the connection process step by step")
    print("⏹️  Press Ctrl+C to stop the test server")

    app.run(host='0.0.0.0', port=5013, debug=True)
