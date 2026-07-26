"""Phase 1: Foundation Models — Basic LLM calls via Amazon Bedrock."""

import json
import sys

import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from config.settings import AWS_REGION, MAX_TOKENS, MODEL_ID, TEMPERATURE


def _get_client():
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def call_llm(
    prompt: str,
    model_id: str = MODEL_ID,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> str:
    """Synchronous call to Amazon Bedrock (Claude Sonnet)."""
    client = _get_client()
    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )
        body = json.loads(response["body"].read())
        return body["content"][0]["text"]
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ThrottlingException":
            raise RuntimeError("Rate limited by Bedrock — retry later.") from e
        if code == "ValidationException":
            raise ValueError(f"Invalid request: {e}") from e
        raise
    except Exception as e:
        raise RuntimeError(f"Bedrock call failed: {e}") from e


def call_llm_streaming(prompt: str) -> str:
    """Streaming response from Bedrock. Yields chunks, returns full text."""
    client = _get_client()
    try:
        response = client.invoke_model_with_response_stream(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )
        full_text = ""
        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                text = chunk["delta"].get("text", "")
                full_text += text
                print(text, end="", flush=True)
        print()
        return full_text
    except ClientError as e:
        raise RuntimeError(f"Streaming call failed: {e}") from e


def call_llm_with_system(system_prompt: str, user_message: str) -> str:
    """Call Bedrock with a system prompt and user message."""
    client = _get_client()
    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_message}],
                }
            ),
        )
        body = json.loads(response["body"].read())
        return body["content"][0]["text"]
    except ClientError as e:
        raise RuntimeError(f"System prompt call failed: {e}") from e


# ── Demo ─────────────────────────────────────────
if __name__ == "__main__":
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    # 1. Basic customer support query
    console.print(Panel("[bold cyan]Demo 1: Basic Customer Support Query[/]"))
    query = "I ordered a laptop 3 days ago and it hasn\'t shipped yet. What should I do?"
    console.print(f"[dim]Prompt:[/] {query}\n")
    result = call_llm(query)
    console.print(Panel(result, title="Response", border_style="green"))

    # 2. Streaming response
    console.print(Panel("[bold cyan]Demo 2: Streaming Response[/]"))
    stream_query = "List 3 tips for a great online shopping experience."
    console.print(f"[dim]Prompt:[/] {stream_query}\n")
    console.print("[yellow]Streaming:[/]")
    call_llm_streaming(stream_query)

    # 3. System + user prompt
    console.print(Panel("[bold cyan]Demo 3: System + User Prompt[/]"))
    system = (
        "You are ShopSmart\'s customer support agent. Be friendly, concise, "
        "and always offer to escalate to a human agent if the customer is unsatisfied."
    )
    user_msg = "I want to return a pair of shoes I bought last week."
    console.print(f"[dim]System:[/] {system}")
    console.print(f"[dim]User:[/] {user_msg}\n")
    result = call_llm_with_system(system, user_msg)
    console.print(Panel(result, title="Response", border_style="green"))
