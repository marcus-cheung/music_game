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
    // let canvas = document.getElementById("audio_visualizer");
    // let canvasCtx = canvas.getContext("2d");
    // let WIDTH = canvas.width
    // let HEIGHT = canvas.height
    let audioCtx = new AudioContext();
    let analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2 ** 7
    let bufferLength = analyser.frequencyBinCount
    console.log(bufferLength)
    let source = audioCtx.createMediaElementSource(audioElement)
    source.connect(analyser)
    source.connect(audioCtx.destination)
    let dataArray = new Uint8Array(analyser.frequencyBinCount)
    console.log(dataArray)
    randomArray = shuffle(Array.from(Array(bufferLength).keys()))

    // var gradient = canvasCtx.createLinearGradient(20, 0, 220, 0);
    // // Add three color stops
    // gradient.addColorStop(0, 'green');
    // gradient.addColorStop(.5, 'cyan');
    // gradient.addColorStop(1, 'green');

    var sing = document.createElement("IMG")
    sing.setAttribute('src', 'static/assets/singing.png')


    var notsing = document.createElement("IMG")
    notsing.setAttribute('src', 'static/assets/notsing.png')




    function loopingFunction() {
        requestAnimationFrame(loopingFunction)
        analyser.getByteFrequencyData(dataArray)
        // draw(dataArray)
        singFunc(dataArray)
    }

    function draw(data) {
        // let CENTER = WIDTH / 2
        console.log(WIDTH)
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT)
        let barWidth = (WIDTH * 4) / bufferLength
        console.log(barWidth)
        let barHeight;
        let x = 0;
        for (let i = 0; i < bufferLength; i++) {
            barHeight = data[i] ** 3.2 / (40 ** 3.2)
            canvasCtx.fillStyle = gradient
            // canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
            canvasCtx.roundRect(x, HEIGHT / 2 - barHeight / 2, barWidth, barHeight, barHeight / 10).fill();
            // if (i != 0) {
            //     canvasCtx.roundRect(CENTER - x, HEIGHT / 2 - barHeight / 2, barWidth, barHeight, barHeight / 10).fill();
            // }
            x += barWidth + 1
        }
    }

    function singFunc(data) {

        // canvasCtx.clearRect(0, 0, WIDTH, HEIGHT)
        // pitcharray = new Array(32).fill(0)
        // len = bufferLength/4
        // for (let i = 0; i < bufferLength; i++) {
        //     pitcharray[i] = (data[i])
        // }
        for (let i = 0; i < 8; i++) {
            console.log(data[i])
            let x = document.getElementById(String(i))
            if (data[i] > 220) {
                x.src = 'static/assets/singing.png'
            } else {
                x.src = 'static/assets/notsing.png'
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