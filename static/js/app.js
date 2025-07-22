// Network Monitor Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeWebSocket();
});

function initializeApp() {
    // Initialize auto-refresh for dashboard
    if (window.location.pathname === '/') {
        initializeDashboardAutoRefresh();
        initializeStatusFiltering();
    }

    // Initialize log filters
    if (window.location.pathname === '/logs') {
        initializeLogFilters();
    }

    // Initialize network interface selection
    if (window.location.pathname === '/settings') {
        initializeSettings();
    }
}

function initializeDashboardAutoRefresh() {
    // Manual refresh button functionality
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            refreshDashboard();
        });
    }
    
    // Preserve tab state and filter state
    preserveTabState();
    preserveFilterState();
}

function refreshDashboard() {
    // Store current tab state
    const activeTab = document.querySelector('.nav-link.active');
    if (activeTab) {
        localStorage.setItem('activeTab', activeTab.id);
    }
    
    // Store current filter state
    const filterIndicator = document.getElementById('filterIndicator');
    if (filterIndicator) {
        const filterText = filterIndicator.textContent;
        const statusMatch = filterText.match(/Онлайн|Оффлайн|Ошибка|Неизвестно/);
        if (statusMatch) {
            const statusMap = {
                'Онлайн': 'up',
                'Оффлайн': 'down',
                'Ошибка': 'error',
                'Неизвестно': 'unknown'
            };
            localStorage.setItem('activeFilter', statusMap[statusMatch[0]]);
        }
    }
    
    // Add loading state to status cards
    const statusCards = document.querySelectorAll('.card');
    statusCards.forEach(card => {
        card.classList.add('loading');
    });

    // Reload the page
    location.reload();
}

function preserveTabState() {
    // Restore tab state on page load
    const savedTab = localStorage.getItem('activeTab');
    if (savedTab) {
        const tabElement = document.getElementById(savedTab);
        if (tabElement) {
            // Remove active from all tabs
            document.querySelectorAll('.nav-link').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Activate the saved tab
            tabElement.classList.add('active');
            const targetPane = document.querySelector(tabElement.getAttribute('data-target'));
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
        }
        localStorage.removeItem('activeTab');
    }
}

function preserveFilterState() {
    // Restore filter state on page load
    const savedFilter = localStorage.getItem('activeFilter');
    if (savedFilter) {
        setTimeout(() => {
            filterByStatus(savedFilter);
        }, 100);
        localStorage.removeItem('activeFilter');
    }
}

function initializeLogFilters() {
    // Auto-submit form when filters change
    const filterForm = document.querySelector('form');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input[type="checkbox"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }

    // Add search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterLogTable(this.value);
        });
    }
}

function filterLogTable(searchTerm) {
    const table = document.querySelector('.table tbody');
    if (!table) return;

    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function initializeSettings() {
    // Scheduler controls
    const schedulerControls = document.querySelectorAll('[data-scheduler-action]');
    schedulerControls.forEach(control => {
        control.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.dataset.schedulerAction;
            handleSchedulerAction(action);
        });
    });

    // Reset defaults button
    const resetDefaultsBtn = document.getElementById('resetDefaults');
    if (resetDefaultsBtn) {
        resetDefaultsBtn.addEventListener('click', function() {
            resetPingSettingsToDefaults();
        });
    }
}



function handleSchedulerAction(action) {
    const url = action === 'start' ? '/scheduler/start' : '/scheduler/stop';
    window.location.href = url;
}

function resetPingSettingsToDefaults() {
    // Reset form values to defaults
    document.getElementById('ping_interval').value = '30';
    document.getElementById('timeout').value = '5';
    document.getElementById('max_retries').value = '3';
    document.getElementById('max_threads').value = '50';
    document.getElementById('batch_size').value = '100';
    
    showToast('Значения сброшены к настройкам по умолчанию', 'info');
}

// Manual ping functionality
function pingAddress(addressId) {
    const button = document.querySelector(`[data-ping-id="${addressId}"]`);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span style="margin-right: 4px;">⏳</span>Pinging...';
    }

    window.location.href = `/ping_now/${addressId}`;
}

// Utility functions
function showToast(message, type = 'info') {
    // Create simple notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? 'var(--success-color)' : type === 'danger' ? 'var(--danger-color)' : type === 'warning' ? 'var(--warning-color)' : 'var(--accent-color)'};
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        box-shadow: var(--shadow);
        z-index: 1000;
        max-width: 300px;
        opacity: 0;
        transition: opacity 0.3s ease, transform 0.3s ease;
        transform: translateX(100%);
    `;
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; margin-left: 10px; cursor: pointer; font-size: 16px;">&times;</button>
        </div>
    `;

    document.body.appendChild(toast);

    // Show toast with animation
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 100);

    // Auto-hide after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, 3000);
}

// Form validation
function validateIPAddress(ip) {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const ipInput = form.querySelector('input[name="ip_address"]');
    if (ipInput && !validateIPAddress(ipInput.value)) {
        showToast('Please enter a valid IP address', 'danger');
        ipInput.focus();
        return false;
    }

    return true;
}

