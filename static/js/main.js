/**
 * Main JavaScript file for the Business Game application.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Production volume slider (if exists)
    const productionVolumeInput = document.getElementById('production_volume');
    const productionVolumeSlider = document.getElementById('production_volume_slider');
    
    if (productionVolumeInput && productionVolumeSlider) {
        // Sync slider with input
        productionVolumeSlider.addEventListener('input', function() {
            productionVolumeInput.value = this.value;
        });
        
        // Sync input with slider
        productionVolumeInput.addEventListener('input', function() {
            productionVolumeSlider.value = this.value;
        });
    }
    
    // Price input (if exists)
    const priceInput = document.getElementById('price');
    if (priceInput) {
        // Format price as currency
        priceInput.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    }
    
    // Game ID copy button (if exists)
    const copyGameIdBtn = document.getElementById('copy-game-id');
    if (copyGameIdBtn) {
        copyGameIdBtn.addEventListener('click', function() {
            const gameId = this.getAttribute('data-game-id');
            navigator.clipboard.writeText(gameId).then(() => {
                // Show success message
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = 'Copy ID';
                }, 2000);
            });
        });
    }
}); 