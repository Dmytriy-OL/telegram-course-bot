const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('avatar');
const preview = document.getElementById('preview');
const removeBtn = document.getElementById('removeBtn');
const dropText = document.getElementById('drop-text');

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    previewImage({ target: { files: [file] } });
  }
});

function previewImage(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function() {
    preview.src = reader.result;
    preview.style.display = 'block';
    removeBtn.style.display = 'inline-block';
    dropText.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  fileInput.value = "";
  preview.src = "";
  preview.style.display = "none";
  removeBtn.style.display = "none";
  dropText.style.display = "block";
}
