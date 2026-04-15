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

async def compile_directive(context: str) -> CompiledDirective:
    # xgrammar is triggered automatically by passing the pydantic schema to response_format
    response = await client.beta.chat.completions.parse(
        model=settings.VLLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a compiler. Turn the following task execution history into a reusable JSON directive."},
            {"role": "user", "content": context}
        ],
        response_format=CompiledDirective
    )
    return response.choices[0].message.parsed
