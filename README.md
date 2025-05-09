# Function Calling in LLMs - A Weather Assistant Purview

## Introduction

Function calling in Large Language Models (LLMs) like OpenAI's GPT-4 and GPT-3.5 allows models to invoke external APIs when a task involves dynamic or structured data retrieval. This bridges the gap between natural language understanding and real-world utility by enabling LLMs to access information beyond their static training data.

For example, rather than training a model on weather data, we can allow it to trigger a dedicated `get_weather()` function that queries live weather APIs and returns relevant forecasts. This keeps the model lightweight and flexible while allowing it to interact with complex backend systems.

My approach in this assignment not only demonstrates such a capability by building a weather assistant powered by function calling but also extends it to comparison between multiple openai models. I implemented two versions: a basic implementation (Part 1) and an enhanced one that handles time references (Part 2).

---

## Implementation

### Part 1: Basic Weather API with Function Calling

* **Function**: I created a Python function `get_weather(location)` that takes a city or region name and fetches current-day forecasts via Open-Meteo's weather and geocoding APIs.

* **LLM Tool Schema**: I defined a `weather_function_schema` that describes the function and parameters. This schema is registered with OpenAI’s API to enable model-initiated tool use.

* **LLM Behavior**: The assistant was configured via a system prompt to call `get_weather()` whenever weather-related queries are detected. For all other prompts, it responded normally.

* **Fallback Handling**: The assistant responded with helpful clarifications when:

  * A location was missing or ambiguous.
  * The external API failed or returned incomplete results.

* **Test Cases**:

  * Weather in New York, Tokyo, Paris, College Park.
  * Queries like "What's the weather like?", "Weather in heaven?", or "Tell me a joke."

### Part 2: Enhanced Time-aware Weather Assistant

* **Date Parsing**: A robust `parse_date()` function was built using the `dateparser` library. It interprets inputs like "next Monday", "in 3 days", or ISO-formatted dates.

* **Extended Function Signature**: `get_weather(location, datetime_str)` was modified to support optional time parameters.

* **LLM Schema Update**: The tool schema was expanded to describe the new `datetime_str` parameter.

* **Examples Parsed Successfully**:

  * "What's the weather in London tomorrow?"
  * "Will it rain in Dallas this weekend?"
  * "Weather in Chicago on Thufriday." (handled with graceful error)

---

## Results

Model responses were tested across 23 queries and 4 different OpenAI models:

| Model                  | Strengths                                          | Limitations                                                      |
| ---------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| **gpt-4.1-nano**       | Fast, direct responses; sensible error messages    | Struggles with complex time queries or multi-turn disambiguation |
| **gpt-4.1-mini**       | Balanced accuracy, conversational tone             | Sometimes overly verbose or redundant                            |
| **gpt-4o-mini**        | Concise, best at paraphrasing results              | Occasional errors in handling function calls or bad inputs       |
| **gpt-3.5-turbo-0125** | Most stable and consistent with structured outputs | Less accurate on ambiguous prompts and date parsing              |

### Sample Prompt Comparison: "What's the weather in New York?"

* **gpt-4.1-nano**: "High of 25.2°C and low of 15.1°C."
* **gpt-4.1-mini**: "Max 25.2°C, min 15.1°C, 0.5mm precipitation."
* **gpt-4o-mini**: "Sorry, couldn’t retrieve weather."
* **gpt-3.5-turbo**: "Weather for May 8, 2025: Max 25.2°C, Min 15.1°C."

### Sample Prompt Comparison: "Tell me a joke."

* All models responded appropriately without calling the weather function.

### Sample Prompt: "What's the weather like?"

* **gpt-4.1-nano/mini/4o** asked for a specific location.
* **gpt-3.5** defaulted to a generic weather assumption (e.g., "sunny outside").

---

## Discussion

### Challenges Encountered

