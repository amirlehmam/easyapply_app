// Global variables
let configEditor = null;
let statusFilter = 'all';
let logs = [];
let expandedRows = new Set();
let dark = localStorage.getItem('darkMode') === 'true';
let refreshInterval = null;
let autoRefresh = localStorage.getItem('autoRefresh') !== 'false';

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set initial dark mode
    setDarkMode(dark);
    
    // Initialize Monaco Editor for config
    initMonacoEditor();
    
    // Initialize tabs
    initTabs();
    
    // Initialize bot controls
    initBotControls();
    
    // Initialize dashboard
    initDashboard();
    
    // Check the bot status initially
    checkBotStatus();
    
    // Set up auto-refresh
    document.getElementById('autoRefresh').checked = autoRefresh;
    if (autoRefresh) {
        startAutoRefresh();
    }
});

// Initialize Monaco Editor
function initMonacoEditor() {
    // Set the container height explicitly to avoid 5px bug
    const editorContainer = document.getElementById('config-editor');
    editorContainer.style.height = '60vh'; // or 70vh as needed
    editorContainer.style.minHeight = '400px';
    editorContainer.style.maxHeight = '80vh';
    editorContainer.style.width = '100%';

    // Try to load Monaco from CDN, fallback to error message if fails
    function loadMonaco() {
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            fetch('/api/config')
                .then(response => response.json())
                .then(config => {
                    // Convert config object to YAML string
                    const yamlString = configToYaml(config);

                    // Create Monaco editor
                    configEditor = monaco.editor.create(editorContainer, {
                        value: yamlString,
                        language: 'yaml',
                        theme: dark ? 'vs-dark' : 'vs',
                        automaticLayout: true,
                        fontSize: 14,
                        tabSize: 2,
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                    });

                    // Set up save button
                    document.getElementById('saveConfig').addEventListener('click', saveConfig);
                })
                .catch(error => {
                    console.error('Error loading configuration:', error);
                    editorContainer.textContent = 'Error loading configuration.';
                });
        }, function(err) {
            editorContainer.textContent = 'Failed to load Monaco Editor. Please check your connection or try again.';
        });
    }

    // If require is not loaded, show error
    if (typeof require === 'undefined') {
        editorContainer.textContent = 'Monaco Editor loader not found. Please check your network or CDN settings.';
        return;
    }
    loadMonaco();
}

// Initialize tab functionality
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Deactivate all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('border-blue-500', 'text-blue-600');
                btn.classList.add('border-transparent', 'text-gray-500');
            });
            
            // Activate clicked button
            button.classList.remove('border-transparent', 'text-gray-500');
            button.classList.add('border-blue-500', 'text-blue-600');
            
            // Hide all content
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // Show corresponding content
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
            
            // Save tab state
            localStorage.setItem('activeTab', tabId);
            
            // Resize editor if switching to config tab
            if (tabId === 'config' && configEditor) {
                configEditor.layout();
            }
        });
    });
    
    // Restore last active tab
    const activeTab = localStorage.getItem('activeTab');
    if (activeTab) {
        document.querySelector(`.tab-button[data-tab="${activeTab}"]`)?.click();
    }
}

// Initialize bot control functionality
function initBotControls() {
    document.getElementById('startBot').addEventListener('click', startBot);
    document.getElementById('stopBot').addEventListener('click', stopBot);
    
    // Toggle dark mode
    document.getElementById('toggleDark').addEventListener('click', () => {
        setDarkMode(!dark);
    });
}

