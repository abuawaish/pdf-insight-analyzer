import requests
from sentence_transformers import SentenceTransformer
from config import HF_API_KEY

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(texts):
    return embed_model.encode(texts).tolist()

def query_llm(context, user_query):
    """Query Hugging Face Inference API"""
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # Format prompt with context and question
    prompt = f"""
    <s>[INST] You are an expert document analyst. Answer the question using ONLY the provided context.
    If the answer isn't in the context, say "I don't know".
    
    Context:
    {context}
    
    Question: {user_query} [/INST]
    """
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.3,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Handle API errors
        if isinstance(result, dict) and "error" in result:
            return f"API Error: {result['error']}"
        
        # Extract generated text
        if isinstance(result, list) and len(result) > 0:
            return result[0]['generated_text'].strip()
        
        return "Unexpected API response format"
    
    except requests.exceptions.RequestException as e:
        return f"API Connection Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"