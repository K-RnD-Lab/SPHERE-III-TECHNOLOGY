const dataUrl = "./data/registry.json";

const searchInput = document.getElementById("search-input");
const sphereFilter = document.getElementById("sphere-filter");
const comboFilter = document.getElementById("combo-filter");
const statusFilter = document.getElementById("status-filter");
const artifactFilter = document.getElementById("artifact-filter");
const registryGrid = document.getElementById("registry-grid");
const stats = document.getElementById("stats");
const resultCount = document.getElementById("result-count");
const cardTemplate = document.getElementById("card-template");

let registryEntries = [];

function titleCase(value) {
  return value
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function prettyLabel(key, value) {
  if (!value) {
    return "";
  }

  if (key === "sphere") {
    return titleCase(value);
  }

  if (key === "artifactType" || key === "validationStage") {
    return titleCase(value);
  }

  return value;
}

function uniqueValues(entries, key) {
  return [...new Set(entries.map((entry) => entry[key]).filter(Boolean))].sort();
}

function fillSelect(select, values, key) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = prettyLabel(key, value);
    select.appendChild(option);
  }
}

function buildStats(entries) {
  const bySphere = ["science", "entrepreneurship", "technology"].map((sphere) => ({
    label: prettyLabel("sphere", sphere),
    value: entries.filter((entry) => entry.primarySphere === sphere).length,
    className: sphere,
  }));

  const cards = [
    { label: "Total entries", value: entries.length, className: "total" },
    ...bySphere,
    {
      label: "Hybrid lanes",
      value: entries.filter((entry) => entry.combo.includes("+")).length,
      className: "hybrid",
    },
  ];

  stats.innerHTML = "";
  for (const card of cards) {
    const wrapper = document.createElement("article");
    wrapper.className = `stat ${card.className}`;
    wrapper.innerHTML = `
      <div class="stat-value">${card.value}</div>
      <div class="stat-label">${card.label}</div>
    `;
    stats.appendChild(wrapper);
  }
}

function setText(target, value) {
  target.textContent = value && value.length ? value : "—";
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
    const sphereBadge = fragment.querySelector(".badge.sphere");
    const comboBadge = fragment.querySelector(".badge.combo");
    const statusBadge = fragment.querySelector(".badge.status");
    const title = fragment.querySelector(".title");
    const summary = fragment.querySelector(".summary");
    const track = fragment.querySelector(".track");
    const artifactType = fragment.querySelector(".artifact-type");
    const secondarySpheres = fragment.querySelector(".secondary-spheres");
    const deliveryLayers = fragment.querySelector(".delivery-layers");
    const validationStage = fragment.querySelector(".validation-stage");
    const tags = fragment.querySelector(".tags");
    const links = fragment.querySelector(".links");

    sphereBadge.textContent = prettyLabel("sphere", entry.primarySphere);
    sphereBadge.classList.add(entry.primarySphere);
    comboBadge.textContent = entry.combo;
    comboBadge.classList.add(`combo-${entry.combo.toLowerCase().replace(/\+/g, "-")}`);
    statusBadge.textContent = prettyLabel("status", entry.status);

    title.textContent = entry.title;
    summary.textContent = entry.summary;
    setText(track, entry.track);
    setText(artifactType, prettyLabel("artifactType", entry.artifactType));
    setText(
      secondarySpheres,
      entry.secondarySpheres.length
        ? entry.secondarySpheres.map((item) => prettyLabel("sphere", item)).join(", ")
        : "",
    );
    setText(deliveryLayers, entry.deliveryLayers.join(", "));
    setText(validationStage, prettyLabel("validationStage", entry.validationStage));
    setText(tags, entry.tags.join(", "));

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
  const combo = comboFilter.value;
  const status = statusFilter.value;
  const artifact = artifactFilter.value;

  const filtered = registryEntries.filter((entry) => {
    const matchesSphere = sphere === "all" || entry.primarySphere === sphere;
    const matchesCombo = combo === "all" || entry.combo === combo;
    const matchesStatus = status === "all" || entry.status === status;
    const matchesArtifact = artifact === "all" || entry.artifactType === artifact;
    const haystack = [
      entry.title,
      entry.summary,
      entry.track,
      entry.entryType,
      entry.primarySphere,
      entry.combo,
      entry.artifactType,
      entry.validationStage,
      ...entry.secondarySpheres,
      ...entry.deliveryLayers,
      ...entry.tags,
    ]
      .join(" ")
      .toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    return matchesSphere && matchesCombo && matchesStatus && matchesArtifact && matchesQuery;
  });

  renderCards(filtered);
}

async function init() {
  const response = await fetch(dataUrl);
  registryEntries = await response.json();

  fillSelect(sphereFilter, uniqueValues(registryEntries, "primarySphere"), "sphere");
  fillSelect(comboFilter, uniqueValues(registryEntries, "combo"), "combo");
  fillSelect(statusFilter, uniqueValues(registryEntries, "status"), "status");
  fillSelect(artifactFilter, uniqueValues(registryEntries, "artifactType"), "artifactType");
  buildStats(registryEntries);
  renderCards(registryEntries);

  searchInput.addEventListener("input", applyFilters);
  sphereFilter.addEventListener("change", applyFilters);
  comboFilter.addEventListener("change", applyFilters);
  statusFilter.addEventListener("change", applyFilters);
  artifactFilter.addEventListener("change", applyFilters);
}

init().catch((error) => {
  registryGrid.innerHTML = `<div class="empty">Failed to load registry data: ${error.message}</div>`;
  resultCount.textContent = "Error";
});
