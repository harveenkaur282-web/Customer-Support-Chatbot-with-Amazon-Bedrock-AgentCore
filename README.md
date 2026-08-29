# Customer Support Chatbot with Amazon Bedrock AgentCore

> **Note for Project Reviewer**:  
> Due to the deprecation of legacy Bedrock Agent Flows (Classic), this project implements the official **Amazon Bedrock AgentCore Managed Harness** with prompt-based routing, stateful multi-turn session tracking, and Gateway Lambda tool integration.

---

## 1. Project Overview

This project implements an automated customer support chatbot using **Amazon Bedrock AgentCore** and **Amazon Nova Pro**. The chatbot classifies incoming customer queries into three distinct categories using prompt-based routing:

1. **Bug Reports**: Handles technical issues, page crashes, and shopping cart freezes. It collects missing bug details (`description`, `stepsToReproduce`, and `environment`) across multi-turn user conversations. Once all three parameters are present, it invokes the `create_bug_report` Lambda tool via AgentCore Gateway, stores the ticket in DynamoDB (`bug-report-tool-stack-bug-reports`), and returns the unique ticket ID to the customer.
2. **Platform Questions**: Responds to questions regarding orders, shipping, returns, and payment policies using ground truth from the embedded FAQ (`online_shop_faq.md`). If a question is not covered in the FAQ, it directs the customer to human support at `+12345678`.
3. **Other Requests**: Acknowledges non-bug administrative requests (e.g. account updates) and directs the customer to human support at `+12345678`.

---

## 2. Prerequisites & Environment Setup

Before running the project, ensure you have:

- **AWS Account & CLI**: Installed and configured with `us-east-1` region credentials (`aws configure` or exported environment variables).
- **Amazon Nova Pro Model Access**: Enabled `us.amazon.nova-pro-v1:0` in AWS Console -> Bedrock -> Model Access.
- **Python 3.10+**: Installed on your system.

---

## 3. How to Reproduce & Run (Step-by-Step)

### Step 1: Clone Repository & Navigate to `starter/`
```bash
git clone https://github.com/harveenkaur282-web/Customer-Support-Chatbot-with-Amazon-Bedrock-AgentCore.git
cd Customer-Support-Chatbot-with-Amazon-Bedrock-AgentCore/starter
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Deploy AWS Serverless Infrastructure
Deploy the CloudFormation stack containing the DynamoDB table (`bug-report-tool-stack-bug-reports`), Lambda function (`bug-report-tool-stack-create-bug-report`), and IAM execution roles:
```bash
aws cloudformation deploy \
  --template-file cloudformation-tool.yaml \
  --stack-name bug-report-tool-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 4: Setup Gateway & Register AgentCore Harness
Create the Gateway tool registration and initialize the Bedrock AgentCore harness (`support_chatbot_v2`):
```bash
python setup_gateway.py
python create_harness.py --name support_chatbot_v2
```

### Step 5: Test the Interactive Chatbot
Run the command-line chat application to converse with the agent:
```bash
python chat.py
```
*Example Conversation:*
- **User**: `The checkout page crashes when I try to pay.`
- **Bot**: `Could you please provide the steps you took that led to this issue and the environment you were using (e.g., browser, OS, device)?`
- **User**: `On my android device i go to the main menu then select search , type shoes then click search button`
- **Bot**: `[tool call] bugreports___create_bug_report` -> `Your bug report has been submitted. Your ticket ID is e3819829-c18e-488a-ad40-efc5b1206f9d.`

### Step 6: Generate Evaluation Dataset
Create evaluation dataset outputs (`output_eval_dataset.jsonl`) for Amazon Bedrock Automated Model Evaluations:
```bash
python generate-eval-dataset.py --tests-json harness_tests.json
```

---

## 4. Project Architecture & Implementation Details

### System Prompt & Routing (`starter/system_prompt.txt`)
The chatbot uses a single system prompt that defines strict classification rules and chain-of-thought `<thinking>` reasoning blocks. At build time, `create_harness.py` dynamically embeds `online_shop_faq.md` into the prompt via the `{{FAQ}}` placeholder.

### Tool Integration & State Persistence
- **AgentCore Gateway**: Connects the Bedrock AgentCore harness to the serverless Lambda function (`bug-report-tool-stack-create-bug-report`).
- **DynamoDB Table**: `bug-report-tool-stack-bug-reports` stores generated tickets containing `ticketId`, `createdAt`, `description`, `stepsToReproduce`, `environment`, and `status`.

### Model Evaluation Results
Model performance was evaluated using Amazon Bedrock Automated Model Evaluations (`us.amazon.nova-pro-v1:0` evaluator):
- **Baseline Test Suite (`harness_tests_v1.json`)**: Score **1.00** (100% correctness on core classification, multi-turn collection, and FAQ answers).
- **Extended Edge-Case Suite (`harness_tests_v2.json`)**: Score **0.75** (Evaluated complex mixed queries and prompt injection attempts).

---

## 5. Submission Evidence & Screenshots

All verification screenshots are stored in `starter/screenshots/`:

| Evidence File | Description | Matching Ticket ID / Data |
| :--- | :--- | :--- |
| `starter/screenshots/chat_terminal_bug_report.png` | `chat.py` transcript showing follow-up questions, thinking blocks, and `[tool call]` execution | `e3819829-c18e-488a-ad40-efc5b1206f9d` |
| `starter/screenshots/dynamodb_bug_reports.png` | AWS DynamoDB Console table scan view showing the persisted ticket | `e3819829-c18e-488a-ad40-efc5b1206f9d` |
| `starter/screenshots/dynamodb_bug_report_item_detail.png` | AWS DynamoDB Console Edit Item view showing all attribute fields | `e3819829-c18e-488a-ad40-efc5b1206f9d` |
| `starter/screenshots/chat_terminal_faq_and_other.png` | `chat.py` transcript showing covered FAQ, uncovered FAQ hand-off, and out-of-scope hand-off | Directs uncovered/other requests to `+12345678` |
| `starter/screenshots/bedrock_evaluations_list.png` | Amazon Bedrock Evaluations console showing completed evaluation jobs | Baseline & Edge-case evaluation runs |
| `starter/screenshots/bedrock_evaluations_run1.png` | Evaluation Run 1 details page | Correctness Score: `1.00` |
| `starter/screenshots/bedrock_evaluations_run2.png` | Evaluation Run 2 details page (Edge cases) | Correctness Score: `0.75` |
