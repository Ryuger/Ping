# Network Monitor Application

## Overview

This is a Flask-based network monitoring application that allows users to track the status of network addresses through automated ping monitoring. The application provides a web dashboard for managing network addresses, viewing ping logs, and configuring monitoring settings.

**Recent Enhancement**: Added asynchronous multithreaded ping capabilities to monitor up to 10,000+ network addresses efficiently with configurable threading and batch processing parameters.

## User Preferences

Preferred communication style: Simple, everyday language.
Language: Russian
Interface language: Russian (UI elements, messages, labels)

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy for database operations
- **Database**: SQLite (exclusive use as requested by user)
- **Task Scheduling**: APScheduler for automated ping operations
- **Network Operations**: Uses ping3 library for ICMP pings only, netifaces for network discovery

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for UI components
- **Styling**: Bootstrap with custom CSS for network-specific styling
- **JavaScript**: Vanilla JavaScript for interactive features like auto-refresh and form handling
- **Theme**: Dark theme implementation using Bootstrap

### Application Structure
```
├── app.py              # Main application factory and configuration
├── main.py             # Application entry point
├── models.py           # Database models and schemas
├── routes.py           # HTTP route handlers
├── services/           # Business logic and services
├── templates/          # HTML templates
└── static/            # CSS, JavaScript, and assets
```

## Key Components

### Database Models
- **NetworkAddress**: Stores IP addresses, group names, and monitoring status
- **PingLog**: Records ping results with timestamps and response times
- **NetworkInterface**: Manages network interface detection and selection
- **PingSettings**: Stores configurable ping settings (interval, timeout, retries, max_threads, batch_size)

### Services
- **NetworkService**: Handles IP validation, network interface detection, and ping operations
- **AsyncPingService**: NEW - Multithreaded asynchronous ping service for high-volume monitoring (up to 10,000+ addresses)
- **PingScheduler**: Manages automated ping scheduling using APScheduler with configurable intervals and async ping integration

### Web Interface
- **Dashboard**: Real-time status overview with summary cards and address management, organized by groups in tabs
- **Logs**: Detailed ping history with filtering and pagination
- **Settings**: Network interface configuration, ping settings, and data import/export

## Data Flow

1. **Address Management**: Users add IP addresses through the web interface
2. **Automated Monitoring**: Background scheduler pings all active addresses periodically
3. **Status Updates**: Ping results update both NetworkAddress status and create PingLog entries
4. **Dashboard Display**: Real-time status displayed with color-coded indicators
5. **Log Retention**: Historical ping data stored for analysis and troubleshooting

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **APScheduler**: Background task scheduling
- **ping3**: ICMP ping operations only
- **netifaces**: Network interface detection
- **ipaddress**: IP address validation and manipulation
- **openpyxl**: Excel file import/export functionality

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library for status indicators
- **Vanilla JavaScript**: Client-side interactivity

## Deployment Strategy

### Configuration
- SQLite database for local development
- Automatic network IP detection for local deployment
- ProxyFix middleware for deployment behind reverse proxies
- Session secret configuration via environment variables

### Database Management
- Automatic table creation on application startup
- Model-first approach with SQLAlchemy declarative base
- Support for database migrations through SQLAlchemy

### Monitoring Service
- Background scheduler starts automatically with the application
- Graceful shutdown handling with atexit hooks
- Configurable ping intervals and retry logic

### Security Considerations
- Session secret configuration via environment variables
- SQL injection prevention through SQLAlchemy ORM
- Input validation for IP addresses and network parameters

## Performance Optimizations (Added 2025-07-16)
- **Asynchronous Ping Processing**: Multithreaded ping execution with configurable thread pools (1-200 threads)
- **Batch Processing**: Configurable batch sizes (10-1000 addresses) for memory optimization
- **Auto-optimization**: Automatic parameter tuning based on address count for optimal performance
- **Real-time WebSocket Updates**: Status changes broadcast instantly without page refresh
- **Scalability**: Supports monitoring 10,000+ addresses with proper thread/batch configuration

