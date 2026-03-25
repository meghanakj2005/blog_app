const BASE_URL = "http://127.0.0.1:5000";

const listContainer = document.getElementById("listContainer");
const details = document.getElementById("details");
const sidebarTitle = document.getElementById("sidebarTitle");
const contentTitle = document.getElementById("contentTitle");

let currentMode = "posts";
let localPosts = [];

function setActiveButton(clickedButton) {
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
    clickedButton.classList.add("active");
}

function showSection(section, button) {
    setActiveButton(button);

    if (section === "posts") {
        currentMode = "posts";
        sidebarTitle.textContent = "Posts";
        contentTitle.textContent = "Post Details";
        details.innerHTML = `<p class="placeholder">Select a post card from the left to view details and JSONPlaceholder comments.</p>`;
        loadJsonPosts();
    } else if (section === "create") {
        currentMode = "create";
        sidebarTitle.textContent = "My Posts";
        contentTitle.textContent = "Create Post";
        renderCreateForm();
        loadLocalPosts();
    }
}

async function loadJsonPosts() {
    listContainer.innerHTML = `<p class="loading">Loading posts...</p>`;

    try {
        const response = await fetch("https://jsonplaceholder.typicode.com/posts?_limit=25");
        if (!response.ok) throw new Error("Failed to fetch JSONPlaceholder posts");

        const posts = await response.json();

        listContainer.innerHTML = "";

        posts.forEach(post => {
            const item = document.createElement("div");
            item.className = "list-item";

            const imageUrl = `https://picsum.photos/seed/json-${post.id}/500/300`;

            item.innerHTML = `
                <img class="sidebar-card-img" src="${imageUrl}" alt="Post image">
                <div class="sidebar-card-body">
                    <h3>${sanitizeHTML(post.title)}</h3>
                    <div class="sidebar-card-meta">Source: JSONPlaceholder</div>
                    <div class="sidebar-card-text">${sanitizeHTML(truncateText(post.body, 80))}</div>
                </div>
            `;

            item.addEventListener("click", () => showJsonPostDetails(post.id));
            listContainer.appendChild(item);
        });
    } catch (error) {
        console.error(error);
        listContainer.innerHTML = `<p>Failed to load posts.</p>`;
    }
}

async function loadLocalPosts() {
    listContainer.innerHTML = `<p class="loading">Loading your posts...</p>`;

    try {
        const response = await fetch(`${BASE_URL}/api/posts`);
        if (!response.ok) throw new Error("Failed to fetch local posts");

        localPosts = await response.json();

        if (!localPosts.length) {
            listContainer.innerHTML = `<p>No created posts yet.</p>`;
            return;
        }

        listContainer.innerHTML = "";

        localPosts.forEach(post => {
            const item = document.createElement("div");
            item.className = "list-item";

            const imageUrl = post.image
                ? post.image
                : `https://picsum.photos/seed/local-${post.id}/500/300`;

            item.innerHTML = `
                <img class="sidebar-card-img" src="${imageUrl}" alt="Post image">
                <div class="sidebar-card-body">
                    <h3>${sanitizeHTML(post.title)}</h3>
                    <div class="sidebar-card-meta">Source: My Post</div>
                    <div class="sidebar-card-text">${sanitizeHTML(truncateText(post.body, 80))}</div>
                </div>
            `;

            item.addEventListener("click", () => showLocalPostDetails(post.id));
            listContainer.appendChild(item);
        });
    } catch (error) {
        console.error(error);
        listContainer.innerHTML = `<p>Failed to load your posts.</p>`;
    }
}

async function showJsonPostDetails(postId) {
    details.innerHTML = `<p class="loading">Loading post details...</p>`;

    try {
        const postResponse = await fetch(`https://jsonplaceholder.typicode.com/posts/${postId}`);
        const commentsResponse = await fetch(`https://jsonplaceholder.typicode.com/comments?postId=${postId}`);

        if (!postResponse.ok || !commentsResponse.ok) {
            throw new Error("Failed to fetch JSONPlaceholder post details");
        }

        const post = await postResponse.json();
        const comments = await commentsResponse.json();

        const imageUrl = `https://picsum.photos/seed/detail-json-${post.id}/1000/450`;

        details.innerHTML = `
            <div class="detail-card">
                <h2>${sanitizeHTML(post.title)}</h2>
                <div class="detail-meta"><strong>User ID:</strong> ${post.userId}</div>
                <div class="detail-meta"><strong>Source:</strong> JSONPlaceholder</div>

                <img class="post-image" src="${imageUrl}" alt="Post image">

                <div class="post-body">${sanitizeHTML(post.body)}</div>

                <hr>

                <div class="section-title">Comments</div>
                <div id="commentList">
                    ${
                        comments.length > 0
                            ? comments.map(comment => `
                                <div class="comment-card">
                                    <p><strong>${sanitizeHTML(comment.name)}</strong></p>
                                    <p>${sanitizeHTML(comment.email)}</p>
                                    <p>${sanitizeHTML(comment.body)}</p>
                                </div>
                            `).join("")
                            : `<p>No comments found.</p>`
                    }
                </div>
            </div>
        `;
    } catch (error) {
        console.error(error);
        details.innerHTML = `<p>Failed to load JSONPlaceholder post details.</p>`;
    }
}

