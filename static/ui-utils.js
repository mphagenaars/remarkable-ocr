/**
 * UI Utilities
 * Handles status messages, loading states, and form validation
 */

window.UIUtils = {
    /**
     * Show status message with type and auto-clear
     */
    showMessage: function(type, message, statusContainer) {
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
    },

    /**
     * Set loading state for form and button
     */
    setLoadingState: function(loading, configForm, testButton) {
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
    },

    /**
     * Form validation helpers
     */
    validateForm: function(showMessageCallback) {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!email || !password) {
            showMessageCallback('error', '❌ E-mail en wachtwoord zijn verplicht');
            return false;
        }
        
        if (!email.includes('@')) {
            showMessageCallback('error', '❌ Voer een geldig e-mailadres in');
            return false;
        }
        
        return true;
    },

    /**
     * Setup real-time port validation
     */
    setupPortValidation: function() {
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
    }
};
