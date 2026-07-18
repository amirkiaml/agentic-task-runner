from agents import function_tool

@function_tool
def TextProcessorTool(text: str, operation: str) -> str:
    """Transforms text. operation: uppercase, lowercase, or word_count."""
    if operation == "uppercase": return text.upper()
    if operation == "lowercase": return text.lower()
    if operation == "word_count": return str(len(text.split()))
    return f"Error: unknown operation '{operation}'."

@function_tool
def CalculatorTool(num1: float, num2: float, operation: str) -> str:
    """operation: addition, subtraction, multiplication, or division."""
    if operation == "addition": return str(num1 + num2)
    if operation == "subtraction": return str(num1 - num2)
    if operation == "multiplication": return str(num1 * num2)
    if operation == "division":
        return "Error: division by zero." if num2 == 0 else str(num1 / num2)
    return f"Error: unknown operation '{operation}'."

@function_tool
def WeatherMockTool(city: str) -> str:
    """Returns mock weather for a city. No real API call."""
    mock_data = {"toronto": "18°C, partly cloudy"}
    return f"[MOCK] Weather in {city}: {mock_data.get(city.strip().lower(), '20°C, clear (default)')}"

@function_tool
def UnitConvertor(value: float, from_unit: str, to_unit: str) -> str:
  """Converts units into each other."""
  conversions = {
      ("km", "miles"): lambda v: v * 0.621371,
      ("miles", "km"): lambda v: v / 0.621371,
      ("celsius", "fahrenheit"): lambda v: v * 9/5 + 32,
      ("fahrenheit", "celsius"): lambda v: (v - 32) * 5/9,
      ("kg", "lbs"): lambda v: v * 2.20462,
      ("lbs", "kg"): lambda v: v / 2.20462,
  }
  key = (from_unit.strip().lower(), to_unit.strip().lower())
  if key not in conversions:
      return f"Error: no conversion available from {from_unit} to {to_unit}."
  return f"{conversions[key](value):.2f} {to_unit}"

@function_tool
def DirectAnswerTool(response: str) -> str:
    """Use this when no other tool applies - greetings, small talk, or
    general-knowledge questions with no matching tool. Pass your direct
    response as the argument."""
    return response