// Add form validation to add address modal
document.addEventListener('DOMContentLoaded', function() {
    const addAddressForm = document.querySelector('#addAddressModal form');
    if (addAddressForm) {
        addAddressForm.addEventListener('submit', function(e) {
            if (!validateForm(this.id)) {
                e.preventDefault();
            }
        });
    }
});

// Status badge animation
function animateStatusChange(element) {
    element.classList.add('animate');
    setTimeout(() => {
        element.classList.remove('animate');
    }, 500);
}

// WebSocket functionality
let socket = null;
let lastNotificationTime = 0;
const NOTIFICATION_THROTTLE = 5000; // 5 seconds between notifications

function initializeWebSocket() {
    // Initialize Socket.IO connection
    socket = io();
    
    // Handle connection events
    socket.on('connect', function() {
        console.log('Connected to WebSocket server');
        // Connection notifications disabled to reduce spam
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket server');
        // Disconnect notifications disabled to reduce spam
    });
    
    // Handle status updates
    socket.on('status_update', function(data) {
        console.log('Status update received:', data);
        handleStatusUpdate(data);
    });
    
    // Handle dashboard updates
    socket.on('dashboard_update', function(data) {
        console.log('Dashboard update received:', data);
        updateDashboardStats(data);
    });
}

function handleStatusUpdate(data) {
    if (data.type === 'status_changes') {
        isWebSocketUpdating = true;
        data.data.forEach(change => {
            updateAddressStatus(change);
            showStatusChangeNotification(change);
        });
        // Clear the flag after updates complete
        setTimeout(() => {
            isWebSocketUpdating = false;
        }, 100);
    }
}

function updateAddressStatus(change) {
    // Save current scroll position
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Update status badges in tables
    const addressRows = document.querySelectorAll(`tr[data-address-id="${change.id}"]`);
    addressRows.forEach(row => {
        const statusCell = row.querySelector('.status-badge');
        if (statusCell) {
            // Remove old status classes
            statusCell.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-secondary');
            
            // Add new status class and update content
            let statusClass = 'bg-secondary';
            let statusIcon = '❓';
            let statusText = 'Неизвестно';
            
            switch (change.new_status) {
                case 'up':
                    statusClass = 'bg-success';
                    statusIcon = '✅';
                    statusText = 'Онлайн';
                    break;
                case 'down':
                    statusClass = 'bg-danger';
                    statusIcon = '❌';
                    statusText = 'Оффлайн';
                    break;
                case 'error':
                    statusClass = 'bg-warning';
                    statusIcon = '⚠️';
                    statusText = 'Ошибка';
                    break;
            }
            
            statusCell.className = `badge ${statusClass}`;
            statusCell.innerHTML = `<span style="margin-right: 4px;">${statusIcon}</span>${statusText}`;
            
            // Animate the change
            animateStatusChange(statusCell);
        }
        
        // Update timestamp
        const timestampCell = row.querySelector('.timestamp');
        if (timestampCell) {
            const timestamp = new Date(change.timestamp);
            timestampCell.textContent = timestamp.toLocaleString('ru-RU');
        }
    });
    
    // Re-apply active filter after status updates
    reapplyActiveFilter();
    
    // Restore scroll position
    window.scrollTo(0, scrollTop);
}

function updateDashboardStats(data) {
    // Mark that we're updating dashboard stats
    const isDashboardUpdating = true;
    
    // Update summary cards using the new horizontal layout
    const statusGrid = document.querySelector('.status-grid');
    if (statusGrid) {
        const totalItem = statusGrid.querySelector('.status-item.info .status-number');
        const upItem = statusGrid.querySelector('.status-item.success .status-number');
        const downItem = statusGrid.querySelector('.status-item.danger .status-number');
        const errorItem = statusGrid.querySelector('.status-item.warning .status-number');
        const unknownItem = statusGrid.querySelector('.status-item:not(.info):not(.success):not(.danger):not(.warning) .status-number');
        
        if (totalItem) totalItem.textContent = data.total;
        if (upItem) upItem.textContent = data.up;
        if (downItem) downItem.textContent = data.down;
        if (errorItem) errorItem.textContent = data.error;
        if (unknownItem) unknownItem.textContent = data.unknown;
        
        // Subtle highlight for updated cards without interfering with clicks
        const statusItems = statusGrid.querySelectorAll('.status-item');
        statusItems.forEach(item => {
            // Only animate if not being clicked
            if (!item.matches(':active')) {
                item.style.transition = 'background-color 0.3s ease';
                item.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                setTimeout(() => {
                    item.style.backgroundColor = '';
                }, 500);
            }
        });
    }
}

