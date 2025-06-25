#!/bin/bash

# Text Annotator Management Script

show_status() {
    echo "=== Text Annotator Status ==="
    echo ""
    echo "Flask Application:"
    sudo systemctl status text-annotator --no-pager -l
    echo ""
    echo "Nginx Server:"
    sudo systemctl status nginx --no-pager -l
    echo ""
    echo "Application URLs:"
    echo "  Local: http://localhost:8080"
    echo "  Network: http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
}

show_logs() {
    echo "=== Recent Flask Application Logs ==="
    sudo journalctl -u text-annotator --no-pager -l -n 20
    echo ""
    echo "=== Recent Nginx Logs ==="
    sudo tail -n 10 /var/log/nginx/error.log
    echo ""
}

restart_services() {
    echo "Restarting services..."
    sudo systemctl restart text-annotator
    sudo systemctl restart nginx
    echo "Services restarted!"
}

stop_services() {
    echo "Stopping services..."
    sudo systemctl stop text-annotator
    sudo systemctl stop nginx
    echo "Services stopped!"
}

start_services() {
    echo "Starting services..."
    sudo systemctl start nginx
    sudo systemctl start text-annotator
    echo "Services started!"
}

case "$1" in
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    restart)
        restart_services
        ;;
    stop)
        stop_services
        ;;
    start)
        start_services
        ;;
    *)
        echo "Text Annotator Management Script"
        echo ""
        echo "Usage: $0 {status|logs|restart|stop|start}"
        echo ""
        echo "Commands:"
        echo "  status   - Show service status and URLs"
        echo "  logs     - Show recent application logs"
        echo "  restart  - Restart both services"
        echo "  stop     - Stop both services"
        echo "  start    - Start both services"
        echo ""
        show_status
        ;;
esac
