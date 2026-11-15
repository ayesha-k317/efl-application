async function send(url, body) {
  showMessage("error", "");
  try {
    const reply = await postJson(url, body);
    if (!reply.ok) {
      showMessage("error", reply.data.error);
      return;
    }
    window.location.href = "/converter";
  } catch (problem) {
    showMessage("error", "Could not reach the server. Please try again.");
  }
}

document.getElementById("login-form").addEventListener("submit", (event) => {
  event.preventDefault();
  send("/api/login", {
    email: document.getElementById("login-email").value,
    password: document.getElementById("login-password").value,
  });
});

document.getElementById("register-form").addEventListener("submit", (event) => {
  event.preventDefault();
  send("/api/register", {
    name: document.getElementById("reg-name").value,
    email: document.getElementById("reg-email").value,
    phone: document.getElementById("reg-phone").value,
    password: document.getElementById("reg-password").value,
  });
});