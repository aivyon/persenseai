# Agent Progress Reward carousel slide copy

## 01 — Not every agent action is progress

More steps, more tools, and more evidence do not automatically produce a better answer. Contrast a noisy action chain with a shorter route to grounded resolution.

## 02 — The agent begins with a bounded goal

The inspectable state contains a hypothesis, available evidence, uncertainty, contradictions, provenance coverage, step budget, and cost budget.

## 03 — It ranks possible next actions

Candidates include inspecting visual or sensor evidence, testing a contradiction, running a counterfactual, comparing modalities, requesting missing evidence, answering, and stopping inconclusive. Ranking exposes modeled value, cost, latency, and reason codes.

## 04 — It selects one registered tool

State → candidate actions → selected tool → structured tool result. There is no arbitrary shell access, unrestricted execution, or hidden action space.

## 05 — The result updates the investigation

One structured result can update the evidence graph, hypothesis support, uncertainty, contradiction state, provenance completeness, and remaining budget.

## 06 — Positive progress reward

Positive components include uncertainty reduction, information gain, a newly grounded claim, provenance improvement, contradiction resolution, cross-modal corroboration, answer coverage, useful graph connectivity, and a grounded cited answer.

## 07 — Penalties prevent fake progress

Penalties expose redundant evidence, repeated tool calls, unsupported claims, cost, latency, wasted budget, unresolved high-value contradiction, premature stopping, and failed tools.

## 08 — The reward-driven agent can be much more selective

Verified redundant-frame scenario: fixed pipeline—12 steps, cost 1.44. Utility-driven agent—4 steps, cost 0.32. The agent reached a comparable supported state while inspecting one useful frame instead of a burst of repeated frames.

Honesty note: the agent is not always cheaper. Contradiction resolution may require additional steps and tools.

## 09 — Continue, answer, or stop inconclusive

The bounded options are inspect, verify, compare, request, answer, and stop inconclusive. Agent Progress Reward measures grounded resolution—not support for a preferred conclusion.

Explore the bounded agent demo at persenseai.com.

Deterministic utility-driven policy. No language model is used for planning.
