import transcrib
import rag
import os

#FUNCTION TO GET LLM RESPONSE BY GIVING JUST THE URL OF LOOM VID AND YOUR TEXT QUERY
#ONLY THIS FUNCTION TO BE USED IN MAIN BOT
def give_answer(url,query):
    name=url.strip().split("/")[-1]
    txt_file_path = name+".txt"
    if not os.path.exists(txt_file_path):
        print(txt_file_path)
        txt_file_path = transcrib.get_transcrib_from_loom(url)
    rag.save_faiss(txt_file_path)
    ans = rag.get_faiss_ans(txt_file_path,query)
    return ans

#trial

#https://persistventure.notion.site/ArtBot-Assignment-887cce76917d4685a0fda7ff41426ba7?pvs=4
#https://www.loom.com/share/de6bd2ea76cb4c29bee798f81becd0ee
# print(give_answer("https://www.loom.com/share/de6bd2ea76cb4c29bee798f81becd0ee","how to do this assignment?"))
    