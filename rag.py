from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import secret
from langchain.llms import OpenAI
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import os
import pickle
from langchain_openai import ChatOpenAI

##RAG MODEL TO CONVERT TEXT FILE TO VECTORS AND GET ANSWER
#NOT TO BE USED IN MAIN BOT FILE
#ALREADY BEING CALLED IN HELPER.PY SCRIPT
def save_faiss(train_text_file_path):
# filepath="space_x_files/XSpaces_AI_Assg_info.txt"
    store_name=train_text_file_path.split('\\')[-1][:-4]
    if not os.path.exists(f"vector_files\\{store_name}"):
        with open(train_text_file_path) as file:
            text=" ".join(file.readlines())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200,
                        chunk_overlap=40,
                        length_function=len)

        texts = text_splitter.split_text(text=text)
        store_name=train_text_file_path.split('\\')[-1][:-4]

        embeddings=OpenAIEmbeddings(api_key=secret.openaiapi)
        Vectorstore=FAISS.from_texts(texts,embeddings)
        FAISS.save_local(Vectorstore,f"vector_files\\{store_name}")
        print("saved vectors")

def get_faiss_ans(train_text_file_path,query):
    store_name=train_text_file_path.split('\\')[-1][:-4]
    # if not os.path.exists(f"vector_files/{store_name}"):
    #     save_faiss(train_text_file_path)

    if os.path.exists(f"vector_files/{store_name}") and store_name:
        print("exists")
        embeddings=OpenAIEmbeddings(api_key=secret.openaiapi)
        Vectorstore = FAISS.load_local(f"vector_files\\{store_name}",embeddings,allow_dangerous_deserialization=True)
        print("Loaded vectors")
        retriever = Vectorstore.as_retriever(search_kwargs=dict(k=1))
        memory = VectorStoreRetrieverMemory(retriever=retriever)
        llm = OpenAI(temperature=0,api_key=secret.openaiapi) # Can be any valid LLM
        _DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI gives short and helpful replies. If the AI does not know the answer to a question, it asks the human to use the /questions command.

        Relevant pieces of previous conversation:
        {history}

        Current conversation:
        Human: {input}
        AI:"""
        PROMPT = PromptTemplate(
            input_variables=["history","input"], template=_DEFAULT_TEMPLATE
        )
        conversation_with_summary = ConversationChain(
            llm=llm,
            prompt=PROMPT,
            memory=memory,
            verbose=True
        )

        res=conversation_with_summary.predict(input=query)
        return res
    else:
        llm = ChatOpenAI(temperature=0,api_key=secret.openaiapi)
        messages = [
            ("system", "You are a helpful assistant. If you don't know the answer to something, ask the human to use the /questions command"),
            ("human", query),
        ]
        res = llm.invoke(messages).content
        return res

# filepath="C:\\Users\\shrey\\OneDrive\\Documents\\audtran\\copied_content.txt"      