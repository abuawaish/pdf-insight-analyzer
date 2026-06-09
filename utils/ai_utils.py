from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embeddings(texts):
    """
    Generate embeddings using OpenAI.
    """
    if isinstance(texts, str):
        texts = [texts]

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    return [item.embedding for item in response.data]


def query_llm(context: str, user_query: str) -> str:
    """
    PDF-grounded QA.

    Rules:
    - Topic must exist in retrieved PDF context.
    - If topic is absent -> "I don't know."
    - If topic exists -> model may explain, elaborate,
      generate examples, analogies, and code examples.
    """

    system_message = """
        You are an expert document analyst and programming assistant.

        PRIMARY RULE
        -------------
        The provided context is the source of truth.

        TASK
        -------------
        Determine whether the user's question is asking about a concept,
        topic, section, definition, process, or information that exists
        in the provided context.

        RESPONSE RULES
        --------------
        1. If the topic exists in the context:
        - Answer the question.
        - Explain concepts in simple language.
        - Expand the explanation when helpful.
        - Provide examples.
        - Provide analogies.
        - Provide step-by-step explanations.
        - Summarize content.
        - Compare concepts found in the context.

        2. If the topic does NOT exist in the context:
        Respond with exactly:

        I don't know.

        PROGRAMMING RULES
        -----------------
        If the context contains a programming concept
        (e.g. slicing, loops, recursion, classes,
        SQL joins, APIs, decorators, generators, etc.):

        You MAY:
        - Generate original code examples.
        - Create sample programs.
        - Show input/output examples.
        - Explain the code line-by-line.
        - Demonstrate best practices.

        The code itself does NOT need to appear
        inside the document.

        However, the underlying concept MUST exist
        in the context before generating code.

        EXAMPLES
        -------------

        Context contains:
        "Python slicing allows extracting portions
        of a sequence."

        Question:
        "Explain slicing with examples."

        Allowed:
        - Explanation
        - Examples
        - Generated Python code

        Question:
        "Write a slicing program."

        Allowed.

        Question:
        "What is a Python decorator?"

        If decorators are not present in the context:

        I don't know.

        QUESTION VARIATIONS
        -------------------
        Treat these as referring to the same concept
        if the concept exists in the context:
        - explain
        - example
        - give sample
        - code example
        - demonstrate
        - how does it work
        - elaborate
        - use case
        - practical example

        OUTPUT FORMAT
        -------------
        - Use markdown.
        - Use headings when useful.
        - Use bullet points when useful.
        - Use numbered steps when useful.
        - Use fenced code blocks with language names.
        - Keep answers grounded in the context.
        - Do not invent document facts.
    """

    user_message = f"""
        CONTEXT:
        {context}

        QUESTION:
        {user_query}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=1500,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"API Error: {str(e)}"