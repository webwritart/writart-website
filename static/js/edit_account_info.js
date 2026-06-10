

function closeAllForms() {
    document.getElementById('name-edit').style.display = 'none';
    document.getElementById('email-edit').style.display = 'none';
    document.getElementById('phone-edit').style.display = 'none';
    document.getElementById('whatsapp-edit').style.display = 'none';
    document.getElementById('profession-edit').style.display = 'none';
    document.getElementById('state-edit').style.display = 'none';
    document.getElementById('facebook-edit').style.display = 'none';
    document.getElementById('instagram-edit').style.display = 'none';
    document.getElementById('x-edit').style.display = 'none';
    document.getElementById('website-edit').style.display = 'none';
}

function openAllDetail() {
    document.getElementById('name').style.display = 'block';
    document.getElementById('email').style.display = 'block';
    document.getElementById('phone').style.display = 'block';
    document.getElementById('whatsapp').style.display = 'block';
    document.getElementById('profession').style.display = 'block';
    document.getElementById('state').style.display = 'block';
    document.getElementById('facebook').style.display = 'block';
    document.getElementById('instagram').style.display = 'block';
    document.getElementById('x').style.display = 'block';
    document.getElementById('website').style.display = 'block';
}

function focusInput() {
    const nameInput = document.getElementById('name-input');
    const emailInput = document.getElementById('email-input');
    const phoneInput = document.getElementById('phone-input');
    const whatsappInput = document.getElementById('whatsapp-input');
    const professionInput = document.getElementById('profession-input');
    const stateInput = document.getElementById('state-input');
    const facebookInput = document.getElementById('facebook-input');
    const instagramInput = document.getElementById('instagram-input');
    const xInput = document.getElementById('x-input');
    const websiteInput = document.getElementById('website-input');
    nameInput.focus();
    emailInput.focus();
    phoneInput.focus();
    whatsappInput.focus();
    professionInput.focus();
    stateInput.focus();
    facebookInput.focus();
    instagramInput.focus();
    xInput.focus();
    websiteInput.focus();
    var name = nameInput.value;
    nameInput.value = '';
    nameInput.value = name;
    var email = emailInput.value;
    emailInput.value = '';
    emailInput.value = email;
    var phone = phoneInput.value;
    phoneInput.value = '';
    phoneInput.value = phone;
    var whatsapp = whatsappInput.value;
    whatsappInput.value = '';
    whatsappInput.value = whatsapp;
    var profession = professionInput.value;
    professionInput.value = '';
    professionInput.value = profession;
    var state = stateInput.value;
    stateInput.value = '';
    stateInput.value = state;
    var facebook = facebookInput.value;
    facebookInput.value = '';
    facebookInput.value = facebook;
    var instagram = instagramInput.value;
    instagramInput.value = '';
    instagramInput.value = instagram;
    var x = xInput.value;
    xInput.value = '';
    xInput.value = x;
    var website = websiteInput.value;
    websiteInput.value = '';
    websiteInput.value = website;
}

function nameForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('name').style.display = 'none';
    document.getElementById('name-edit').style.display = 'block';
    focusInput();
}
function emailForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('email').style.display = 'none';
    document.getElementById('email-edit').style.display = 'block';
    focusInput();
}
function phoneForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('phone').style.display = 'none';
    document.getElementById('phone-edit').style.display = 'block';
    focusInput();
}
function whatsappForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('whatsapp').style.display = 'none';
    document.getElementById('whatsapp-edit').style.display = 'block';
    focusInput();
}
function professionForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('profession').style.display = 'none';
    document.getElementById('profession-edit').style.display = 'block';
    focusInput();
}
function stateForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('state').style.display = 'none';
    document.getElementById('state-edit').style.display = 'block';
    focusInput();
}
function facebookForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('facebook').style.display = 'none';
    document.getElementById('facebook-edit').style.display = 'block';
    focusInput();
}
function instagramForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('instagram').style.display = 'none';
    document.getElementById('instagram-edit').style.display = 'block';
    focusInput();
}
function xForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('x').style.display = 'none';
    document.getElementById('x-edit').style.display = 'block';
    focusInput();
}
function websiteForm() {
    closeAllForms();
    openAllDetail();
    document.getElementById('website').style.display = 'none';
    document.getElementById('website-edit').style.display = 'block';
    focusInput();
}