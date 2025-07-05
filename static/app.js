/**
 * Remarkable OCR - Frontend JavaScript
 * Handles email configuration form and connectivity testing
 */

document.addEventListener('DOMContentLoaded', function() {
    const configForm = document.getElementById('config-form');
    const statusContainer = document.getElementById('status-message');
    const testButton = document.getElementById('test-btn');
    
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
    
    console.log('📝 Remarkable OCR Frontend geïnitialiseerd');
});
