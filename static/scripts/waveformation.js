
function audio_visualizer(audioElement) {
    console.log('audio_visualizer called')
    let canvas = document.getElementById("audio_visualizer");
    let canvasCtx = canvas.getContext("2d");
    let audioCtx = new AudioContext();
    let analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2 ** 8
    let bufferLength = analyser.frequencyBinCount
    console.log(bufferLength)
    let source = audioCtx.createMediaElementSource(audioElement)
    source.connect(analyser)
    source.connect(audioCtx.destination)
    let dataArray = new Uint8Array(analyser.frequencyBinCount)
    console.log(dataArray)
    let WIDTH = canvas.width
    let HEIGHT = canvas.height
    let origin = [WIDTH / 2, HEIGHT / 2]
    let N = 1000
    let manual_scale = 5000
    let scaleFactor = Math.min(WIDTH / manual_scale, HEIGHT / manual_scale)
    function loopingFunction() {
        analyser.getByteFrequencyData(dataArray)
        //graph data array
        graph(dataArray)
        requestAnimationFrame(loopingFunction)
    }

    function graph(frequencyData) {
        console.log('Graphing!')
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT)


        for (let j = 0; j < N; j++) {
            console.log(`Graphing step ${j}`)
            let t = 2 * Math.PI * j
            let x1 = 0
            let y1 = 0
            for (let k = 0; k < frequencyData.length / 12; k++) {
                x1 += frequencyData[k] * Math.cos(k * t)
                y1 += frequencyData[k] * Math.sin(k * t)
            }
            let x2 = 0
            let y2 = 0
            for (let k = 0; k < frequencyData.length / 12; k++) {
                x2 += frequencyData[k] * Math.sin(k * t)
                y2 += frequencyData[k] * Math.cos(k * t)
            }
            let y = y1
            let x = x2  
            plot(x, y)
        }
    }

    function plot(x, y) {
        console.log(`Plotted ${x}, ${y}`)

        canvasCtx.fillType = 'rgb(0, 0, 0)'
        canvasCtx.fillRect(origin[0] + x * scaleFactor, origin[1] - y * scaleFactor, 1, 1);
    }


    requestAnimationFrame(loopingFunction)
}

function fourier_transform(freq){
    return 
}


//summation of volume(i)*sin(i*)