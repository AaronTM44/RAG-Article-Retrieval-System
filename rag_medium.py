import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import TokenTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.runnables import  RunnablePassthrough

#load api key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


#load the knowledge base(article)
df = pd.read_csv('file/medium.csv')
article = DataFrameLoader(df, page_content_column = "Title")
document = article.load()


# chunking
splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=75)
splitted_doc = splitter.split_documents(document)

#convert each chunk into higher dimensional vector space - embeddings
embeddings = OpenAIEmbeddings()

#in memory vector store
vectorstore = DocArrayInMemorySearch.from_documents(splitted_doc, embeddings)


#LLM model
model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model='gpt-3.5-turbo')

#parsing the ai messsage
parser = StrOutputParser()


#prompt template
template = """
Answer the question based on the context below. If you 
can't answer the question, reply "No content related in the knowledge base".

Context: {context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# langchain ussage
chain = (
    {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)


#searching the article
def search_article(query):
    docs = vectorstore.similarity_search(query, k=4)
    print(f'Query: {query}')
    print(f'Retrieved Documents: {len(docs)}')
    for doc in docs:
        details = doc.to_json()['kwargs']
        print("\nSource (Article Title):", details['page_content'])
        print("\nText: ", details['metadata']['Text'][:350] + "...")
        print('\n\n\n')


#rag_q&n
def rag_app(query):
    print('Query: '+query)
    print('\n')
    print('Answer: '+chain.invoke(query))





if __name__ == '__main__':
    query = "what is artificial general intelligence?"

    search_article(query)

    print('########################################\n')
    print('chatgpt answer\n')

    rag_app(query)

    









