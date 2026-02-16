(() => {
  const email = "gudbot.comics@gmail.com";
  const subject = "OpenClaw News Inquiry";
  const mailto = `mailto:${email}?subject=${encodeURIComponent(subject)}`;

  const contactLinks = document.querySelectorAll("[data-contact-link]");
  contactLinks.forEach((link) => link.setAttribute("href", mailto));

  const status = document.getElementById("contactStatus");
  try {
    window.location.href = mailto;
    if (status) {
      status.textContent = "If your email app did not open, use the button below.";
    }
  } catch (err) {
    if (status) {
      status.textContent = "Automatic launch was blocked. Use the button below.";
    }
  }
})();
