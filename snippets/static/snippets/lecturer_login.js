
const loginForm = document.getElementById("lecturerLoginForm");

loginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");
    const button = document.getElementById("loginButton");

    button.disabled = true;
    button.textContent = "Logging in...";
    message.textContent = "";

    try {
        const response = await fetch("/lecturer-login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Login failed.");
        }

        sessionStorage.setItem("lecturerToken", data.token);
        sessionStorage.setItem(
            "lecturerUsername",
            data.lecturer.username
        );

        window.location.href = "/lecturer-dashboard-page/";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    } finally {
        button.disabled = false;
        button.textContent = "Sign In";
    }
});
