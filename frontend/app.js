/**
 * DefectVision AI - Modern JavaScript
 * YOLOv11 Defect Detection System
 */

// Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    MAX_FILE_SIZE: 16 * 1024 * 1024, // 16MB
    ACCEPTED_FORMATS: ['image/jpeg', 'image/png', 'image/bmp', 'image/jpg'],
    ANIMATION_DURATION: 300,
};

// State Management
const state = {
    currentImage: null,
    currentFile: null,
    detectionResults: null,
    isProcessing: false,
};

// DOM Elements
const elements = {
    // Navigation
    navLinks: document.querySelectorAll('.nav-link'),
    pages: document.querySelectorAll('.page'),
    
    // Upload
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    imagePreview: document.getElementById('imagePreview'),
    previewImage: document.getElementById('previewImage'),
    imageInfo: document.getElementById('imageInfo'),
    removeImage: document.getElementById('removeImage'),
    
    // Controls
    confidenceSlider: document.getElementById('confidenceSlider'),
    confidenceValue: document.getElementById('confidenceValue'),
    iouSlider: document.getElementById('iouSlider'),
    iouValue: document.getElementById('iouValue'),
    detectBtn: document.getElementById('detectBtn'),
    
    // Results
    resultsSection: document.getElementById('resultsSection'),
    totalDefects: document.getElementById('totalDefects'),
    crackCount: document.getElementById('crackCount'),
    scratchCount: document.getElementById('scratchCount'),
    deformationCount: document.getElementById('deformationCount'),
    missingCount: document.getElementById('missingCount'),
    avgConfidence: document.getElementById('avgConfidence'),
    resultImage: document.getElementById('resultImage'),
    detailsTableBody: document.getElementById('detailsTableBody'),
    downloadBtn: document.getElementById('downloadBtn'),
    
    // Overlay
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer'),
};

// ============================================
// Navigation
// ============================================

function initNavigation() {
    elements.navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            switchPage(page);
        });
    });
}

function switchPage(pageName) {
    // Update nav links
    elements.navLinks.forEach(link => {
        link.classList.toggle('active', link.dataset.page === pageName);
    });
    
    // Update pages
    elements.pages.forEach(page => {
        page.classList.toggle('active', page.id === `${pageName}Page`);
    });
}

// ============================================
// Upload Handling
// ============================================

function initUpload() {
    // Click to upload
    elements.uploadZone.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    // File input change
    elements.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });
    
    // Drag and drop
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.add('drag-over');
    });
    
    elements.uploadZone.addEventListener('dragleave', () => {
        elements.uploadZone.classList.remove('drag-over');
    });
    
    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('drag-over');
        
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });
    
    // Remove image
    elements.removeImage.addEventListener('click', (e) => {
        e.stopPropagation();
        clearImage();
    });
}

function handleFile(file) {
    // Validate file type
    if (!CONFIG.ACCEPTED_FORMATS.includes(file.type)) {
        showToast('Please upload a valid image (JPG, PNG, or BMP)', 'error');
        return;
    }
    
    // Validate file size
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showToast('File size must be less than 16MB', 'error');
        return;
    }
    
    // Store file
    state.currentFile = file;
    
    // Read and display image
    const reader = new FileReader();
    reader.onload = (e) => {
        state.currentImage = e.target.result;
        displayPreview(e.target.result, file);
    };
    reader.readAsDataURL(file);
}

function displayPreview(imageSrc, file) {
    // Show preview
    elements.previewImage.src = imageSrc;
    elements.uploadZone.style.display = 'none';
    elements.imagePreview.style.display = 'block';
    
    // Update info
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    elements.imageInfo.textContent = `${file.name} • ${sizeMB} MB`;
    
    // Enable detect button
    elements.detectBtn.disabled = false;
    
    // Hide results
    elements.resultsSection.style.display = 'none';
    
    // Show success toast
    showToast('Image uploaded successfully', 'success');
}

function clearImage() {
    state.currentImage = null;
    state.currentFile = null;
    state.detectionResults = null;
    
    elements.uploadZone.style.display = 'block';
    elements.imagePreview.style.display = 'none';
    elements.previewImage.src = '';
    elements.imageInfo.textContent = '';
    elements.fileInput.value = '';
    
    elements.detectBtn.disabled = true;
    elements.resultsSection.style.display = 'none';
}

// ============================================
// Controls
// ============================================

function initControls() {
    // Confidence slider
    elements.confidenceSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        elements.confidenceValue.textContent = `${value}%`;
    });
    
    // IOU slider
    elements.iouSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        elements.iouValue.textContent = `${value}%`;
    });
    
    // Detect button
    elements.detectBtn.addEventListener('click', runDetection);
    
    // Download button
    elements.downloadBtn.addEventListener('click', downloadResults);
}

// ============================================
// Detection
// ============================================

