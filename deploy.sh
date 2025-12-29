#!/bin/bash

# German AI Learner - Production Deployment Script
# This script automates the deployment process

set -e  # Exit on error

echo "🚀 German AI Learner - Production Deployment"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE="./backend/.env"
BACKUP_DIR="./backups"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check NVIDIA GPU (optional)
    if command -v nvidia-smi &> /dev/null; then
        log_info "NVIDIA GPU detected"
    else
        log_warn "No NVIDIA GPU detected - AI features will run on CPU (slower)"
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Please create it from .env.example"
        exit 1
    fi
    
    log_info "All requirements met ✓"
}

backup_data() {
    log_info "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    # Backup MongoDB
    if docker ps | grep -q german_mongodb_prod; then
        docker exec german_mongodb_prod mongodump --archive=/tmp/backup.archive
        docker cp german_mongodb_prod:/tmp/backup.archive "$BACKUP_DIR/mongodb_$TIMESTAMP.archive"
        log_info "MongoDB backup created ✓"
    fi
    
    # Backup volumes
    docker run --rm \
        -v german_ai_mongodb_data:/data/mongodb \
        -v german_ai_redis_data:/data/redis \
        -v "$(pwd)/$BACKUP_DIR:/backup" \
        alpine tar czf "/backup/volumes_$TIMESTAMP.tar.gz" /data 2>/dev/null || true
    
    log_info "Backup completed: $BACKUP_FILE ✓"
}

pull_images() {
    log_info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull
    log_info "Images updated ✓"
}

build_services() {
    log_info "Building services..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    log_info "Build completed ✓"
}

start_services() {
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    log_info "Services started ✓"
}

wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    MAX_WAIT=300  # 5 minutes
    ELAPSED=0
    
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        UNHEALTHY=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" | wc -l)
        STARTING=$(docker ps --filter "health=starting" --format "{{.Names}}" | wc -l)
        
        if [ "$UNHEALTHY" -eq 0 ] && [ "$STARTING" -eq 0 ]; then
            log_info "All services are healthy ✓"
            return 0
        fi
        
        echo -n "."
        sleep 5
        ELAPSED=$((ELAPSED + 5))
    done
    
    log_error "Services did not become healthy in time"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"
    return 1
}

initialize_ollama() {
    log_info "Initializing Ollama with Mistral 7B model..."
    
    # Wait for Ollama to be ready
    sleep 10
    
    # Pull Mistral model
    docker exec german_ollama_prod ollama pull mistral:7b
    
    log_info "Ollama initialized ✓"
}

seed_database() {
    log_info "Seeding database..."
    
    # Check if database is already seeded
    VOCAB_COUNT=$(docker exec german_mongodb_prod mongosh german_ai \
        --quiet --eval "db.vocabulary.countDocuments()" 2>/dev/null || echo "0")
    
    if [ "$VOCAB_COUNT" -gt 0 ]; then
        log_warn "Database already seeded (skipping)"
        return 0
    fi
    
    # Run seed script
    docker exec german_backend_prod python -m app.seed.seed_all
    
    log_info "Database seeded ✓"
}

run_tests() {
    log_info "Running health checks..."
    
    # Test backend
    BACKEND_STATUS=$(curl -s http://localhost:8000/ | grep -o '"status":"ok"' || echo "")
    if [ -n "$BACKEND_STATUS" ]; then
        log_info "Backend: ✓"
    else
        log_error "Backend: ✗"
        return 1
    fi
    
    # Test frontend
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
    if [ "$FRONTEND_STATUS" = "200" ]; then
        log_info "Frontend: ✓"
    else
        log_error "Frontend: ✗"
        return 1
    fi
    
    # Test Ollama
    OLLAMA_STATUS=$(curl -s http://localhost:11434/api/tags | grep -o "models" || echo "")
    if [ -n "$OLLAMA_STATUS" ]; then
        log_info "Ollama: ✓"
    else
        log_error "Ollama: ✗"
        return 1
    fi
    
    log_info "All health checks passed ✓"
}

show_status() {
    echo ""
    echo "=============================================="
    echo "📊 Deployment Status"
    echo "=============================================="
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    echo "🌐 Access URLs:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📝 Logs:"
    echo "  docker-compose -f $COMPOSE_FILE logs -f [service]"
    echo ""
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        deploy)
            check_requirements
            backup_data
            pull_images
            build_services
            start_services
            wait_for_services
            initialize_ollama
            seed_database
            run_tests
            show_status
            log_info "🎉 Deployment completed successfully!"
            ;;
        
        start)
            log_info "Starting services..."
            docker-compose -f "$COMPOSE_FILE" up -d
            show_status
            ;;
        
        stop)
            log_info "Stopping services..."
            docker-compose -f "$COMPOSE_FILE" down
            log_info "Services stopped ✓"
            ;;
        
        restart)
            log_info "Restarting services..."
            docker-compose -f "$COMPOSE_FILE" restart
            show_status
            ;;
        
        logs)
            docker-compose -f "$COMPOSE_FILE" logs -f "${2:-}"
            ;;
        
        status)
            show_status
            ;;
        
        backup)
            backup_data
            ;;
        
        update)
            log_info "Updating deployment..."
            backup_data
            pull_images
            build_services
            docker-compose -f "$COMPOSE_FILE" up -d --force-recreate
            wait_for_services
            run_tests
            show_status
            log_info "Update completed ✓"
            ;;
        
        clean)
            log_warn "This will remove all containers and volumes!"
            read -p "Are you sure? (yes/no): " -r
            if [ "$REPLY" = "yes" ]; then
                docker-compose -f "$COMPOSE_FILE" down -v
                log_info "Cleanup completed ✓"
            else
                log_info "Cleanup cancelled"
            fi
            ;;
        
        *)
            echo "Usage: $0 {deploy|start|stop|restart|logs|status|backup|update|clean}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (default)"
            echo "  start    - Start all services"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  logs     - View logs (optionally specify service)"
            echo "  status   - Show deployment status"
            echo "  backup   - Create backup"
            echo "  update   - Update and redeploy"
            echo "  clean    - Remove all containers and volumes"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
