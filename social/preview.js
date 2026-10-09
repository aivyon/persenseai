const carouselData = {
  agent: [
    ["agent-reward-carousel/png/agent-reward-01.png", "Not every agent action is progress", "A long noisy action route contrasted with a shorter grounded route."],
    ["agent-reward-carousel/png/agent-reward-02.png", "The agent begins with a bounded goal", "An inspectable agent state lists its hypothesis, evidence, uncertainty, contradictions, provenance, and finite budgets."],
    ["agent-reward-carousel/png/agent-reward-03.png", "It ranks possible next actions", "Eight bounded action candidates expose modeled value, cost, latency, and reason codes."],
    ["agent-reward-carousel/png/agent-reward-04.png", "It selects one registered tool", "A closed flow selects a registered tool and returns a structured cited result."],
    ["agent-reward-carousel/png/agent-reward-05.png", "The result updates the investigation", "Before-and-after graphs accompany updates to support, uncertainty, and provenance."],
    ["agent-reward-carousel/png/agent-reward-06.png", "Positive progress reward", "Nine transparent positive components show better-grounded state changes."],
    ["agent-reward-carousel/png/agent-reward-07.png", "Penalties prevent fake progress", "Nine penalty bars expose repetition, unsupported output, cost, latency, and premature stopping."],
    ["agent-reward-carousel/png/agent-reward-08.png", "The reward-driven agent can be much more selective", "A verified redundant-frame scenario compares 12 fixed steps at cost 1.44 with 4 utility-driven steps at cost 0.32."],
    ["agent-reward-carousel/png/agent-reward-09.png", "Continue, answer, or stop inconclusive", "A bounded state can inspect, verify, compare, request, answer, or stop inconclusive."]
  ],
  pipeline: [
    ["pipeline-carousel/png/pipeline-01.png", "From observations to grounded reasoning", "Five modality streams converge into a unified observation and evidence timeline."],
    ["pipeline-carousel/png/pipeline-02.png", "Multimodal inputs become observations", "Video, image, text, audio, and sensor streams become structured observation cards."],
    ["pipeline-carousel/png/pipeline-03.png", "Visual Reward Timeline", "Visual frames align with a temporal reward curve and failure marker."],
    ["pipeline-carousel/png/pipeline-04.png", "Evidence Graph Timeline", "A temporal graph distinguishes support, contradiction, and unresolved evidence."],
    ["pipeline-carousel/png/pipeline-05.png", "Evidence Utility Timeline", "Evidence is ranked by modeled utility while a redundant item is visibly penalized."],
    ["pipeline-carousel/png/pipeline-06.png", "Evidence Orchestration Agent", "Candidate actions lead to a selected registered tool, cited result, and state update."],
    ["pipeline-carousel/png/pipeline-07.png", "Answer—or stop honestly", "Grounded answer conditions are contrasted with an inconclusive stop."],
    ["pipeline-carousel/png/pipeline-08.png", "One pipeline. Four inspectable research modules.", "The four PersenseAI modules are listed above a research question and site call to action."]
  ]
};

let activeCarousel = null;

function setupCarousel(root) {
  const key = root.dataset.carousel;
  const slides = carouselData[key];
  const image = root.querySelector("img");
  const label = root.querySelector(".slide-label");
  const title = root.querySelector(".slide-title");
  const dots = root.querySelector(".dots");
  let index = 0;

  function render(nextIndex, focusDot = false) {
    index = (nextIndex + slides.length) % slides.length;
    const [src, heading, alt] = slides[index];
    image.src = src;
    image.alt = alt;
    label.textContent = `Slide ${index + 1} of ${slides.length}`;
    title.textContent = heading;
    [...dots.children].forEach((dot, dotIndex) => dot.setAttribute("aria-current", String(dotIndex === index)));
    if (focusDot) dots.children[index].focus();
  }

  slides.forEach((slide, slideIndex) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.textContent = String(slideIndex + 1);
    dot.setAttribute("aria-label", `Show ${key} slide ${slideIndex + 1}: ${slide[1]}`);
    dot.addEventListener("click", () => render(slideIndex));
    dots.append(dot);
  });

  root.addEventListener("pointerenter", () => { activeCarousel = root; });
  root.addEventListener("focusin", () => { activeCarousel = root; });
  root.querySelector('[data-direction="previous"]').addEventListener("click", () => render(index - 1));
  root.querySelector('[data-direction="next"]').addEventListener("click", () => render(index + 1));
  root.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") { event.preventDefault(); render(index - 1); }
    if (event.key === "ArrowRight") { event.preventDefault(); render(index + 1); }
    if (event.key === "Home") { event.preventDefault(); render(0, true); }
    if (event.key === "End") { event.preventDefault(); render(slides.length - 1, true); }
  });
  root.carouselMove = (direction) => render(index + direction);
  render(0);
}

document.querySelectorAll("[data-carousel]").forEach(setupCarousel);

document.addEventListener("keydown", (event) => {
  if (event.defaultPrevented || !activeCarousel || ["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
  if (event.key === "ArrowLeft") activeCarousel.carouselMove(-1);
  if (event.key === "ArrowRight") activeCarousel.carouselMove(1);
});

document.querySelectorAll("[data-markdown]").forEach(async (block) => {
  try {
    const response = await fetch(block.dataset.markdown);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    block.textContent = await response.text();
  } catch (error) {
    block.textContent = "This text is available when preview.html is served from the repository root.";
  }
});
