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