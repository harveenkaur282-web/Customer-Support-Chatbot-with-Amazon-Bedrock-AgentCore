# Screenshots Guide for Project Submission

Store your submission screenshots in this `screenshots/` directory.

### Required Screenshots as per Rubric:

1. `dynamodb_bug_reports.png`
   - **Where**: AWS Console -> DynamoDB -> Tables -> `bug-report-tool-stack-bug-reports` -> Explore table items.
   - **Content**: Shows persisted bug report items in the DynamoDB table.

2. `bedrock_evaluations_list.png`
   - **Where**: AWS Console -> Amazon Bedrock (us-east-1) -> Evaluations.
   - **Content**: Shows both completed evaluation jobs (`support-chatbot-eval-run-1` and `support-chatbot-eval-run-2`).

3. `bedrock_evaluations_run1.png` & `bedrock_evaluations_results.png`
   - **Where**: AWS Console -> Amazon Bedrock (us-east-1) -> Evaluations -> Job `support-chatbot-eval-run-1`.
   - **Content**: Shows evaluation job details and 1.00 correctness score.

4. `bedrock_evaluations_run2.png`
   - **Where**: AWS Console -> Amazon Bedrock (us-east-1) -> Evaluations -> Job `support-chatbot-eval-run-2`.
   - **Content**: Shows evaluation job details and 0.75 correctness score on edge cases.

5. `chat_terminal_bug_report.png`
   - **Where**: Terminal execution of `python chat.py`.
   - **Content**: Shows multi-turn bug parameter collection and ticket submission.

6. `chat_terminal_faq_and_other.png`
   - **Where**: Terminal execution of `python chat.py`.
   - **Content**: Shows covered FAQ answers, uncovered FAQ hand-offs, and out-of-scope request redirects.
