// Скрываем форму и кнопки при загрузке страницы, но показываем Sign In
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("loginFormContainer").classList.remove("visible");
    document.querySelector(".user-info-btn").classList.remove("visible");
    document.querySelector(".logout-btn").classList.remove("visible");
    document.querySelector(".sign-in-btn").classList.add("visible"); // Показываем Sign In
});

function toggleLoginForm() {
    const formContainer = document.getElementById("loginFormContainer");
    const isVisible = formContainer.classList.contains("visible");
    if (isVisible) {
        formContainer.classList.remove("visible");
    } else {
        formContainer.classList.add("visible");
    }
}

function hideLoginForm() {
    document.getElementById("loginFormContainer").classList.remove("visible");
    document.getElementById("loginError").style.display = "none";
}

async function handleLogin(event) {
    event.preventDefault();
    const form = document.getElementById("loginForm");
    const formData = new FormData(form);
    const errorElement = document.getElementById("loginError");

    try {
        const response = await fetch("/auth/token", {
            method: "POST",
            body: formData
        });
        const result = await response.json();
        console.log("Login response:", result);

        if (response.ok) {
            // Сохраняем токены в localStorage
            if (result.access_token && result.refresh_token) {
                localStorage.setItem("access_token", result.access_token);
                localStorage.setItem("refresh_token", result.refresh_token);
                console.log("Tokens saved to localStorage:", {
                    access_token: localStorage.getItem("access_token"),
                    refresh_token: localStorage.getItem("refresh_token")
                });
            } else {
                console.error("Tokens not found in response:", result);
                errorElement.textContent = "Invalid response from server.";
                errorElement.style.display = "block";
                return;
            }

            hideLoginForm();
            // Скрываем кнопку Sign In
            document.querySelector(".sign-in-btn").classList.remove("visible");
            // Показываем кнопки Get Info и Logout
            document.querySelector(".user-info-btn").classList.add("visible");
            document.querySelector(".logout-btn").classList.add("visible");
        } else {
            errorElement.textContent = result.detail || "Login failed";
            errorElement.style.display = "block";
        }
    } catch (error) {
        console.error("Login error:", error);
        errorElement.textContent = "An error occurred. Please try again.";
        errorElement.style.display = "block";
    }
}

async function getUserInfo() {
    const accessToken = localStorage.getItem("access_token");
    console.log("Access token from localStorage:", accessToken);

    if (!accessToken) {
        alert("Please sign in first!");
        return;
    }

    try {
        const response = await fetch("/auth/me", {
            headers: {
                "Authorization": `Bearer ${accessToken}`
            }
        });
        console.log("Get Info response status:", response.status);

        if (response.ok) {
            const userData = await response.json();
            console.log("User data:", userData);
            document.getElementById("userInfo").innerHTML = `
                <h3>User Info:</h3>
                <p>Username: ${userData.username}</p>
            `;
            document.querySelector(".user-info").classList.add("visible");
        } else {
            alert("Access denied. Please sign in again.");
        }
    } catch (error) {
        console.error("Get Info error:", error);
        alert("An error occurred. Please try again.");
    }
}

function logout() {
    // Удаляем токены из localStorage
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    console.log("Tokens removed from localStorage");

    // Скрываем кнопки Get Info и Logout
    document.querySelector(".user-info-btn").classList.remove("visible");
    document.querySelector(".logout-btn").classList.remove("visible");
    // Показываем кнопку Sign In
    document.querySelector(".sign-in-btn").classList.add("visible");
    // Скрываем блок с информацией о пользователе
    document.querySelector(".user-info").classList.remove("visible");
    document.getElementById("userInfo").innerHTML = "";
}