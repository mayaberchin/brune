function PostPreview({ postData, onOpen, isSelected, showClass, onDelete }) {
  const previewClassName = isSelected
    ? "post-preview selected"
    : "post-preview";

  function deletePost(event) {
    event.stopPropagation();

    if (confirm("Delete this post?")) {
      onDelete(postData.post_id);
    }
  }

  return (
    <div className={previewClassName} onClick={() => onOpen(postData)}>
      <div className="post-preview-top">
        <h2 className="post-preview-title">{postData.title}</h2>

        {postData.can_delete && (
          <button
            type="button"
            className="post-delete-button"
            onClick={deletePost}
            aria-label="Delete post"
          >
            Delete
          </button>
        )}
      </div>

      {showClass && (
        <p className="post-preview-meta">Class: {postData.class_id}</p>
      )}

      <p className="post-preview-body">{postData.body}</p>
    </div>
  );
}

export default PostPreview;
