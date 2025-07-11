/**
 * Email Provider Presets
 * Pre-configured IMAP/SMTP settings for common email providers
 */

window.EmailPresets = {
    providerPresets: {
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
    },

    /**
     * Auto-fill form fields based on email domain
     */
    setupAutoFill: function(showMessageCallback) {
        document.getElementById('email').addEventListener('blur', function() {
            const email = this.value;
            const domain = email.split('@')[1];
            
            if (domain && window.EmailPresets.providerPresets[domain]) {
                const preset = window.EmailPresets.providerPresets[domain];
                document.getElementById('imap_server').value = preset.imap_server;
                document.getElementById('imap_port').value = preset.imap_port;
                document.getElementById('smtp_server').value = preset.smtp_server;
                document.getElementById('smtp_port').value = preset.smtp_port;
                
                showMessageCallback('info', `⚡ Instellingen automatisch ingevuld voor ${domain}`);
            }
        });
    }
};
