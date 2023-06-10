"use strict";
// handle firebase auth start

function setCookie(name, value, days) {
  // ...
  const date = new Date();
  date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
  const expires = "; expires=" + date.toUTCString();
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}
function UUIDGeneratorBrowser() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  );
}
function getCookie(name) {
  const nameEQ = name + "=";
  const ca = document.cookie.split(";");
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === " ") {
      c = c.substring(1, c.length);
    }
    if (c.indexOf(nameEQ) === 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
}

function authComponent() {
  return {
    user: undefined,
    email: "",
    password: "",
    statusMessage: "",
    isLoading: false,
    cookieValue: null,
    init() {
      this.cookieValue = getCookie("isloggedin");

      if (this.cookieValue) {
        this.user = this.cookieValue;
      } else {
        this.user = null;
      }

      const observer = new MutationObserver(() => {
        this.user = getCookie("isloggedin");
      });
      observer.observe(document, {
        attributes: true,
        attributeFilter: ["cookie"],
      });
      // // console.log(this.cookieValue)
    },
    async login() {
      this.isLoading = true;
      this.statusMessage = "";
      try {
        // await firebase.auth().signInWithEmailAndPassword(this.email, this.password);
        const response = await fetch("/tokengenerate", {
          method: "POST",
          body: JSON.stringify({
            message: this.password,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        });
        const data = await response.json();
        if (data.message === "accepted") {
          setCookie("isloggedin", "true", 2);
          this.user = "true";
        } else {
          throw new Error("Access Denied");
        }
      } catch (error) {
        if (error.code === "auth/user-not-found") {
          await this.signup();
        } else {
          this.statusMessage = error.message;
          console.error("Login error:", error);
        }
      }
      this.isLoading = false;
    },

    async logout() {
      // await firebase.auth().signOut();
      document.cookie = "isloggedin=; Max-Age=0";
      this.user = null;
      this.cookieValue = ""; // Update cookieValue
      window.location.href = "/";
    },
  };
}

//   handle firebase auth end

// handle form request to backend

function askQuestion() {
  return {
    searchValue: "",
    isLoading: false,
    isWaiting: false,
    result: "",
    reference: "",
    statusMessage: "",
    stream: "",
    token: "",
    refer: false,
    refcontent: "",
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam rutrum est sit amet mauris condimentum imperdiet.\n Nullam ultrices dui quis nisl volutpat, vel ullamcorper sapien laoreet. Vestibulum ut risus imperdiet,\n imperdiet lacus bibendum, efficitur quam. Integer quis ipsum tempor, malesuada libero id, porttitor magna. Nulla sagittis aliquam tellus, blandit pharetra arcu viverra eget. Integer lectus ligula, facilisis in tristique quis, commodo porta elit. Suspendisse potenti.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam rutrum est sit amet mauris condimentum imperdiet. Nullam ultrices dui quis nisl volutpat, vel ullamcorper sapien laoreet. Vestibulum ut risus imperdiet, imperdiet lacus bibendum, efficitur quam. Integer quis ipsum tempor, malesuada libero id, porttitor magna. Nulla sagittis aliquam tellus, blandit pharetra arcu viverra eget. Integer lectus ligula, facilisis in tristique quis, commodo porta elit. Suspendisse potenti quis nisl volutpat, vel ullamcorper sapien laoreet. Vestibulum ut risus imperdiet,\n imperdiet lacus bibendum, efficitur quam. Integer quis ipsum tempor, malesuada libero id, porttitor magna. Nulla sagittis aliquam tellus, blandit pharetra arcu viverra eget. Integer lectus ligula, facilisis in tristique quis, commodo porta elit. Suspendisse potenti.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam rutrum est sit amet mauris condimentum imperdiet. Nullam ultrices dui quis nisl volutpat, vel ullamcorper sapien laoreet. Vestibulum ut risus imperdiet, imperdiet lacus bibendum, efficitur quam. Integer quis ipsum tempor, malesuada libero id, porttitor magna. Nulla sagittis aliquam tellus, blandit pharetra arcu viverra eget. Integer lectus ligula, facilisis in tristique quis, commodo porta elit. Suspendisse potenti blandit pharetra arcu viverra eget. Integer lectus ligula, facilisis in tristique quis, commodo porta elit.",
    abortController: new AbortController(),
    ai: "openai",
    async handleSubmit() {
      this.abortController = new AbortController(); // Reset the abort controller
      this.result = "";
      this.reference = "";
      this.stream = "";
      this.refcontent = "";
      // Show the Answer component after submitting the form
      // console.log('went there')
      if (this.searchValue.trim().length === 0) {
        alert("Enter Text");
        return;
      }

      if (this.ai === null) {
        alert("Select Ai Model");
        return;
      }
      if (Alpine.store("globalState").showAnswer) {
        Alpine.store("globalState").toggleAnswer();
        Alpine.store("globalState").toggleReference(false);
      }
      this.isLoading = true;
      this.isWaiting = true;
      //  this.token = getCookie('token')
      try {
        // console.log('fetching');
        const response = await fetch("/submit", {
          method: "POST",
          body: JSON.stringify({
            message: this.searchValue,
            ai: this.ai,
            // token:this.token,
          }),
          headers: {
            "Content-Type": "application/json",
          },
          signal: this.abortController.signal,
        });

        if (!response.ok) {
          const json = await response.text();
          throw new Error(json);
        }

        const data = response.body;
        if (!data) {
          return;
        }

        await this.getContent(this.searchValue);
        const reader = data.pipeThrough(new TextDecoderStream()).getReader();
        Alpine.store("globalState").toggleAnswer();
        this.isWaiting = false;
        while (true) {
          const { value, done } = await reader.read();
          if (done) {
            // Alpine.store('globalState').toggleAnswer();
            // console.log('Reference Content ',this.refcontent.trim());
            if (this.refcontent.trim() !== "") {
              Alpine.store("globalState").toggleReference(true);
            }

            this.isLoading = false;
            break;
          }

          this.result += value;
        }
      } catch (error) {
        // Check if the error is caused by request cancellation
        if (error.name === "AbortError") {
          // console.log("Request cancelled");
          this.isLoading = false;
          this.statusMessage = "Request cancelled";
          this.isWaiting = false;
        } else {
          this.isLoading = false;
          console.error("Error:", error);
          this.statusMessage = error;
          this.isWaiting = false;
        }
      }
    },
    async getContent(userprompt) {
      // console.log('start running - ',userprompt);
      try {
        const response = await fetch("/content", {
          method: "POST",
          body: JSON.stringify({
            message: userprompt,
            // token:this.token,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        });
        const data = await response.json();
        //    console.log(data)
        if (data.documentcontent.toString().replace(",", " ") !== "") {
          this.refcontent = data.documentcontent.toString().replace(",", " ");
          this.reference = data.document.toString().replace(",", " ");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },
    cancelRequest() {
      this.abortController.abort(); // Abort the fetch request
    },
  };
}
// handle form request to backend end

// handle typing animation
function typingAnimation() {
  return {
    displayText: "",
    words: ["Generating", "Predicting", "Researching"],
    currentWordIndex: 0,
    typingSpeed: 150,
    deletingSpeed: 100,
    pauseDuration: 1000,
    isDeleting: false,

    async type(currentText, wordIndex) {
      for (let i = 0; i < currentText.length; i++) {
        if (this.currentWordIndex !== wordIndex) return;
        this.displayText = currentText.substr(0, i + 1);
        await this.sleep(this.typingSpeed);
      }
    },

    async delete(currentText, wordIndex) {
      for (let i = currentText.length; i > 0; i--) {
        if (this.currentWordIndex !== wordIndex) return;
        this.displayText = currentText.substr(0, i - 1);
        await this.sleep(this.deletingSpeed);
      }
    },

    async sleep(ms) {
      return new Promise((resolve) => {
        setTimeout(() => resolve(), ms);
      });
    },

    async init() {
      while (true) {
        const currentText = this.words[this.currentWordIndex];
        const wordIndex = this.currentWordIndex;
        await this.type(currentText, wordIndex);
        await this.sleep(this.pauseDuration);
        await this.delete(currentText, wordIndex);
        await this.sleep(this.pauseDuration);
        this.currentWordIndex = (this.currentWordIndex + 1) % this.words.length;
      }
    },
  };
}

// handle answer component start

function answerComponent() {
  return {
    visible: false,
    expanded: false,
    baseClasses:
      "flex justify-center whitespace-pre-wrap text-black border border-gray-300 bg-white items-center transition-all duration-500 ease-in-out mt-5 p-4 rounded",
    sizeClasses: "",
    expand() {
      this.expanded = true;
      this.sizeClasses = this.expanded ? "w-full h-full" : "w-24 h-24";
    },
    showAnswer() {
      this.visible = true;
      setTimeout(() => {
        this.expand();
      }, 1000);
    },
  };
}

// handle answer component end

// global state management start

document.addEventListener("alpine:init", () => {
  Alpine.store("globalState", {
    showAnswer: false,
    showReference: false,
    showBookReference: false,
    toggleAnswer() {
      this.showAnswer = !this.showAnswer;
    },
    toggleReference(status) {
      this.showReference = status;
    },
    toggleBookReference() {
      this.showBookReference = !this.showBookReference;
    },
  });
});

// global state managment end
