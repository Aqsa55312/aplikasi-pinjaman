// Global variables
let currentLoanId = null;

// DOM Elements
const loanForm = document.getElementById('loanForm');
const calculationPreview = document.getElementById('calculationPreview');
const receiptModal = document.getElementById('receiptModal');
const loadingOverlay = document.getElementById('loadingOverlay');

// Form inputs
const amountInput = document.getElementById('amount');
const rateInput = document.getElementById('rate');
const monthsInput = document.getElementById('months');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupCalculationPreview();
});

function setupEventListeners() {
    // Form submission
    loanForm.addEventListener('submit', handleLoanSubmission);
    
    // Real-time calculation preview
    [amountInput, rateInput, monthsInput].forEach(input => {
        input.addEventListener('input', updateCalculationPreview);
        input.addEventListener('change', updateCalculationPreview);
    });
    
    // Modal close on background click
    receiptModal.addEventListener('click', function(e) {
        if (e.target === receiptModal) {
            closeModal();
        }
    });
    
    // Format currency input
    amountInput.addEventListener('input', formatCurrencyInput);
}

function setupCalculationPreview() {
    updateCalculationPreview();
}

function formatCurrencyInput(e) {
    let value = e.target.value.replace(/[^\d]/g, '');
    e.target.value = value;
}

function updateCalculationPreview() {
    const amount = parseFloat(amountInput.value);
    const rate = parseFloat(rateInput.value);
    const months = parseInt(monthsInput.value);
    
    if (amount && rate >= 0 && months) {
        const calculation = calculateLoanDetails(amount, rate, months);
        
        document.getElementById('monthlyPayment').textContent = formatCurrency(calculation.monthlyPayment);
        document.getElementById('totalInterest').textContent = formatCurrency(calculation.totalInterest);
        document.getElementById('totalPayment').textContent = formatCurrency(calculation.totalPayment);
        
        calculationPreview.style.display = 'block';
        calculationPreview.style.animation = 'slideIn 0.5s ease-out';
    } else {
        calculationPreview.style.display = 'none';
    }
}

function calculateLoanDetails(principal, rate, months) {
    const monthlyRate = rate / 100 / 12;
    let monthlyPayment;
    
    if (monthlyRate === 0) {
        monthlyPayment = principal / months;
    } else {
        monthlyPayment = principal * (monthlyRate * Math.pow(1 + monthlyRate, months)) / 
                        (Math.pow(1 + monthlyRate, months) - 1);
    }
    
    const totalPayment = monthlyPayment * months;
    const totalInterest = totalPayment - principal;
    
    return {
        monthlyPayment: Math.round(monthlyPayment * 100) / 100,
        totalPayment: Math.round(totalPayment * 100) / 100,
        totalInterest: Math.round(totalInterest * 100) / 100
    };
}

async function handleLoanSubmission(e) {
    e.preventDefault();
    
    // Show loading
    showLoading();
    
    // Get form data
    const formData = new FormData(loanForm);
    const loanData = {
        name: formData.get('name'),
        phone: formData.get('phone'),
        address: formData.get('address'),
        amount: formData.get('amount'),
        rate: formData.get('rate'),
        months: formData.get('months')
    };
    
    // Validate form data
    const validation = validateLoanData(loanData);
    if (!validation.valid) {
        hideLoading();
        showAlert(validation.message, 'error');
        return;
    }
    
    try {
        // Submit loan application
        const response = await fetch('/apply_loan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loanData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentLoanId = result.loan.id;
            showReceipt(result.loan);
            resetForm();
            showAlert(result.message, 'success');
        } else {
            showAlert(result.error || 'Terjadi kesalahan saat memproses pinjaman', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Gagal terhubung ke server. Silakan coba lagi.', 'error');
    } finally {
        hideLoading();
    }
}

function validateLoanData(data) {
    // Check required fields
    const requiredFields = ['name', 'phone', 'address', 'amount', 'rate', 'months'];
    for (let field of requiredFields) {
        if (!data[field] || data[field].toString().trim() === '') {
            return { valid: false, message: `Field ${field} harus diisi` };
        }
    }
    
    // Validate numeric fields
    const amount = parseFloat(data.amount);
    const rate = parseFloat(data.rate);
    const months = parseInt(data.months);
    
    if (isNaN(amount) || amount < 100000) {
        return { valid: false, message: 'Jumlah pinjaman minimal Rp 100,000' };
    }
    
    if (isNaN(rate) || rate < 0 || rate > 50) {
        return { valid: false, message: 'Suku bunga harus antara 0% - 50%' };
    }
    
    if (isNaN(months) || months < 1 || months > 60) {
        return { valid: false, message: 'Jangka waktu harus antara 1 - 60 bulan' };
    }
    
    // Validate phone number (basic)
    const phoneRegex = /^[0-9+\-\s\(\)]{8,20}$/;
    if (!phoneRegex.test(data.phone)) {
        return { valid: false, message: 'Format nomor telepon tidak valid' };
    }
    
    return { valid: true };
}

function showReceipt(loan) {
    // Populate receipt data
    document.getElementById('receiptNumber').textContent = loan.id;
    document.getElementById('receiptDate').textContent = formatDate(loan.application_date);
    document.getElementById('receiptName').textContent = loan.name;
    document.getElementById('receiptPhone').textContent = loan.phone;
    document.getElementById('receiptAddress').textContent = loan.address;
    document.getElementById('receiptPrincipal').textContent = formatCurrency(loan.principal);
    document.getElementById('receiptRate').textContent = loan.rate + '% per tahun';
    document.getElementById('receiptMonths').textContent = loan.months + ' bulan';
    document.getElementById('receiptMonthly').textContent = formatCurrency(loan.monthly_payment);
    document.getElementById('receiptTotalInterest').textContent = formatCurrency(loan.total_interest);
    document.getElementById('receiptTotalPayment').textContent = formatCurrency(loan.total_payment);
    document.getElementById('receiptDueDate').textContent = formatDate(loan.due_date);
    document.getElementById('receiptStatus').textContent = loan.status;
    
    // Show modal
    receiptModal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    receiptModal.style.display = 'none';
    document.body.style.overflow = 'auto';
    currentLoanId = null;
}

function printReceipt() {
    if (currentLoanId) {
        window.open(`/print_receipt/${currentLoanId}`, '_blank', 'width=600,height=800');
    }
}

function resetForm() {
    loanForm.reset();
    calculationPreview.style.display = 'none';
}

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <div class="alert-content">
            <span class="alert-icon">${getAlertIcon(type)}</span>
            <span class="alert-message">${message}</span>
            <button class="alert-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    // Add alert styles
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        animation: slideInRight 0.3s ease-out;
    `;
    
    alert.querySelector('.alert-content').style.cssText = `
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    alert.querySelector('.alert-close').style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        margin-left: auto;
    `;
    
    // Add to page
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);

// Export functions for global access
window.closeModal = closeModal;
window.printReceipt = printReceipt;