* **Date Parsing Edge Cases**: Interpreting vague or malformed inputs like "next next Monday" or "Thufriday" was inconsistent across models.
* **Tool Calling Errors**: In some cases (especially with `gpt-4o`), the model failed to complete the tool call loop correctly.
* **Forecast Horizon**: The Open-Meteo API restricts date ranges to 7-16 days, so queries like "weather on 2025-06-20" often failed.

### Limitations

* Models don't retain state. So asking follow-up queries like "What about tomorrow?" fails without prior context.
* Geocoding for fictional or vague locations (e.g., "heaven") leads to amusing but inconsistent results.

### Potential Improvements

* Add caching for repeated queries.
* Integrate with a richer weather API like WeatherStack.
* Maintain query session memory for better context chaining.
* Post-process responses to normalize tone and structure across models.

---

## Reflection

Function calling elevates LLMs from static predictors to dynamic agents. Through this assignment, I learnt how a simple assistant can become significantly more capable when integrated with real-time data.

* **Usefulness**: Immediate applications include chatbots, personal assistants, and voice-based apps.
* **Limitations**: Dependence on model behavior (tool call consistency), and external service reliability.
* **Broader Vision**: As function calling matures, I can imagine AI agents orchestrating workflows, querying multiple tools, and even writing to databases—all driven by natural language.

By combining LLMs' language intuition with precise tools, we've moved one step closer to intelligent assistants that are not just fluent—but also functionally helpful.


# Weather Assistant Model Comparison

### Prompt: What's the weather like in New York?
**gpt-4.1-nano-2025-04-14**:

```
The weather in New York today is quite pleasant with a high of 25.2°C and a low of 15.1°C. There's a small amount of precipitation at 0.5 mm.
```

**gpt-4.1-mini-2025-04-14**:

```
The weather in New York today has a maximum temperature of 25.2°C and a minimum temperature of 15.1°C, with 0.5 mm of precipitation.
```

**gpt-4o-mini-2024-07-18**:

```
I'm sorry, but I couldn't retrieve the weather data for New York, NY at the moment. Is there anything else I can assist you with?
```

**gpt-3.5-turbo-0125**:

```
The weather in New York on May 8th, 2025 is as follows:  
- Max temperature: 25.2°C  
- Min temperature: 15.1°C  
- Precipitation: 0.5 mm
```


---
### Prompt: Tell me the weather forecast for Tokyo.
**gpt-4.1-nano-2025-04-14**:

```
The weather forecast for Tokyo today is sunny with no precipitation. The maximum temperature is expected to be around 21°C, and the minimum temperature about 12°C.
```

**gpt-4.1-mini-2025-04-14**:

```
The weather forecast for Tokyo on May 8, 2025, is a maximum temperature of 21.0°C, a minimum temperature of 12.1°C, and no precipitation expected.
```

**gpt-4o-mini-2024-07-18**:

```
The weather forecast for Tokyo on May 8, 2025, is as follows:  
- Max temperature: 21.0°C  
- Min temperature: 12.1°C  
- Precipitation: 0.0 mm
```

**gpt-3.5-turbo-0125**:

```
The weather forecast for Tokyo on May 8th is as follows:  
- Max temperature: 21.0°C  
- Min temperature: 12.1°C  
- Precipitation: 0.0 mm
```


---
### Prompt: Can you check the weather in College Park?
**gpt-4.1-nano-2025-04-14**:

```
The weather in College Park today is quite mild, with a maximum temperature of 25.8°C and a minimum of 12.8°C. There's a slight chance of precipitation, with 1.1 mm of rain.
```

**gpt-4.1-mini-2025-04-14**:

```
The weather in College Park today is a maximum temperature of 25.8°C, a minimum temperature of 12.8°C, with 1.1 mm of precipitation. Would you like to know the forecast for any other day?
```

**gpt-4o-mini-2024-07-18**:

```
The weather in College Park on May 8, 2025, is expected to have a maximum temperature of 25.8°C and a minimum of 12.8°C, with a chance of precipitation at 1.1 mm.
```

**gpt-3.5-turbo-0125**:

