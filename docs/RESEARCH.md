# Research Notes — Agentic AI for FEA and Engineering Simulation

This document is a presentation-oriented reading list for the **FEA Engineering Agent** project. It separates peer-reviewed work from current preprints and focuses on the ideas that directly support the proposed demos: solver-connected agents, verification, model interrogation, multimodal review, root-cause analysis, and model updating.

---

## 1. ALL-FEM: Agentic Large Language Models Fine-Tuned for Finite Element Methods

**Venue:** *Computer Methods in Applied Mechanics and Engineering (CMAME)*, 2026  
**DOI:** https://doi.org/10.1016/j.cma.2026.118985  
**Status:** Peer-reviewed journal article

### What they did

ALL-FEM builds an autonomous simulation system around specialized, fine-tuned LLMs for FEniCS. The system formulates PDE problems, generates code, debugs failed implementations, checks consistency between formulation and implementation, and visualizes results. The authors evaluate the workflow on 39 solid, fluid, and multiphysics benchmarks.

### Result worth mentioning

The paper reports **71.79% code-level success** for its best fine-tuned model when embedded in the agentic workflow, outperforming a non-agentic GPT-5 Thinking baseline used by the authors.

### Why it matters to our project

The strongest lesson is not "LLMs can write FEM code." It is that **runtime feedback, specialized roles, and a closed execution loop materially improve reliability**. This supports our architecture:

> LLM plans -> solver executes -> deterministic checks verify -> agent revises.

### One-sentence presentation summary

> "A 2026 CMAME paper showed that the frontier is moving from code generation to closed-loop autonomous FEM workflows with execution feedback and verification."

---

## 2. AutoFEA: Enhancing AI Copilot by Integrating Finite Element Analysis Using LLMs with Graph Neural Networks

**Venue:** *AAAI Conference on Artificial Intelligence*, 2025  
**DOI:** https://doi.org/10.1609/aaai.v39i22.34582  
**Status:** Peer-reviewed conference paper

### What they did

AutoFEA combines LLM planning with a graph-based retrieval model to generate FEA input files. The graph neural network / transformer component retrieves relevant examples based on relationships among steps in the FEA workflow, reducing unsupported or hallucinated generation.

### Data / evaluation

The authors use a specialized dataset of **512 FEA projects**.

### Why it matters to our project

This is strong support for our **engineering knowledge graph / semantic model representation** idea. Instead of treating an FE model as isolated text, the agent should understand relationships among:

`node -> element -> material -> section -> support -> load -> analysis -> result`

### One-sentence presentation summary

> "AutoFEA shows that grounding an LLM in structured relationships between FEA steps can reduce hallucination and improve simulation generation."

---

## 3. OpenFOAMGPT 2.0: End-to-End, Trustworthy Automation for Computational Fluid Dynamics

**Venue:** *International Journal of Heat and Fluid Flow*, 2026  
**DOI:** https://doi.org/10.1016/j.ijheatfluidflow.2026.110399  
**Status:** Peer-reviewed journal article

### What they did

The authors use four specialized agents for preprocessing, prompt generation, simulation, and postprocessing to automate complete OpenFOAM workflows from natural-language requests.

### Result worth mentioning

The paper reports **100% success and reproducibility across more than 450 simulations** on its defined benchmark suite.

### Why it matters to our project

It is CFD rather than FEA, but that is useful for the presentation: **agentic simulation is broader than ANSYS or structural mechanics**. It also reinforces the importance of benchmarking, reproducibility, and specialized agents rather than relying on a single chat interface.

### One-sentence presentation summary

> "The same movement is happening outside FEA: recent CFD work is demonstrating end-to-end solver automation with explicit reproducibility benchmarks."

---

## 4. FeaGPT: An End-to-End Agentic-AI for Finite Element Analysis

**Source:** arXiv, 2025  
**Link:** https://arxiv.org/abs/2510.21993  
**Status:** Preprint — treat as frontier work, not established consensus

### What they did

FeaGPT proposes a conversational Geometry-Mesh-Simulation-Analysis workflow. It interprets engineering requirements, creates/adapts meshes, configures FEA, runs CalculiX, and analyzes results in a closed loop.

### Why it matters to our project

It establishes a useful baseline: **natural-language-to-FEA is already being explored**. Therefore our differentiation should not be "AI can run a solver." Our stronger focus is:

- existing-model intelligence,
- revision-to-revision comparison,
- migration,
- behavioral equivalence,
- traceability,
- review.

### One-sentence presentation summary

> "If natural-language-to-simulation is becoming possible, the harder engineering question is whether the agent can understand and verify an existing model."

---

## 5. VFEAgent: A Multimodal Agent Framework for End-to-End Automated Finite Element Analysis

**Source:** arXiv, 2026  
**Link:** https://arxiv.org/abs/2605.28978  
**Status:** Preprint

### What they did

VFEAgent accepts **images plus problem descriptions**, extracts structured FEA specifications with a multimodal agent pipeline, synthesizes code, and emphasizes verification-first execution with self-debugging and fallback mechanisms.

### Why it matters to our project

This is the closest research support for our **drawing-to-model reviewer** idea:

> Drawing / support detail -> inferred physical intent -> corresponding FE entities -> inconsistency check.

The verification-first philosophy also aligns closely with our migration workflow.

### One-sentence presentation summary

> "VFEAgent suggests that the next step is multimodal: agents can reason from engineering images as well as text, then build and verify simulations."

---

