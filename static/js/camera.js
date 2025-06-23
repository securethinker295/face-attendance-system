class CameraHandler {
  constructor(videoElementId, canvasElementId) {
    this.video = document.getElementById(videoElementId);
    this.canvas = document.getElementById(canvasElementId);
    this.stream = null;
    this.isStreaming = false;
  }

  async startCamera() {
    try {
      // Request camera access
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      });

      // Set video source
      this.video.srcObject = this.stream;
      this.isStreaming = true;

      // Wait for video to load
      return new Promise((resolve) => {
        this.video.onloadedmetadata = () => {
          this.video.play();
          resolve(true);
        };
      });
    } catch (error) {
      console.error('Error accessing camera:', error);
      this.showCameraError(error);
      return false;
    }
  }

  captureImage() {
    if (!this.isStreaming || !this.video.videoWidth) {
      console.error('Camera not ready');
      return null;
    }

    try {
      // Set canvas dimensions to match video
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;

      // Draw video frame to canvas
      const context = this.canvas.getContext('2d');
      context.drawImage(this.video, 0, 0);

      // Convert to base64 image data
      const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
      return imageData;
    } catch (error) {
      console.error('Error capturing image:', error);
      return null;
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        track.stop();
      });
      this.stream = null;
      this.isStreaming = false;
    }
  }

  showCameraError(error) {
    let message = 'Camera access failed. ';
    
    switch (error.name) {
      case 'NotAllowedError':
        message += 'Please allow camera access and refresh the page.';
        break;
      case 'NotFoundError':
        message += 'No camera found on this device.';
        break;
      case 'NotSupportedError':
        message += 'Camera not supported in this browser.';
        break;
      default:
        message += 'Please check your camera and try again.';
    }

    // Show error message
    const messageDiv = document.getElementById('message') || this.createMessageDiv();
    messageDiv.textContent = message;
    messageDiv.className = 'message error';
    messageDiv.style.display = 'block';
  }

  createMessageDiv() {
    const messageDiv = document.createElement('div');
    messageDiv.id = 'message';
    messageDiv.className = 'message';
    document.querySelector('.form-container').appendChild(messageDiv);
    return messageDiv;
  }
}

// Utility functions
function showMessage(text, type = 'info') {
  const messageDiv = document.getElementById('message');
  if (messageDiv) {
    messageDiv.textContent = text;
    messageDiv.className = 'message ' + type;
    messageDiv.style.display = 'block';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
      messageDiv.style.display = 'none';
    }, 5000);
  }
}

// Check browser compatibility
function checkBrowserSupport() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showMessage('Your browser does not support camera access. Please use a modern browser.', 'error');
    return false;
  }
  return true;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  checkBrowserSupport();
  
  // Add cleanup on page unload
  window.addEventListener('beforeunload', function() {
    // Stop any active camera streams
    if (window.cameraHandler) {
      window.cameraHandler.stopCamera();
    }
  });
});