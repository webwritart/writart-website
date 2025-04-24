function openFullImage(img_path) {
    document.getElementById('full-size-img-box').style.display = 'block';
    document.getElementById('full-size-img').src = img_path;
}
function closeFullImage() {
    document.getElementById('full-size-img-box').style.display = 'none';
}