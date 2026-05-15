const newPostButton = document.getElementById("newPostButton");
const postEditor = document.getElementById("postEditor");
const cancelPostButton = document.getElementById("cancelPostButton");
const postForm = document.getElementById("postForm");
const postErrorBox = document.getElementById("postErrorBox");

const postTitle = document.getElementById("postTitle");
const postType = document.getElementById("postType");
const postTemplate = document.getElementById("postTemplate");
const postBody = document.getElementById("postBody");

const isAnonymous = document.getElementById("isAnonymous");
const shareWithDojo = document.getElementById("shareWithDojo");

const postTemplates = {
  question:
`QWonderful:

Awe-inspiring:

Incredible:`,


  debug:
`DWonderful:

Awe-inspiring:

Incredible:`,


  announcement:
`AWonderful:

Awe-inspiring:

Incredible:`
};

function showPostEditor() {
  postEditor.classList.remove("d-none");
  resizePostBody();
}

function hidePostEditor() {
  postEditor.classList.add("d-none");
  postForm.reset();
  postBody.style.height = "";
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

function resizePostBody() {
  postBody.style.height = "auto";
  postBody.style.height = postBody.scrollHeight + "px";
}

newPostButton.addEventListener("click", showPostEditor);
cancelPostButton.addEventListener("click", hidePostEditor);
postBody.addEventListener("input", resizePostBody);

postTemplate.addEventListener("change", function() {
  const selectedTemplate = postTemplate.value;

  if (postBody.value.trim() !== "") {
    showError("Please clear the post body before applying a template.");
    return;
  }

  if (selectedTemplate === "") {
    postBody.value = "";
    resizePostBody();
    return;
  }

  postBody.value = postTemplates[selectedTemplate];
  resizePostBody();
});

postForm.addEventListener("submit", function(event) {
  event.preventDefault(); // stop refreshing!!!

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
