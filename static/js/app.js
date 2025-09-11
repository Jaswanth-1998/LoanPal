// Daily Loan Collection System - JavaScript

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancements
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Loan calculation functionality
    setupLoanCalculator();
    
    // File upload preview
    setupFilePreview();
});

// Loan calculation setup
function setupLoanCalculator() {
    const loanForm = document.getElementById('loanForm');
    if (!loanForm) return;

    const amountInput = document.getElementById('loan_amount');
    const periodSelect = document.getElementById('period');
    const durationInput = document.getElementById('duration_days');
    const interestInput = document.getElementById('interest_rate');
    
    // Auto-populate interest rate based on period
    if (periodSelect && interestInput) {
        periodSelect.addEventListener('change', function() {
            const period = this.value;
            if (period) {
                fetch(`/api/interest-rate/${period}`)
                    .then(response => response.json())
                    .then(data => {
                        interestInput.value = data.rate || 10.0;
                        calculateLoan();
                    })
                    .catch(console.error);
            }
        });
    }

    // Auto-calculate loan details
    [amountInput, periodSelect, durationInput, interestInput].forEach(input => {
        if (input) {
            input.addEventListener('input', calculateLoan);
            input.addEventListener('change', calculateLoan);
        }
    });
}

// Calculate loan details
function calculateLoan() {
    const amount = document.getElementById('loan_amount')?.value;
    const period = document.getElementById('period')?.value;
    const duration = document.getElementById('duration_days')?.value;
    const interest = document.getElementById('interest_rate')?.value;

    if (!amount || !period || !duration || !interest) return;

    const data = {
        loan_amount: parseFloat(amount),
        period: period,
        duration_days: parseInt(duration),
        interest_rate: parseFloat(interest)
    };

    fetch('/api/calculate-loan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            console.error('Calculation error:', result.error);
            return;
        }
        
        // Update calculation display
        updateCalculationDisplay(result);
    })
    .catch(console.error);
}

// Update loan calculation display
function updateCalculationDisplay(calculation) {
    const displayElement = document.getElementById('calculationDisplay');
    if (!displayElement) return;

    let html = `
        <div class="card mt-3">
            <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-calculator"></i> Loan Calculation</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Total Interest:</strong> ₹${calculation.total_interest.toFixed(2)}</p>
                        <p><strong>Total Amount:</strong> ₹${calculation.total_amount.toFixed(2)}</p>
                    </div>
                    <div class="col-md-6">
    `;

    if (calculation.daily_amount) {
        html += `<p><strong>Daily Payment:</strong> ₹${calculation.daily_amount.toFixed(2)}</p>`;
    }
    if (calculation.weekly_amount) {
        html += `<p><strong>Weekly Payment:</strong> ₹${calculation.weekly_amount.toFixed(2)}</p>`;
    }
    if (calculation.monthly_amount) {
        html += `<p><strong>Monthly Payment:</strong> ₹${calculation.monthly_amount.toFixed(2)}</p>`;
    }

    html += `
                    </div>
                </div>
            </div>
        </div>
    `;

    displayElement.innerHTML = html;
}

// File upload preview setup
function setupFilePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (!file) return;
            
            const previewContainer = this.parentNode.querySelector('.file-preview') ||
                                   this.insertAdjacentElement('afterend', createPreviewContainer());
            
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <div class="mt-2">
                            <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                            <p class="small text-muted mt-1">${file.name} (${(file.size / 1024).toFixed(2)} KB)</p>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = `
                    <div class="mt-2">
                        <div class="alert alert-info">
                            <i class="bi bi-file-earmark"></i> ${file.name} (${(file.size / 1024).toFixed(2)} KB)
                        </div>
                    </div>
                `;
            }
        });
    });
}

// Create preview container
function createPreviewContainer() {
    const container = document.createElement('div');
    container.className = 'file-preview';
    return container;
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function showLoading(button) {
    if (button) {
        button.classList.add('loading');
        button.disabled = true;
    }
}

function hideLoading(button) {
    if (button) {
        button.classList.remove('loading');
        button.disabled = false;
    }
}