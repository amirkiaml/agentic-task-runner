
from agents import Agent, ModelSettings
from tools import CalculatorTool, DirectAnswerTool, TextProcessorTool, UnitConvertor, WeatherMockTool
from config import Model_Name

agent = Agent(
    name="task_agent",
    instructions="""Always use the most specific applicable tool for any part
    of the task - never perform that operation yourself (no manual math, no
    manual text transforms). If no other tool applies to part of the request
    (greetings, small talk, general knowledge), use DirectAnswerTool - do not
    use TextProcessorTool, CalculatorTool, WeatherMockTool, or UnitConvertor
    for anything they weren't designed for.""",
    model=Model_Name,
    tools=[TextProcessorTool, CalculatorTool, WeatherMockTool, UnitConvertor, DirectAnswerTool],
    model_settings=ModelSettings(tool_choice="required"),
)