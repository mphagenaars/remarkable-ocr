/**
 * Remarkable OCR - Frontend JavaScript
 * Handles email configuration form and connectivity testing
 */

document.addEventListener('DOMContentLoaded', function() {
    const configForm = document.getElementById('config-form');
    const statusContainer = document.getElementById('status-message');
    const testButton = document.getElementById('test-btn');
    let currentEmail = null;
    let pollingActive = false;
    
    // Pre-fill common provider settings
    const providerPresets = {
        'gmail.com': {
            imap_server: 'imap.gmail.com',
            imap_port: 993,
            smtp_server: 'smtp.gmail.com',
            smtp_port: 587
        },
        'outlook.com': {
            imap_server: 'outlook.office365.com',
            imap_port: 993,
            smtp_server: 'smtp-mail.outlook.com',
            smtp_port: 587
        },
        'hotmail.com': {
            imap_server: 'outlook.office365.com',
            imap_port: 993,
            smtp_server: 'smtp-mail.outlook.com',
            smtp_port: 587
        },
        'yahoo.com': {
            imap_server: 'imap.mail.yahoo.com',
            imap_port: 993,
            smtp_server: 'smtp.mail.yahoo.com',
            smtp_port: 587
        },
        'zohomail.eu': {
            imap_server: 'imap.zoho.eu',
            imap_port: 993,
            smtp_server: 'smtp.zoho.eu',
            smtp_port: 587
        },
        'zoho.com': {
            imap_server: 'imap.zoho.com',
            imap_port: 993,
            smtp_server: 'smtp.zoho.com',
            smtp_port: 587
        }
    };
    
    // Auto-fill server settings based on email domain
    document.getElementById('email').addEventListener('blur', function() {
        const email = this.value;
        const domain = email.split('@')[1];
        
        if (domain && providerPresets[domain]) {
            const preset = providerPresets[domain];
            document.getElementById('imap_server').value = preset.imap_server;
            document.getElementById('imap_port').value = preset.imap_port;
            document.getElementById('smtp_server').value = preset.smtp_server;
            document.getElementById('smtp_port').value = preset.smtp_port;
            
            showMessage('info', `⚡ Instellingen automatisch ingevuld voor ${domain}`);
        }
    });
    
    // Form submission handler
    configForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(configForm);
        
        // Show loading state
        setLoadingState(true);
        showMessage('loading', '🔄 Verbinding testen...');
        
        try {
            const response = await fetch('/test-connection', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                showMessage('success', result.message);
                currentEmail = formData.get('email');
                
                // Show polling controls after successful connection
                showPollingControls();
                
                // Show additional details if available
                if (result.details) {
                    setTimeout(() => {
                        showMessage('info', `ℹ️ Details: ${result.details}`);
                    }, 1000);
                }
            } else {
                showMessage('error', result.message);
                
                // Show troubleshooting details
                if (result.details) {
                    setTimeout(() => {
                        showMessage('warning', `💡 Tip: ${result.details}`);
                    }, 1000);
                }
            }
        } catch (error) {
            showMessage('error', `❌ Netwerkfout: ${error.message}`);
            console.error('Connection test error:', error);
        } finally {
            setLoadingState(false);
        }
    });
    
    /**
     * Show status message with type and auto-clear
     */
    function showMessage(type, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `status ${type}`;
        messageDiv.innerHTML = message;
        
        // Clear previous messages
        statusContainer.innerHTML = '';
        statusContainer.appendChild(messageDiv);
        
        // Auto-clear non-critical messages
        if (type === 'info' || type === 'warning') {
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.style.opacity = '0';
                    setTimeout(() => messageDiv.remove(), 300);
                }
            }, 5000);
        }
    }
    
    /**
     * Set loading state for form and button
     */
    function setLoadingState(loading) {
        const inputs = configForm.querySelectorAll('input, button');
        
        if (loading) {
            testButton.disabled = true;
            testButton.innerHTML = '<span class="loading-spinner"></span>Testen...';
            inputs.forEach(input => input.disabled = true);
        } else {
            testButton.disabled = false;
            testButton.innerHTML = '🔍 Test Verbinding';
            inputs.forEach(input => input.disabled = false);
        }
    }
    
    /**
     * Form validation helpers
     */
    function validateForm() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!email || !password) {
            showMessage('error', '❌ E-mail en wachtwoord zijn verplicht');
            return false;
        }
        
        if (!email.includes('@')) {
            showMessage('error', '❌ Voer een geldig e-mailadres in');
            return false;
        }
        
        return true;
    }
    
    // Add form validation on submit
    configForm.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
    });
    
    // Real-time port validation
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value < 1 || value > 65535) {
                this.setCustomValidity('Poort moet tussen 1 en 65535 zijn');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    /**
     * Show polling controls after successful connection test
     */
    function showPollingControls() {
        const existingControls = document.getElementById('polling-controls');
        if (existingControls) {
            existingControls.remove();
        }
        
        const controlsDiv = document.createElement('div');
        controlsDiv.id = 'polling-controls';
        controlsDiv.className = 'polling-controls';
        controlsDiv.innerHTML = `
            <h3>� Mailbox Monitoring</h3>
            <p>Start automatische polling om nieuwe Remarkable PDF's te verwerken.</p>
            <div class="polling-buttons">
                <button type="button" id="start-polling-btn" class="btn-primary">
                    ▶️ Start Polling
                </button>
                <button type="button" id="stop-polling-btn" class="btn-secondary" style="display: none;">
                    ⏹️ Stop Polling
                </button>
            </div>
            <div id="polling-status" class="polling-status"></div>
        `;
        
        // Insert after form container
        const formContainer = document.querySelector('.form-container');
        formContainer.parentNode.insertBefore(controlsDiv, formContainer.nextSibling);
        
        // Add event listeners
        document.getElementById('start-polling-btn').addEventListener('click', startPolling);
        document.getElementById('stop-polling-btn').addEventListener('click', stopPolling);
    }
    
    /**
     * Start mailbox polling
     */
    async function startPolling() {
        if (!currentEmail) {
            showMessage('error', '❌ Geen email geconfigureerd');
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('email', currentEmail);
            
            const response = await fetch('/start-polling', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                pollingActive = true;
                updatePollingUI(true);
                showMessage('success', result.message);
                
                if (result.details) {
                    setTimeout(() => {
                        showMessage('info', `ℹ️ ${result.details}`);
                    }, 1000);
                }
                
                // Start status updates
                startStatusUpdates();
            } else {
                showMessage('error', result.message);
            }
        } catch (error) {
            showMessage('error', `❌ Polling start fout: ${error.message}`);
        }
    }
    
    /**
     * Stop mailbox polling
     */
    async function stopPolling() {
        if (!currentEmail) return;
        
        try {
            const formData = new FormData();
            formData.append('email', currentEmail);
            
            const response = await fetch('/stop-polling', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            pollingActive = false;
            updatePollingUI(false);
            showMessage('info', result.message);
            
        } catch (error) {
            showMessage('error', `❌ Polling stop fout: ${error.message}`);
        }
    }
    
    /**
     * Update polling UI state
     */
    function updatePollingUI(isActive) {
        const startBtn = document.getElementById('start-polling-btn');
        const stopBtn = document.getElementById('stop-polling-btn');
        const statusDiv = document.getElementById('polling-status');
        
        if (startBtn && stopBtn && statusDiv) {
            if (isActive) {
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';
                statusDiv.innerHTML = '<div class="status-active">🟢 Polling actief - monitoring inbox...</div>';
            } else {
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
                statusDiv.innerHTML = '<div class="status-inactive">⚪ Polling gestopt</div>';
            }
        }
    }
    
    /**
     * Start periodic status updates
     */
    function startStatusUpdates() {
        // Update status every 10 seconds while polling is active
        const updateInterval = setInterval(async () => {
            if (!pollingActive || !currentEmail) {
                clearInterval(updateInterval);
                return;
            }
            
            try {
                const response = await fetch(`/polling-status/${currentEmail}`);
                const status = await response.json();
                
                if (!status.polling) {
                    // Polling stopped externally
                    pollingActive = false;
                    updatePollingUI(false);
                    clearInterval(updateInterval);
                }
            } catch (error) {
                console.log('Status update error:', error);
            }
        }, 10000);
    }
});
