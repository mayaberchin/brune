const newPostButton = document.getElementById("newPostButton");
const postEditor = document.getElementById("postEditor");
const cancelPostButton = document.getElementById("cancelPostButton");
const postForm = document.getElementById("postForm");
const postErrorBox = document.getElementById("postErrorBox");

const postTitle = document.getElementById("postTitle");
const postType = document.getElementById("postType");
const postClass = document.getElementById("postClass");
const postTemplate = document.getElementById("postTemplate");
const postBody = document.getElementById("postBody");

const isAnonymous = document.getElementById("isAnonymous");
const shareWithDojo = document.getElementById("shareWithDojo");

const templateConfirmModalElement = document.getElementById("templateConfirmModal");
const templateConfirmModal = new bootstrap.Modal(templateConfirmModalElement);
const applyTemplateButton = document.getElementById("applyTemplateButton");
let maybeTemplate = "";

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

function applyTemplate(template) {
  if (template === "") {
    postBody.value = "";
  }
  else {
    postBody.value = postTemplates[template];
  }
  resizePostBody();
  postTemplate.value = "";
  maybeTemplate = "";
}

newPostButton.addEventListener("click", showPostEditor);
cancelPostButton.addEventListener("click", hidePostEditor);
postBody.addEventListener("input", resizePostBody);

postTemplate.addEventListener("change", function() {
  const selectedTemplate = postTemplate.value;

  if (selectedTemplate === "") {
    postBody.value = "";
    resizePostBody();
    return;
  }

  if (postBody.value.trim() !== "") {
    maybeTemplate = selectedTemplate;
    templateConfirmModal.show();
    return;
  }

  applyTemplate(selectedTemplate);
});

applyTemplateButton.addEventListener("click", function() {
  applyTemplate(maybeTemplate);
  templateConfirmModal.hide();
});

templateConfirmModalElement.addEventListener("hidden.bs.modal", function() {
  postTemplate.value = "";
  maybeTemplate = "";
});

postForm.addEventListener("submit", function(event) {
  event.preventDefault(); // stop refreshing!!!

  const selectedClass = postClass.options[postClass.selectedIndex];

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
  hidePostEditor();
});
