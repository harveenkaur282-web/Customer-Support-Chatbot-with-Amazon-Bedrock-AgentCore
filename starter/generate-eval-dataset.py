#!/usr/bin/env python3
"""Run harness test suite against AgentCore harness and produce JSONL for Bedrock Evaluations."""

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict

import boto3
from botocore.config import Config
from botocore.eventstream import EventStream


def event_stream(response):
    for value in response.values():
        if isinstance(value, EventStream):
            return value
    raise RuntimeError(f"No event stream in response: {list(response)}")


def invoke_harness_once(rt, config, prompt_text: str) -> str:
    session_id = f"{uuid.uuid4()}-eval-session"
    response = rt.invoke_harness(
        harnessArn=config["harness_arn"],
        runtimeSessionId=session_id,
        tools=[{
            "type": "agentcore_gateway",
            "name": "bugreports",
            "config": {
                "agentCoreGateway": {
                    "gatewayArn": config["gateway_arn"],
                    "outboundAuth": {"awsIam": {}}
                }
            },
        }],
        allowedTools=["*"],
        messages=[{
            "role": "user",
            "content": [{"text": prompt_text}]
        }],
    )

    texts = []
    buffer = []

    for event in event_stream(response):
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                buffer.append(delta["text"])
        elif "messageStop" in event:
            if buffer:
                texts.append("".join(buffer))
                buffer = []

    if buffer:
        texts.append("".join(buffer))

    return texts[-1] if texts else ""


def main():
    p = argparse.ArgumentParser(description="Run AgentCore Harness tests and emit Bedrock Evaluations JSONL.")
    p.add_argument("--tests-json", default="harness_tests.json", help="Path to the test suite JSON.")
    p.add_argument("--config", default="agentcore_config.json", help="AgentCore config file.")
    p.add_argument("--model-identifier", default="my-support-chatbot", help="Model identifier for BYOI eval.")
    p.add_argument("--out-jsonl", default="output_eval_dataset.jsonl", help="Where to write output JSONL.")
    args = p.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    suite = json.loads(Path(args.tests_json).read_text(encoding="utf-8"))
    tests = suite.get("tests", [])

    rt = boto3.client(
        "bedrock-agentcore",
        region_name=config["region"],
        config=Config(read_timeout=300, retries={"max_attempts": 1})
    )

    out_path = Path(args.out_jsonl)
    n_ok = 0

    with out_path.open("w", encoding="utf-8") as f:
        for t in tests:
            test_id = t["id"]
            prompt = t.get("prompt", "")
            reference = t.get("expected", "")

            print(f"Running test: {test_id}...", end="", flush=True)
            try:
                response_text = invoke_harness_once(rt, config, prompt)
                n_ok += 1
                print(" OK")
            except Exception as e:
                print(f" ERROR ({e})")
                response_text = f"[HARNESS_ERROR] {type(e).__name__}: {e}"

            record = {
                "prompt": prompt,
                "referenceResponse": reference,
                "modelResponses": [
                    {
                        "response": response_text,
                        "modelIdentifier": args.model_identifier,
                    }
                ],
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"  {test_id}: wrote eval line", file=sys.stderr)

    print(f"\nWrote {len(tests)} JSONL lines to {out_path} ({n_ok}/{len(tests)} harness calls succeeded).")


if __name__ == "__main__":
    main()