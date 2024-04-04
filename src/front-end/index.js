let localStream;
let remoteStream;
let peerConnection;
let socket;
let polite = true;
let makingOffer = false;

let init = async () => {
  localStream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: true,
  });
  document.getElementById("user-1").srcObject = localStream;
  await connect();
};

let connect = async () => {
  let roomName = window.location.pathname.split("/")[1]
  socket = new WebSocket(`ws://localhost:8000/ws/${roomName}"`);
  socket.onopen = (_) => {
    console.log("Connected succesfully");
  };

  socket.onmessage = handleMessage;
};

let handleMessage = async ({ data }) => {
  data = JSON.parse(data);
  if (data["type"] == "USER_JOIN") {
    createAndSendOffer()
  }
  if (data["type"] === "OFFER") {
    console.log("received offer")
    handleOffers(data)
  }
  if (data["type"] === "ANSWER") {
    console.log("received answer")
    handleAnswers(data)
  }
  if(data["type"] === "candidate") {
    handleIceCandidate(data)
  }

};

let handleOffers = async ({ message }) => {
    await createAndSendAnswer(message);
}

let handleAnswers = async({message}) => {
  await peerConnection.setRemoteDescription(message)
}

let handleIceCandidate = async ({candidate}) => {
  if (peerConnection) {
    peerConnection.addIceCandidate(candidate)
  }
}


const config = {
  iceServers: [
    {
      urls: [
        "stun:stun1.l.google.com:19302",
        "stun:stun1.l.google.com:19302",
        "stun:stun2.l.google.com:19302",
      ],
    },
  ],
};

let createStreams = async () => {
  peerConnection = new RTCPeerConnection(config);
  remoteStream = new MediaStream();

  localStream.getTracks().forEach((track) => {
    peerConnection.addTrack(track, localStream);
  });

  // This function is called each time a peer connects.
  peerConnection.ontrack = (event) => {
    console.log("adding track")
    event.streams[0]
      .getTracks()
      .forEach((track) => remoteStream.addTrack(track));
  };

  peerConnection.onicecandidate = async (event) => {
    if (event.candidate) {
      socket.send(
        JSON.stringify({ type: "candidate", candidate: event.candidate })
      );
    }
  };

  document.getElementById("user-2").srcObject = remoteStream;
};

let createAndSendOffer = async () => {
  await createStreams();
  let offer = await peerConnection.createOffer();
  await peerConnection.setLocalDescription(offer);
  socket.send(JSON.stringify({type:"OFFER", message: offer}))
};

let createAndSendAnswer = async (message) => {
  await createStreams()
  await peerConnection.setRemoteDescription(message)
  let answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);
  socket.send(JSON.stringify({type:"ANSWER", message: answer}))
};

document.addEventListener(
  "DOMContentLoaded",
  async function () {
    await init();
  },
  false
);
