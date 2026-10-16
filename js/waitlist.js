(function () {
  "use strict";

  /*
    The waitlist endpoint lives in index.html, on the form's data-endpoint
    attribute. Leave it empty to keep the mailto fallback. See the comment
    above #waitlist-form, and the README, for Formspree setup.
  */

  var form = document.getElementById("waitlist-form");
  if (!form) return;

  var endpoint = (form.getAttribute("data-endpoint") || "").trim();
  var emailInput = document.getElementById("waitlist-email");
  var statusEl = document.getElementById("form-status");
  var submitBtn = form.querySelector("button[type='submit']");
  var defaultLabel = submitBtn.textContent;
  var contact = "info@rhinoroster.com";

  function setStatus(message, isError) {
    statusEl.textContent = message;
    statusEl.classList.toggle("is-error", Boolean(isError));
    if (isError) {
      emailInput.setAttribute("aria-invalid", "true");
    } else {
      emailInput.removeAttribute("aria-invalid");
    }
  }

  function isEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  emailInput.addEventListener("invalid", function (event) {
    event.preventDefault();
    setStatus("Enter a valid email address.", true);
  });

  form.addEventListener("submit", function (event) {
    var email = emailInput.value.trim().replace(/[\r\n]/g, "");
    var honeypot = form.querySelector("[name='_gotcha']");

    if (honeypot && honeypot.value) {
      event.preventDefault();
      return;
    }

    if (!isEmail(email)) {
      event.preventDefault();
      setStatus("Enter a valid email address.", true);
      emailInput.focus();
      return;
    }

    if (!endpoint) {
      event.preventDefault();
      var subject = encodeURIComponent("Rhino Roster waitlist");
      var body = encodeURIComponent(
        "Please add this email to the Rhino Roster waitlist:\n\n" + email + "\n"
      );
      setStatus(
        "Your email app should open with a note to " +
          contact +
          ". Send it to join the waitlist. If nothing opens, email that address directly.",
        false
      );
      window.location.href =
        "mailto:" + contact + "?subject=" + subject + "&body=" + body;
      return;
    }

    event.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";
    setStatus("Sending your email.", false);

    fetch(endpoint, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email: email })
    })
      .then(function (response) {
        if (!response.ok) throw new Error("Request failed");
        emailInput.value = "";
        setStatus("You're on the list. We'll email you when there's something to show.", false);
      })
      .catch(function () {
        setStatus(
          "That didn't send. Email " + contact + " and we'll add you by hand.",
          true
        );
      })
      .then(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = defaultLabel;
      });
  });
})();
