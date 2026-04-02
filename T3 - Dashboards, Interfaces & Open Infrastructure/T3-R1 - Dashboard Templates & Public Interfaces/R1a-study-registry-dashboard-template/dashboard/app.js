const dataUrl = "./data/registry.json";

const searchInput = document.getElementById("search-input");
const sphereFilter = document.getElementById("sphere-filter");
const statusFilter = document.getElementById("status-filter");
const registryGrid = document.getElementById("registry-grid");
const stats = document.getElementById("stats");
const resultCount = document.getElementById("result-count");
const cardTemplate = document.getElementById("card-template");

let registryEntries = [];

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function uniqueValues(entries, key) {
  return [...new Set(entries.map((entry) => entry[key]).filter(Boolean))].sort();
}

function fillSelect(select, values) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = titleCase(value);
    select.appendChild(option);
  }
}

function buildStats(entries) {
  const bySphere = ["science", "entrepreneurship", "technology"].map((sphere) => ({
    label: sphere,
    value: entries.filter((entry) => entry.sphere === sphere).length,
  }));

  const total = { label: "total entries", value: entries.length };
  const cards = [total, ...bySphere];

  stats.innerHTML = "";
  for (const card of cards) {
    const wrapper = document.createElement("article");
    wrapper.className = "stat";
    wrapper.innerHTML = `
      <div class="stat-value">${card.value}</div>
      <div class="stat-label">${titleCase(card.label)}</div>
    `;
    stats.appendChild(wrapper);
  }
}

function renderCards(entries) {
  registryGrid.innerHTML = "";
  resultCount.textContent = `${entries.length} result${entries.length === 1 ? "" : "s"}`;

  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No entries match the current filters yet.";
    registryGrid.appendChild(empty);
    return;
  }

  for (const entry of entries) {
    const fragment = cardTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".card");
    const sphereBadge = fragment.querySelector(".badge.sphere");
    const statusBadge = fragment.querySelector(".badge.status");
    const title = fragment.querySelector(".title");
    const summary = fragment.querySelector(".summary");
    const track = fragment.querySelector(".track");
    const entryType = fragment.querySelector(".entry-type");
    const tags = fragment.querySelector(".tags");
    const links = fragment.querySelector(".links");

    sphereBadge.textContent = titleCase(entry.sphere);
    sphereBadge.classList.add(entry.sphere);
    statusBadge.textContent = titleCase(entry.status);
    title.textContent = entry.title;
    summary.textContent = entry.summary;
    track.textContent = entry.track;
    entryType.textContent = entry.entryType;
    tags.textContent = entry.tags.join(", ");

    for (const link of entry.links) {
      const anchor = document.createElement("a");
      anchor.href = link.href;
      anchor.textContent = link.label;
      anchor.target = "_blank";
      anchor.rel = "noreferrer";
      links.appendChild(anchor);
    }

    registryGrid.appendChild(fragment);
  }
}

function applyFilters() {
  const query = searchInput.value.trim().toLowerCase();
  const sphere = sphereFilter.value;
  const status = statusFilter.value;

  const filtered = registryEntries.filter((entry) => {
    const matchesSphere = sphere === "all" || entry.sphere === sphere;
    const matchesStatus = status === "all" || entry.status === status;
    const haystack = [
      entry.title,
      entry.summary,
      entry.track,
      entry.entryType,
      ...entry.tags,
    ].join(" ").toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    return matchesSphere && matchesStatus && matchesQuery;
  });

  renderCards(filtered);
}

async function init() {
  const response = await fetch(dataUrl);
  registryEntries = await response.json();

  fillSelect(sphereFilter, uniqueValues(registryEntries, "sphere"));
  fillSelect(statusFilter, uniqueValues(registryEntries, "status"));
  buildStats(registryEntries);
  renderCards(registryEntries);

  searchInput.addEventListener("input", applyFilters);
  sphereFilter.addEventListener("change", applyFilters);
  statusFilter.addEventListener("change", applyFilters);
}

init().catch((error) => {
  registryGrid.innerHTML = `<div class="empty">Failed to load registry data: ${error.message}</div>`;
  resultCount.textContent = "Error";
});
