const copyButtons = document.querySelectorAll("[data-copy]");
const statusNode = document.querySelector("[data-copy-status]");
const reviewLink = document.querySelector("[data-review-link]");

function setStatus(message) {
  if (!statusNode) return;
  statusNode.textContent = message;
  window.setTimeout(() => {
    statusNode.textContent = "";
  }, 2200);
}

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch (error) {
      // Fall through to the textarea fallback for browsers that expose
      // Clipboard API but block writes in previews or embedded browsers.
    }
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.top = "-999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

copyButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const value = button.getAttribute("data-copy") || "";
    try {
      await copyText(value);
      setStatus("복사되었습니다.");
    } catch (error) {
      setStatus(`복사가 제한된 브라우저입니다. ${value}`);
    }
  });
});

function setupReviewLink() {
  if (!reviewLink) return;

  const url = (reviewLink.getAttribute("data-review-url") || "").trim();
  if (!url) return;

  try {
    const parsedUrl = new URL(url, window.location.href);
    if (!["http:", "https:"].includes(parsedUrl.protocol)) return;

    reviewLink.href = parsedUrl.href;
    reviewLink.textContent = "후기 작성하기";
    reviewLink.classList.remove("is-disabled");
    reviewLink.removeAttribute("aria-disabled");
    reviewLink.removeAttribute("tabindex");
  } catch (error) {
    // Keep the review link disabled when the configured URL is not valid.
  }
}

setupReviewLink();
