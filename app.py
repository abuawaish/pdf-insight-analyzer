from flask import Flask, render_template, request, jsonify
import os
from utils import pdf_utils, db_utils, ai_utils
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize on startup
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    pdf_list = db_utils.get_pdf_list()
    return render_template('index.html', pdf_list=pdf_list)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF
        text = pdf_utils.extract_text(filepath)
        chunks = pdf_utils.chunk_text(text)
        embeddings = ai_utils.get_embeddings(chunks)
        db_utils.store_embeddings(filename, chunks, embeddings)
        
        os.remove(filepath)
        return jsonify({"success": True, "filename": filename})
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    pdf_name = data['pdf_name']
    user_query = data['query']
    
    # Get relevant context
    query_embedding = ai_utils.get_embeddings([user_query])[0]
    results = db_utils.search_documents(query_embedding, pdf_name)
    context = "\n".join([hit.payload['text'] for hit in results])
    
    # Query Hugging Face
    response = ai_utils.query_llm(context, user_query)
    return jsonify({"response": response})

if __name__ == '__main__':
    from utils import db_utils
    db_utils.initialize_collection()
    app.run(debug=True)