from openai import AsyncOpenAI
from config import settings
from llm.schemas import CompiledDirective

client = AsyncOpenAI(base_url=settings.VLLM_API_BASE, api_key="local-no-key")


async def generate_response(messages: list) -> str:
    response = await client.chat.completions.create(
        model=settings.VLLM_MODEL_NAME,
        messages=messages,
        temperature=0.1
    )
    return response.choices[0].message.content


async def compile_directive(context: str, valid_tools: list) -> CompiledDirective:
    # Use xgrammar to force the JSON structure [cite: 23]
    response = await client.beta.chat.completions.parse(
        model=settings.VLLM_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""You are a compiler. Turn task history into a reusable JSON directive.
                CRITICAL: You MUST ONLY use the following tools in your 'steps': {valid_tools}
                If a tool used in the history is not in this list, do not include it."""
            },
            {"role": "user", "content": context}
        ],
        response_format=CompiledDirective
    )
    return response.choices[0].message.parsed
