function openFullImage(img_path, title) {
    document.getElementById('full-size-img').src = img_path;
    document.getElementById('artwork-title').innerHTML = title;
    document.getElementById('artwork-popup-overlay').style.display = 'block';
    document.getElementById('artwork-popup').style.display = 'block';
}
function closeFullImage() {
    document.getElementById('artwork-popup').style.display = 'none';
    document.getElementById('artwork-popup-overlay').style.display = 'none';
}

const detailsBtn = document.getElementById('details');
const descriptionBtn = document.getElementById('description');
const detailsContent = document.getElementById('details-content');
const descriptionContent = document.getElementById('description-content');

descriptionBtn.addEventListener('click', function(event) {
    detailsContent.style.display = 'none';
    descriptionContent.style.display = 'block';
    detailsBtn.style.backgroundColor = "rgba(0, 0, 0, 0)";
    descriptionBtn.style.backgroundColor = "rgb(160, 187, 140)";
});
detailsBtn.addEventListener('click', function(event) {
    detailsContent.style.display = 'block';
    descriptionContent.style.display = 'none';
    detailsBtn.style.backgroundColor = "rgb(160, 187, 140)";
    descriptionBtn.style.backgroundColor = "rgba(0, 0, 0, 0)";
})