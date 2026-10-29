
from groq import Groq

from backend.config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a legal compliance assistant specializing in
Indian business regulations.

Answer using only the supplied context. If the context does not contain
enough information, clearly state that limitation. Never invent Acts,
sections, rules, or legal requirements. Cite a source only when its
identity is present in the supplied context.

Your responses provide general information, not legal advice. Recommend
checking current official legislation or consulting a qualified lawyer
for important legal decisions.
"""


def generate_answer(query: str, context_chunks: list[dict]) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Set it in your local "
            "environment or Hugging Face Space secrets."
        )

    client = Groq(api_key=GROQ_API_KEY)

    context = "\n\n".join(
        f"[Source: {chunk.get('legal_address', chunk.get('source', 'unknown'))}]\n"
        f"{chunk['text']}"
        for chunk in context_chunks
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            },
        ],
        max_tokens=1024,
        temperature=0.1,
    )

    answer = response.choices[0].message.content or ""

    sources = sorted({
        str(chunk.get("legal_address", chunk.get("source", "unknown")))
        for chunk in context_chunks
    })

    return {"answer": answer, "sources": sources}
