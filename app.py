import getpass
import os
import pandas as pd
import uvicorn
import sys
import nltk
import hashlib
import ibm_boto3
import os

from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError

from tqdm import tqdm

# langchain 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_milvus import Milvus
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,UnstructuredHTMLLoader

# watsonx
from ibm_watsonx_ai.foundation_models.prompts import PromptTemplate, PromptTemplateManager
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes, PromptTemplateFormats
from ibm_watsonx_ai import APIClient,Credentials
#from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.foundation_models import ModelInference

# Fast API
from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.middleware.cors import CORSMiddleware

# Custom type classes
from customTypes.queryLLMRequest import queryLLMRequest
from customTypes.queryLLMResponse import queryLLMResponse
from customTypes.ingestDocsRequest import ingestDocsRequest
from customTypes.ingestDocsResponse import ingestDocsResponse
from customTypes.ingestDocsCOSRequest import ingestDocsCOSRequest
from customTypes.ingestDocsCOSResponse import ingestDocsCOSResponse

from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from dotenv import load_dotenv

load_dotenv()

API_KEY_NAME = "RAG_APP_API_KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

#watsonx
ibm_cloud_api_key = os.environ.get("IBM_CLOUD_API_KEY")
wx_url = os.environ.get("WX_URL")
project_id = os.environ.get("WX_PROJECT_ID")
wx_space_id = os.environ.get("WX_SPACE_ID")
prompt = os.environ.get("PROMPT_NAME")

#watsonx.data
wxd_milvus_host = os.environ.get("WXD_MILVUS_HOST")
wxd_milvus_port = os.environ.get("WXD_MILVUS_PORT")
wxd_milvus_user = os.environ.get("WXD_MILVUS_USER")
wxd_milvus_password = os.environ.get("WXD_MILVUS_PASSWORD")
wxd_milvus_collection = os.environ.get("WXD_MILVUS_COLLECTION")
wxd_milvus_num_results = os.environ.get("WXD_MILVUS_NUM_RESULTS")
wxd_milvus_min_score=os.environ.get("WXD_MILVUS_MIN_SCORE")

#IBM Cloud Storage
cos_service_instance_id = os.environ.get('COS_INSTANCE_ID')
cos_auth_endpoint = os.environ.get('COS_AUTH_ENDPOINT')
cos_endpoint = os.environ.get('COS_ENDPOINT')
cos_bucket_name = os.environ.get('COS_BUCKET_NAME')
ibm_cloud_api_key=os.environ.get('IBM_CLOUD_API_KEY' )
default_docs_folder=os.environ.get("DEFAULT_DOCS_FOLDER")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

QA_CHAIN_PROMPT ={}
model = {}
vector_db=""

async def lifespan(app: FastAPI):
    # Load the ML model
    yield
    # Clean up the ML models and release the resources

#app = FastAPI(lifespan=lifespan)
app = FastAPI()


milvus_credentials = {
     'server_name': wxd_milvus_host, 
     'host': wxd_milvus_host, 
     'port': wxd_milvus_port,  
     "secure": True, 
     'user': wxd_milvus_user, 
     'password': wxd_milvus_password}

index_params = {"index_type": "HNSW","metric_type": "L2","params":{"M": 16,"efConstruction": 200,"efSearch": 16}}

def getPrompt(prompt, prompt_mgr):
    
    df_prompts = prompt_mgr.list()
    #print("Prompts : " + df_prompts)

    df_prompts = df_prompts.assign(
            NAME=df_prompts['NAME'].astype(str),
            LAST_MODIFIED=pd.to_datetime(df_prompts['LAST MODIFIED'])
    )
    filtered_df = df_prompts[df_prompts['NAME'] == prompt]

    if filtered_df.empty:
        raise ValueError(f"Prompt file does not exist for NAME = " + str(prompt))
    # Find the latest record and prompt id based on 'LAST MODIFIED'
    latest_index = filtered_df['LAST MODIFIED'].idxmax()
    latest_record = filtered_df.loc[latest_index]
    latest_prompt_id = latest_record['ID']
    
    return dict(latest_prompt_id=latest_prompt_id)

vector_db = Milvus(
        embedding_function=embeddings,
        connection_args=milvus_credentials,
        index_params=index_params,
        primary_field='id',
        collection_name=wxd_milvus_collection
    )

print("Vector Store Created")

wml_credentials = Credentials(api_key=ibm_cloud_api_key, url=wx_url)
client = APIClient(wml_credentials)
client.set.default_project(project_id=project_id)

prompt_mgr = PromptTemplateManager(
        credentials=wml_credentials,
        space_id=wx_space_id
    )

prompt_attributes = getPrompt(prompt, prompt_mgr)
QA_CHAIN_PROMPT = prompt_mgr.load_prompt(prompt_attributes.get("latest_prompt_id"), PromptTemplateFormats.LANGCHAIN)
prompt_model = prompt_mgr.load_prompt(prompt_attributes.get("latest_prompt_id"))

if 'stop_sequences' in prompt_model.model_params:
            prompt_model.model_params['stop_sequences'] = ['<|endoftext|>']

model = ModelInference(
            model_id=prompt_model.model_id,
            params=prompt_model.model_params,
            credentials=wml_credentials,
            project_id=project_id
)

