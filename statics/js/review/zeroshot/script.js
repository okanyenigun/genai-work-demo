// RADIO BUTTONS -> TABS
const radioBtns = document.querySelectorAll(".btn-check");

const textFrame = document.getElementById("text-frame");
const crossFrame = document.getElementById("cross-frame");
const allFrame = document.getElementById("all-frame");
const exportFrame = document.getElementById("export-frame");
const modelsFrame = document.getElementById("models-frame");

function displayCheckedForm_by_radio(radio) {
  textFrame.style.display = "none";
  crossFrame.style.display = "none";
  allFrame.style.display = "none";
  exportFrame.style.display = "none";
  modelsFrame.style.display = "none";
  if (radio.id === "btnradio1") {
    // display text
    textFrame.style.display = "block";
  } else if (radio.id === "btnradio2") {
    // display cross
    crossFrame.style.display = "block";
  } else if (radio.id === "btnradio3") {
    // display all
    allFrame.style.display = "block";
  } else if (radio.id === "btnradio4") {
    // display export
    exportFrame.style.display = "block";
  } else if (radio.id === "btnradio5") {
    // display models
    modelsFrame.style.display = "block";
  }
}

function displayCheckedForm_by_textname(text) {
  textFrame.style.display = "none";
  crossFrame.style.display = "none";
  allFrame.style.display = "none";
  exportFrame.style.display = "none";
  modelsFrame.style.display = "none";
  if (text === "text") {
    // display text
    textFrame.style.display = "block";
  } else if (text === "cross") {
    // display cross
    crossFrame.style.display = "block";
  } else if (text === "all") {
    // display all
    allFrame.style.display = "block";
  } else if (text === "export") {
    // display export
    exportFrame.style.display = "block";
  } else if (text === "models") {
    // display models
    modelsFrame.style.display = "block";
  }
}

radioBtns.forEach((radio) => {
  radio.addEventListener("change", () => {
    if (radio.checked) {
      displayCheckedForm_by_radio(radio);
    }
  });
});
console.log("tabValue", tabValue);
if (tabValue) {
  displayCheckedForm_by_textname(tabValue);
}
