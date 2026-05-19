import { useEffect, useRef, useState } from "react";

const questionTemplate =
`What problem did you encounter?


What steps have you taken to remedy this problem?


Any resources/code snippets?


`;

function PostEditor({ selectedPostType, classes, onCancel, onSubmit }) {
  const [title, setTitle] = useState("");
  const [postClass, setPostClass] = useState("");

  const [body, setBody] = useState(
    selectedPostType === "question" ? questionTemplate : ""
  );

  const [isAnonymous, setIsAnonymous] = useState(false);
  const [shareWithDojo, setShareWithDojo] = useState(false);

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
      shareWithDojo: shareWithDojo
    };

    if (postData.title === "" || postData.class_id === "" || postData.body === "") {
      setError("Please fill out the title, class, and post body.");
      return;
    }

    onSubmit(postData);
  }

  return (
    <section className="post-editor-card">
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
            name="classId"
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
          <label htmlFor="postBody" className="form-label"> Post Body </label>
          <textarea
            ref={postBodyRef}
            id="postBody"
            name="postBody"
            className="form-control post-body-input"
            placeholder="Type your post here..."
            value={body}
            onChange={(event) => setBody(event.target.value)}
          ></textarea>
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
