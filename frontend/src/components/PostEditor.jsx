import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";

const questionTemplate =
`Problem encountered:


Steps already taken:


Additional context:


`;

function PostEditor({ selectedPostType, classes, onCancel, onSubmit }) {
  const [title, setTitle] = useState("");
  const [postClass, setPostClass] = useState("");

  const [body, setBody] = useState(
    selectedPostType === "question" ? questionTemplate : ""
  );

  const [isAnonymous, setIsAnonymous] = useState(false);
  const [shareWithDojo, setShareWithDojo] = useState(false);
  const [mode, setMode] = useState("editor");
  const [showPreview, setShowPreview] = useState(true);
  const [attachment, setAttachment] = useState(null);

  const [error, setError] = useState("");

  // manual DOM manipulation htmlFor text-box adjustments!
  const postBodyRef = useRef(null);
  useEffect(() => {
    resizePostBody();
  }, [body]);

  function resizePostBody() {
    if (postBodyRef.current === null) {
      return;
    }

    postBodyRef.current.style.height = "auto";
    postBodyRef.current.style.height = postBodyRef.current.scrollHeight + "px";
  }

  function handleSubmit(event) {
    // prevents refresh!
    event.preventDefault();

    const postData = {
      title: title.trim(),
      category: selectedPostType,
      class_id: postClass,
      body: body.trim(),
      isAnonymous: isAnonymous,
      shareWithDojo: shareWithDojo,
      attachment: attachment,
    };

    if (postData.title === "" || postData.class_id === "" || postData.body === "") {
      setError("Please fill out the title, class, and post body.");
      return;
    }

    onSubmit(postData);
  }

  function addStyle(left, right, exampleText) {
    const box = postBodyRef.current;

    if (box === null) {
      return;
    }

    const start = box.selectionStart;
    const end = box.selectionEnd;
    const selected = body.slice(start, end);
    const textToAdd = selected || exampleText;
    const styledText = left + textToAdd + right;
    const newBody = body.slice(0, start) + styledText + body.slice(end);

    setBody(newBody);

    setTimeout(() => {
      box.focus();

      if (selected === "") {
        const textStart = start + left.length;
        const textEnd = textStart + exampleText.length;
        box.setSelectionRange(textStart, textEnd);
      } else {
        box.setSelectionRange(start, start + styledText.length);
      }
    }, 0);
  }

  return (
    <section className="post-editor-preview">
      <h2 className="mb-2">New Post</h2>
      <p className="text-muted mb-4">
        Write a question, note, or announcement for your class.
      </p>

      {error !== "" ? (
        <div className="alert alert-danger">
          {error}
        </div>
      ) : null}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="postTitle" className="form-label"> Title </label>
          <input
            id="postTitle"
            name="title"
            type="text"
            className="form-control"
            maxLength="120"
            placeholder="What is this post about?"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
        </div>

        <div className="mb-3">
          <label htmlFor="postClass" className="form-label"> Class </label>
          <select
            id="postClass"
            name="class_id"
            className="form-select"
            value={postClass}
            onChange={(event) => setPostClass(event.target.value)}
            required>
            <option value=""> Choose a class </option>
            {classes.map((classInfo) => (
              <option key={classInfo.class_id} value={classInfo.class_id}>
                {classInfo.name}
              </option>
            ))}
          </select>
        </div>

        <div className="mb-3">
          <div className="post-body-label-row">
            <label htmlFor="postBody" className="form-label"> Post Body </label>

            <button
              type="button"
              className="btn btn-outline-secondary btn-sm"
              onClick={() => setShowPreview(!showPreview)}
            >
              {showPreview ? "Hide Preview" : "Preview"}
            </button>
          </div>

          <div className="post-editor-tabs">

            {/* Default Editor  */}
            <button
              type="button"
              className={mode === "editor" ? "post-editor-tab active" : "post-editor-tab"}
              onClick={() => setMode("editor")}
            >
              Editor
            </button>

            {/* Markdown Editor  */}
            <button
              type="button"
              className={mode === "markdown" ? "post-editor-tab active" : "post-editor-tab"}
              onClick={() => setMode("markdown")}
            >
              Markdown Editor
            </button>

            {/* Quill Editor  */}
            <button
              type="button"
              className={mode === "quill" ? "post-editor-tab active" : "post-editor-tab"}
              onClick={() => setMode("quill")}
            >
              Quill Editor
            </button>

          </div>

          {mode === "editor" && (
            <div className="post-format-toolbar" aria-label="Text formatting">
              <button
                type="button"
                className="post-format-button"
                onClick={() => addStyle("**", "**", "bold text")}
                title="Bold"
              >
                <strong>B</strong>
              </button>

              <button
                type="button"
                className="post-format-button"
                onClick={() => addStyle("*", "*", "italic text")}
                title="Italic"
              >
                <em>I</em>
              </button>

              <button
                type="button"
                className="post-format-button"
                onClick={() => addStyle("<u>", "</u>", "underlined text")}
                title="Underline"
              >
                <u>U</u>
              </button>
            </div>
          )}

          <div className={showPreview ? "post-body-area has-preview" : "post-body-area"}>
            <textarea
              ref={postBodyRef}
              id="postBody"
              name="postBody"
              className="form-control post-body-input"
              placeholder="Type your post here..."
              value={body}
              onChange={(event) => setBody(event.target.value)}
            ></textarea>

            {showPreview && (
              <div className={mode === "markdown" ? "post-body-preview" : "post-body-preview plain"}>
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                  {body === "" ? "Nothing to preview yet." : body}
                </ReactMarkdown>
                {/* Guide:
                Text Formatting:
                  - **Bold** or __Bold__
                  - *Italic* or _Italic_
                  - ***Bold and Italic** or ___Bold and Italic___
                  - ~~Strikethrough~~
                  - `Inline Code`

                Line Breaks:
                  - https://www.craftmarkdown.com/markdown-cheat-sheet */}
              </div>
            )}
          </div>
        </div>

        <div className="form-check mb-2">
          <input
            id="isAnonymous"
            type="checkbox"
            className="form-check-input"
            checked={isAnonymous}
            onChange={(event) => setIsAnonymous(event.target.checked)}
          />
          <label htmlFor="isAnonymous" className="form-check-label"> Post Anonymously </label>
        </div>

        <div className="form-check mb-4">
          <input
            id="shareWithDojo"
            type="checkbox"
            className="form-check-input"
            checked={shareWithDojo}
            onChange={(event) => setShareWithDojo(event.target.checked)}
          />
          <label htmlFor="shareWithDojo" className="form-check-label"> Share with Dojo </label>
        </div>

        <div className="mb-4">
          <label htmlFor="postAttachment" className="form-label"> Attachment </label>
          <input
            id="postAttachment"
            type="file"
            className="form-control"
            accept=".png,.jpg,.jpeg,.gif,.pdf,.txt,.doc,.docx"
            onChange={(event) => setAttachment(event.target.files[0] || null)}
          />
        </div>

        <div className="d-flex justify-content-end gap-2">
          <button
            type="button"
            className="btn btn-outline-secondary"
            onClick={onCancel}
          >
            Cancel
          </button>

          <button type="submit" className="btn btn-primary"> Post </button>
        </div>
      </form>
    </section>

    // <!-- Bootstrap modal htmlFor template confirmation -->
    // <div className="modal fade" id="templateConfirmModal" tabindex="-1">
    //   <div className="modal-dialog modal-dialog-centered">
    //     <div className="modal-content">
    //
    //       <div className="modal-header">
    //         <h2 className="modal-title fs-5" id="templateConfirmTitle"> Replace current post body? </h2>
    //         <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
    //       </div>
    //
    //       <div className="modal-body">
    //         Applying this post type's template will replace the text currently in the post body.
    //       </div>
    //
    //       <div className="modal-footer">
    //         <button type="button" className="btn btn-outline-secondary" data-bs-dismiss="modal"> Cancel </button>
    //         <button id="applyTemplateButton" type="button" className="btn btn-primary"> Apply Template </button>
    //       </div>
    //     </div>
    //
    //   </div>
    // </div>
  );
}

export default PostEditor;