async function runDetection() {
    if (!state.currentFile || state.isProcessing) return;
    
    state.isProcessing = true;
    showLoading(true);
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('image', state.currentFile);
        formData.append('confidence', elements.confidenceSlider.value / 100);
        formData.append('iou', elements.iouSlider.value / 100);
        
        // Call API
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/detect`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            state.detectionResults = result;
            displayResults(result);
            showToast('Detection completed successfully', 'success');
        } else {
            throw new Error(result.error || 'Detection failed');
        }
        
    } catch (error) {
        console.error('Detection error:', error);
        showToast(`Detection failed: ${error.message}`, 'error');
    } finally {
        state.isProcessing = false;
        showLoading(false);
    }
}

// ============================================
// Results Display
// ============================================

function displayResults(result) {
    // Animate transition
    elements.resultsSection.style.display = 'block';
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
    
    // Update statistics
    updateStatistics(result);
    
    // Display annotated image
    if (result.image) {
        elements.resultImage.src = result.image;
    }
    
    // Populate details table
    populateDetailsTable(result.detections);
}

function updateStatistics(result) {
    const { summary } = result;
    
    // Animate numbers
    animateNumber(elements.totalDefects, summary.total_defects);
    animateNumber(elements.crackCount, summary.defect_types.crack || 0);
    animateNumber(elements.scratchCount, summary.defect_types.scratch || 0);
    animateNumber(elements.deformationCount, summary.defect_types.deformation || 0);
    animateNumber(elements.missingCount, summary.defect_types.missing || 0);
    
    // Update confidence
    const avgConf = (summary.avg_confidence * 100).toFixed(1);
    elements.avgConfidence.textContent = `${avgConf}%`;
}

function animateNumber(element, target) {
    const duration = 1000;
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

function populateDetailsTable(detections) {
    elements.detailsTableBody.innerHTML = '';
    
    if (!detections || detections.length === 0) {
        elements.detailsTableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: var(--color-text-muted);">
                    No defects detected
                </td>
            </tr>
        `;
        return;
    }
    
    detections.forEach((det, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>
                <span style="display: inline-flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: ${getDefectColor(det.class)};"></span>
                    <span style="text-transform: capitalize; font-weight: 500;">${det.class}</span>
                </span>
            </td>
            <td>
                <span style="color: ${getConfidenceColor(det.confidence)}; font-weight: 600;">
                    ${(det.confidence * 100).toFixed(1)}%
                </span>
            </td>
            <td style="font-family: monospace; font-size: 0.875rem;">
                (${det.center[0]}, ${det.center[1]})
            </td>
            <td style="font-family: monospace; font-size: 0.875rem;">
                ${det.bbox[2]} × ${det.bbox[3]}
            </td>
        `;
        elements.detailsTableBody.appendChild(row);
    });
}

function getDefectColor(defectType) {
    const colors = {
        crack: '#ef4444',
        scratch: '#f59e0b',
        deformation: '#8b5cf6',
        missing: '#f97316',
    };
    return colors[defectType] || '#3b82f6';
}

function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
}

// ============================================
// Download Results
// ============================================

function downloadResults() {
    if (!state.detectionResults) return;
    
    // Download annotated image
    const link = document.createElement('a');
    link.href = elements.resultImage.src;
    link.download = `defect_detection_${Date.now()}.jpg`;
    link.click();
    
    showToast('Results downloaded successfully', 'success');
}

// ============================================
// UI Utilities
// ============================================

function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.add('active');
    } else {
        elements.loadingOverlay.classList.remove('active');
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = getToastIcon(type);
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

function getToastIcon(type) {
    const icons = {
        success: `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 24px; height: 24px; color: #10b981;">
                <path d="M20 6L9 17L4 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `,
        error: `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 24px; height: 24px; color: #ef4444;">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path d="M12 8V12" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="16" r="1" fill="currentColor"/>
            </svg>
        `,
        info: `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 24px; height: 24px; color: #3b82f6;">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path d="M12 16V12" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="8" r="1" fill="currentColor"/>
            </svg>
        `,
    };
    return icons[type] || icons.info;
}

// ============================================
// Keyboard Shortcuts
// ============================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + U: Upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            elements.fileInput.click();
        }
        
        // Ctrl/Cmd + D: Detect
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            if (!elements.detectBtn.disabled) {
                runDetection();
            }
        }
        
        // Escape: Clear image
        if (e.key === 'Escape' && state.currentImage) {
            clearImage();
        }
    });
}

// ============================================
// Enhanced Features
// ============================================

function initEnhancedFeatures() {
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.glass-card').forEach(card => {
        observer.observe(card);
    });
    
    // Add parallax effect to background
    let ticking = false;
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const scrolled = window.pageYOffset;
                const bgGradient = document.querySelector('.bg-gradient');
                if (bgGradient) {
                    bgGradient.style.transform = `translateY(${scrolled * 0.3}px)`;
                }
                ticking = false;
            });
            ticking = true;
        }
    });
}

// ============================================
// System Status
// ============================================

async function checkSystemStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/health`);
        const data = await response.json();
        
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-pulse');
        
        if (data.status === 'healthy') {
            statusText.textContent = 'System Active';
            statusDot.style.background = '#10b981';
        } else {
            statusText.textContent = 'System Offline';
            statusDot.style.background = '#ef4444';
        }
    } catch (error) {
        console.error('Status check failed:', error);
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-pulse');
        statusText.textContent = 'System Offline';
        statusDot.style.background = '#ef4444';
    }
}

// ============================================
// Initialization
// ============================================

function init() {
    console.log('🚀 DefectVision AI - Initializing...');
    
    // Initialize all components
    initNavigation();
    initUpload();
    initControls();
    initKeyboardShortcuts();
    initEnhancedFeatures();
    
    // Check system status
    checkSystemStatus();
    
    // Periodic status check (every 30 seconds)
    setInterval(checkSystemStatus, 30000);
    
    console.log('✅ DefectVision AI - Ready!');
    
    // Show welcome message
    setTimeout(() => {
        showToast('Welcome to DefectVision AI - Powered by YOLOv11', 'info');
    }, 1000);
}

// Start application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
