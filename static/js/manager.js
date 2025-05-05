function closeAll() {
    document.getElementById("manager-img").style.display = 'none';
    document.getElementById("add-ws").style.display = 'none';
    document.getElementById("add-ws-details").style.display = 'none';
    document.getElementById("add-recording-link").style.display = 'none';
    document.getElementById("add-session-link").style.display = 'none';
    document.getElementById("close-reg").style.display = 'none';
    document.getElementById("ws-promo").style.display = 'none';
    document.getElementById("last-day-reminder").style.display = 'none';
    document.getElementById("session-link").style.display = 'none';
    document.getElementById("session-reminder").style.display = 'none';
    document.getElementById("certificate-dist").style.display = 'none';
    document.getElementById("csv-export-cert").style.display = 'none';
    document.getElementById("open-reg").style.display = 'none';
    document.getElementById("overview-content").style.display = 'none';
    document.getElementById("gallery").style.display = 'none';
    document.getElementById("open-demo").style.display = 'none';
    document.getElementById("send-email").style.display = 'none';
    document.getElementById("add-ws-files").style.display = 'none';
    document.getElementById("add-quiz-data").style.display = 'none';
}

function addNewWs() {
    closeAll();
    document.getElementById("add-ws").style.display = 'block';
}

function addWsDetails() {
    closeAll();
    document.getElementById("add-ws-details").style.display = 'block';
}

function openRegistration() {
    closeAll();
    document.getElementById("open-reg").style.display = 'block';
}

function addRecordingLink() {
    closeAll();
    document.getElementById("add-recording-link").style.display = 'block';
}

function addSessionLink() {
    closeAll();
    document.getElementById("add-session-link").style.display = 'block';
}

function closeRegistration() {
    closeAll();
    document.getElementById("close-reg").style.display = 'block';
}

function promotion() {
    closeAll();
    document.getElementById("ws-promo").style.display = 'block';
}

function lastDateReminder() {
    closeAll();
    document.getElementById("last-day-reminder").style.display = 'block';
}

function sessionLink() {
    closeAll();
    document.getElementById("session-link").style.display = 'block';
}

function sessionReminder() {
    closeAll();
    document.getElementById("session-reminder").style.display = 'block';
}

function addWsFiles() {
    closeAll();
    document.getElementById("add-ws-files").style.display = 'block';
}
function openQuizData() {
    closeAll();
    document.getElementById("add-quiz-data").style.display = 'block';
}

function certificateDistribution() {
    closeAll();
    document.getElementById("certificate-dist").style.display = 'block';
}

function csvForCertificates() {
    closeAll();
    document.getElementById("csv-export-cert").style.display = 'block';
}

function reports() {
    closeAll();
}

function gstFilingSheet() {
    closeAll();
}

function    overview() {
    closeAll();
    document.getElementById("overview-content").style.display = 'block';
}
function gallery()  {
    closeAll();
    document.getElementById("gallery").style.display = 'block';
}
function sendEmail() {
    closeAll();
    document.getElementById("send-email").style.display = "block";
}
function sendWa() {
    closeAll();
    document.getElementById("send-wa").style.display = "block";
}
function openDemo() {
    closeAll();
    document.getElementById("open-demo").style.display = "block";
}
function recipientPopup() {
    if (document.getElementById("recipient").value == "workshop") {
        document.getElementById("workshop-recipient").style.display = "block";
        document.getElementById("workshop-list").style.display = "block";
        document.getElementById("manual-recipients").style.display = "none";
    }else if(document.getElementById("recipient").value == "manual") {
        document.getElementById("manual-recipients").style.display = "block";
        document.getElementById("workshop-list").style.display = "none";
        document.getElementById("workshop-recipient").style.display = "none";
    }else {
        document.getElementById("workshop-recipient").style.display = "none";
        document.getElementById("workshop-list").style.display = "none";
        document.getElementById("manual-recipients").style.display = "none";
    }
}

function    workshopDetails(n, count_list) {
    var list = count_list
    for (var i in list) {
        if (i != n) {
            document.getElementById(i).style.display = 'none';
        }
    }
    document.getElementById(n).style.display = 'block';
}


function    closeAllOptions() {
    // document.getElementById("blank").style.display = 'none';
    document.getElementById("user-opt").style.display = 'none';
    document.getElementById("workshop1-opt").style.display = 'none';
    document.getElementById("query-opt").style.display = 'none';
    document.getElementById("accountant-opt").style.display = 'none';
    document.getElementById("gst-opt").style.display = 'none';

}

function user() {
    closeAllOptions();
    document.getElementById("user-opt").style.display = 'block';
}

function workshop() {
    closeAllOptions();
    document.getElementById("workshop1-opt").style.display = 'block';
}

function query() {
    closeAllOptions();
    document.getElementById("query-opt").style.display = 'block';
}

function accountant() {
    closeAllOptions();
    document.getElementById("accountant-opt").style.display = 'block';
}

function gst() {
    closeAllOptions();
    document.getElementById("gst-opt").style.display = 'block';
}

