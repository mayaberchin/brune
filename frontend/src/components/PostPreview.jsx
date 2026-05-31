function PostPreview({ postData, onOpen, isSelected, showClass }) {
  const previewClassName = isSelected
    ? "post-preview selected"
    : "post-preview";

  return (
    <div className={previewClassName} onClick={() => onOpen(postData)}>
      <h2 className="post-preview-title">{postData.title}</h2>

      {showClass && (
        <p className="post-preview-meta">Class: {postData.class_id}</p>
      )}

      <p className="post-preview-body">{postData.body}</p>
    </div>
  );
}

export default PostPreview;
