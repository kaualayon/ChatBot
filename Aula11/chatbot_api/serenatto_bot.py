# inclusao das bibliotecas
import os # biblioteca de funçoes do sistema operacional
from typing import List # biblioteca para criar uma lista
# Bibliotecas para ler os diretorio do pdf
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter # biblioteca para separar as informações do pdf e dividir
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # biblioteca para fazer o
#embedding
from llama_index.vector_stores.chroma import ChromaVectorStore # biblioteca para o banco de dados
from llama_index.llms.groq import Groq # Biblioteca para importar a api do groq
from llama_index.core.memory import ChatSummaryMemoryBuffer # biblioteca para criar a LLM
import chromadb # biblioteca do banco de dados vetorial
from tempfile import TemporaryDirectory # biblioteca para ler o diretorio 
from PyPDF2 import PdfReader # biblioteca para ler o pdf

class ChromaEmbeddingWrapper:
    # cria funçao para iniciar o embedding do pdf
    def __init__(self,model_name:str):
        self.model = HuggingFaceEmbedding(model_name= model_name)
    
    def __call__(self, input:List[str])->List[List[float]]:
       return self.model.embed_documents(input)
    


#cria classe chamada SerenattoBot

class SerenattoBot:
    def __init__(self): 
        #modelo para fazer o embedding
        self.embed_model = HuggingFaceEmbedding(model_name='intfloat/multilingual-e5-large')


        chroma_client = chromadb.PersistentClient(path='./chroma_db')
        collection_name = 'documentos_serenatto'
        chroma_collection = chroma_client.get_or_create_collection(
            name = collection_name,
            embedding_function=self.embed_model_chroma
        )

        # transforma os dados em vetor
        self.vector_store = ChromaVectorStore(chroma_collection = chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        #api para conectar no Groq
        self.llms = Groq(model ='llama3-70b-8192',api_key='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')
        
        self.document_index = None
        self.chat_engine = None
        self.carregar_pdf()

    

    #Cria funçao para carregar o pdf

    def carregar_pdf(self):
        with TemporaryDirectory() as tmpdir:
            pdf_path = "documentos/serenatto.pdf"
            text=""
            reader = PdfReader(pdf_path)

            for page in reader.pages:
                text += page.extract_text() or ""

            with open(os.path.join(tmpdir,"temp.txt"),"w",encoding="utf-8") as f:
                f.write(text)

            
            documentos = SimpleDirectoryReader(input_dir=tmpdir)
            docs =  documentos.load_data()

            node_parser = SentenceSplitter(chunk_size=1200)
            nodes = node_parser.get_nodes_from_documents(docs)
            self.document_index = VectorStoreIndex(nodes,storage_context=self.storage_context,
                                                   embed_model=self.embed_model)
            
            memory = ChatSummaryMemoryBuffer(llm= self.llms, token_limit=256)

            self.chat_engine = self.document_index.as_chat_engine(
                chat_mode='context',
                llm= self.llms,
                memory=memory,
                system_prompt='''Você é especialista em cafes da loja Serenatto. 
                Responda de forma simpatica e natural sobre os graos disponiveis'''
            )
    
    # funçao que ira responder as mensagens que enviarmos
    def responder(self, mensagem:str)->str:
        if self.chat_engine is None:
            return "Erro: o bot ainda não está pronto"
        response = self.chat_engine.chat(mensagem)
        return response.response

    def resetar(self):
        if self.chat_engine:
            self.chat_engine.reset()


        