# Basic security for accessing the App
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.environ.get("RAG_APP_API_KEY"):
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate RAG APP credentials. Please check your ENV."
        )

def retrieve_with_scores(query, num_results, min_score,filter=None):
    search_kwargs = {
                "k": int(num_results),
                "score_threshold": float(min_score),
                "include_scores": True,
                "verbose": True
    }
    if filter is not None:
                search_kwargs["filter"] = filter

    results = vector_db.similarity_search_with_score_by_vector(embeddings.embed_query(query), **search_kwargs)
    return [{"document": doc, "score": score} for doc, score in results]

def format_docs(docs_with_scores):
    print("DOC WITH SCORE" + str(docs_with_scores))
    return "".join([f"[Document]\n{d['document'].page_content}[End]\n\n" for d in docs_with_scores])

def retrieve_with_scores_wrapper(inputs):
            query = inputs["query"]
            filter = inputs.get("filter")
            num_results = inputs.get("num_results")
            min_score = inputs.get("min_score")
            return retrieve_with_scores(query,num_results, min_score,filter)

def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

@app.post("/ingestDocs")
async def ingestDocs(request: ingestDocsRequest, api_key: str = Security(get_api_key)):
    
    chunk_size = request.chunk_size
    chunk_overlap = request.chunk_overlap

    documents_message = ingestObjectsFromFolder(default_docs_folder,chunk_size, chunk_overlap)

    return ingestDocsResponse(response=str(documents_message))

@app.post("/ingestDocsCOS")
async def ingestDocsCOS(request: ingestDocsCOSRequest, api_key: str = Security(get_api_key)):
    
    chunk_size = request.chunk_size
    chunk_overlap = request.chunk_overlap

    cos = ibm_boto3.client(service_name='s3',
        ibm_api_key_id=ibm_cloud_api_key,
        ibm_service_instance_id=cos_service_instance_id,
        ibm_auth_endpoint=cos_auth_endpoint,
        config=Config(signature_version='oauth'),
        endpoint_url=cos_endpoint)

    files = cos.list_objects(Bucket=cos_bucket_name)
    #cos.download_file('mybucket', 'invoice.json', '/tmp/invoice.json')
    #cos.Bucket(cos_bucket_name).download_file('invoice.json', '/tmp/invoice.json')
    for file in files.get("Contents", []):
        file_name = file["Key"]
        cos.download_file(Bucket=cos_bucket_name,Key=file_name,Filename=default_docs_folder + '/' + file_name)

    documents_message = ingestObjectsFromFolder(default_docs_folder,chunk_size, chunk_overlap)

    return ingestDocsCOSResponse(response=str(documents_message))

def ingestObjectsFromFolder(directory,chunk_size, chunk_overlap):
    
    loaders = [
        DirectoryLoader(directory, glob="**/*.html",show_progress=True),
        DirectoryLoader(directory, glob="**/*.pdf",show_progress=True, loader_cls=PyPDFLoader),
        DirectoryLoader(directory, glob="**/*.pptx",show_progress=True),
        DirectoryLoader(directory, glob="**/*.docx",show_progress=True)
    ]

    documents=[]
    for loader in loaders:
        data =loader.load()
        documents.extend(data)

    content=[]
    metadata = []
    for doc in documents:
        document_title = doc.metadata["title"] if "title" in doc.metadata else doc.metadata['source'].split("/")[-1].split(".")[0]
        content.append("Document Title: " + document_title+"\n"+"Document Content: "+doc.page_content)
        print(document_title)
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=int(chunk_size),
        chunk_overlap=int(chunk_overlap),
        disallowed_special=()
    )
    split_docs = text_splitter.create_documents(content, metadatas=metadata)
    print(f"{len(documents)} Documents are split into {len(split_docs)} documents with a chunk size",chunk_size)

    id_list=[]
    for doc in split_docs:
        id_list.append(hashlib.sha256(doc.page_content.encode()).hexdigest())  
    print(len(id_list) - len(set(id_list)),"duplicate documents found.")

    with tqdm(total=len(split_docs), desc="Inserting Documents", unit="docs") as pbar:
        try:
            for i in range(0, len(split_docs), int(chunk_size)):
                chunk = split_docs[i:i + int(chunk_size)]
                id_chunk = [generate_hash(doc.page_content) for doc in chunk]
                vector_db.add_documents(chunk, ids=id_chunk)
                pbar.update(len(chunk))
            print("Documents are inserted into vector database")
        except Exception as e:
            print(f"An error occurred: {e}")

    return "Documents are inserted into vector database: " + str(len(documents))


@app.post("/queryLLM")
async def queryLLM(request: queryLLMRequest, api_key: str = Security(get_api_key)):
    question = request.question
    num_results = request.num_results
    min_score = request.min_score

    llm_chain = (
                RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
                | QA_CHAIN_PROMPT
                | model.to_langchain()
                | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel({
            "context": retrieve_with_scores_wrapper,
            "question": RunnablePassthrough(),
        }).assign(answer=llm_chain)

    inputs = {"query": question,
              "num_results": num_results,
              "min_score": min_score}

    llm_response = rag_chain_with_source.invoke(inputs)

    return queryLLMResponse(response=str(str(llm_response.get("answer"))))

if __name__ == '__main__':
    if 'uvicorn' not in sys.argv[0]:
        uvicorn.run("app:app", host='0.0.0.0', port=4050, reload=True)
