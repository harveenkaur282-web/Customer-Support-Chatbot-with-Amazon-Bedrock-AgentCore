# Customer Support Chatbot with Amazon Bedrock AgentCore

## 1. Overview & Architecture

This project implements a multi-turn customer support chatbot built on top of the **Amazon Bedrock AgentCore managed harness**. The chatbot acts as an automated customer support agent for an online shop, handling three distinct customer intent categories through a single, prompt-engineered system prompt located in `starter/system_prompt.txt`:

1. **Bug Reports**: Collects required bug details (`description`, `stepsToReproduce`, and `environment`) across multi-turn stateful harness sessions. Once all three fields are provided, it executes the `bugreports___create_bug_report` tool (an AWS Lambda function exposed through an AgentCore Gateway) to persist the ticket in an Amazon DynamoDB table (`bug-report-tool-stack-bug-reports`) and relays the generated ticket ID to the customer.
2. **Platform Questions**: Answers common customer questions regarding orders, shipping, returns, and payments using **only** the embedded FAQ document (`starter/online_shop_faq.md` inserted via `{{FAQ}}`). If a question is not covered in the FAQ, it gracefully hands off to human support at `+12345678`.
3. **Other Requests**: Politely acknowledges out-of-scope requests (e.g., account detail changes, complaints) and directs the customer to the human support phone line (`+12345678`).

---

## 2. Infrastructure Setup & Deployed Resources

The project infrastructure was deployed in region **`us-east-1`** using AWS CloudFormation and Python setup scripts located inside the `starter/` directory:

- **CloudFormation Tool Stack (`bug-report-tool-stack`)**:
  - **DynamoDB Table**: `bug-report-tool-stack-bug-reports`
  - **Lambda Function**: `bug-report-tool-stack-create-bug-report`
  - **IAM Roles**:
    - Lambda Execution Role (`bug-report-tool-stack-lambda-role`)
    - Gateway Role (`bug-report-tool-stack-gateway-role`)
    - Harness Execution Role (`bug-report-tool-stack-harness-role`)
- **AgentCore Gateway**:
  - Gateway Name: `bug-report-tool-stack-gateway`
  - Protocol: `MCP` | Auth: `AWS_IAM`
  - Gateway Target Name: `bugreports` (Exposing `create_bug_report`)
- **AgentCore Harness**:
  - Harness Name: `support_chatbot_v2`
  - Pinned Model: `us.amazon.nova-pro-v1:0` (Greedy decoding: temperature `0.0`, `topK: 1`)
- **Testing & Evaluation Stack (`bug-report-testing-stack`)**:
  - **S3 Bucket**: `udacity-agentic-engineer-c1-eval-375974875288`
  - **Bedrock Evaluation Role**: `arn:aws:iam::375974875288:role/bedrock-eval-role`

---

## 3. How to Run & Test (from `starter/`)

Navigate into the `starter/` folder to run scripts:
```bash
cd starter
```

1. **Interactive Chat Terminal**:
   ```bash
   python chat.py
   ```
2. **Generate Evaluation Dataset**:
   ```bash
   python generate-eval-dataset.py --tests-json harness_tests.json
   ```

---

## 4. Tool Verification & DynamoDB Record Evidence

The `create_bug_report` Lambda tool was tested directly and through the AgentCore Harness loop. 

### DynamoDB Scan Results (`bug-report-tool-stack-bug-reports`):
```json
{
  "Items": [
    {
      "ticketId": {"S": "d25c9ea4-3d0c-4dca-9786-aa35b831c436"},
      "description": {"S": "The checkout page crashes when I try to pay. I click Checkout, enter my card details, and press Pay."},
      "stepsToReproduce": {"S": "Click Checkout, enter card details, press Pay."},
      "environment": {"S": "Chrome 151 on Windows 11 desktop"},
      "status": {"S": "OPEN"},
      "createdAt": {"S": "2026-08-23T23:19:55.296398+00:00"}
    },
    {
      "ticketId": {"S": "40ce25e9-3636-4091-904a-26802d48b4b4"},
      "description": {"S": "Checkout page crashes on Pay button"},
      "stepsToReproduce": {"S": "1. Add item. 2. Pay."},
      "environment": {"S": "Chrome 120 on macOS"},
      "status": {"S": "OPEN"},
      "createdAt": {"S": "2026-08-29T06:18:30.726844+00:00"}
    }
  ],
  "Count": 2
}
```

---

## 5. Automated Testing & Comparative Evaluation Runs

To thoroughly evaluate model performance and guard against overfitting, two evaluation runs were conducted using Amazon Nova Pro (LLM-as-a-judge):

### Test Runs Breakdown:

1. **Evaluation Run 1 (`support-chatbot-eval-run-1`)** - *Standard Baseline Suite (`starter/harness_tests_v1.json`)*:
   - Evaluated 8 baseline test cases covering core message classification, FAQ retrieval, multi-turn bug collection, prompt injection, and human hand-offs.
   - **Correctness Score**: `1.0` (100% adherence to defined ground truth intents).

2. **Evaluation Run 2 (`support-chatbot-eval-run-2`)** - *Extended Edge Case Suite (`starter/harness_tests_v2.json` / `starter/harness_tests.json`)*:
   - Expanded the test suite to 10 prompts by adding complex multi-part queries (e.g., combined bug report + billing address change) and ambiguous order tracking inquiries.
   - **Observed Correctness Score**: `0.75` (Reflects realistic grading behavior on complex, multi-intent prompts while maintaining high overall routing accuracy).

---

## 6. Submission Screenshots Index

All required evidence screenshots are stored in `starter/screenshots/`:

1. `starter/screenshots/dynamodb_bug_reports.png` — DynamoDB table showing persisted bug report records.
2. `starter/screenshots/bedrock_evaluations_list.png` — Amazon Bedrock Evaluations console showing both completed evaluation runs.
3. `starter/screenshots/bedrock_evaluations_run1.png` — Evaluation Run 1 details (1.00 Correctness score on `starter/harness_tests_v1.json`).
4. `starter/screenshots/bedrock_evaluations_run2.png` — Evaluation Run 2 details (0.75 Correctness score on `starter/harness_tests_v2.json` edge cases).
5. `starter/screenshots/chat_terminal_bug_report.png` — Interactive multi-turn conversation showing step-by-step bug parameter collection and ticket submission.
6. `starter/screenshots/chat_terminal_faq_and_other.png` — Interactive conversation showing covered FAQ answers, uncovered FAQ hand-offs, and out-of-scope request redirects.