async function showLocalPostDetails(postId) {
    details.innerHTML = `<p class="loading">Loading your post...</p>`;

    try {
        const postResponse = await fetch(`${BASE_URL}/api/posts/${postId}`);
        const commentsResponse = await fetch(`${BASE_URL}/api/comments?postId=${postId}`);

        if (!postResponse.ok || !commentsResponse.ok) {
            throw new Error("Failed to fetch local post details");
        }

        const post = await postResponse.json();
        const comments = await commentsResponse.json();

        const imageUrl = post.image
            ? post.image
            : `https://picsum.photos/seed/detail-local-${post.id}/1000/450`;

        details.innerHTML = `
            <div class="detail-card">
                <h2>${sanitizeHTML(post.title)}</h2>
                <div class="detail-meta"><strong>User ID:</strong> ${sanitizeHTML(post.user_id)}</div>
                <div class="detail-meta"><strong>Category:</strong> ${sanitizeHTML(post.category || "General")}</div>
                <div class="detail-meta"><strong>Source:</strong> My Post</div>

                <img class="post-image" src="${imageUrl}" alt="Post image">

                <div class="post-body">${sanitizeHTML(post.body)}</div>

                <hr>

                <div class="section-title">Comments</div>
                <div id="commentList">
                    ${
                        comments.length > 0
                            ? comments.map(comment => `
                                <div class="comment-card">
                                    <p><strong>${sanitizeHTML(comment.name)}</strong></p>
                                    <p>${sanitizeHTML(comment.body)}</p>
                                </div>
                            `).join("")
                            : `<p>No comments yet.</p>`
                    }
                </div>

                <hr>

                <div class="section-title">Add Comment</div>
                <form id="commentForm">
                    <input type="text" id="commentName" placeholder="Your name" required>
                    <textarea id="commentBody" placeholder="Write your comment" required></textarea>
                    <button type="submit" class="btn">Add Comment</button>
                </form>
            </div>
        `;

        document.getElementById("commentForm").addEventListener("submit", async function (e) {
            e.preventDefault();

            const name = document.getElementById("commentName").value.trim();
            const body = document.getElementById("commentBody").value.trim();

            if (!name || !body) {
                alert("Please fill all comment fields");
                return;
            }

            const response = await fetch(`${BASE_URL}/api/comments`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    post_id: post.id,
                    name,
                    body
                })
            });

            if (response.ok) {
                showLocalPostDetails(post.id);
            } else {
                alert("Failed to add comment");
            }
        });
    } catch (error) {
        console.error(error);
        details.innerHTML = `<p>Failed to load your post details.</p>`;
    }
}

function renderCreateForm() {
    details.innerHTML = `
        <form id="postForm" enctype="multipart/form-data" class="form-card">
            <input type="number" name="user_id" placeholder="User ID" required>
            <input type="text" name="title" placeholder="Post Title" required>
            <textarea name="body" placeholder="Post Body" required></textarea>
            <input type="text" name="category" placeholder="Category" required>
            <input type="file" name="image" accept="image/*">
            <button type="submit" class="btn">Create Post</button>
        </form>
    `;

    document.getElementById("postForm").addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(this);

        try {
            const response = await fetch(`${BASE_URL}/api/posts`, {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                alert("Post created successfully");
                this.reset();
                await loadLocalPosts();
                details.innerHTML = `<p class="placeholder">Post created. Click your post from the left and add comments.</p>`;
            } else {
                alert("Failed to create post");
            }
        } catch (error) {
            console.error(error);
            alert("Server error while creating post");
        }
    });
}

function truncateText(text, maxLength) {
    const str = String(text ?? "");
    return str.length > maxLength ? str.slice(0, maxLength) + "..." : str;
}

function sanitizeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

loadJsonPosts();