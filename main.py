import asyncio
from agents import Runner
from agent import agent
from config import user_input
from utils import build_trace


async def main():
    result = await Runner.run(agent, user_input)

    trace = build_trace(user_input, result)

    print("FINAL OUTPUT:")
    print(result.final_output)

    print("\nTRACE:")
    for step in trace:
        print(step)


if __name__ == "__main__":
    asyncio.run(main())