// Initialize dashboard functionality
function initDashboard() {
    // Set up status filter buttons
    document.querySelectorAll('.status-filter').forEach(btn => {
        btn.addEventListener('click', function() {
            statusFilter = this.getAttribute('data-status');
            document.querySelectorAll('.status-filter').forEach(b => {
                b.classList.remove('ring-2', 'ring-blue-500');
            });
            this.classList.add('ring-2', 'ring-blue-500');
            renderTable();
        });
    });
    
    // Set up search functionality
    document.getElementById('searchInput').addEventListener('input', renderTable);
    
    // Set up auto-refresh toggle
    document.getElementById('autoRefresh').addEventListener('change', function() {
        autoRefresh = this.checked;
        localStorage.setItem('autoRefresh', autoRefresh);
        if (autoRefresh) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Set up export buttons
    document.getElementById('exportCSV').addEventListener('click', () => exportLogs('csv'));
    document.getElementById('exportJSON').addEventListener('click', () => exportLogs('json'));
    
    // Load logs initially
    loadLogs();
}

// Set dark mode
function setDarkMode(isDark) {
    dark = isDark;
    document.body.classList.toggle('dark', dark);
    localStorage.setItem('darkMode', dark);
    
    // Update editor theme if it exists
    if (configEditor) {
        monaco.editor.setTheme(dark ? 'vs-dark' : 'vs');
    }
}

// Start auto-refresh
function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    refreshInterval = setInterval(() => {
        const activeTab = document.querySelector('.tab-content.active').id;
        if (activeTab === 'dashboard-tab') {
            loadLogs();
        } else if (activeTab === 'control-tab') {
            checkBotStatus();
        }
    }, 5000); // Refresh every 5 seconds
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Load logs from API
function loadLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            logs = data;
            renderStats();
            renderTable();
            document.getElementById('lastUpdated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
        })
        .catch(error => {
            console.error('Error loading logs:', error);
            document.getElementById('lastUpdated').textContent = 'Error loading logs.';
        });
}

// Render statistics
function renderStats() {
    const stats = {success: 0, failed: 0, timeout: 0, skipped: 0};
    logs.forEach(l => { 
        if (l.status && stats.hasOwnProperty(l.status.toLowerCase())) {
            stats[l.status.toLowerCase()]++;
        }
    });
    
    const total = logs.length;
    const successRate = total ? Math.round((stats.success/total)*100) : 0;
    
    document.getElementById('stats').innerHTML = `
        <div class="rounded bg-green-100 dark:bg-green-900/30 p-3">
            <div class="text-2xl font-bold">${stats.success}</div>
            <div class="text-xs uppercase">Success</div>
        </div>
        <div class="rounded bg-red-100 dark:bg-red-900/30 p-3">
            <div class="text-2xl font-bold">${stats.failed}</div>
            <div class="text-xs uppercase">Failed</div>
        </div>
        <div class="rounded bg-yellow-100 dark:bg-yellow-900/30 p-3">
            <div class="text-2xl font-bold">${stats.timeout}</div>
            <div class="text-xs uppercase">Timeout</div>
        </div>
        <div class="rounded bg-gray-100 dark:bg-gray-700/50 p-3">
            <div class="text-2xl font-bold">${stats.skipped}</div>
            <div class="text-xs uppercase">Skipped</div>
        </div>
        <div class="rounded bg-blue-100 dark:bg-blue-900/30 p-3">
            <div class="text-2xl font-bold">${successRate}%</div>
            <div class="text-xs uppercase">Success Rate</div>
        </div>
    `;
}