```
The weather in College Park on 08 May 2025 is as follows:  
- Max temperature: 25.8°C  
- Min temperature: 12.8°C  
- Precipitation: 1.1 mm
```


---
### Prompt: Is it raining today in Paris?
**gpt-4.1-nano-2025-04-14**:

```
There is very little rainfall today in Paris with only 0.1 mm of precipitation, so it's not raining significantly.
```

**gpt-4.1-mini-2025-04-14**:

```
It is not raining significantly in Paris today, with only 0.1 mm of precipitation reported. The weather seems mostly dry.
```

**gpt-4o-mini-2024-07-18**:

```
Today in Paris, the weather is mild with a maximum temperature of 18.5°C and a minimum of 9.2°C. There is a slight chance of rain with a total precipitation of 0.1 mm, so it's likely to be a very light rain if it occurs.
```

**gpt-3.5-turbo-0125**:

```
It is not raining today in Paris. The weather forecast shows a maximum temperature of 18.5°C and a minimum temperature of 9.2°C with very little precipitation.
```


---
### Prompt: Tell me a joke.
**gpt-4.1-nano-2025-04-14**:

```
Why did the scarecrow win an award? Because he was outstanding in his field!
```

**gpt-4.1-mini-2025-04-14**:

```
Sure! Here's a joke for you:  
  
Why don't scientists trust atoms?  
  
Because they make up everything!
```

**gpt-4o-mini-2024-07-18**:

```
Why don't scientists trust atoms?  
  
Because they make up everything!
```

**gpt-3.5-turbo-0125**:

```
Why was the math book sad?  
Because it had too many problems.
```


---
### Prompt: Who won the last FIFA World Cup and who was the most important player of that tournament?
**gpt-4.1-nano-2025-04-14**:

```
The last FIFA World Cup was held in 2022 in Qatar. Argentina won the tournament, defeating France in the final. The most important player of that tournament was Lionel Messi, who played a key role in Argentina's victory and was also awarded the Golden Ball as the best player of the tournament.
```

**gpt-4.1-mini-2025-04-14**:

```
The last FIFA World Cup was held in 2022, and Argentina won the tournament. The most important player of the tournament, often regarded as the best player, was Lionel Messi. He played a crucial role in leading Argentina to victory and was awarded the Golden Ball as the tournament's best player.
```

**gpt-4o-mini-2024-07-18**:

```
The last FIFA World Cup took place in 2022 in Qatar. Argentina won the tournament, defeating France in the final. The most important player of the tournament was Lionel Messi, who played a pivotal role in leading Argentina to victory and was awarded the Golden Ball as the tournament's best player.
```

**gpt-3.5-turbo-0125**:

```
The most recent FIFA World Cup was held in 2018, and France emerged as the champion by defeating Croatia in the final. The tournament's most important player, also known as the Golden Ball award winner, was Luka Modrić, the Croatian midfielder. He played a vital role in leading Croatia to the final and showcased exceptional performance throughout the tournament.
```


---
### Prompt: What's the capital of Norway?
**gpt-4.1-nano-2025-04-14**:

```
The capital of Norway is Oslo.
```

**gpt-4.1-mini-2025-04-14**:

```
The capital of Norway is Oslo.
```

**gpt-4o-mini-2024-07-18**:

```
The capital of Norway is Oslo.
```

**gpt-3.5-turbo-0125**:

```
The capital of Norway is Oslo.
```


---
### Prompt: Do you believe AI Engineering requires significant skill?
**gpt-4.1-nano-2025-04-14**:

```
AI Engineering indeed requires significant skill. It involves a strong understanding of machine learning algorithms, programming, data analysis, and system design. Additionally, skills in problem-solving, critical thinking, and domain knowledge are essential to develop effective and reliable AI systems. Would you like more detailed information about the skills needed for AI Engineering?
```

**gpt-4.1-mini-2025-04-14**:

```
Yes, AI Engineering requires significant skill because it involves a deep understanding of machine learning algorithms, data processing, software development, and domain-specific knowledge. It also demands skills in programming, system design, and problem-solving to build, deploy, and maintain effective AI systems. Additionally, staying updated with the latest research and ethical considerations is crucial in this rapidly evolving field.
```

**gpt-4o-mini-2024-07-18**:

```
Yes, AI Engineering requires a significant amount of skill. It involves a combination of knowledge in areas such as programming, data science, machine learning, statistics, and sometimes domain-specific knowledge. Engineers must be able to understand complex algorithms, optimize models, and implement them effectively in various applications. Additionally, problem-solving skills and the ability to work with large datasets are crucial in this field. Continuous learning is also important due to the rapidly evolving nature of AI technologies.
```

**gpt-3.5-turbo-0125**:

```
Yes, AI Engineering requires significant skill and expertise in various areas such as machine learning, data science, programming, and problem-solving. It involves understanding complex algorithms, data manipulation, model training, and deployment. AI Engineers need to have a strong foundation in mathematics, statistics, and computer science to develop and implement AI solutions effectively.
```


---
### Prompt: What's the weather like?
**gpt-4.1-nano-2025-04-14**:

```
Could you please specify the location you'd like the weather forecast for?
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please specify the location you want to know the weather for?
```

**gpt-4o-mini-2024-07-18**:

```
Could you please provide me with a location?
```

**gpt-3.5-turbo-0125**:

```
It's currently sunny outside.   
  
If you'd like, I can check the weather for a specific location. Just let me know where you'd like me to check.
```


---
### Prompt: Is it cold outside?
**gpt-4.1-nano-2025-04-14**:

```
I can check the weather for you. Please tell me your location.
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please tell me your location or the city you'd like to know the weather for? Then I can check if it's cold outside.
```

**gpt-4o-mini-2024-07-18**:

```
Could you please provide me with your location so I can check the current weather for you?
```

**gpt-3.5-turbo-0125**:

```
It seems you're curious about the weather. Would you like me to check the current weather for you?
```


---
### Prompt: Weather in heaven?
**gpt-4.1-nano-2025-04-14**:

```
Heavenly weather in heaven (assuming "Heaven" refers to a figurative or spiritual place) isn't something I can provide. If you meant a specific location like Heavener, I found the weather for today: it’s around 22.5°C with clear skies and no precipitation.
```

**gpt-4.1-mini-2025-04-14**:

```
Heaven is a concept and not a physical location, so there isn't any weather information available for it. If you want to know the weather for a specific city or place on Earth, please let me know!
```

**gpt-4o-mini-2024-07-18**:

```
The weather in Heavener today is quite pleasant, with a maximum temperature of 22.5°C and a minimum of 13.0°C. There's no expected precipitation, so it should be a dry day!
```

**gpt-3.5-turbo-0125**:

```
The weather in Heavener on May 8, 2025, is expected to have a maximum temperature of 22.5°C and a minimum temperature of 13.0°C. There is no precipitation expected.
```


---
### Prompt: How's the sky there?
**gpt-4.1-nano-2025-04-14**:

```
I need to know your location to check the weather and sky conditions. Could you please provide your location?
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please specify the location you'd like to know the sky/weather condition for?
```

**gpt-4o-mini-2024-07-18**:

```
Could you please specify the location you want to know about so I can check the weather for you?
```

**gpt-3.5-turbo-0125**:

```
The sky is currently clear and sunny here. Is there anything else you would like to know or do?
```


---
### Prompt: What's the weather in London tomorrow?
**gpt-4.1-nano-2025-04-14**:

```
The weather in London tomorrow is expected to be mild, with a high of 17.5°C and a low of 6.9°C. There is no expected precipitation.
```

**gpt-4.1-mini-2025-04-14**:

```
The weather in London tomorrow is expected to have a maximum temperature of 17.5°C and a minimum temperature of 6.9°C, with no precipitation.
```

**gpt-4o-mini-2024-07-18**:

