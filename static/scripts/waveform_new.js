

function audio_visualizer(audioElement) {
    console.log('audio_visualizer called')
    let canvas = document.getElementById("audio_visualizer");
    let canvasCtx = canvas.getContext("2d");
    let audioCtx = new AudioContext();
    let hilbert = createHilbertFilter(audioCtx)
    hilbert.connect(audioCtx.destination)
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
    let manual_scale = 50000
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
            let t =  j
            let x = 0
            let y = 0
            for (let k = 0; k < frequencyData.length / 12; k++) {
                x += frequencyData[k] * Math.cos(k*t)
                y += frequencyData[k] * Math.sin(k*t)
            }
            plot(x, y)
        }
    }

    function plot(x, y) {
        console.log(`Plotted ${x}, ${y}`)

        canvasCtx.fillType = 'rgb(0, 0, 0)'
        canvasCtx.fillRect(origin[0] + x * scaleFactor, origin[1] - y * scaleFactor, 1, 1);
    }

    function createHilbertFilter(context) {
        let filterLength = 2 ** 8
        // let filterLength = FFT_SIZE - N
        if (filterLength % 2 === 0) {
            filterLength -= 1
        }
        let impulse = new Float32Array(filterLength)

        let mid = ((filterLength - 1) / 2) | 0

        for (let i = 0; i <= mid; i++) {
            // hamming window
            let k = 0.53836 + 0.46164 * Math.cos(i * Math.PI / (mid + 1))
            if (i % 2 === 1) {
                let im = 2 / Math.PI / i
                impulse[mid + i] = k * im
                impulse[mid - i] = k * -im
            }
        }

        let impulseBuffer = context.createBuffer(2, filterLength, context.sampleRate)
        impulseBuffer.copyToChannel(impulse, 0)
        impulseBuffer.copyToChannel(impulse, 1)
        let hilbert = context.createConvolver()
        hilbert.normalize = false
        hilbert.buffer = impulseBuffer
        return hilbert
    }

    requestAnimationFrame(loopingFunction)
}




