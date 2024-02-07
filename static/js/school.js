function    openInterestedForm2(workshop) {
    document.getElementById("interested-form2").style.display = 'block';
    document.getElementById("interested-form-hidden-workshop2").value = workshop;
}

function    closeFormInterested2() {
    document.getElementById("interested-form2").style.display = 'none';
}
function    openInterestedForm3(workshop) {
    document.getElementById("interested-form3").style.display = 'block';
    document.getElementById("interested-form-hidden-workshop3").value = workshop;
}

function    closeFormInterested3() {
    document.getElementById("interested-form3").style.display = 'none';
}
function    openInterestedForm(workshop) {
    document.getElementById("interested-form").style.display = 'block';
    document.getElementById("interested-form-hidden-workshop").value = workshop;
}

function    closeFormInterested() {
    document.getElementById("interested-form").style.display = 'none';
}

function    workshopDetails(n) {
    document.getElementById("view_workshop_table").style.display = 'block';
    document.getElementById("name").innerHTML = "{{upcoming_ws_dict['ws'][n]['name']}}"
    document.getElementById("topic").innerHTML = "{{upcoming_ws_dict['ws'][n]['topic']}}"
    document.getElementById("instructor").innerHTML = "{{upcoming_ws_dict['ws'][n]['instructor']}}"
}