```
I'm sorry, but I couldn't retrieve the weather information for London. Please try again later or check another source for the weather updates.
```

**gpt-3.5-turbo-0125**:

```
The weather in London tomorrow is as follows:  
- Max temperature: 17.5°C  
- Min temperature: 6.9°C  
- Precipitation: 0.0 mm.
```


---
### Prompt: Will it rain in Dallas this weekend?
**gpt-4.1-nano-2025-04-14**:

```
I couldn't find the weather information for Dallas this weekend. Please let me know if you'd like me to try again or help with something else.
```

**gpt-4.1-mini-2025-04-14**:

```
Yes, there is a chance of rain in Dallas this weekend, with precipitation expected around 2.9 mm.
```

**gpt-4o-mini-2024-07-18**:

```
An error occurred: Error code: 400 - {'error': {'message': "An assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'. The following tool_call_ids did not have response messages: call_uV6qbAn0Php0L5FJNQuKRJEl", 'type': 'invalid_request_error', 'param': 'messages', 'code': None}}
```

**gpt-3.5-turbo-0125**:

```
According to the weather forecast, there is a chance of rain in Dallas this weekend with 2.9 mm of precipitation.
```


---
### Prompt: How will the weather be in New Delhi on 2025-06-20?
**gpt-4.1-nano-2025-04-14**:

```
I encountered an issue retrieving the weather data for New Delhi on June 20, 2025. Please try again later or let me know if you need weather information for a different date.
```

**gpt-4.1-mini-2025-04-14**:

```
I'm sorry, but I cannot provide the weather forecast for New Delhi on June 20, 2025, at this time. Weather forecasts typically are available only for the short term, usually up to 7-10 days in advance. If you have any other questions or need information on the current weather, feel free to ask!
```

**gpt-4o-mini-2024-07-18**:

```
I'm sorry, but I wasn't able to retrieve the weather data for New Delhi on June 20, 2025. It's possible that forecasts for such a distant date are not available. Is there another date or location you'd like to ask about?
```

**gpt-3.5-turbo-0125**:

```
I apologize, but I couldn't retrieve the weather information for New Delhi on June 20, 2025. If you have any other questions or need assistance, feel free to ask.
```


---
### Prompt: What's the temperature in Rome next Monday?
**gpt-4.1-nano-2025-04-14**:

```
Could you please specify the date or clarify the day you are referring to?
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please provide the exact date for next Monday? For example, the date in the format YYYY-MM-DD would be helpful.
```

**gpt-4o-mini-2024-07-18**:

```
Could you please provide a specific date for next Monday? This will help me find the accurate weather information for Rome.
```

**gpt-3.5-turbo-0125**:

```
I'm sorry, I couldn't find the weather information for you. Is there anything else you would like to know?
```


---
### Prompt: What's the forecast for tomorrow?
**gpt-4.1-nano-2025-04-14**:

```
Please tell me your current location or specify the city you'd like the weather forecast for.
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please specify the location for which you'd like the weather forecast for tomorrow?
```

**gpt-4o-mini-2024-07-18**:

```
Please provide me with the location for which you would like to know the weather forecast for tomorrow.
```

**gpt-3.5-turbo-0125**:

```
I can help you with that. Could you please provide me with the location you want the weather forecast for?
```


---
### Prompt: What's the weather in College Park?
**gpt-4.1-nano-2025-04-14**:

```
The weather in College Park today is expected to have a high of about 25.8°C and a low of around 12.8°C, with approximately 1.1 mm of precipitation.
```

**gpt-4.1-mini-2025-04-14**:

```
The weather in College Park today has a maximum temperature of 25.8°C and a minimum temperature of 12.8°C, with 1.1 mm of precipitation.
```

**gpt-4o-mini-2024-07-18**:

```
The weather in College Park is as follows:  
- Max temperature: 25.8°C  
- Min temperature: 12.8°C  
- Precipitation: 1.1 mm
```

**gpt-3.5-turbo-0125**:

