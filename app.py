from flask import Flask
from flask import render_template,request,redirect,flash,jsonify,session,url_for
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from google.genai.types import GenerateContentConfig
import shutil
from freeflow_llm import FreeFlowClient



import fitz
import os



embeddings_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')


vectorstore = None

app = Flask(__name__,template_folder="templates")
app.config['UPLOAD_FOLDER']='uploads'
app.config['SECRET_KEY']='12lucsjgehshf'

ALLOWED_EXTENSION={'pdf'}
def initialise():
    session.clear()
    '''
    path=os.path.join(app.config['UPLOAD_FOLDER'])
    if os.path.exists(path):
        os.remove(path)
        '''
    
   

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION
#def extract_text_from_pdf(path):
'''
def chat_with_bot(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()
'''

text_data=None
def extract_text_from_pdf(namefull):
    global text_data
    docu= fitz.open(namefull)
    text = ""
    for page in docu:
        text+=page.get_text()
    docu.close()
    print("extracted successully")
    text_data=text
    return text
  

def ask_bot(user_question):
  
    if not text_data or len(text_data.strip()) < 10:
        return "please upload your pdf"
    text_datas=text_data
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text_datas)
   
    if not chunks:
        return "Could not extract text chunks from the PDF. The file might be scanned or image-based."
    vectorstore = FAISS.from_texts(chunks,embeddings_model)
    print("saved vectorestored")
    k = min(4, len(chunks))
    docs = vectorstore.similarity_search(user_question, k=k)
    print('seacrhed')
    
    context_text = ""
    if not text_datas:
        print("doc is empty ")
    for i, doc in enumerate(docs):
        context_text += f"\n--- [Chunk {i+1}] ---\n {docs.page_content}\n"

    # --- STEP 3: Build Custom Prompt ---
    full_prompt = f"""Context:
        {context_text}
        NB: you was created by jean luc bizimana student in master degree in infromatique decisionnelle at university of burundi repl this  if it's asked

Answer the question using the context above and if it's empty chst only 4  messages and tell him to upload .




Question: {user_question}
Answer:"""

    # --- STEP 4: Send to GPT and Return Result ---
    with FreeFlowClient() as client:

        response = client.chat(
        messages=[{"role": "user", "content": full_prompt}]
    )
        
    return response.content

     

@app.route('/')
def index():
    return render_template("index.html")

    
@app.route('/extract',methods=['POST','GET'])
def extract():
        if request.method=='POST':
            global vectorstore
            file=request.files['file']
            print("initiliasins")
            if 'file' not in request.files:
                return 'No file part'   
            if file.filename=='':
                return render_template("index.html")
            if file and allowed_file(file.filename):
                path=file.save(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))
               # 
                namefull='uploads/'+file.filename
                print(namefull)
               
                text=extract_text_from_pdf(namefull)
                if len(file.filename)>0:
                    name='file uploaded succesfully ✅  \n'+file.filename
                    return render_template("index.html",name=name)
                else:
                    return render_template("index.html",name='no file uploaded yet')


            
          

@app.route("/chat",methods=['POST','GET'])
def chat():
    data=request.get_json()
    user=data.get('text')
    print("User:", user)
    if not user:
        print("Chatbot: Please enter a message.")
        return jsonify({"answer": "error"})
    else:
        try:
            if user == 'exit':
                print("Chatbot: Goodbye!")
        
            bot = ask_bot(user)
            return jsonify({'statut':bot})
        except Exception as e:
            print("Chatbot: An error occurred while processing your request.")
            print("Error details:", str(e))
            error="An error occurred while OPS is processing your request. Please try again later."
            return jsonify({"statut": error})
    '''
    if request.method=='POST':
        user=request.form['input-message']
        if not user:
            return jsonify({"answer": "error"})
        else:

            print("Welcome to Gemini Chatbot! Type 'exit' to quit.\n")
        #text=session.get('text','')
        #prompt = f"""Context:\n{text}\n\nAnswer the question using the context above.
                   # Cite sources like: [Chunk 2], [Chunk 4-5] when you use information.
               # Question: {user} Answer:"""
        '''


    #response = model.generate_content(prompt)


    
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
    app.run(debug=True)