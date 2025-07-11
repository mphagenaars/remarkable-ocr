/**
 * Polling Module
 * Handles mailbox polling functionality and UI
 */

window.PollingModule = {
    pollingActive: false,
    
    /**
     * Setup polling button listeners
     */
    setupPollingButtons: function(startPolling, stopPolling) {
        const startPollingBtn = document.getElementById('start-polling-btn');
        const stopPollingBtn = document.getElementById('stop-polling-btn');
        
        if (startPollingBtn) {
            startPollingBtn.addEventListener('click', startPolling);
        }
        
        if (stopPollingBtn) {
            stopPollingBtn.addEventListener('click', stopPolling);
        }
    },

    /**
     * Show polling controls after successful connection test
     */
    showPollingControls: function(currentEmail) {
        const existingControls = document.getElementById('polling-controls');
        if (existingControls) {
            existingControls.remove();
        }
        
        const controlsDiv = document.createElement('div');
        controlsDiv.id = 'polling-controls';
        controlsDiv.className = 'polling-controls';
        controlsDiv.innerHTML = `
            <h3>📧 Mailbox Monitoring</h3>
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
        
        // Show notification controls
        const notificationControls = document.getElementById('notification-controls');
        if (notificationControls) {
            notificationControls.style.display = 'block';
            
            // Set hidden email field to current email
            document.getElementById('notification_account').value = currentEmail;
        }
        
        // Insert after form container
        const formContainer = document.querySelector('.form-container');
        formContainer.parentNode.insertBefore(controlsDiv, formContainer.nextSibling);
        
        // Add event listeners (get fresh references after DOM insertion)
        const newStartBtn = document.getElementById('start-polling-btn');
        const newStopBtn = document.getElementById('stop-polling-btn');
        
        if (newStartBtn) {
            newStartBtn.addEventListener('click', () => this.startPolling(
                () => currentEmail, 
                (type, msg) => window.UIUtils.showMessage(type, msg, document.getElementById('status-message'))
            ));
        }
        
        if (newStopBtn) {
            newStopBtn.addEventListener('click', () => this.stopPolling(
                () => currentEmail,
                (type, msg) => window.UIUtils.showMessage(type, msg, document.getElementById('status-message'))
            ));
        }
    },

    /**
     * Start mailbox polling
     */
    startPolling: async function(getCurrentEmailCallback, showMessageCallback) {
        const currentEmail = getCurrentEmailCallback();
        if (!currentEmail) {
            showMessageCallback('error', '❌ Geen email geconfigureerd');
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
                window.PollingModule.pollingActive = true;
                window.PollingModule.updatePollingUI(true);
                showMessageCallback('success', result.message);
                
                if (result.details) {
                    setTimeout(() => {
                        showMessageCallback('info', `ℹ️ ${result.details}`);
                    }, 1000);
                }
                
                // Start status updates
                window.PollingModule.startStatusUpdates(currentEmail);
            } else {
                showMessageCallback('error', result.message);
            }
        } catch (error) {
            showMessageCallback('error', `❌ Polling start fout: ${error.message}`);
        }
    },

    /**
     * Stop mailbox polling
     */
    stopPolling: async function(getCurrentEmailCallback, showMessageCallback) {
        const currentEmail = getCurrentEmailCallback();
        if (!currentEmail) return;
        
        try {
            const formData = new FormData();
            formData.append('email', currentEmail);
            
            const response = await fetch('/stop-polling', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            window.PollingModule.pollingActive = false;
            window.PollingModule.updatePollingUI(false);
            showMessageCallback('info', result.message);
            
        } catch (error) {
            showMessageCallback('error', `❌ Polling stop fout: ${error.message}`);
        }
    },

    /**
     * Update polling UI state
     */
    updatePollingUI: function(isActive) {
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
    },

    /**
     * Start periodic status updates
     */
    startStatusUpdates: function(currentEmail) {
        // Update status every 10 seconds while polling is active
        const updateInterval = setInterval(async () => {
            if (!window.PollingModule.pollingActive || !currentEmail) {
                clearInterval(updateInterval);
                return;
            }
            
            try {
                const response = await fetch(`/polling-status/${currentEmail}`);
                const status = await response.json();
                
                if (!status.polling) {
                    // Polling stopped externally
                    window.PollingModule.pollingActive = false;
                    window.PollingModule.updatePollingUI(false);
                    clearInterval(updateInterval);
                }
            } catch (error) {
                console.log('Status update error:', error);
            }
        }, 10000);
    }
};
