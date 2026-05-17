const newPostButton = document.getElementById("newPostButton");
const postEditor = document.getElementById("postEditor");
const cancelPostButton = document.getElementById("cancelPostButton");
const postForm = document.getElementById("postForm");
const postErrorBox = document.getElementById("postErrorBox");

const postTitle = document.getElementById("postTitle");
const postType = document.getElementById("postType");
const postClass = document.getElementById("postClass");
const postBody = document.getElementById("postBody");

const isAnonymous = document.getElementById("isAnonymous");
const shareWithDojo = document.getElementById("shareWithDojo");

const templateConfirmModalElement = document.getElementById("templateConfirmModal");
const templateConfirmModal = new bootstrap.Modal(templateConfirmModalElement);
const applyTemplateButton = document.getElementById("applyTemplateButton");

let maybePostType = "";

const postTemplates = {
  question:
`QWonderful:

Awe-inspiring:

Incredible:`,

  note:
`NWonderful:

Awe-inspiring:

Incredible:`,

  announcement:
`AWonderful:

Awe-inspiring:

Incredible:`
};

const postsList = document.getElementById("postsList");

function showPostEditor() {
  postEditor.classList.remove("d-none");

  if (postBody.value.trim() === "") {
    applyTemplate(postType.value);
  }

  resizePostBody();
}

function hidePostEditor() {
  postEditor.classList.add("d-none");
  postForm.reset();
  postBody.style.height = "";
  maybePostType = "";
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

function applyTemplate(postType) {
  postBody.value = postTemplates[postType];
  resizePostBody();
  maybePostType = "";
}

function handlePostTypeChange() {
  const selectedPostType = postType.value;
  if (postBody.value.trim() !== "") {
    maybePostType = selectedPostType;
    templateConfirmModal.show();
    return;
  }

  applyTemplate(selectedPostType);
}

function addPostToPage(postData) {
  const postCard = document.createElement("div");
  postCard.className = "card mb-3";

  postCard.innerHTML = `
  <div class="card-body">
    <h2 class="h5 mb-1"></h2>
    <p class="text-muted mb-2"></p>
    <p class="mb-0"></p>
  </div>
`;

  postCard.querySelector("h2").textContent = postData.title;
  postCard.querySelector(".text-muted").textContent = `Type: ${postData.postType} | Class: ${postData.classId}`;
  postCard.querySelector(".mb-0").textContent = postData.body;

  postsList.prepend(postCard);
}

newPostButton.addEventListener("click", showPostEditor);
cancelPostButton.addEventListener("click", hidePostEditor);
postBody.addEventListener("input", resizePostBody);

postType.addEventListener("change", handlePostTypeChange);

applyTemplateButton.addEventListener("click", function() {
  applyTemplate(maybePostType);
  templateConfirmModal.hide();
});

templateConfirmModalElement.addEventListener("hidden.bs.modal", function() {
  maybePostType = "";
});

postForm.addEventListener("submit", function(event) {
  event.preventDefault(); // stop refreshing!!!

  const postData = {
    title: postTitle.value.trim(),
    postType: postType.value,
    classId: postClass.value,
    body: postBody.value.trim(),
    isAnonymous: isAnonymous.checked,
    shareWithDojo: shareWithDojo.checked
  };

  if (postData.title === "" || postData.classId === "" || postData.body === "") {
    showError("Please fill out the title, class, and post body.");
    return;
  }

  console.log(postData);
  addPostToPage(postData);
  hidePostEditor();
});