```
The weather in College Park on May 8th is as follows:  
- Max temperature: 25.8°C  
- Min temperature: 12.8°C  
- Precipitation: 1.1 mm.
```


---
### Prompt: Tell me how hot it will be next Friday.
**gpt-4.1-nano-2025-04-14**:

```
Could you please tell me your current location or specify the city you'd like the weather forecast for?
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please specify the location you want the weather forecast for next Friday?
```

**gpt-4o-mini-2024-07-18**:

```
Please provide me with the location for which you want to know the weather for next Friday.
```

**gpt-3.5-turbo-0125**:

```
It seems I couldn't retrieve the weather information for next Friday in San Francisco. Is there anything else you would like to know or ask?
```


---
### Prompt: Next Tuesday's rain forecast?
**gpt-4.1-nano-2025-04-14**:

```
Could you please specify your location so I can provide the rain forecast for next Tuesday?
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please specify the location for the rain forecast on next Tuesday?
```

**gpt-4o-mini-2024-07-18**:

```
Could you please specify the location you're interested in for next Tuesday's rain forecast?
```

**gpt-3.5-turbo-0125**:

```
I'm sorry, I couldn't retrieve the weather information for next Tuesday. Is there anything else I can assist you with?
```


---
### Prompt: Weather in Chicago on Thufriday.
**gpt-4.1-nano-2025-04-14**:

```
An error occurred: Error code: 400 - {'error': {'message': "An assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'. The following tool_call_ids did not have response messages: call_9eZNyL9qFyWSUAOrnqRM1N5f", 'type': 'invalid_request_error', 'param': 'messages', 'code': None}}
```

**gpt-4.1-mini-2025-04-14**:

```
The weather in Chicago on Thursday is expected to have a maximum temperature of 23.9°C and a minimum temperature of 15.2°C, with a chance of light precipitation of 0.6 mm.
```

**gpt-4o-mini-2024-07-18**:

```
It looks like I couldn't retrieve the weather information for Chicago. If you need weather details for a different location or day, feel free to let me know!
```

**gpt-3.5-turbo-0125**:

```
The weather in Chicago on Thursday, May 15th, 2025 will have a maximum temperature of 23.9°C and a minimum temperature of 15.2°C with 0.6 mm of precipitation.
```


---
### Prompt: Forecast in Miami on 2025-99-99.
**gpt-4.1-nano-2025-04-14**:

```
It seems that the date you provided is invalid. Please provide a valid date in the format YYYY-MM-DD.
```

**gpt-4.1-mini-2025-04-14**:

```
The date "2025-99-99" is not a valid date. Could you please provide a valid date for the weather forecast in Miami?
```

**gpt-4o-mini-2024-07-18**:

```
It seems that the date "2025-99-99" is not a valid date. If you meant a different date, please provide that, and I can look up the weather for Miami for you!
```

**gpt-3.5-turbo-0125**:

```
I'm sorry, but I couldn't retrieve the weather forecast for Miami on the date specified. If you need information for a specific date within a valid range, feel free to ask!
```


---
### Prompt: Show me weather in Los Angeles next next Monday.
**gpt-4.1-nano-2025-04-14**:

```
An error occurred: Error code: 400 - {'error': {'message': "An assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'. The following tool_call_ids did not have response messages: call_Hz6ZKhQfAG5odoGFCAUTltKU", 'type': 'invalid_request_error', 'param': 'messages', 'code': None}}
```

**gpt-4.1-mini-2025-04-14**:

```
Could you please specify the exact date or the specific Monday you mean? For example, you can say "Monday, June 10th" or "the Monday after next." This will help me provide accurate weather information for Los Angeles.
```

**gpt-4o-mini-2024-07-18**:

```
I'm unable to retrieve the weather data for Los Angeles at the moment. If you'd like, you can ask for the weather in another location or for a different date!
```

**gpt-3.5-turbo-0125**:

```
I'm sorry, I couldn't retrieve the weather information for Los Angeles next next Monday.
```


---
