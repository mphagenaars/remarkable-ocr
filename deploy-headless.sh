#!/bin/bash

# Remarkable OCR - Headless LXC Deployment Script
# Eenvoudige deployment met screen sessie voor betrouwbare achtergrond uitvoering

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="remarkable-ocr"
LOG_FILE="$SCRIPT_DIR/remarkable.log"

echo "🚀 Remarkable OCR Headless Deployment"
echo "======================================"

# Functie: Check of screen geïnstalleerd is
check_screen() {
    if ! command -v screen &> /dev/null; then
        echo "❌ Screen niet gevonden. Installeren..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y screen
        elif command -v yum &> /dev/null; then
            sudo yum install -y screen
        else
            echo "❌ Kan screen niet automatisch installeren. Installeer handmatig: apt-get install screen"
            exit 1
        fi
    fi
    echo "✅ Screen beschikbaar"
}

# Functie: Check virtual environment
check_venv() {
    if [[ ! -d "$SCRIPT_DIR/.venv" ]]; then
        echo "❌ Virtual environment niet gevonden in $SCRIPT_DIR/.venv"
        echo "   Run eerst: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
        exit 1
    fi
    echo "✅ Virtual environment gevonden"
}

# Functie: Stop bestaande sessie
stop_service() {
    if screen -list | grep -q "$SESSION_NAME"; then
        echo "🛑 Stopping bestaande remarkable-ocr sessie..."
        screen -S "$SESSION_NAME" -X quit 2>/dev/null || true
        sleep 2
    fi
}

# Functie: Start service in screen
start_service() {
    echo "🎬 Starting remarkable-ocr in screen sessie..."
    
    # Start screen sessie in detached modus
    screen -dmS "$SESSION_NAME" bash -c "
        cd '$SCRIPT_DIR'
        source .venv/bin/activate
        echo 'Starting Remarkable OCR at \$(date)' >> '$LOG_FILE'
        python app.py 2>&1 | tee -a '$LOG_FILE'
    "
    
    sleep 3
    
    # Check of sessie draait
    if screen -list | grep -q "$SESSION_NAME"; then
        echo "✅ Service gestart in screen sessie: $SESSION_NAME"
        echo "📋 Management commando's:"
        echo "   - Bekijk status: screen -list"
        echo "   - Attach sessie: screen -r $SESSION_NAME"
        echo "   - Detach sessie: Ctrl+A, D"
        echo "   - Stop service: screen -S $SESSION_NAME -X quit"
        echo "   - Bekijk logs: tail -f $LOG_FILE"
    else
        echo "❌ Service start gefaald. Check logs: $LOG_FILE"
        exit 1
    fi
}

# Functie: Status check
check_status() {
    echo "📊 Service Status:"
    if screen -list | grep -q "$SESSION_NAME"; then
        echo "✅ Screen sessie actief: $SESSION_NAME"
        
        # Check of app daadwerkelijk draait (poort 8000)
        if netstat -tlnp 2>/dev/null | grep -q ':8000 '; then
            echo "✅ App draait op poort 8000"
        else
            echo "⚠️  Screen sessie actief maar app mogelijk niet gestart"
        fi
    else
        echo "❌ Geen actieve screen sessie gevonden"
    fi
    
    if [[ -f "$LOG_FILE" ]]; then
        echo "📜 Laatste log entries:"
        tail -5 "$LOG_FILE"
    fi
}

# Functie: Auto-start setup met cron
setup_autostart() {
    CRON_ENTRY="@reboot sleep 30 && cd $SCRIPT_DIR && ./deploy-headless.sh start"
    
    echo "🔄 Auto-start setup..."
    
    # Check of cron entry al bestaat
    if crontab -l 2>/dev/null | grep -q "deploy-headless.sh"; then
        echo "✅ Auto-start al geconfigureerd"
    else
        # Voeg toe aan crontab
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        echo "✅ Auto-start toegevoegd aan crontab"
        echo "   Service start automatisch 30 seconden na reboot"
    fi
}

# Main script logic
case "${1:-start}" in
    "start")
        check_screen
        check_venv
        stop_service
        start_service
        check_status
        ;;
    "stop")
        stop_service
        echo "✅ Service gestopt"
        ;;
    "restart")
        stop_service
        start_service
        check_status
        ;;
    "status")
        check_status
        ;;
    "autostart")
        setup_autostart
        ;;
    "logs")
        if [[ -f "$LOG_FILE" ]]; then
            tail -f "$LOG_FILE"
        else
            echo "❌ Geen log file gevonden: $LOG_FILE"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|autostart|logs}"
        echo ""
        echo "Commands:"
        echo "  start     - Start service in screen sessie"
        echo "  stop      - Stop service"
        echo "  restart   - Restart service"
        echo "  status    - Toon service status"
        echo "  autostart - Setup automatische start bij reboot"
        echo "  logs      - Toon live logs"
        exit 1
        ;;
esac
