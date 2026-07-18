from agents.items import ToolCallItem, ToolCallOutputItem, MessageOutputItem


def build_trace(user_input: str, result) -> list[str]:
    """Numbered, human-readable execution trace matching the challenge's
    example format exactly."""
    steps = []
    n = 1

    steps.append(f'Step {n}: Received input "{user_input}"')
    n += 1

    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            steps.append(f"Step {n}: Selected tool: {item.raw_item.name}")
            n += 1

        elif isinstance(item, ToolCallOutputItem):
            steps.append(f"Step {n}: Tool result: {item.output}")
            n += 1

        elif isinstance(item, MessageOutputItem):
            text = "".join(
                part.text for part in item.raw_item.content
                if hasattr(part, "text")
            )
            steps.append(f"Step {n}: Agent response: {text}")
            n += 1

    steps.append(f"Step {n}: Returning result to user")
    return steps


def extract_tools_used(result) -> list[str]:
    return [item.raw_item.name for item in result.new_items if isinstance(item, ToolCallItem)]