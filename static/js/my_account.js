
function validateForm() {
    let newPwd = document.forms["change-password"]["new-pwd"].value;
    let retypedPwd = document.forms["change-password"]["pwd-retyped"].value;
   
    if (retypedPwd != newPwd) {
        alert("New password and retyped password doesn't match!");
        return false;
    }
}

function openForm() {
    document.getElementById("change-password").style.display = "block";
    closeForm2();
    closeForm3();
    closeCertificateList();
}

function closeForm() {
    document.getElementById("change-password").style.display = "none";
}

function openForm2() {
    document.getElementById("update-profile-details").style.display = "block";
    closeForm();
    closeForm3();
    closeCertificateList();
}

function closeForm2() {
    document.getElementById("update-profile-details").style.display = "none";
}

function openSocialUpdatePopup() {
    document.getElementById("update-social-media").style.display = "block";
    closeForm();
    closeForm2();
    closeCertificateList();
}

function closeForm3() {
    document.getElementById("update-social-media").style.display = "none";
}

function openCertificateList() {
    document.getElementById("certificate_list").style.display = "block";
    closeForm();
    closeForm2();
    closeForm3();
}

function closeCertificateList() {
    document.getElementById("certificate_list").style.display = "none";
}

function deleteAccountPopup() {
    document.getElementById("delete-account").style.display = "block";
    closeForm();
    closeForm2();
    closeForm3();
    closeCertificateList();
}
function closeDeleteAccountPopup() {
    document.getElementById("delete-account").style.display = "none";
}


function validateForm2() {
    let newPwd = document.forms['set-password']['password'].value;
    let retypedPwd = document.forms['set-password']['reenter-password'].value;
    if (retypedPwd != newPwd) {
        alert("Re-entered password doesn't match!");
        return false;
    }
}

function validateRegistration() {
    const dates = ['1', '01', '2', '02', '3', '03', '4', '04', '5', '05', '6', '06', '7', '07', '8', '08', '9', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    const months = ['1', '01', '2', '02', '3', '03', '4', '04', '5', '05', '6', '06', '7', '07', '8', '08', '9', '09', '10', '11', '12']
    let date = document.forms["registration"]["date"].value
    let month = document.forms["registration"]["month"].value
    let year = document.forms["registration"]["year"].value
    let email = document.forms["registration"]["email"].value
    let password = document.forms["registration"]["password"].value
    let retypePassword = document.forms["registration"]["retype-password"].value

    if (!dates.includes(date)) {
        alert("Wrong date. Please check again!");
        return false;
    }
    if (!months.includes(month)) {
        alert("Wrong month. Please check again!");
        return false;
    }
    if (password != retypePassword) {
        alert("The Retyped message doesn't match. Please enter again");
        return false;
    }
}

function validateUpdateDetails() {
    const dates = ['1', '01', '2', '02', '3', '03', '4', '04', '5', '05', '6', '06', '7', '07', '8', '08', '9', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    const months = ['1', '01', '2', '02', '3', '03', '4', '04', '5', '05', '6', '06', '7', '07', '8', '08', '9', '09', '10', '11', '12']
    let date = document.forms["update_details"]["date"].value
    let month = document.forms["update_details"]["month"].value
    let year = document.forms["update_details"]["year"].value
    let email = document.forms["update_details"]["email"].value
    let password = document.forms["update_details"]["password2"].value
    let retypePassword = document.forms["update_details"]["retype-password2"].value

    if (!dates.includes(date)) {
        alert("Wrong date. Please check again!");
        return false;
    }
    if (!months.includes(month)) {
        alert("Wrong month. Please check again!");
        return false;
    }
    if (password != retypePassword) {
        alert("The Retyped message doesn't match. Please enter again");
        return false;
    }
}