function showStatusChangeNotification(change) {
    const now = Date.now();
    
    // Throttle notifications to prevent spam
    if (now - lastNotificationTime < NOTIFICATION_THROTTLE) {
        return;
    }
    
    const statusText = change.new_status === 'up' ? 'онлайн' : 
                      change.new_status === 'down' ? 'оффлайн' : 'ошибка';
    
    const toastType = change.new_status === 'up' ? 'success' : 
                     change.new_status === 'down' ? 'danger' : 'warning';
    
    showToast(`${change.ip_address} теперь ${statusText}`, toastType);
    lastNotificationTime = now;
}

// Status filtering functionality
let currentFilter = null;
let isWebSocketUpdating = false;

function initializeStatusFiltering() {
    const statusCards = document.querySelectorAll('.clickable-card');
    
    statusCards.forEach(card => {
        card.addEventListener('click', function() {
            const status = this.dataset.status;
            filterByStatus(status);
        });
    });
    
    // Add click handler for Total card to clear filter
    const totalCard = document.querySelector('.card-total');
    if (totalCard) {
        totalCard.style.cursor = 'pointer';
        totalCard.addEventListener('click', function() {
            clearStatusFilter();
        });
    }
}

function filterByStatus(status) {
    // Don't change filter during WebSocket updates
    if (isWebSocketUpdating) return;
    
    // Remove previous filtering
    clearStatusFilter();
    
    // Set current filter
    currentFilter = status;
    
    // Get all address rows
    const addressRows = document.querySelectorAll('[data-address-id]');
    
    // Show only rows with matching status
    addressRows.forEach(row => {
        const statusBadge = row.querySelector('.status-badge');
        if (statusBadge) {
            const rowStatus = getRowStatus(statusBadge);
            if (rowStatus === status) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
    
    // Show filter indicator
    showFilterIndicator(status);
}

function getRowStatus(statusBadge) {
    if (statusBadge.classList.contains('bg-success')) return 'up';
    if (statusBadge.classList.contains('bg-danger')) return 'down';
    if (statusBadge.classList.contains('bg-warning')) return 'error';
    if (statusBadge.classList.contains('bg-secondary')) return 'unknown';
    return 'unknown';
}

function clearStatusFilter() {
    // Don't change filter during WebSocket updates
    if (isWebSocketUpdating) return;
    
    currentFilter = null;
    
    const addressRows = document.querySelectorAll('[data-address-id]');
    addressRows.forEach(row => {
        row.style.display = '';
    });
    
    // Remove filter indicator
    const filterIndicator = document.getElementById('filterIndicator');
    if (filterIndicator) {
        filterIndicator.remove();
    }
}

function reapplyActiveFilter() {
    if (currentFilter) {
        // Get all address rows
        const addressRows = document.querySelectorAll('[data-address-id]');
        
        // Show only rows with matching status
        addressRows.forEach(row => {
            const statusBadge = row.querySelector('.status-badge');
            if (statusBadge) {
                const rowStatus = getRowStatus(statusBadge);
                if (rowStatus === currentFilter) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }
}

function showFilterIndicator(status) {
    const statusText = {
        'up': 'Онлайн',
        'down': 'Оффлайн',
        'error': 'Ошибка',
        'unknown': 'Неизвестно'
    };
    
    // Remove existing indicator
    const existingIndicator = document.getElementById('filterIndicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    // Create new indicator
    const indicator = document.createElement('div');
    indicator.id = 'filterIndicator';
    indicator.className = 'alert alert-info alert-dismissible fade show';
    indicator.innerHTML = `
        <span style="margin-right: 8px;">🔍</span>
        Отображаются только устройства со статусом: <strong>${statusText[status]}</strong>
        <button type="button" class="btn btn-sm btn-outline-info ms-2" onclick="clearStatusFilter()">
            <span style="margin-right: 4px;">❌</span>Показать все
        </button>
        <button type="button" class="btn-close" aria-label="Close" onclick="clearStatusFilter()"></button>
    `;
    
    // Insert before the network addresses card
    const networkCard = document.querySelector('.card .card-header h5');
    if (networkCard) {
        const cardElement = networkCard.closest('.card');
        if (cardElement) {
            cardElement.parentNode.insertBefore(indicator, cardElement);
        }
    }
}

// Tab state management
function saveActiveTab() {
    const activeTab = document.querySelector('.nav-link.active');
    if (activeTab) {
        const tabId = activeTab.id;
        if (tabId) {
            localStorage.setItem('currentActiveTab', tabId);
        }
    }
}

function getCurrentActiveTab() {
    return localStorage.getItem('currentActiveTab');
}

function preserveActiveTab() {
    const savedTab = getCurrentActiveTab();
    if (savedTab) {
        const tabElement = document.getElementById(savedTab);
        if (tabElement && !tabElement.classList.contains('active')) {
            // Click the tab to activate it
            tabElement.click();
        }
    }
}

// Add event listeners for tab changes
document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            saveActiveTab();
        });
    });
    
    // Preserve active tab on page load
    preserveActiveTab();
});

// Export functions for use in templates
window.NetworkMonitor = {
    pingAddress,
    showToast,
    validateIPAddress,
    validateForm,
    animateStatusChange,
    clearStatusFilter,
    socket,
    saveActiveTab,
    preserveActiveTab
};