## 6. PDE-Agents: An LLM-Orchestrated Multi-Agent Framework for Automated FEM Simulations with Knowledge-Graph-Augmented Reasoning

**Source:** arXiv, 2026  
**Link:** https://arxiv.org/abs/2606.07850  
**Status:** Preprint

### What they did

PDE-Agents combines simulation, analytics, and database agents with a GraphRAG / Neo4j knowledge base containing material properties, known failure patterns, and prior-run lineage.

### Results worth mentioning

The paper reports production-style metrics across **1,369 runs** and studies when knowledge-graph retrieval helps or hurts. It also includes V&V and ablation studies rather than only qualitative demos.

### Why it matters to our project

This directly motivates two ideas:

1. **Engineering memory / prior-run lineage** — the agent should know what was tried before.
2. **Evidence graph** — a result should be traceable back through model entities, assumptions, source files, and prior runs.

### One-sentence presentation summary

> "Knowledge graphs become valuable when the agent needs structured engineering memory — materials, failure patterns, prior runs, and result lineage — rather than generic chat history."

---

## 7. Differentiable Finite Element Method with Galerkin Discretization for Fast and Accurate Inverse Analysis

**Venue:** *Computer Methods in Applied Mechanics and Engineering*, 2025  
**DOI:** https://doi.org/10.1016/j.cma.2025.117755  
**Status:** Peer-reviewed journal article

### What they did

The paper develops a differentiable FEM formulation for inverse analysis of heterogeneous engineering structures. Unknown loads or material parameters can be inferred efficiently while preserving physics through a Galerkin-based formulation.

### Why it matters to our project

This supports a future capability that is more advanced than model interrogation:

> "Given a target response, what model parameter or boundary condition best explains it?"

This can eventually underpin **inverse engineering / automated calibration**, especially when real measurements are available.

### Important presentation distinction

Our current root-cause demo can be **simulation-to-simulation**. This paper becomes relevant when the target is experimental or measured data and the problem becomes true model updating / inverse analysis.

### One-sentence presentation summary

> "Differentiable FEM points toward agents that do not only run simulations; they can infer which parameters would reproduce an observed response."

---

## 8. A State-of-the-Art Review of Bayesian Finite Element Model Updating Techniques for Structural Systems

**Venue:** *Probabilistic Engineering Mechanics*, 2025  
**DOI:** https://doi.org/10.1016/j.probengmech.2025.103761  
**Status:** Peer-reviewed review article

### What it covers

The review summarizes Bayesian FE model updating, uncertainty quantification, modal/time/frequency-domain likelihoods, model-class selection, structural health monitoring, and hierarchical Bayesian methods.

### Why it matters to our project

This is the correct research foundation for any future statement like:

> "Measured modes differ from the FE model. What model parameters most likely explain the difference?"

Without test or sensor data, we should **not** frame our current demo as model updating. We should call it **revision comparison / counterfactual root-cause investigation** instead.

### One-sentence presentation summary

> "When real test data are available, Bayesian FE model updating provides the rigorous framework for calibrating the model while quantifying uncertainty."

---

# Suggested presentation slide: "Where the research frontier is moving"

Use only 4 papers on the main slide and keep the rest in backup.

| Work | Venue / year | Key idea | Connection to our project |
|---|---|---|---|
| **ALL-FEM** | CMAME, 2026 | Agentic closed-loop FEM + runtime feedback | Solver-connected autonomous workflow |
| **AutoFEA** | AAAI, 2025 | Graph-grounded FEA generation | Semantic model / knowledge graph |
| **VFEAgent** | arXiv, 2026 | Multimodal + verification-first FEA | Drawing-to-model review |
| **PDE-Agents** | arXiv, 2026 | Knowledge graph + run lineage | Evidence graph / engineering memory |

### Speaker-note version

> "The recent literature is moving in a consistent direction. ALL-FEM shows that agentic execution and runtime feedback improve FEM automation. AutoFEA uses graph structure to ground the model and reduce hallucination. VFEAgent adds multimodal inputs and verification-first execution, which is relevant to comparing drawings with the FE model. PDE-Agents adds a knowledge graph and prior-run lineage, which is close to the evidence and traceability layer I want for engineering review. The opportunity I see is to combine these ideas with existing-model intelligence, migration, regression testing, and engineering equivalence checks."

---

# Recommended backup papers / adjacent work

## Foam-Agent (2025)

**Preprint:** https://arxiv.org/abs/2509.18178  
Uses MCP-exposed services, dependency-aware case generation, and iterative failure repair for OpenFOAM. Useful if the presentation needs a concrete example of MCP being used as a deployment layer for simulation tools.

## PyMAPDL-MCP (official Ansys open-source project)

**Repository:** https://github.com/ansys/pymapdl-mcp  
Not a paper, but extremely important for the implementation story. It exposes MAPDL/PyMAPDL capabilities to AI assistants through MCP, including session management, command execution, Python execution, and visualization.

---

# What to say — and what not to say

### Safe / accurate

- "Recent research is exploring end-to-end agentic FEA workflows."
- "The papers increasingly emphasize execution feedback, verification, structured retrieval, and multimodal inputs."
- "Our focus is different: existing-model intelligence, migration, behavioral equivalence, revision review, and traceability."

### Avoid unless we actually implement / demonstrate it

- "The AI independently validated the engineering model."
- "The system proves the model is correct."
- "The agent used measured mode data" unless real test data were supplied.
- "This is production-ready for safety-related analysis."

