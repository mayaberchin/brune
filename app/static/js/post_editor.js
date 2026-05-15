const newPostButton = document.getElementById("newPostButton");
const postEditor = document.getElementById("postEditor");
const cancelPostButton = document.getElementById("cancelPostButton");
const postForm = document.getElementById("postForm");
const postErrorBox = document.getElementById("postErrorBox");
const postTitle = document.getElementById("postTitle");
const postType = document.getElementById("postType");
const postBody = document.getElementById("postBody");
const isAnonymous = document.getElementById("isAnonymous");
const shareWithDojo = document.getElementById("shareWithDojo");

function showPostEditor() {
  postEditor.classList.remove("d-none");
}

function hidePostEditor() {
  postEditor.classList.add("d-none");
  postForm.reset();
  hideError();
}

function showError(message) {
  postErrorBox.textContent = message;
  postErrorBox.classList.remove("d-none");
}

function hideError() {
  postErrorBox.textContent = "";
  postErrorBox.classList.add("d-none");
}

newPostButton.addEventListener("click", showPostEditor);
cancelPostButton.addEventListener("click", hidePostEditor);

postForm.addEventListener("submit", function(event) {
  const postData = {
    title: postTitle.value.trim(),
    postType: postType.value,
    body: postBody.value.trim(),
    isAnonymous: isAnonymous.checked,
    shareWithDojo: shareWithDojo.checked
  };

  if (postData.title === "" || postData.body === "") {
    showError("Please fill out the title and post body.");
    return;
  }

  console.log(postData);
  hidePostEditor();
});
