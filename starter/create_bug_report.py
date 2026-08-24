import json
import os
import uuid
from datetime import datetime, timezone
import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

REQUIRED_FIELDS = ("description", "stepsToReproduce", "environment")

def lambda_handler(event, _):
    print("EVENT:", json.dumps(event, indent=2, default=str))

    if event.get("messageVersion") != "1.0" or event.get("function") != "create_bug_report":
        return _resp(event, {"error": "unsupported"})

    params = event.get("parameters") or []
    body = {
        p.get("name"): p.get("value")
        for p in params
        if isinstance(p, dict) and p.get("name") is not None
    }

    description = (body.get("description") or "").strip()
    steps = (body.get("stepsToReproduce") or "").strip()
    environment = (body.get("environment") or "").strip()

    if not description:
        return _resp(event, {"error": "missing", "field": "description"})

    ticket_id = str(uuid.uuid4())
    item = {
        "ticketId": ticket_id,
        "description": description,
        "stepsToReproduce": steps,
        "environment": environment,
        "status": "OPEN",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    table.put_item(Item=item)

    return _resp(event, {"ticketId": ticket_id, "status": "OPEN"})


def _resp(event, obj):
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "function": event.get("function"),
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": json.dumps(obj)
                    }
                }
            },
        },
    }