// Render log table
function renderTable() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const table = document.getElementById('logTable');
    table.innerHTML = '';
    
    let filtered = logs.filter(l => {
        if (statusFilter !== 'all' && (!l.status || l.status.toLowerCase() !== statusFilter)) {
            return false;
        }
        
        return !search || 
            (l.job_title || '').toLowerCase().includes(search) ||
            (l.company || '').toLowerCase().includes(search) ||
            (l.status || '').toLowerCase().includes(search) ||
            (l.reason || '').toLowerCase().includes(search) ||
            (l.error || '').toLowerCase().includes(search);
    });
    
    // Sort by timestamp, newest first
    filtered.sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));
    
    if (filtered.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="7" class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    No logs matching your criteria.
                </td>
            </tr>
        `;
        return;
    }
    
    filtered.forEach((log, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'log-row';
        tr.innerHTML = `
            <td class="px-4 py-2 whitespace-nowrap">
                <div>${log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">${relativeTime(log.timestamp)}</div>
            </td>
            <td class="px-4 py-2">${log.job_title || 'N/A'}</td>
            <td class="px-4 py-2">${log.company || 'N/A'}</td>
            <td class="px-4 py-2">${log.location || 'N/A'}</td>
            <td class="px-4 py-2"><span class="px-2 py-1 rounded ${statusColor(log.status)}">${log.status || 'N/A'}</span></td>
            <td class="px-4 py-2">${log.reason || log.error || 'N/A'}</td>
            <td class="px-4 py-2">
                <button class="text-blue-600 dark:text-blue-400 hover:underline view-details" data-index="${idx}">
                    View Details
                </button>
            </td>
        `;
        table.appendChild(tr);
    });
    
    // Add event listeners for details buttons
    document.querySelectorAll('.view-details').forEach(btn => {
        btn.addEventListener('click', function() {
            const idx = parseInt(this.getAttribute('data-index'));
            showDetailsModal(filtered[idx]);
        });
    });
}

// Show details modal
function showDetailsModal(log) {
    const modal = document.getElementById('detailsModal');
    const title = document.getElementById('modalTitle');
    const content = document.getElementById('modalContent');
    
    // Set title
    title.textContent = `${log.job_title || 'Job'} at ${log.company || 'Company'}`;
    
    // Build content
    content.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <div class="font-semibold mb-1">Job Link:</div>
                <a href="${log.job_link || '#'}" target="_blank" class="text-blue-500 underline break-all">${log.job_link || 'N/A'}</a>
                
                <div class="mt-2 font-semibold">Status:</div>
                <div><span class="px-2 py-1 rounded ${statusColor(log.status)}">${log.status || 'N/A'}</span></div>
                
                <div class="mt-2 font-semibold">Time:</div>
                <div>${log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}</div>
                
                <div class="mt-2 font-semibold">Time Taken:</div>
                <div>${log.time_taken_sec ? log.time_taken_sec + ' sec' : 'N/A'}</div>
                
                <div class="mt-2 font-semibold">Reason:</div>
                <div>${log.reason || 'N/A'}</div>
            </div>
            <div>
                <div class="font-semibold mb-1">Answers:</div>
                <pre class="bg-gray-100 dark:bg-gray-900 rounded p-2 text-xs overflow-auto">${formatJSON(log.answers)}</pre>
                
                <div class="mt-2 font-semibold">AI Answers:</div>
                <pre class="bg-gray-100 dark:bg-gray-900 rounded p-2 text-xs overflow-auto">${formatJSON(log.ai_answers)}</pre>
                
                <div class="mt-2 font-semibold">Error:</div>
                <div class="text-red-500">${log.error || 'None'}</div>
                
                <div class="mt-2 font-semibold">Screenshot:</div>
                ${log.screenshot ? `<a href="${log.screenshot}" target="_blank" class="text-blue-500 underline break-all">${log.screenshot}</a>` : 'None'}
            </div>
        </div>
    `;
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Set up close button
    document.getElementById('closeModal').onclick = function() {
        modal.classList.add('hidden');
    };
    
    // Close on outside click
    modal.onclick = function(e) {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    };
}

// Format JSON for display
function formatJSON(obj) {
    if (!obj) return 'None';
    try {
        return JSON.stringify(obj, null, 2);
    } catch (e) {
        return String(obj);
    }
}

// Convert config object to YAML string
function configToYaml(obj) {
    // This is a simplified YAML formatter
    if (typeof obj !== 'object' || obj === null) {
        return String(obj);
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => `- ${item}`).join('\n');
    }
    
    let result = '';
    for (const [key, value] of Object.entries(obj)) {
        if (value === null) {
            result += `${key}: null\n`;
        } else if (typeof value === 'object') {
            if (Array.isArray(value)) {
                result += `${key}:\n`;
                value.forEach(item => {
                    result += `  - ${item}\n`;
                });
            } else {
                result += `${key}:\n`;
                const nestedYaml = configToYaml(value);
                result += nestedYaml.split('\n').map(line => `  ${line}`).join('\n') + '\n';
            }
        } else {
            result += `${key}: ${value}\n`;
        }
    }
    return result;
}

// Save config
function saveConfig() {
    const yamlString = configEditor.getValue();
    
    fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ config_yaml: yamlString })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save configuration');
        }
        return response.json();
    })
    .then(data => {
        showMessage('Configuration saved successfully!', 'success');
    })
    .catch(error => {
        console.error('Error saving configuration:', error);
        showMessage('Error saving configuration: ' + error.message, 'error');
    });
}

// Start bot
function startBot() {
    fetch('/api/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'already_running') {
                showMessage('Bot is already running.', 'info');
            } else {
                showMessage('Bot started successfully!', 'success');
            }
            checkBotStatus();
        })
        .catch(error => {
            console.error('Error starting bot:', error);
            showMessage('Error starting bot: ' + error.message, 'error');
        });
}

// Stop bot
function stopBot() {
    fetch('/api/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'not_running') {
                showMessage('Bot is not running.', 'info');
            } else {
                showMessage('Bot stopped successfully!', 'success');
            }
            checkBotStatus();
        })
        .catch(error => {
            console.error('Error stopping bot:', error);
            showMessage('Error stopping bot: ' + error.message, 'error');
        });
}

