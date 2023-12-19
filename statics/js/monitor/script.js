const predictionsFrame = document.getElementById("predictions");
function displayPredictions(lr, rf, inputs) {
  predictionsFrame.innerHTML = "";
  if (lr === 1) {
    predictionsFrame.innerHTML += `
        <div class="card text-white bg-success mb-3" style="max-width: 20rem;">
            <div class="card-header">Logistic Regression</div>
            <div class="card-body">
                <h4 class="card-title">Prediction: ${lr}</h4>
                <p class="card-text">${inputs}</p>
            </div>
        </div>`;
  } else if (lr === 0) {
    predictionsFrame.innerHTML += `
        <div class="card text-white bg-danger mb-3" style="max-width: 20rem;">
            <div class="card-header">Logistic Regression</div>
            <div class="card-body">
                <h4 class="card-title">Prediction: ${lr}</h4>
                <p class="card-text">${inputs}</p>
            </div>
        </div>
`;
  }
  if (rf === 1) {
    predictionsFrame.innerHTML += `
        <div class="card text-white bg-success mb-3" style="max-width: 20rem;">
            <div class="card-header">Random Forest</div>
            <div class="card-body">
                <h4 class="card-title">Prediction: ${rf}</h4>
                <p class="card-text">${inputs}</p>
            </div>
        </div>
`;
  } else {
    predictionsFrame.innerHTML += `
        <div class="card text-white bg-danger mb-3" style="max-width: 20rem;">
            <div class="card-header">Random Forest</div>
            <div class="card-body">
                <h4 class="card-title">Prediction: ${rf}</h4>
                <p class="card-text">${inputs}</p>
            </div>
        </div>
`;
  }
}

function displayModelParameterTable(jsonString) {
  let jsonData = JSON.parse(jsonString);
  let table = "<table border='1' class='table table-hover table-sm'>";
  table +=
    "<thead><tr><th scope='col'>Model Name</th><th scope='col'>Parameter Name</th><th scope='col'>Previous Model Value</th><th scope='col'>New Model Value</th></tr></thead>";

  jsonData.forEach(function (row) {
    table += "<tr class='table-secondary'>";
    table += `<td>${row["Model Name"]}</td>`;
    table += `<td>${row["Parameter Name"]}</td>`;
    table += `<td>${row["Previous Model Value"]}</td>`;
    table += `<td>${row["New Model Value"]}</td>`;
    table += "</tr>";
  });

  table += "</table>";
  document.getElementById("model-parameter-table").innerHTML = table;
}

function displayModelEvalTable(jsonString) {
  let jsonData = JSON.parse(jsonString);
  let table = "<table border='1' class='table table-hover'>";
  table +=
    "<thead><tr><th scope='col'>Model Name</th><th scope='col'>Metric Name</th><th scope='col'>Previous Model Score</th><th scope='col'>New Model Score</th><th scope='col'>Performance</th></tr></thead>";

  jsonData.forEach(function (row) {
    table += "<tr class='table-secondary'>";
    table += `<td>${row["Model Name"]}</td>`;
    table += `<td>${row["Metric Name"]}</td>`;
    table += `<td>${row["Previous Model Score"]}</td>`;
    table += `<td>${row["New Model Score"]}</td>`;
    table += `<td>${row["Performance"]}</td>`;
    table += "</tr>";
  });

  table += "</table>";
  document.getElementById("model-eval-table").innerHTML = table;
}

function displayDataDriftChart(existedCounts, new_data) {
  // Update existing data
  myChart.data.datasets[0].data = existedCounts;
  myChart.data.datasets[1].data = new_data;
  myChart.update();
}

function displayConceptDriftChart(existedVals, newVals) {
  scatterChart.data.datasets[0].data = existedVals;
  scatterChart.data.datasets[1].data = newVals;
  scatterChart.update();
}

function handleAll(data) {
  console.log(data);
  displayPredictions(data["logreg_pred"], data["rf_pred"], data["inputs"]);
  displayModelParameterTable(data["model_parameters"]);
  displayModelEvalTable(data["model_evaluations"]);
  displayDataDriftChart(
    data["data_drift_existed_counts"],
    data["data_drift_new_points"]
  );
  displayConceptDriftChart(
    data["concept_drift_existed_values"],
    data["concept_drift_new_points"]
  );
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function sendChartImageToServer(chart, filename) {
  var imageData = chart.toBase64Image();

  // Use AJAX to send data to the server
  fetch("ajax/saveimage/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"), // Add this if you're using CSRF tokens
    },
    body: JSON.stringify({ imageData: imageData, filename: filename }),
  }).then((response) => {
    if (response.ok) {
      console.log("Image saved successfully");
    } else {
      console.error("Failed to save the image");
    }
  });
}

const chatBot = document.getElementById("chatbot");
$(document).ready(function () {
  $("#ask").on("click", (e) => {
    console.log("clicked");
    var message = $("#exampleTextarea").val();
    console.log("message: ", message);
    sendChartImageToServer(myChart, "data_drift.png");
    sendChartImageToServer(scatterChart, "concept_drift.png");
    e.preventDefault();
    $.ajax({
      type: "GET",
      url: "/ajax/message_handler_monitor/",
      data: {
        message: message,
      },
      success: function (response) {
        console.log("response: ", response);
        chatBot.innerHTML = `<p>${response["definition"]}</p><p>${response["explanation"]}</p>`;
      },
    });
  });
});
