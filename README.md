# Non-Determinism Regression Catcher

> **LLMs don't crash. They drift.**
>
> An observability-driven framework for detecting silent regressions in Large Language Model (LLM) applications using **OpenTelemetry** and **SigNoz**.

---

## Overview

Large Language Models are inherently non-deterministic. The same prompt can produce different outputs across multiple executions, making it difficult to distinguish expected variation from genuine regressions introduced by prompt changes, model updates, or inference parameter tweaks.

This project explores how **observability** can be used to monitor LLM behavior instead of relying solely on traditional testing.

Every LLM execution is instrumented using **OpenTelemetry**, exported to **SigNoz**, and analyzed using custom metrics such as schema validity, task success, and output variance. Instead of asking *"Did the model respond?"*, this project asks a more meaningful question:

> **"Is the model behaving differently than it used to?"**

---

## Features

- Instrument every LLM execution using OpenTelemetry
- Visualize traces and metrics in SigNoz
- Execute the same prompt repeatedly to observe behavioral consistency
- Compute custom metrics such as task success, schema validity, and output variance
- Detect silent regressions using dashboards and alerts
- Modular design that can be extended to different LLM providers

---

## Repository Structure

```text
.
├── agent.py                  # Main regression catcher pipeline
├── at.py                     # Agent orchestration
├── config.py                 # Configuration
├── llm_call.py               # Shared LLM interface
├── metrics_setup.py          # Metric definitions
├── tracer_setup.py           # OpenTelemetry initialization
├── tools.py                  # Tool implementations
├── tool_schemas.py           # Tool definitions
│
├── stage1_tracer_basics.py   # Introduction to OpenTelemetry tracing
├── stage2_send_to_signoz.py  # Export traces to SigNoz
├── task1_span_hierarchy.py   # Span hierarchy implementation
├── task2_metrics.py          # Custom metric instrumentation
├── task3_loop.py             # Repeated execution loop
│
├── test_tools.py             # Tool testing
├── run_batch.py              # Batch execution utility
│
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## How It Works

The project follows a progressive workflow.

### Stage 1 — Basic Tracing

Learn the fundamentals of creating OpenTelemetry traces.

```bash
python stage1_tracer_basics.py
```

---

### Stage 2 — Exporting to SigNoz

Configure the OTLP exporter and verify traces appear inside SigNoz.

```bash
python stage2_send_to_signoz.py
```

---

### Task 1 — Building the Span Hierarchy

Represent a complete LLM execution as a trace.

```
test_run
├── prompt_build
├── llm_call
└── parse_validate
```

```bash
python task1_span_hierarchy.py
```

---

### Task 2 — Collecting Metrics

Generate custom behavioral metrics including:

- Task Success
- Schema Validity
- Output Variance

```bash
python task2_metrics.py
```

---

### Task 3 — Observing Non-Determinism

Execute the same prompt repeatedly and compare behavioral changes across runs.

```bash
python task3_loop.py
```

---

### Final Pipeline

Run the complete Non-Determinism Regression Catcher.

```bash
python agent.py
```

---

## System Architecture

```text
                  Prompt
                     │
                     ▼
          Repeated LLM Executions
                     │
                     ▼
       OpenTelemetry Instrumentation
           │                   │
           ▼                   ▼
        Traces             Metrics
           │                   │
           └─────────┬─────────┘
                     ▼
              OTLP Exporter
                     │
                     ▼
                  SigNoz
                     │
      ┌──────────────┴──────────────┐
      ▼                             ▼
 Dashboards                     Alerts
```

---

## Metrics Collected

| Metric | Description |
|----------|-------------|
| Task Success | Indicates whether the model successfully completed the task |
| Schema Validity | Tracks whether outputs conform to the expected structure |
| Output Variance | Measures consistency across repeated executions |
| Latency | Measures inference time |
| Semantic Drift *(Future Work)* | Compares responses against a trusted baseline |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mmithra29/Non-Determinism-Regression-Catcher.git

cd Non-Determinism-Regression-Catcher
```

### 2. Install Dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -e .
```

### 3. Start SigNoz

Start your self-hosted SigNoz deployment.

```bash
docker compose up -d
```

Once the containers are running, open the dashboard:

```
http://localhost:8080
```

If using the default installation, log in with:

| Field | Value |
|-------|-------|
| Email | `admin@signoz.io` |
| Password | `admin` |

### 4. Run the Complete Pipeline

```bash
python agent.py
```

Or explore each stage individually:

```bash
python stage1_tracer_basics.py

python stage2_send_to_signoz.py

python task1_span_hierarchy.py

python task2_metrics.py

python task3_loop.py
```

---

## Technology Stack

- Python
- OpenTelemetry
- SigNoz
- Docker
- Ollama compatible LLMs

---

## Future Work

- Semantic similarity using embeddings
- Automated regression scoring
- CI/CD integration
- Multi-agent observability
- Prompt version comparison
- Automatic root-cause analysis
- Production deployment support

---

## Demo

The repository demonstrates:

- OpenTelemetry instrumentation of LLM pipelines
- Trace visualization in SigNoz
- Custom behavioral metrics
- Detection of silent regressions through repeated execution
- Dashboard-based monitoring and alerting

> Add screenshots of:
>
> - Architecture
> - OpenTelemetry traces
> - SigNoz dashboards
> - Alert configuration

---

## Motivation

Traditional monitoring tells you when your infrastructure is unhealthy.

Traditional testing tells you whether an expected output changed.

This project fills the gap between the two by answering a different question:

> **"Is my AI behaving differently than it used to?"**

By treating every LLM execution as telemetry, developers gain continuous visibility into behavioral changes, allowing regressions to be detected before they impact end users.

---

## Built For

**Agents of SigNoz Hackathon**

This project explores how observability principles can be applied to monitor the behavioral reliability of LLM-powered applications.

---

## License

This project is licensed under the MIT License.
