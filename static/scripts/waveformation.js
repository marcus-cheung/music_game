function audio_visualizer(audioElement) {
    console.log('audio_visualizer called')
    let canvas = document.getElementById("audio_visualizer");
    let canvasCtx = canvas.getContext("2d");
    let audioCtx = new AudioContext();
    let analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2 ** 8
    let bufferLength = analyser.frequencyBinCount
    let source = audioCtx.createMediaElementSource(audioElement)
    source.connect(analyser)
    source.connect(audioCtx.destination)
    let dataArray = new Uint8Array(analyser.frequencyBinCount)
    let WIDTH = canvas.width
    let HEIGHT = canvas.height
    let origin = [WIDTH / 2, HEIGHT / 2]
    let N = 1000
    let manual_scale = 50000
    let scaleFactor = Math.min(WIDTH / manual_scale, HEIGHT / manual_scale)
    function loopingFunction() {
        analyser.getByteFrequencyData(dataArray) 
        //graph data array
        driver(dataArray)
        requestAnimationFrame(loopingFunction)
    }

    function driver(frequencyData) {
        
        frequencyData = frequencyData.filter(freq=>freq>50)
        let xfunc = SummationHigherorder(freq=> Math.cos(Math.log2(realFreq(freq))), frequencyData)
        let yfunc = SummationHigherorder(freq=> Math.sin(Math.log2(realFreq(freq))), frequencyData)
        graphEquation(xfunc, yfunc, N)
    }

    function graphEquation(xfunc, yfunc, divisions){
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT)
        // for full period
        divisions = divisions/Math.PI
        
        for (i=2; i<=divisions; i++){
            //path
            canvasCtx.beginPath()
            //color
            canvasCtx.strokeStyle = `red`
            //starting point
            canvasCtx.moveTo(xpoint(xfunc(i-1)), ypoint(yfunc(i-1)))
            //end point
            canvasCtx.lineTo(xpoint(xfunc(i)), ypoint(yfunc(i)))
            //draw line
            canvasCtx.stroke()
        }
    }

    function xpoint (x){
        return origin[0] + x * scaleFactor
    }
    function ypoint (y){
        return origin[1] + y * scaleFactor
    }

    //summmation (inclusive) of functions, returns the super func for adding up all circles
    function SummationHigherorder(func, frequencyData){
        function higherOrder(freq){
            return t => frequencyData[freq] * func(freq*t)
        }
        let listFuncs = []
        for (const freq in frequencyData){
            listFuncs.push(higherOrder(freq))
        }
        function compose(...fns){
            return x => fns.reduce((result,f)=>result+f(x),0)
        }
        return compose(...listFuncs)
        
    }

    function realFreq(freq){
        return freq*(44100/bufferLength/2)
    }

    requestAnimationFrame(loopingFunction)
}



