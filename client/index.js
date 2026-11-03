const socket = new WebSocket("ws://localhost:8000/ws");

socket.onopen = () => {socket.send("Hello Websocket Server!");}

socket.onmessage = (event) => {console.log("Server says: " + event.data);}

socket.onclose = () => { console.log("Websocket connection closed")}