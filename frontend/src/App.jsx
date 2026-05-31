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

// get classes from flask later!
const testClasses = [
  { class_id: "1", name: "Software Development" },
  { class_id: "2", name: "Systems" },
  { class_id: "3", name: "Cybersecurity" },
];

function App() {
  const [showPostEditor, setShowPostEditor] = useState(false);
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);

  useEffect(() => { // runs after React renders the pg
    async function loadPosts() { // GET request fo Flask
      const response = await fetch(`/api/posts?category=${selectedPostType}`);
      const data = await response.json();
      setPosts(data.posts);
    }

    loadPosts();
  }, []);

  async function addPost(postData) {
    const response = await fetch("/api/posts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postData),
    });
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

  if (selectedPostType === "chat") {
    return (
      <ChatLayout
        classes={testClasses}
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
      classes={testClasses}
      posts={posts}
      selectedPost={selectedPost}
      showPostEditor={showPostEditor}
      canPost={canPost}
      setSelectedPost={setSelectedPost}
      setShowPostEditor={setShowPostEditor}
      addPost={addPost}
      onVote={votePost}
    />
  );

}

export default App;
