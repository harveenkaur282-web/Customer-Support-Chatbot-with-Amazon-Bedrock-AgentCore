# Customer Support Chatbot with Amazon Bedrock AgentCore

> **Note:**:  
> Due to the deprecation of legacy Bedrock Agent Flows (Classic), this project implements **Amazon Bedrock AgentCore Managed Harness** with prompt-based routing, stateful multi-turn session tracking, and Gateway Lambda tool integration.

---

## 1. Project Overview & Architecture

The chatbot is built using a single prompt-engineered system prompt (`starter/system_prompt.txt`) on the **Amazon Bedrock AgentCore managed harness** (`support_chatbot_v2` pinned to `us.amazon.nova-pro-v1:0`):

1. **Bug Reports**: Collects required bug details (`description`, `stepsToReproduce`, and `environment`) across multi-turn stateful harness sessions. When all details are provided, it executes the `bugreports___create_bug_report` Lambda tool via the AgentCore Gateway, persisting the ticket in DynamoDB table `bug-report-tool-stack-bug-reports` and returning the generated ticket ID to the customer.
2. **Platform Questions**: Answers questions regarding orders, shipping, returns, and payments using **only** the embedded FAQ (`starter/online_shop_faq.md`). Uncovered questions are directed to human support at `+12345678`.
3. **Other Requests**: Acknowledges out-of-scope requests (e.g. account updates) and directs the customer to human support (`+12345678`).

---

## 2. Evidence & Required Screenshots

All evidence files are located in `starter/screenshots/`:

| Evidence File | Description | Matching Data / Key Lines |
| :--- | :--- | :--- |
| `starter/screenshots/chat_terminal_bug_report.png` | `chat.py` transcript showing follow-up questions, thinking blocks, and `[tool call]` line | Ticket ID: **`e3819829-c18e-488a-ad40-efc5b1206f9d`** |
| `starter/screenshots/dynamodb_bug_reports.png` | AWS DynamoDB Console item view matching the ticket ID created by `chat.py` | Ticket ID: **`e3819829-c18e-488a-ad40-efc5b1206f9d`** |
| `starter/screenshots/chat_terminal_faq_and_other.png` | `chat.py` transcript showing covered FAQ, uncovered FAQ hand-off, and out-of-scope hand-off | Directs uncovered/other requests to `+12345678` |
| `starter/screenshots/bedrock_evaluations_list.png` | Amazon Bedrock Evaluations console showing completed evaluation jobs | Baseline & Edge-case evaluation runs |
| `starter/screenshots/bedrock_evaluations_run1.png` | Evaluation Run 1 details | Correctness Score: **`1.00`** |
| `starter/screenshots/bedrock_evaluations_run2.png` | Evaluation Run 2 details (Edge cases) | Correctness Score: **`0.75`** |

---

## 3. How to Run (from `starter/`)

```bash
cd starter

# Interactive Chat Terminal
python chat.py

# Generate Evaluation Dataset
python generate-eval-dataset.py --tests-json harness_tests.json
```
