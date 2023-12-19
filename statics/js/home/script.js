const appStoreReview = document.getElementById("app-store-review-box");
const loanFinder = document.getElementById("loan-finder-box");
const monitor = document.getElementById("monitor-box");

appStoreReview.addEventListener("click", () => {
  window.location.href = "review/main/";
});

loanFinder.addEventListener("click", () => {
  window.location.href = "loan/main/";
});

monitor.addEventListener("click", () => {
  window.location.href = "two/";
});
