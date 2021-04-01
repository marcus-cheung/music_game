<script src="https://unpkg.com/wavesurfer.js"></script>

function play_audio(file) {
    let audio = new Audio(file);
    audio.play();
    wavesurfer.load(file);
}

