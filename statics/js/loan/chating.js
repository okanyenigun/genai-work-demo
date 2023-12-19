window.onload = function () {
  // Find the span element by its ID
  var span = document.getElementById("bot-chat-start-time");

  // Get the current date and time
  var now = new Date();

  // Format the time as H:M
  var timeFormatted =
    now.getHours() +
    ":" +
    (now.getMinutes() < 10 ? "0" : "") +
    now.getMinutes();

  // Append the formatted time to the span
  span.textContent = timeFormatted;
};

const chatHistory = document.getElementById("chat-history");
const messageInput = document.getElementById("message-input");

function enterUserText(message) {
  var now = new Date();

  // Format the time as H:M
  var timeFormatted =
    now.getHours() +
    ":" +
    (now.getMinutes() < 10 ? "0" : "") +
    now.getMinutes();
  chatHistory.innerHTML += `
    <div class="chat-message clearfix">
      <img
        src="${userImageSrc}"
        alt=""
        width="32"
        height="32"
      />

      <div class="chat-message-content clearfix">
        <span class="chat-time">${timeFormatted}</span>

          <h5>Customer</h5>

          <p>
           ${message}
          </p>
        </div>
      </div>
      <hr />
  `;
  messageInput.value = "";
}
function enterBotText(message) {
  var now = new Date();

  // Format the time as H:M
  var timeFormatted =
    now.getHours() +
    ":" +
    (now.getMinutes() < 10 ? "0" : "") +
    now.getMinutes();
  chatHistory.innerHTML += `
    <div class="chat-message clearfix">
      <img
        src="${userMediaSrc}chatbot.png"
        alt=""
        width="32"
        height="32"
      />

      <div class="chat-message-content clearfix">
        <span class="chat-time" id="bot-chat-start-time">${timeFormatted}</span>

        <h5>Bot</h5>

        <p>${message}</p>
      </div>
 
    </div>
    <hr />
  `;
}

let bankContainer = document.getElementById("bank-proposal-container");
const container = document.getElementById("container");
function createBankCards(bankResponses, loanTerm) {
  if (!bankContainer) {
    bankContainer = document.createElement("div");
    bankContainer.classList.add("bank-proposal-container");
    bankContainer.id = "bank-proposal-container";
  }
  console.log(bankContainer);
  container.appendChild(bankContainer);
  bankContainer.innerHTML = "";
  var now = new Date();

  // Format the time as H:M
  var timeFormatted =
    now.getHours() +
    ":" +
    (now.getMinutes() < 10 ? "0" : "") +
    now.getMinutes();
  for (let item in bankResponses) {
    let bankProp = bankResponses[item];
    bankContainer.innerHTML += `
      <div class="card">
        <h3 class="card-header">${item}</h3>
    <img src="${userMediaSrc}${item}.png" alt="" />
  
    <div class="card-body">
      <p class="card-text">${loanTerm} AY için ${item} Teklifi</p>
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item">Faiz Oranı: ${bankProp["interest_rate"]} %</li>
      <li class="list-group-item">
        Aylık Taksit: ${bankProp["monthly_payment"]} TL
      </li>
      <li class="list-group-item">
        Toplam Ödeme: ${bankProp["total_payment"]} TL
      </li>
    </ul>
    <div class="card-footer text-muted">${timeFormatted}</div>
  </div>
    `;
  }
}

function requestLoanProposalResponse(data) {
  console.log("data", data);
  let bankResponses = JSON.parse(data["bank_responses"]);
  createBankCards(bankResponses, data["loan_term"]);
  enterBotText("İşte bankaların size özel tekliflerini listeledim.");
}

function colorBankCard(bank) {
  cardEls = document.querySelectorAll(".card");
  console.log("cardEls: ", cardEls);
}

function inquireLoanDetailResponse(data) {
  enterBotText(`${data["answer"]}: ${data["promoting_text"]}`);
  colorBankCard(data["answer"]);
}

function generalInquiry(data) {
  console.log("here");
  console.log(data["answer"]);
  enterBotText(`${data["answer"]}`);
}

function proceedWithLoan(data) {
  window.location.href = "loading/";
}

$(document).ready(function () {
  $("#chat-form").submit(function (event) {
    console.log("inside");
    var message = $("#message-input").val(); // Gets the message from the input field
    var selectedModel = $('input[name="btnradio"]:checked').attr("id"); // Gets the ID of the checked radio button
    enterUserText(message);
    console.log("message: ", message);
    console.log("selectedModel: ", selectedModel);
    event.preventDefault(); // Prevents the default form submission action
    $.ajax({
      type: "POST",
      url: "/ajax/message_handler/",
      data: {
        message: message,
        selected_model: selectedModel,
        csrfmiddlewaretoken: "{{ csrf_token }}", // Include CSRF token
      },
      success: function (response) {
        // Handle response here
        console.log(response); // Log the response from the Django view
        if (response["error"]) {
          enterBotText(`${response["error"]}`);
        }
        if (response["intent"] === "Request Loan Proposals") {
          requestLoanProposalResponse(response);
        } else if (response["intent"] == "Inquire Loan Details") {
          inquireLoanDetailResponse(response);
        } else if (response["intent"] == "General Inquiry") {
          generalInquiry(response);
        } else if (response["intent"] == "Proceed With Loan") {
          proceedWithLoan(response);
        }
      },
    });
  });
});
