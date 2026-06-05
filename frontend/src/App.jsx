import { useState, useEffect } from "react";
import PostEditor from "./components/PostEditor";
import PostPreview from "./components/PostPreview";
import PostView from "./components/PostView";
import PostLayout from "./layouts/PostLayout";
import ChatLayout from "./layouts/ChatLayout";

const root = document.getElementById("root");

const selectedPostType = root.dataset.postType;
const pageTitle = root.dataset.pageTitle;
const pageDescription = root.dataset.pageDescription;
const newPostLabel = root.dataset.newPostLabel;
const canPost = root.dataset.canPost === "yes";
const currentUserEmail = root.dataset.currentUserEmail;

function App() {
  const [showPostEditor, setShowPostEditor] = useState(false);
  const [posts, setPosts] = useState([]);
  const [classes, setClasses] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);

  useEffect(() => { // runs after React renders the pg
    async function loadClasses() {
      const response = await fetch("/api/classes");
      const data = await response.json();
      setClasses(data.classes);
    }

    async function loadPosts() { // GET request fo Flask
      const response = await fetch(`/api/posts?category=${selectedPostType}`);
      const data = await response.json();
      setPosts(data.posts);
    }

    loadClasses();
    loadPosts();
  }, []);

  async function addPost(postData) {
    let requestInfo = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postData),
    };

    if (postData.attachment != null) {
      const formData = new FormData();
      formData.append("title", postData.title);
      formData.append("category", postData.category);
      formData.append("class_id", postData.class_id);
      formData.append("body", postData.body);
      formData.append("isAnonymous", postData.isAnonymous ? "yes" : "");
      formData.append("shareWithDojo", postData.shareWithDojo ? "yes" : "");
      formData.append("attachment", postData.attachment);

      requestInfo = {
        method: "POST",
        body: formData,
      };
    }

    const response = await fetch("/api/posts", requestInfo);
    const data = await response.json();

    if (!response.ok) {
      alert(data.error);
      return null;
    }

    // crete array w/ newest post in front
    setPosts((currentPosts) => [data.post, ...currentPosts]);
    setShowPostEditor(false);
    return data.post;
  }

  function addLivePost(post) {
    setPosts((currentPosts) => {
      const alreadyLoaded = currentPosts.some(
        (currentPost) => currentPost.post_id === post.post_id
      );

      if (alreadyLoaded) {
        return currentPosts;
      }

      return [post, ...currentPosts];
    });
  }

  async function votePost(postId) {
    const response = await fetch(`/api/posts/${postId}/upvote`, {
      method: "POST",
    });
    const data = await response.json();

    if (!response.ok) {
      alert(data.error);
      return null;
    }

    setPosts((currentPosts) => (
      currentPosts.map((post) => (
        post.post_id === postId ? data.post : post
      ))
    ));

    setSelectedPost((currentPost) => (
      currentPost !== null && currentPost.post_id === postId
        ? data.post
        : currentPost
    ));

    return data.post;
  }

  async function deletePost(postId) {
    const response = await fetch(`/api/posts/${postId}`, {
      method: "DELETE",
    });
    const data = await response.json();

    if (!response.ok) {
      alert(data.error);
      return false;
    }

    setPosts((currentPosts) => (
      currentPosts.filter((post) => post.post_id !== postId)
    ));

    setSelectedPost((currentPost) => (
      currentPost !== null && currentPost.post_id === postId
        ? null
        : currentPost
    ));
    return true;
  }

  const canPostOnPage =
    selectedPostType === "announcement"
      ? classes.some((classInfo) => classInfo.is_teacher)
      : canPost;

  if (selectedPostType === "chat") {
    return (
      <ChatLayout
        classes={classes}
        posts={posts}
        selectedPostType={selectedPostType}
        currentUserEmail={currentUserEmail}
        addPost={addPost}
        addLivePost={addLivePost}
        onVote={votePost}
      />
    );
  }

  return (
    <PostLayout
      pageTitle={pageTitle}
      pageDescription={pageDescription}
      newPostLabel={newPostLabel}
      selectedPostType={selectedPostType}
      classes={classes}
      posts={posts}
      selectedPost={selectedPost}
      showPostEditor={showPostEditor}
      canPost={canPostOnPage}
      setSelectedPost={setSelectedPost}
      setShowPostEditor={setShowPostEditor}
      addPost={addPost}
      onVote={votePost}
      onDelete={deletePost}
    />
  );

}

export default App;
