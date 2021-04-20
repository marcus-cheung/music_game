CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    if (w < 2 * r) r = w / 2;
    if (h < 2 * r) r = h / 2;
    this.beginPath();
    this.moveTo(x+r, y);
    this.arcTo(x+w, y,   x+w, y+h, r);
    this.arcTo(x+w, y+h, x,   y+h, r);
    this.arcTo(x,   y+h, x,   y,   r);
    this.arcTo(x,   y,   x+w, y,   r);
    this.closePath();
    return this;
}
                
function audio_visualizer(audioElement) {
    let canvas = document.getElementById("audio_visualizer");
    let canvasCtx = canvas.getContext("2d");
    let audioCtx = new AudioContext();
    let analyser = audioCtx.createAnalyser();
    analyser.fftSize = 128
    let bufferLength = analyser.frequencyBinCount
    let source = audioCtx.createMediaElementSource(audioElement)
    source.connect(analyser)
    source.connect(audioCtx.destination)
    let dataArray = new Uint8Array(analyser.frequencyBinCount)
    console.log(dataArray)

    function loopingFunction() {
        console.log(looping)
        requestAnimationFrame(loopingFunction)
        analyser.getByteFrequencyData(dataArray)
        draw(dataArray)
    }

    function draw(data) {
        let WIDTH = canvas.width
        let HEIGHT = canvas.height
        let CENTER = WIDTH / 2
        console.log(WIDTH)
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT)
        let barWidth = (WIDTH * 1.0) / bufferLength / 2
        console.log(barWidth)
        let barHeight;
        let x = 0;
        for (let i = 0; i < bufferLength; i++) {
            barHeight = data[i] / 3
            canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
            canvasCtx.roundRect(CENTER + x, HEIGHT / 2 - barHeight / 2, barWidth, barHeight, barHeight / 10).fill();
            if (i != 0){
                canvasCtx.roundRect(CENTER - x, HEIGHT / 2 - barHeight / 2, barWidth, barHeight, barHeight / 10).fill();
            }
            x += barWidth + 1
        }
    }
    requestAnimationFrame(loopingFunction);
}
