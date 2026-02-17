import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_community.tools import DuckDuckGoSearchRun
from opencc import OpenCC

# ==========================================
# 1. 核心初始化 (維持原樣)
# ==========================================
cc = OpenCC('s2twp')
search = DuckDuckGoSearchRun()

# 修改網頁分頁標題
st.set_page_config(page_title="太空 AI | 12B 研究終端", layout="wide")

st.markdown("""
    <style>
    .stApp h1, .stApp h2, .stApp h3, .stApp p { text-align: center !important; }
    .stChatMessage { display: flex !important; justify-content: center !important; }
    .stChatMessageContent { max-width: 800px !important; text-align: left !important; margin: 0 auto !important; }
    header {visibility: hidden;}
    .stSpinner { display: flex; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 側邊欄 (System Settings)
# ==========================================
with st.sidebar:
    st.markdown("### 🛰️ 太空 AI 控制中心")  # 改為太空 AI
    st.divider()
    internet_on = st.toggle("🌐 全球連網模式", value=True)
    st.divider()
    st.subheader("硬體動力來源")
    st.code("GPU: RTX 4060 8GB\nCore: Mistral NeMo 12B\nType: Local Edge Computing")
    
    if st.button("🗑️ 清空記憶體", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. 加載 Ollama 模型 (維持原樣)
# ==========================================
@st.cache_resource
def load_llm():
    return OllamaLLM(model="mistral-nemo")

try:
    llm = load_llm()
except Exception:
    st.error("❌ 模型引擎未啟動，請確認 Ollama 是否執行中")

# ==========================================
# 4. 授權鎖 (極簡登入介面)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-weight: 300; letter-spacing: 8px;'>太空 AI 研究終端</h2>", unsafe_allow_html=True) # 改為太空 AI
    st.markdown("<p style='color: #888;'>此連線受端對端加密保護，請輸入驗證金鑰</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        auth_code = st.text_input("Access Key", type="password", label_visibility="collapsed")
        if st.button("驗證進入", use_container_width=True):
            if auth_code == "12345":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("金鑰無效")
    st.stop()

# ==========================================
# 5. 主對話介面
# ==========================================
st.markdown("<h1 style='color: #0056b3; letter-spacing: 5px;'>太空 AI 研究系統</h1>", unsafe_allow_html=True) # 改回藍色大標題
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("請輸入指令..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response_container = st.empty()
        
        try:
            with st.spinner("🛰️ 正在擷取衛星數據並進行 12B 運算..."):
                context = ""
                if internet_on:
                    # 調整搜尋關鍵字以獲得更佳效果
                    search_result = search.run(f"太空 航太 最新資訊 {prompt}")
                    context = f"\n【即時參考資訊】：{search_result}\n"

                # 系統 Prompt 設定
                system_prompt = (
                    "你是由 yangyanmao0707 開發的『太空 AI』。\n"
                    "1. 必須完全使用臺灣繁體中文回應。\n"
                    "2. 嚴禁使用大陸用語（例如：視頻、軟件、打印）。\n"
                    "3. 語氣保持專業、簡潔、科學化。"
                )
                
                full_response = ""
                input_query = f"{system_prompt}\n{context}\n使用者指令：{prompt}"
                
                for chunk in llm.stream(input_query):
                    converted_chunk = cc.convert(chunk)
                    full_response += converted_chunk
                    response_container.markdown(full_response + "▌")
                
                response_container.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"🛰️ 連線異常：{str(e)}")
