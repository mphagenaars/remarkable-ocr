/**
 * Remarkable OCR - Frontend JavaScript
 * Handles email configuration form and connectivity testing
 */

document.addEventListener('DOMContentLoaded', function() {
    const configForm = document.getElementById('config-form');
    const statusContainer = document.getElementById('status-message');
    const testButton = document.getElementById('test-btn');
    const notificationForm = document.getElementById('notification-form');
    const senderForm = document.getElementById('sender-form');
    let currentEmail = null;
    
    // Create showMessage wrapper function
    function showMessage(type, message) {
        window.UIUtils.showMessage(type, message, statusContainer);
    }
    
    // Helper functions for callbacks
    function setCurrentEmail(email) {
        currentEmail = email;
    }
    
    function getCurrentEmail() {
        return currentEmail;
    }
    
    // Create wrapper function for showPollingControls
    function showPollingControls() {
        window.PollingModule.showPollingControls(currentEmail);
    }
    
    // Create wrapper functions for polling
    function startPolling() {
        window.PollingModule.startPolling(getCurrentEmail, showMessage);
    }
    
    function stopPolling() {
        window.PollingModule.stopPolling(getCurrentEmail, showMessage);
    }
    
    // Setup UI utilities
    window.UIUtils.setupPortValidation();
    
    // Setup polling button listeners
    window.PollingModule.setupPollingButtons(startPolling, stopPolling);
    
    // Setup email provider auto-fill
    window.EmailPresets.setupAutoFill(showMessage);
    
    // Setup form handlers
    window.FormHandlers.setupConfigForm(
        configForm, 
        showMessage, 
        showPollingControls, 
        setCurrentEmail
    );

    window.FormHandlers.setupNotificationForm(notificationForm, getCurrentEmail, showMessage);
    window.FormHandlers.setupSenderForm(senderForm, getCurrentEmail, showMessage);
});