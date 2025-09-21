// Novel Translator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                // Store original content
                submitBtn.setAttribute('data-original-content', submitBtn.innerHTML);
                
                // Add loading state
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 30 seconds as fallback
                setTimeout(function() {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = submitBtn.getAttribute('data-original-content');
                        submitBtn.disabled = false;
                    }
                }, 30000);
            }
        });
    });

    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            validateFileUpload(this);
        });
    });

    function validateFileUpload(input) {
        const file = input.files[0];
        if (!file) return;

        const maxSize = 100 * 1024 * 1024; // 100MB
        const allowedTypes = {
            'chapter': ['.txt', '.text'],
            'novel': ['.zip']
        };

        // Check file size
        if (file.size > maxSize) {
            showAlert('danger', 'File size exceeds 100MB limit.');
            input.value = '';
            return false;
        }

        // Check file type based on input name/id
        let inputType = 'chapter';
        if (input.accept && input.accept.includes('.zip')) {
            inputType = 'novel';
        }

        const fileName = file.name.toLowerCase();
        const isValidType = allowedTypes[inputType].some(ext => fileName.endsWith(ext));

        if (!isValidType) {
            const expectedTypes = allowedTypes[inputType].join(', ');
            showAlert('danger', `Please select a valid file type: ${expectedTypes}`);
            input.value = '';
            return false;
        }

        return true;
    }

    // Show alert helper function
    function showAlert(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
        alertContainer.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of main content
        const main = document.querySelector('main');
        if (main && main.firstChild) {
            main.insertBefore(alertContainer, main.firstChild);
        }

        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            if (alertContainer && alertContainer.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alertContainer);
                bsAlert.close();
            }
        }, 5000);
    }

    // Character counter for text areas
    const textAreas = document.querySelectorAll('textarea');
    textAreas.forEach(function(textarea) {
        // Create counter element
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.style.fontSize = '0.875rem';
        
        // Insert after textarea
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        
        // Update counter
        function updateCounter() {
            const length = textarea.value.length;
            const words = textarea.value.trim() ? textarea.value.trim().split(/\s+/).length : 0;
            counter.innerHTML = `<i class="fas fa-info-circle me-1"></i>${length} characters, ${words} words`;
        }
        
        // Initial count
        updateCounter();
        
        // Update on input
        textarea.addEventListener('input', updateCounter);
    });

    // Copy to clipboard functionality
    function addCopyButton(element) {
        if (element.querySelector('.copy-btn')) return; // Already has copy button
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary copy-btn position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy to clipboard';
        
        // Make parent relative if needed
        if (getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
        }
        
        element.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const text = element.textContent || element.innerText;
            
            navigator.clipboard.writeText(text).then(function() {
                // Change button to success state
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                copyBtn.classList.remove('btn-outline-secondary');
                copyBtn.classList.add('btn-success');
                
                // Reset after 2 seconds
                setTimeout(function() {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                    copyBtn.classList.remove('btn-success');
                    copyBtn.classList.add('btn-outline-secondary');
                }, 2000);
            }).catch(function(err) {
                console.error('Failed to copy text: ', err);
                showAlert('danger', 'Failed to copy to clipboard');
            });
        });
    }

    // Add copy buttons to text content areas
    const textContents = document.querySelectorAll('.text-content');
    textContents.forEach(addCopyButton);

    // Progress tracking for novel translation (WebSocket would be better in production)
    function trackTranslationProgress() {
        const progressCard = document.getElementById('progressCard');
        if (!progressCard || progressCard.style.display === 'none') return;

        // This is a simplified version - in production, use WebSocket or Server-Sent Events
        let progress = 0;
        const interval = setInterval(function() {
            progress += Math.random() * 5;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                
                // Show completion
                updateProgressDisplay(100, 'Translation completed! Preparing download...');
                
                setTimeout(function() {
                    progressCard.style.display = 'none';
                }, 3000);
            } else {
                updateProgressDisplay(progress, `Processing chapter ${Math.floor(progress/10) + 1}...`);
            }
        }, 1000);
    }

    function updateProgressDisplay(percent, message) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar && progressText) {
            progressBar.style.width = percent + '%';
            progressBar.innerHTML = `<span class="fw-bold">${Math.round(percent)}%</span>`;
            progressText.innerHTML = `<i class="fas fa-cogs me-2"></i>${message}`;
        }
    }

    // Initialize progress tracking if on novel page
    if (window.location.pathname === '/novel') {
        // Check for existing progress every few seconds
        setInterval(trackTranslationProgress, 2000);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.querySelector('form:hover') || document.querySelector('form');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.click();
                }
            }
        }
        
        // Escape to close modals/alerts
        if (e.key === 'Escape') {
            const openAlerts = document.querySelectorAll('.alert.show');
            openAlerts.forEach(function(alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }
    });

    // Language detection preview (client-side basic detection)
    function detectLanguageBasic(text) {
        if (!text || text.length < 10) return 'Unknown';
        
        const sample = text.toLowerCase().substring(0, 200);
        
        // Simple pattern matching for demonstration
        if (/\b(the|and|of|to|a|in|is|it|you|that|he|was|for|on|are|as|with|his|they)\b/g.test(sample)) {
            return 'English';
        } else if (/\b(el|la|de|que|y|a|en|un|es|se|no|te|lo|le|da|su|por|son|con|para)\b/g.test(sample)) {
            return 'Spanish';
        } else if (/\b(le|de|et|à|un|il|être|en|avoir|que|pour|dans|ce|son|une|sur|avec|ne)\b/g.test(sample)) {
            return 'French';
        } else if (/\b(der|die|und|in|den|von|zu|das|mit|sich|des|auf|für|ist|im|dem|nicht)\b/g.test(sample)) {
            return 'German';
        }
        
        return 'Unknown';
    }

    // Add language detection preview to text areas
    const mainTextArea = document.getElementById('text_input');
    if (mainTextArea) {
        let detectionTimeout;
        
        mainTextArea.addEventListener('input', function() {
            clearTimeout(detectionTimeout);
            
            detectionTimeout = setTimeout(function() {
                const text = mainTextArea.value;
                if (text.length > 50) {
                    const detectedLang = detectLanguageBasic(text);
                    
                    // Show detection result
                    let detectionResult = mainTextArea.parentNode.querySelector('.language-detection');
                    if (!detectionResult) {
                        detectionResult = document.createElement('div');
                        detectionResult.className = 'language-detection form-text mt-2';
                        mainTextArea.parentNode.appendChild(detectionResult);
                    }
                    
                    detectionResult.innerHTML = `<i class="fas fa-search me-1"></i>Detected language: <strong>${detectedLang}</strong>`;
                }
            }, 1000);
        });
    }
});

// Utility functions
window.NovelTranslator = {
    showAlert: function(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
        alertContainer.innerHTML = `
            <i class="fas fa-${type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const main = document.querySelector('main');
        if (main && main.firstChild) {
            main.insertBefore(alertContainer, main.firstChild);
        }

        setTimeout(function() {
            if (alertContainer && alertContainer.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alertContainer);
                bsAlert.close();
            }
        }, 5000);
    },
    
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    validateFile: function(file, maxSize, allowedExtensions) {
        if (file.size > maxSize) {
            return { valid: false, error: `File size exceeds ${this.formatFileSize(maxSize)} limit.` };
        }
        
        const fileName = file.name.toLowerCase();
        const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        if (!isValidExtension) {
            return { valid: false, error: `Invalid file type. Allowed: ${allowedExtensions.join(', ')}` };
        }
        
        return { valid: true };
    }
};