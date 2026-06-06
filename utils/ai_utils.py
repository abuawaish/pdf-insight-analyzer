from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Optional: list of keywords that indicate a code‑related question
CODE_KEYWORDS = [
    "code", "function", "algorithm", "program", "script",
    "python", "java", "javascript", "c++", "c#", "ruby", "go", "rust",
    "explain this code", "write a program", "syntax", "debug", "implement"
]

def is_code_question(query: str) -> bool:
    """Return True if the user's question appears to be about code/programming."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in CODE_KEYWORDS)

def get_embeddings(texts):
    """Get embeddings using OpenAI API."""
    if isinstance(texts, str):
        texts = [texts]
    
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]

def query_llm(context: str, user_query: str) -> str:
    """
    Query OpenAI API for context‑based answers.
    For code questions, the model may use its own programming knowledge.
    For other questions, it answers strictly from the provided context.
    """
    # Dynamically adjust system message based on question type
    if is_code_question(user_query):
        code_mode_instruction = """
        This is a CODE‑RELATED question. You MAY use your own general programming knowledge,
        even if the exact code is not present in the provided context. 
        Format your answer with clear steps, bullet points, and code blocks using triple backticks.
        Always include the language name after the opening backticks (e.g., ```python, ```java).
        """
    else:
        code_mode_instruction = """
        This is a DOCUMENT‑SPECIFIC question. Answer ONLY using the provided context.
        If the answer is not in the context, say "I don't know" without making up information.
        """
    
    system_message = f"""
    You are an expert document analyst and a skilled programmer.
    {code_mode_instruction}

    For ALL answers:
    - Use a clean, structured format: headings, numbered steps, bullet points, and proper code blocks.
    - Never escape quotes or backslashes inside code blocks – return raw code as plain text.
    - Wrap inline code in single backticks (`).
    """
    
    user_message = f"Context:\n{context}\n\nQuestion: {user_query}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",   # or "gpt-4" for better code reasoning
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1200,          # increased for longer code explanations
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"API Error: {str(e)}"