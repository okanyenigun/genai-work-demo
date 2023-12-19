$(document).ready(function () {
  $("#live-chat header").on("click", function () {
    console.log("clicked");
    $(".chat").slideToggle(300, "swing");
    $(".chat-message-counter").fadeToggle(300, "swing");
  });

  $(".chat-close").on("click", function (e) {
    e.preventDefault();
    $("#live-chat").fadeOut(300);
  });
});
