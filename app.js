(() => {
  "use strict";

  const printButton = document.getElementById("print-btn");
  if (printButton) {
    printButton.addEventListener("click", () => window.print());
  }

  const searchInput = document.getElementById("search");
  const counter = document.getElementById("counter");
  const resetButton = document.getElementById("reset");
  const emptyMessage = document.getElementById("empty");
  const toggleButton = document.getElementById("toggle");
  const filterBody = document.getElementById("filter-body");

  const hasFilterUi =
    searchInput && counter && resetButton && emptyMessage && toggleButton && filterBody;
  if (!hasFilterUi) return;

  const chips = Array.from(document.querySelectorAll(".chip"));
  const entries = Array.from(document.querySelectorAll(".entry"));

  const activeTags = new Set();

  const entryIndex = entries.map((entry) => ({
    element: entry,
    tags: new Set((entry.dataset.tags || "").split(/\s+/).filter(Boolean)),
    text: entry.textContent.toLowerCase().replace(/\s+/g, " "),
  }));

  const hasEveryTag = (tags) => {
    for (const tag of activeTags) {
      if (!tags.has(tag)) return false;
    }
    return true;
  };

  const matchesQuery = (text, query) => !query || text.includes(query);

  const isEnglish = document.documentElement.lang === "en";

  const pluralize = (count) => {
    const tail = count % 100;
    if (tail >= 11 && tail <= 14) return "записей";
    const last = count % 10;
    if (last === 1) return "запись";
    if (last >= 2 && last <= 4) return "записи";
    return "записей";
  };

  const describe = (visible, isFiltered) => {
    if (isEnglish) {
      if (!isFiltered) return "Showing all";
      if (visible === 0) return "Nothing found";
      return `${visible} of ${entryIndex.length} entries`;
    }

    if (!isFiltered) return "Показано всё";
    if (visible === 0) return "Ничего не найдено";
    return `${visible} ${pluralize(visible)} из ${entryIndex.length}`;
  };

  const syncLocation = () => {
    const params = new URLSearchParams();
    if (activeTags.size > 0) params.set("t", Array.from(activeTags).join(","));

    const query = searchInput.value.trim();
    if (query) params.set("q", query);

    const suffix = params.toString();
    const url = suffix ? `?${suffix}` : location.pathname;
    history.replaceState(null, "", url);
  };

  const apply = () => {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;

    for (const item of entryIndex) {
      const isVisible = hasEveryTag(item.tags) && matchesQuery(item.text, query);
      item.element.hidden = !isVisible;
      if (isVisible) visible += 1;
    }

    const isFiltered = activeTags.size > 0 || query.length > 0;
    counter.textContent = describe(visible, isFiltered);
    resetButton.hidden = !isFiltered;
    emptyMessage.hidden = visible !== 0;
    syncLocation();
  };

  const toggleChip = (chip) => {
    const tag = chip.dataset.tag;
    if (!tag) return;

    const wasPressed = chip.getAttribute("aria-pressed") === "true";
    chip.setAttribute("aria-pressed", String(!wasPressed));

    if (wasPressed) activeTags.delete(tag);
    else activeTags.add(tag);

    apply();
  };

  const setPanelOpen = (isOpen) => {
    toggleButton.setAttribute("aria-expanded", String(isOpen));
    filterBody.hidden = !isOpen;
  };

  const resetAll = () => {
    activeTags.clear();
    for (const chip of chips) chip.setAttribute("aria-pressed", "false");
    searchInput.value = "";
    apply();
  };

  const restoreFromLocation = () => {
    const params = new URLSearchParams(location.search);
    const tags = (params.get("t") || "").split(",").filter(Boolean);

    for (const chip of chips) {
      if (!tags.includes(chip.dataset.tag)) continue;
      chip.setAttribute("aria-pressed", "true");
      activeTags.add(chip.dataset.tag);
    }

    searchInput.value = params.get("q") || "";
  };

  for (const chip of chips) {
    chip.addEventListener("click", () => toggleChip(chip));
  }

  searchInput.addEventListener("input", apply);
  resetButton.addEventListener("click", resetAll);

  toggleButton.addEventListener("click", () => {
    setPanelOpen(toggleButton.getAttribute("aria-expanded") !== "true");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && document.activeElement === searchInput) {
      resetAll();
      searchInput.blur();
    }
  });

  restoreFromLocation();
  setPanelOpen(activeTags.size > 0);
  apply();
})();
