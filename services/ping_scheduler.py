from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import atexit

from app import app, db
from models import NetworkAddress, PingLog, PingSettings
from services.network_service import NetworkService
from services.async_ping_service import AsyncPingService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None

def ping_all_addresses():
    """Ping all active network addresses using async service"""
    with app.app_context():
        try:
            # Get all active addresses
            addresses = NetworkAddress.query.filter_by(is_active=True).all()
            
            if not addresses:
                logger.info("No active addresses to ping")
                return
            
            # Get current settings
            settings = PingSettings.get_current()
            
            # Extract IP addresses
            ip_addresses = [addr.ip_address for addr in addresses]
            
            logger.info(f"Pinging {len(ip_addresses)} addresses with {settings.max_threads} threads, batch size {settings.batch_size}")
            
            # Use async ping service
            async_service = AsyncPingService(
                max_threads=settings.max_threads,
                batch_size=settings.batch_size
            )
            
            # Progress callback for large batches
            def progress_callback(progress, batch_num, total_batches):
                logger.info(f"Async ping progress: {progress:.1f}% (batch {batch_num}/{total_batches})")
            
            # Ping all addresses asynchronously
            results = async_service.ping_all_async(ip_addresses, progress_callback)
            
            # Process results and track status changes
            status_changes = []
            
            for result in results:
                # Find the corresponding address
                address = next((addr for addr in addresses if addr.ip_address == result['ip_address']), None)
                
                if address:
                    # Store old status for comparison
                    old_status = address.last_status
                    
                    # Update address status
                    address.last_status = result['status']
                    address.last_ping_time = result['timestamp']
                    
                    # Create ping log
                    ping_log = PingLog(
                        network_address_id=address.id,
                        status=result['status'],
                        response_time=result['response_time'],
                        error_message=result.get('error_message')
                    )
                    
                    db.session.add(ping_log)
                    
                    # Check if status changed
                    if old_status != result['status']:
                        status_changes.append({
                            'id': address.id,
                            'ip_address': address.ip_address,
                            'old_status': old_status,
                            'new_status': result['status'],
                            'group_name': address.group_name,
                            'timestamp': result['timestamp'].isoformat(),
                            'response_time': result['response_time']
                        })
            
            # Commit all changes
            db.session.commit()
            
            # Send WebSocket updates if there were status changes
            if status_changes:
                try:
                    from app import socketio
                    socketio.emit('status_update', {
                        'type': 'status_changes',
                        'data': status_changes
                    })
                    logger.info(f"Sent WebSocket update for {len(status_changes)} status changes")
                except Exception as e:
                    logger.error(f"Error sending WebSocket update: {str(e)}")
            
            # Always send dashboard update
            try:
                from app import socketio
                # Get updated stats
                total_addresses = NetworkAddress.query.filter_by(is_active=True).count()
                up_count = NetworkAddress.query.filter_by(is_active=True, last_status='up').count()
                down_count = NetworkAddress.query.filter_by(is_active=True, last_status='down').count()
                error_count = NetworkAddress.query.filter_by(is_active=True, last_status='error').count()
                unknown_count = total_addresses - up_count - down_count - error_count
                
                socketio.emit('dashboard_update', {
                    'total': total_addresses,
                    'up': up_count,
                    'down': down_count,
                    'error': error_count,
                    'unknown': unknown_count
                })
            except Exception as e:
                logger.error(f"Error sending dashboard update: {str(e)}")
            
            logger.info(f"Successfully processed {len(results)} ping results")
            
        except Exception as e:
            logger.error(f"Error in ping_all_addresses: {str(e)}")
            db.session.rollback()

def start_scheduler():
    """Start the background scheduler for periodic pings"""
    global scheduler
    
    if scheduler is not None and scheduler.running:
        logger.info("Scheduler is already running")
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # Get current ping settings
        with app.app_context():
            settings = PingSettings.get_current()
            ping_interval = settings.ping_interval
        
        # Schedule ping job with configurable interval
        scheduler.add_job(
            func=ping_all_addresses,
            trigger=IntervalTrigger(seconds=ping_interval),
            id='ping_job',
            name='Ping all network addresses',
            replace_existing=True
        )
        
        scheduler.start()
        
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown() if scheduler else None)
        
        logger.info(f"Ping scheduler started successfully with {ping_interval}s interval")
        
        # Run initial ping
        ping_all_addresses()
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")

def restart_scheduler():
    """Restart the scheduler with updated settings"""
    global scheduler
    
    try:
        # Stop current scheduler
        if scheduler and scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped for restart")
        
        # Start new scheduler
        start_scheduler()
        
    except Exception as e:
        logger.error(f"Error restarting scheduler: {str(e)}")

def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Ping scheduler stopped")
    else:
        logger.info("Scheduler is not running")

def get_scheduler_status():
    """Get the current status of the scheduler"""
    global scheduler
    
    if scheduler and scheduler.running:
        return {
            'running': True,
            'jobs': len(scheduler.get_jobs())
        }
    else:
        return {
            'running': False,
            'jobs': 0
        }
