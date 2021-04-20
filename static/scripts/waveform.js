CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    if (w < 2 * r) r = w / 2;
    if (h < 2 * r) r = h / 2;
    this.beginPath();
    this.moveTo(x + r, y);
    this.arcTo(x + w, y, x + w, y + h, r);
    this.arcTo(x + w, y + h, x, y + h, r);
    this.arcTo(x, y + h, x, y, r);
    this.arcTo(x, y, x + w, y, r);
    this.closePath();
    return this;
}

function audio_visualizer(audioElement) {
    console.log('audio_visualizer called')
    let canvas = document.getElementById("audio_visualizer");
    let canvasCtx = canvas.getContext("2d");
    let audioCtx = new AudioContext();
    let analyser = audioCtx.createAnalyser();
    analyser.fftSize = 64
    let bufferLength = analyser.frequencyBinCount
    let source = audioCtx.createMediaElementSource(audioElement)
    source.connect(analyser)
    source.connect(audioCtx.destination)
    let dataArray = new Uint8Array(analyser.frequencyBinCount)
    console.log(dataArray)
    randomArray = shuffle(Array.from(Array(bufferLength).keys()))


    function loopingFunction() {
        console.log('looping')
        requestAnimationFrame(loopingFunction)
        analyser.getByteFrequencyData(dataArray)
        draw(dataArray, randomArray)
    }

    function draw(data, random_array) {
        let WIDTH = canvas.width
        let HEIGHT = canvas.height
        // let CENTER = WIDTH / 2
        console.log(WIDTH)
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT)
        let barWidth = (WIDTH * 1.0) / bufferLength
        console.log(barWidth)
        let barHeight;
        let x = 0;
        random = shuffle(data)
        for (let i = 0; i < bufferLength; i++) {
            barHeight = random[i]**1.5 * (HEIGHT / (150 ** 1.5))
            if (barHeight > 0) {
                canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
                canvasCtx.roundRect(x, HEIGHT / 2 - barHeight / 2, barWidth, barHeight, barHeight / 10).fill();
                // if (i != 0) {
                //     canvasCtx.roundRect(CENTER - x, HEIGHT / 2 - barHeight / 2, barWidth, barHeight, barHeight / 10).fill();
                // }
                x += barWidth + 1
            }
            
        }
    }   
    requestAnimationFrame(loopingFunction);
}

function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;
  
    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
  
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;
  
      // And swap it with the current element.
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }
    return array
}