## UI/UX Improvements (Updated 2025-07-16)
- **Status Filtering**: Clickable status cards for filtering devices by status (Online, Offline, Error, Unknown)
- **Filter Persistence**: Active filters are maintained during WebSocket updates and tab switching
- **Notification Throttling**: Reduced notification spam with 5-second throttling between messages
- **Filter Reset**: Total card click clears all filters, plus dedicated "Show All" button
- **Tab State Preservation**: Active tab state is preserved during page refreshes
- **Smooth Animations**: Improved card animations without disrupting user interaction
- **Settings Persistence**: Ping settings are properly saved and validated

## Recent Bug Fixes (2025-07-16)
- **Fixed Filter State Persistence**: Filters now remain active during WebSocket updates and status changes
- **Fixed Notification Spam**: Added 5-second throttling between status change notifications
- **Fixed Interface Detection**: Removed duplicate interface detection logic from main.py
- **Fixed Status Filter Reapplication**: Filters are properly reapplied after WebSocket status updates
- **Enhanced Filter UI**: Added clear "Show All" button and improved filter indicator styling

## UI Redesign (2025-07-16)
- **Horizontal Stats Layout**: Redesigned status cards to horizontal layout with "Всего:", "Онлайн:", "Ошибка:" format
- **Emphasized Offline Status**: "ОФФЛАЙН" card is prominently displayed on the right with larger numbers
- **Compact Design**: All status information fits in a single horizontal card with better visual hierarchy
- **Enhanced Styling**: Added gradient effects, shadows, and improved typography for better visual appeal
- **Responsive Layout**: Optimized for different screen sizes with proper mobile adaptations

## Theme System Removal (2025-07-18)
- **Light Theme Only**: Completely removed dark theme implementation per user request
- **CSS Cleanup**: Removed all [data-theme="dark"] CSS rules and theme-related variables
- **Template Updates**: Removed theme toggle buttons and theme switching JavaScript
- **Simplified Styling**: Application now uses only light theme with clean, minimal design
- **Removed Bootstrap Dependencies**: Eliminated Bootstrap from JavaScript to prevent errors and improve performance

## Real-Time Whitelist Updates (2025-07-18)
- **WebSocket Integration**: Added real-time WebSocket updates for IP whitelist changes
- **Live Notifications**: Instant notifications when IPs are added, removed, or status changes
- **File Change Detection**: Automatic detection of external configuration file changes
- **Refresh Functionality**: Added manual refresh button to reload whitelist from file
- **Client-Side Updates**: Enhanced JavaScript to handle real-time updates without page reloads
- **Superadmin Experience**: Real-time updates ensure superadmin sees all changes immediately
- **Notification System**: Toast notifications for all whitelist operations with success/error states

## Windows Batch File Fixes (2025-07-18)
- **Encoding Issues**: Fixed UTF-8 encoding problems in Windows batch files
- **Character Set**: Added `chcp 65001` for proper Unicode support
- **English Interface**: Converted batch file messages to English to avoid encoding issues
- **Improved Script**: Created `start_monitor_improved.bat` with better error handling
- **Dependency Checks**: Enhanced Python and pip validation
- **Directory Creation**: Automatic creation of required directories
- **Error Messages**: Clear error messages for troubleshooting startup issues

## IP Address Security System (2025-07-17, Updated 2025-07-18)
- **JSON Configuration**: Created `config/ip_whitelist.json` for IP address management
- **Group-Based Organization**: Restructured to use groups (system, user, networks) for better management
- **Protected System Group**: System addresses (127.0.0.1, ::1, 0.0.0.0) are protected from deletion by admin users
- **Server IP Auto-Addition**: Server interface IP is automatically added to system group on startup
- **Middleware Protection**: Added `middleware/ip_filter.py` for request filtering
- **Comprehensive IP Validation**: Supports individual IPs, subnets, and IPv4/IPv6 addresses
- **Admin and Superadmin Management**: Added `/ip_whitelist` page accessible by admin and superadmin users
- **Role-Based Permissions**: Admin users can add/remove IPs but cannot modify protected system group
- **Security Audit Logging**: All IP whitelist changes are logged in audit system
- **Automatic Blocking**: Non-whitelisted IPs are automatically blocked with 403 error
- **Removed Login Hints**: Eliminated security vulnerability by removing default login credentials from login page

