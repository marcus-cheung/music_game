function play_audio(file) {
    let audio = new Audio(file);
    audio.play();
}

 document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Listens for the music file
    socket.on('music file', function(data) {
        file = data.music
        play_audio(file)
        alert('Music playing')
    })
 })