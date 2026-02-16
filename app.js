const state = {
  topicMap: {
    openai: "OpenAI",
    openclaw: "OpenClaw",
  },
};

async function loadNews() {
  const updatedAt = document.getElementById("updatedAt");
  const lists = document.getElementById("lists");
  const error = document.getElementById("error");

  try {
    const response = await fetch("./data/news.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    const items = Array.isArray(payload.items) ? payload.items : [];

    lists.innerHTML = "";
    const groups = groupByTopic(items);
    render(groups, lists);
    updatedAt.textContent =
      payload.generatedAt ? `Last updated: ${new Date(payload.generatedAt).toLocaleString()}` : "Last updated: unknown";

    error.classList.add("hidden");
  } catch (err) {
    updatedAt.textContent = "Last updated: unavailable";
    error.textContent = "Could not load data from data/news.json. Run the fetch script or deploy from GitHub Actions.";
    error.classList.remove("hidden");
  }
}

function sanitizeUrl(value) {
  if (!value) {
    return "#";
  }

  try {
    const parsed = new URL(value);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return "#";
    }
    return parsed.href;
  } catch {
    return "#";
  }
}

function groupByTopic(items) {
  const map = { openai: [], openclaw: [] };
  for (const item of items) {
    const key = (item.topic || "").toLowerCase();
    if (map[key]) {
      map[key].push(item);
    }
  }
  return map;
}

function render(groups, container) {
  const topicTemplate = document.getElementById("topic-template");
  const itemTemplate = document.getElementById("item-template");

  for (const [topic, label] of Object.entries(state.topicMap)) {
    const section = topicTemplate.content.firstElementChild.cloneNode(true);
    section.querySelector(".topic-title").textContent = label;

    const list = section.querySelector(".news-list");
    const items = groups[topic] || [];
    if (!items.length) {
      const li = document.createElement("li");
      li.className = "news-item";
      li.textContent = "No stories yet. Try again in a few minutes.";
      list.appendChild(li);
    } else {
      for (const item of items) {
        const row = itemTemplate.content.firstElementChild.cloneNode(true);
        const anchor = row.querySelector("a");
        const meta = row.querySelector(".meta");
        const href = sanitizeUrl(item.url);

        anchor.textContent = item.title || "Untitled story";
        if (href === "#") {
          anchor.setAttribute("href", "#");
          anchor.removeAttribute("target");
          anchor.removeAttribute("rel");
          anchor.setAttribute("aria-disabled", "true");
          anchor.classList.add("disabled");
        } else {
          anchor.href = href;
          anchor.setAttribute("rel", "noopener noreferrer");
          anchor.setAttribute("target", "_blank");
        }
        meta.textContent = formatMeta(item);
        list.appendChild(row);
      }
    }

    container.appendChild(section);
  }
}

function formatMeta(item) {
  const source = item.source || "Unknown source";
  const date = item.publishedAt ? new Date(item.publishedAt).toLocaleString() : "";
  if (item.summary) {
    return `${source} • ${item.summary}${date ? " • " + date : ""}`;
  }
  return date ? `${source} • ${date}` : source;
}

loadNews();
