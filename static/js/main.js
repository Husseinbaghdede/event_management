// Main JavaScript for Event Scheduler

// Global utilities and event handlers
class EventScheduler {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupQuickSearch();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Auto-hide alerts after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.alert').forEach(alert => {
                if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                    this.fadeOut(alert);
                }
            });
        }, 5000);

        // Enhanced form interactions
        this.setupFormEnhancements();
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });

        // Add loading states to buttons
        this.setupButtonLoading();
    }

    setupQuickSearch() {
        const quickSearchInput = document.querySelector('input[name="q"]');
        if (quickSearchInput) {
            let searchTimeout;
            
            quickSearchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        this.performQuickSearch(query);
                    }, 300);
                } else {
                    this.hideSearchSuggestions();
                }
            });

            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-container')) {
                    this.hideSearchSuggestions();
                }
            });
        }
    }

    async performQuickSearch(query) {
        try {
            const response = await fetch(`/search/api/quick-search?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();
            
            if (data.success && data.results.length > 0) {
                this.showSearchSuggestions(data.results, query);
            } else {
                this.hideSearchSuggestions();
            }
        } catch (error) {
            console.error('Quick search error:', error);
            this.hideSearchSuggestions();
        }
    }

    showSearchSuggestions(results, query) {
        let suggestionsContainer = document.getElementById('searchSuggestions');
        
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.id = 'searchSuggestions';
            suggestionsContainer.className = 'position-absolute bg-white border rounded-3 shadow-lg mt-1 w-100 z-index-1000';
            suggestionsContainer.style.cssText = 'z-index: 1000; max-height: 300px; overflow-y: auto;';
            
            const searchInput = document.querySelector('input[name="q"]');
            searchInput.parentNode.style.position = 'relative';
            searchInput.parentNode.appendChild(suggestionsContainer);
        }

        const suggestionsHTML = results.map(event => `
            <div class="suggestion-item p-3 border-bottom hover-bg-light cursor-pointer" 
                 onclick="window.location.href='/events/edit/${event.id}'">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1 fw-bold">${this.highlightText(event.title, query)}</h6>
                        <small class="text-muted">
                            <i class="bi bi-calendar3 me-1"></i>${this.formatDate(event.date)}
                            ${event.location ? `<i class="bi bi-geo-alt ms-2 me-1"></i>${event.location}` : ''}
                        </small>
                    </div>
                    <span class="badge bg-${this.getStatusColor(event.status)}">${event.status}</span>
                </div>
            </div>
        `).join('');

        suggestionsContainer.innerHTML = suggestionsHTML + `
            <div class="p-2 text-center border-top">
                <a href="/search?q=${encodeURIComponent(query)}" class="btn btn-sm btn-outline-primary">
                    View all results (${results.length}+)
                </a>
            </div>
        `;
    }

    hideSearchSuggestions() {
        const suggestionsContainer = document.getElementById('searchSuggestions');
        if (suggestionsContainer) {
            suggestionsContainer.remove();
        }
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.showValidationErrors(form);
                }
                form.classList.add('was-validated');
            });
        });
    }

    setupFormEnhancements() {
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            this.autoResize(textarea);
            textarea.addEventListener('input', () => this.autoResize(textarea));
        });

        // Date input enhancements
        const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
        dateInputs.forEach(input => {
            if (!input.value) {
                // Set default to current date + 1 hour
                const now = new Date();
                now.setHours(now.getHours() + 1);
                now.setMinutes(0);
                input.value = now.toISOString().slice(0, 16);
            }
        });

        // Character count for textareas
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            this.addCharacterCounter(textarea);
        });
    }

    setupButtonLoading() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && form.checkValidity()) {
                    this.setButtonLoading(submitBtn, true);
                }
            });
        });
    }

    // Utility functions
    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    addCharacterCounter(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted small mt-1';
        counter.textContent = `0 / ${maxLength}`;
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', () => {
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength} / ${maxLength}`;
            
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
            
            if (currentLength >= maxLength) {
                counter.classList.add('text-danger');
                counter.classList.remove('text-warning');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    }

    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Loading...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    }

    showValidationErrors(form) {
        const invalidFields = form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            invalidFields[0].focus();
            this.showToast('Please fill in all required fields correctly', 'error');
        }
    }

    fadeOut(element) {
        element.style.transition = 'opacity 0.5s ease';
        element.style.opacity = '0';
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    }

    highlightText(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    getStatusColor(status) {
        const colors = {
            'upcoming': 'primary',
            'attending': 'success',
            'maybe': 'warning',
            'declined': 'danger'
        };
        return colors[status] || 'secondary';
    }

    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi bi-${this.getToastIcon(type)} me-2"></i>${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // API helpers
    async makeApiCall(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showToast('An error occurred. Please try again.', 'error');
            throw error;
        }
    }
}

