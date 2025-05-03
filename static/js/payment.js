function validatePaymentForm() {
    let state = document.getElementById('state').value;
    if (state == 'default') {
        alert('Please select state first!');
        return false;
    }
}