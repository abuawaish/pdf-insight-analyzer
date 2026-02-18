from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embeddings(texts):
    """Get embeddings using OpenAI API"""
    if isinstance(texts, str):
        texts = [texts]
    
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    
    return [item.embedding for item in response.data]

def query_llm(context, user_query):
    """Query OpenAI API for context-based answers"""
    
    # Format prompt with context and question
    system_message = "You are an expert document analyst. Answer questions using ONLY the provided context. If the answer isn't in the context, say 'I don't know'."
    
    user_message = f"""Context:
{context}

Question: {user_query}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Extract generated text from response
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"