// Event-specific functions (global scope for template access)
window.EventSchedulerApp = {
    // Delete event function
    deleteEvent: async function(eventId, eventTitle) {
        if (!confirm(`Are you sure you want to delete "${eventTitle}"?`)) {
            return;
        }

        try {
            await fetch(`/events/delete/${eventId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            // Show success message
            app.showToast(`Event "${eventTitle}" deleted successfully`, 'success');
            
            // Reload page or redirect
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('Error deleting event:', error);
            app.showToast('Failed to delete event', 'error');
        }
    },

    // View event details
    viewEventDetails: async function(eventId) {
        try {
            const data = await app.makeApiCall(`/events/api/${eventId}`);
            
            if (data.success) {
                const event = data.event;
                const content = `
                    <div class="event-details-modal">
                        <div class="row mb-3">
                            <div class="col-md-8">
                                <h4 class="text-primary fw-bold">${event.title}</h4>
                            </div>
                            <div class="col-md-4 text-md-end">
                                <span class="badge bg-${app.getStatusColor(event.status)} fs-6">
                                    ${event.status.charAt(0).toUpperCase() + event.status.slice(1)}
                                </span>
                            </div>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong><i class="bi bi-calendar3 me-2"></i>Date & Time:</strong><br>
                                <span class="text-muted">${app.formatDate(event.date)}</span>
                            </div>
                            ${event.location ? `
                            <div class="col-md-6">
                                <strong><i class="bi bi-geo-alt me-2"></i>Location:</strong><br>
                                <span class="text-muted">${event.location}</span>
                            </div>
                            ` : ''}
                        </div>
                        
                        ${event.description ? `
                        <div class="mb-3">
                            <strong><i class="bi bi-card-text me-2"></i>Description:</strong><br>
                            <p class="text-muted mt-2">${event.description}</p>
                        </div>
                        ` : ''}
                        
                        <div class="row text-muted small">
                            <div class="col-md-6">
                                <strong>Created:</strong> ${app.formatDate(event.created_at)}
                            </div>
                            <div class="col-md-6">
                                <strong>Last Updated:</strong> ${app.formatDate(event.updated_at)}
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById('eventDetailsContent').innerHTML = content;
                document.getElementById('editEventBtn').onclick = () => {
                    window.location.href = `/events/edit/${eventId}`;
                };
                
                new bootstrap.Modal(document.getElementById('eventDetailsModal')).show();
            }
        } catch (error) {
            app.showToast('Failed to load event details', 'error');
        }
    },

    // Enhance description with AI
    enhanceDescription: async function() {
        const titleInput = document.getElementById('title');
        const locationInput = document.getElementById('location');
        const descriptionInput = document.getElementById('description');
        const enhanceBtn = event.target;
        
        if (!titleInput.value.trim()) {
            app.showToast('Please enter an event title first', 'warning');
            titleInput.focus();
            return;
        }
        
        // Set loading state
        app.setButtonLoading(enhanceBtn, true);
        
        try {
            const data = await app.makeApiCall('/events/api/enhance-description', {
                method: 'POST',
                body: JSON.stringify({
                    title: titleInput.value,
                    location: locationInput.value
                })
            });
            
            if (data.success) {
                descriptionInput.value = data.description;
                descriptionInput.focus();
                app.autoResize(descriptionInput);
                app.showToast('Description enhanced successfully!', 'success');
            }
        } catch (error) {
            app.showToast('Failed to enhance description', 'error');
        } finally {
            app.setButtonLoading(enhanceBtn, false);
        }
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for quick search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + N for new event
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        window.location.href = '/events/add';
    }
    
    // Escape to close modals/suggestions
    if (e.key === 'Escape') {
        app.hideSearchSuggestions();
        // Close any open modals
        document.querySelectorAll('.modal.show').forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new EventScheduler();
    
    // Make functions globally available for templates
    window.deleteEvent = window.EventSchedulerApp.deleteEvent;
    window.viewEventDetails = window.EventSchedulerApp.viewEventDetails;
    window.enhanceDescription = window.EventSchedulerApp.enhanceDescription;
    
    // Add fade-in animation to main content
    document.querySelector('main').classList.add('fade-in');
    
    console.log('Event Scheduler initialized successfully!');
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js') // Uncomment when adding PWA features
    });
}

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventScheduler;
}