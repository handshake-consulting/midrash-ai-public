"use strict";

window.addEventListener("load", function () {
  // [START gae_python38_auth_signout]
  // [START gae_python3_auth_signout]
  document.getElementById("sign-out").onclick = function () {
    firebase.auth().signOut();
  };
  // [END gae_python3_auth_signout]
  // [END gae_python38_auth_signout]

  // [START gae_python38_auth_UIconfig_variable]
  // [START gae_python3_auth_UIconfig_variable]
  // FirebaseUI config.
  var uiConfig = {
    signInSuccessUrl: "/",
    signInOptions: [
      // Remove any lines corresponding to providers you did not check in
      // the Firebase console.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
    ],
    // Terms of service url.
    tosUrl: "<your-tos-url>",
  };
  // [END gae_python3_auth_UIconfig_variable]
  // [END gae_python38_auth_UIconfig_variable]

  // [START gae_python38_auth_request]
  // [START gae_python3_auth_request]
  firebase.auth().onAuthStateChanged(
    function (user) {
      if (user) {
        // User is signed in, so display the "sign out" button and login info.
        document.getElementById("sign-out").hidden = false;
        console.log(`Signed in as ${user.displayName} (${user.email})`);
        user.getIdToken().then(function (token) {
          // Add the token to the browser's cookies. The server will then be
          // able to verify the token against the API.
          // SECURITY NOTE: As cookies can easily be modified, only put the
          // token (which is verified server-side) in a cookie; do not add other
          // user information.
          document.cookie = "token=" + token;
        });
      } else {
        // User is signed out.
        // Initialize the FirebaseUI Widget using Firebase.
        var ui = new firebaseui.auth.AuthUI(firebase.auth());
        // Show the Firebase login button.
        ui.start("#firebaseui-auth-container", uiConfig);
        // Update the login state indicators.
        document.getElementById("sign-out").hidden = true;
        // Clear the token cookie.
        document.cookie = "token=";
      }
    },
    function (error) {
      console.log(error);
      alert("Unable to log in: " + error);
    }
  );
  // [END gae_python3_auth_request]
  // [END gae_python38_auth_request]
});

const form = document.querySelector(".chatbot-form");
const input = document.querySelector(".chatbot-input");
const uploadForm = document.querySelector(".upload-form");
const uploadMessage = document.querySelector("#docuemnt-message");
const ai_select = document.getElementById("dropdown");
let index = 0;
// const namespaceOption = document.getElementById("options");

let messages = [];

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    // Check if the Enter key was pressed
    event.preventDefault(); // Prevent the default Enter key behavior (i.e. adding a newline)
    chatbotMessage();
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault(); // Prevent the default form submission
  chatbotMessage();
});

function chatbotMessage() {
  const message = input.value.trim();
  // const namespace = namespaceOption.value;
  if (message !== "") {
    // Check if the message is not empty

    addMessage(message, "user"); // Add the user's message to the chat
    input.value = ""; // Clear the input field
    postMessageToLLM(message, ai_select.value); //, namespace); // Send the user's message to the chatbot API
    contentRetrieval(message);
  }
}

async function contentRetrieval(message) {
  try {
    const response = await fetch("/content", {
      method: "POST",
      body: JSON.stringify({
        message: message,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        console.log(data.documentcontent);
        addMessage(data.documentcontent, "from");
      });
  } catch {}
}

// Create a message and send it back to the server
async function postMessageToLLM(message, ai) {
  try {
    const response = await fetch("/submit", {
      method: "POST",
      body: JSON.stringify({
        message: message,
        ai: ai
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const reader = response.body
      .pipeThrough(new TextDecoderStream())
      .getReader();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      addMessage(value, "talmud");
      console.log("Received", value);
    }

    console.log("Response fully received");
  } catch (error) {
    addMessage(
      "Something went wrong handeling the request.  Try again.",
      "talmud"
    );
    console.error("Error:", error);
  }
  index = index + 1;
}

function addMessage(message, sender) {
  const messagesContainer = document.querySelector(
    ".chatbot-messages-container"
  );
  const messageBox = document.querySelector(
    ".chatbot-message." + sender + ".id" + String(index)
  );

  if (messageBox === null || sender === "user") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chatbot-message", sender, "id" + String(index));
    messageDiv.innerText =
      String(sender.charAt(0).toUpperCase()) +
      String(sender.substring(1)) +
      " : " +
      message;
    messagesContainer.appendChild(messageDiv);
  } else {
    messageBox.innerText += message;
  }
}

function uploadJsonFile() {
  const systemMessages = document.getElementsByClassName(
    "chatbot-message talmud"
  );
  const systemFrom = document.getElementsByClassName("chatbot-message from");
  const userMessages = document.getElementsByClassName("chatbot-message user");

  let sysMessage = {};
  let sysFrom = {};
  let userMessage = {};

  for (let i = 0; i < systemMessages.length; i++) {
    sysMessage[i] = systemMessages[i].innerText;
    sysFrom[i] = systemFrom[i].innerText;
    userMessage[i] = userMessages[i].innerText;
  }

  // Get the text from the text input element
  const textInput = document.getElementById("textInput").value;
  const data = {
    systemMessages: sysMessage,
    userMessages: userMessage,
    systemFrom: sysFrom,
    message: textInput,
  };

  // Send a POST request to the Flask server using AJAX
  $.ajax({
    url: "/feedback",
    type: "POST",
    data: JSON.stringify(data),
    traditional: true,
    contentType: "application/json; charset=utf-8",
    success: function (response) {
      document.getElementById("response").innerHTML = response["message"];
    },
    error: function (xhr, status, error) {
      console.error("Error uploading JSON file:", error);
    },
  });
}