## Error Handling System (2025-07-17)
- **Custom Error Pages**: Added readable HTML error pages for 404, 403, 500, and general exceptions
- **Russian Language Support**: All error messages are in Russian with clear explanations
- **IP Address Display**: 403 errors show blocked IP address for easier troubleshooting
- **Route Error Handler**: Added decorator for consistent error handling across application routes
- **Unified Error Styling**: Professional error pages with consistent design and navigation
- **Eliminated Unicode Errors**: Replaced raw server error responses with human-readable messages

## Offline Asset Management (2025-07-17)
- **Local Asset Storage**: External resources (Bootstrap, Font Awesome, Socket.IO) are automatically downloaded to local files
- **Fallback System**: HTML includes fallback to CDN if local files are unavailable
- **Automatic Download**: Assets are downloaded automatically on first application startup
- **Internet Independence**: Application works fully offline after initial setup
- **Asset Scripts**: Created `download_assets.py` for manual asset management and Windows batch files for easy resource downloading
- **WebSocket Restored**: Socket.IO functionality restored with local files for real-time updates
- **Bootstrap Support**: Added Bootstrap CSS and JavaScript for enhanced UI components with local storage
- **Font Files**: Font Awesome WOFF2 fonts are downloaded locally with automatic path correction in CSS files
- **Batch Files**: Created `download_external_resources.bat` and `download_resources.cmd` for Windows users to easily download all external resources

## Font Awesome Replacement (2025-07-18)
- **Emoji Icons**: Replaced all Font Awesome icons with appropriate emoji alternatives for full autonomy
- **Icon Mapping**: 🌙/☀️ for theme toggle, 📡 for ping, 🖥️ for devices, ✅❌⚠️ for statuses, 📋 for logs, 🗑️ for delete, ➕ for add
- **Complete Migration**: All templates systematically updated - index.html, user_management.html, settings.html, logs.html, all authentication pages
- **JavaScript Updates**: Dynamic icon changes in force_password_change.html now use emoji (✅/❌) instead of Font Awesome classes
- **CSS Cleanup**: Removed Font Awesome CSS dependency from base.html template and replaced fa-2x/fa-3x classes with inline styles
- **Complete Autonomy**: Application now works completely offline without any external icon dependencies
- **Dark Theme Fix**: Comprehensive CSS overhaul to fix dark theme text visibility issues - all text now properly white/light gray on dark backgrounds
- **Form Controls**: Fixed form inputs, buttons, cards, tables, and all UI elements to display correctly in dark mode
- **Bootstrap Dark Theme**: Enhanced Bootstrap component styling for proper dark theme support with correct text colors

## WebSocket and Admin Access Fixes (2025-07-18)
- **WebSocket Handler Fix**: Fixed `handle_connect()` function to properly accept auth parameter preventing connection errors
- **Missing Import Fix**: Added `join_room` and `leave_room` imports to resolve WebSocket room management errors
- **Admin IP Whitelist Access**: Extended IP whitelist management access to admin users (previously superadmin only)
- **System Address Protection**: Admin users can manage IP whitelist but cannot modify protected system group addresses
- **Login Page Asset Fix**: Updated login.html to use local Bootstrap and Font Awesome assets for complete offline functionality
- **Offline Asset Support**: Login page now works without internet connection using locally stored CSS and JavaScript files
- **Navigation Fix**: Updated base.html to show IP whitelist tab for admin users using `can_manage_users()` permission check
- **Font Awesome JavaScript Fix**: Replaced Font Awesome icons with emoji in app.js to eliminate dependency errors
- **Visual IP Status Indicators**: Added comprehensive visual indicators for IP address types in whitelist interface
- **Enhanced Status Display**: System IPs now show "🔒 Защищен" badge and clear protection status in actions column
- **IP Type Documentation**: Added informational panel explaining different IP address types and their protection levels