// Check bot status
function checkBotStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateBotStatus(data);
        })
        .catch(error => {
            console.error('Error checking bot status:', error);
            document.getElementById('botStatusText').textContent = 'Error checking status';
            document.getElementById('botStatusDot').className = 'h-3 w-3 rounded-full mr-2 bg-gray-500';
            document.getElementById('botStatusIndicator').className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
        });
}

// Update bot status UI
function updateBotStatus(data) {
    const statusText = document.getElementById('botStatusText');
    const statusDot = document.getElementById('botStatusDot');
    const statusIndicator = document.getElementById('botStatusIndicator');
    const outputContainer = document.getElementById('output-container');
    
    statusText.textContent = data.status;
    
    if (data.running) {
        statusDot.className = 'h-3 w-3 rounded-full mr-2 bg-green-500';
        statusIndicator.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
        document.getElementById('startBot').disabled = true;
        document.getElementById('startBot').classList.add('opacity-50', 'cursor-not-allowed');
        document.getElementById('stopBot').disabled = false;
        document.getElementById('stopBot').classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
        statusDot.className = 'h-3 w-3 rounded-full mr-2 bg-red-500';
        statusIndicator.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
        document.getElementById('startBot').disabled = false;
        document.getElementById('startBot').classList.remove('opacity-50', 'cursor-not-allowed');
        document.getElementById('stopBot').disabled = true;
        document.getElementById('stopBot').classList.add('opacity-50', 'cursor-not-allowed');
    }
    
    // Update output
    outputContainer.innerHTML = '';
    if (data.output && data.output.length > 0) {
        data.output.forEach(line => {
            const div = document.createElement('div');
            div.textContent = line;
            outputContainer.appendChild(div);
        });
        // Scroll to bottom
        outputContainer.scrollTop = outputContainer.scrollHeight;
    } else {
        outputContainer.textContent = 'No output available.';
    }
}

// Show message
function showMessage(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500'
    };
    
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 ${colors[type]} text-white px-4 py-2 rounded shadow-lg z-50 transition-all duration-300 transform translate-y-0`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Export logs
function exportLogs(format) {
    const search = document.getElementById('searchInput').value.toLowerCase();
    let filtered = logs.filter(l => {
        if (statusFilter !== 'all' && (!l.status || l.status.toLowerCase() !== statusFilter)) {
            return false;
        }
        
        return !search || 
            (l.job_title || '').toLowerCase().includes(search) ||
            (l.company || '').toLowerCase().includes(search) ||
            (l.status || '').toLowerCase().includes(search) ||
            (l.reason || '').toLowerCase().includes(search) ||
            (l.error || '').toLowerCase().includes(search);
    });
    
    if (filtered.length === 0) {
        showMessage('No logs to export.', 'warning');
        return;
    }
    
    let fileContent, fileName, mimeType;
    
    if (format === 'csv') {
        // Generate CSV
        const headers = [
            'Timestamp', 'Job Title', 'Company', 'Location', 'Status', 
            'Reason', 'Error', 'Time Taken', 'Job Link'
        ];
        
        const rows = filtered.map(log => [
            log.timestamp || '',
            log.job_title || '',
            log.company || '',
            log.location || '',
            log.status || '',
            log.reason || '',
            log.error || '',
            log.time_taken_sec || '',
            log.job_link || ''
        ]);
        
        fileContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        ].join('\n');
        
        fileName = `easyapply_logs_${new Date().toISOString().slice(0, 10)}.csv`;
        mimeType = 'text/csv';
    } else {
        // Generate JSON
        fileContent = JSON.stringify(filtered, null, 2);
        fileName = `easyapply_logs_${new Date().toISOString().slice(0, 10)}.json`;
        mimeType = 'application/json';
    }
    
    // Create download link
    const blob = new Blob([fileContent], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 0);
}

// Utility functions
function statusColor(status) {
    switch ((status || '').toLowerCase()) {
        case 'success': return 'bg-green-500 text-white';
        case 'failed': return 'bg-red-500 text-white';
        case 'timeout': return 'bg-yellow-500 text-white';
        case 'skipped': return 'bg-gray-500 text-white';
        default: return 'bg-gray-300 dark:bg-gray-700';
    }
}

function relativeTime(ts) {
    if (!ts) return '';
    const now = Date.now();
    const t = new Date(ts).getTime();
    const diff = Math.floor((now-t)/1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
    return `${Math.floor(diff/86400)}d ago`;
} 