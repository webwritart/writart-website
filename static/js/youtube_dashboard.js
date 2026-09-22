function draw(e) {
    if (!isDrawing) return;

    const pos = getCanvasCoordinates(e);

    let pressure = e.pressure;

    if (e.pointerType === 'mouse' && pressure === 0) {
        pressure = 0.5;
    }
    // Some devices can report 0 pressure
    if (pressure <= 0) {
        pressure = 0.5;
    }
    // ======================================
    // PEN
    // ======================================

    if (!isEraser) {

        ctx.globalCompositeOperation = 'source-over';

        ctx.strokeStyle = '#000000';

        ctx.lineWidth =
            pressure * BASE_LINE_WIDTH;
    }


    // ======================================
    // ERASER
    // ======================================

    else {

        ctx.globalCompositeOperation =
            'source-over';
        
        ctx.strokeStyle = '#ffffff';

        ctx.lineWidth =
            pressure * ERASER_LINE_WIDTH;
    }
    // ======================================
    // DRAW LINE
    // ======================================

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();

    lastX = pos.x;
    lastY = pos.y;
}

const uploadImagesForm = document.getElementById('upload-images-form');
const uploadVideoForm = document.getElementById('upload-video-form');
const addTitleForm = document.getElementById('add-title-form');
const addDescriptionForm = document.getElementById('add-description-form');
const addTagsForm = document.getElementById('add-tags-form');


uploadImagesForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('upload-images-btn');
    const imgUploadEndpointUrl = "{{ url_for('youtube.upload_images') }}";
    const fileInput = document.getElementById('image-files');
    const imageText = document.getElementById('image-text').value;
    const statusMessage = document.getElementById('status-message');
    const videoUuid = document.getElementById('img-upload-video-uuid').value;
    if (fileInput.files.length === 0) {
        statusMessage.textContent = 'Please select at least one image file.';
        return;
    }

    submitBtn.textContent = 'Uploading...';
    submitBtn.disabled = true;
    const formData = new FormData();
    for (const file of fileInput.files) {
        formData.append('files', file);
    }
    formData.append('video_uuid', videoUuid);
    formData.append('image_text', imageText);
    formData.append('type', 'upload_images');
    try {
        const response = await fetch(imgUploadEndpointUrl, {
        method: 'POST',
        body: formData // Passed directly; do not set Content-Type header
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        alert(result);
        console.log('Success:', result);
        statusMessage.textContent = 'Image uploaded successfully.';
    
    } catch (error) {
        console.error('Submission failed:', error);
        statusMessage.textContent = 'Image upload failed. Please try again.';
    } finally {
        uploadImagesForm.reset();
        submitBtn.textContent = 'Upload images';
        submitBtn.disabled = false;
    }
});