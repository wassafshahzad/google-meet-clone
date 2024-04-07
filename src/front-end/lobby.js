
let createRoom = () => {
    const roomName = document.getElementById("createRoom").value
    if (roomName){
        window.location.href = `/room/${roomName}`
    }
    else {
        alert("Room Name cannot be empty")
    }
}
