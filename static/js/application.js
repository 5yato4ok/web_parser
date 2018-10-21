
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/');
    var text_received = [];

    //receive details from server
    socket.on('newText', function(msg) {
        console.log("Received number" + msg.number);     
        text_received.push(msg.number);
        text_string = '';
        for (var i = 0; i < text_received.length; i++){
            text_string = text_string + '<p>' + text_received[i].toString() + '</p>';
        }
        $('#log').html(text_string);
    });

});