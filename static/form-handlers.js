/**
 * Form Handlers
 * Handles form submission logic for config and notification forms
 */

window.FormHandlers = {
    /**
     * Setup configuration form handler
     */
    setupConfigForm: function(configForm, showMessageCallback, showPollingControlsCallback, setCurrentEmailCallback) {
        configForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validate form first
            if (!window.UIUtils.validateForm(showMessageCallback)) {
                return false;
            }
            
            const formData = new FormData(configForm);
            const testButton = document.getElementById('test-btn');
            
            // Show loading state
            window.UIUtils.setLoadingState(true, configForm, testButton);
            showMessageCallback('loading', '🔄 Verbinding testen...');
            
            try {
                const response = await fetch('/test-connection', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === 'success') {
                    showMessageCallback('success', result.message);
                    setCurrentEmailCallback(formData.get('email'));
                    
                    // Show polling controls after successful connection
                    showPollingControlsCallback();
                    
                    // Show additional details if available
                    if (result.details) {
                        setTimeout(() => {
                            showMessageCallback('info', `ℹ️ Details: ${result.details}`);
                        }, 1000);
                    }
                } else {
                    showMessageCallback('error', result.message);
                    
                    // Show troubleshooting details
                    if (result.details) {
                        setTimeout(() => {
                            showMessageCallback('warning', `💡 Tip: ${result.details}`);
                        }, 1000);
                    }
                }
            } catch (error) {
                showMessageCallback('error', `❌ Netwerkfout: ${error.message}`);
                console.error('Connection test error:', error);
            } finally {
                // Always reset loading state
                window.UIUtils.setLoadingState(false, configForm, testButton);
            }
        });
    },

    /**
     * Setup notification email form handler
     */
    setupNotificationForm: function(notificationForm, getCurrentEmailCallback, showMessageCallback) {
        if (!notificationForm) return;

        notificationForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const currentEmail = getCurrentEmailCallback();
            if (!currentEmail) {
                showMessageCallback('error', '❌ Configureer eerst je email instellingen');
                return;
            }
            
            const formData = new FormData(notificationForm);
            formData.set('email', currentEmail); // Ensure current email is set
            
            try {
                const response = await fetch('/set-notification-email', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === 'success') {
                    showMessageCallback('success', result.message);
                } else {
                    showMessageCallback('error', result.message);
                }
            } catch (error) {
                showMessageCallback('error', `❌ Fout bij instellen notificatie-email: ${error.message}`);
            }
        });
    }
};
