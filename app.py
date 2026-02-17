import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_community.tools import DuckDuckGoSearchRun # 新功能：聯網搜尋
from opencc import OpenCC

# 初始化轉換器與搜尋工具
cc = OpenCC('s2twp')
search = DuckDuckGoSearchRun()

# ==========================================
# 1. 網頁基本設定 & CSS 全域置中注入 (完全維持原版)
# ==========================================
st.set_page_config(page_title="太空 AI | 12B 全速終端", layout="wide")

st.markdown("""
    <style>
    /* 1. 讓主標題與所有 Markdown 文字置中 */
    .stApp h1, .stApp h2, .stApp h3, .stApp p {
        text-align: center !important;
    }
    
    /* 2. 讓對話氣泡容器置中 */
    .stChatMessage {
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
    }
    
    /* 3. 限制對話內容寬度並維持置中 */
    .stChatMessageContent {
        max-width: 800px !important;
        text-align: left !important; 
        margin: 0 auto !important;
    }

    /* 4. 讓 spinner 載入圖示置中 */
    .stSpinner {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 側邊欄 (維持原樣，僅增加聯網開關)
# ==========================================
with st.sidebar:
    st.markdown("# 🛰️ 任務控制中心")
    st.divider()
    internet_on = st.toggle("🌐 開啟聯網模式", value=True) # 新增開關
    st.divider()
    st.subheader("硬體動力來源")
    st.code("GPU: RTX 4060 8GB\nModel: Mistral NeMo")
    if st.button("🗑️ 清空記憶體", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. 初始化模型
# ==========================================
@st.cache_resource
def load_llm():
    return OllamaLLM(model="mistral-nemo")

try:
    llm = load_llm()
except Exception:
    st.error("❌ 模型引擎未啟動")

# ==========================================
# 4. 授權鎖 (維持原樣)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("##  太空 AI 研究終端")
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        auth_code = st.text_input("🔑 輸入驗證碼", type="password")
        if st.button("驗證進入", use_container_width=True):
            if auth_code == "12345":
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# ==========================================
# 5. 主對話介面 (維持原樣)
# ==========================================
st.markdown("<h1 style='color: #0056b3;'> 太空 AI 研究系統</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 處理輸入
if prompt := st.chat_input("請輸入航太指令..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        response_container = st.empty() # 用於動態串流更新
        
        try:
            with st.spinner("🛰️ 衛星通訊計算中..."):
                context = ""
                # 功能 1：聯網搜尋 (如果開關打開)
                if internet_on:
                    search_result = search.run(f"太空 航太 最新 {prompt}")
                    context = f"\n【即時資訊】：{search_result}\n"

                system_prompt = (
                    "你是由台灣開發的『太空 AI』。請遵循：\n"
                    "1. 必須使用臺灣繁體中文回應。\n"
                    "2. 嚴禁用大陸用語。"
                )
                
                # 功能 2：串流輸出 (讓文字逐字出現)
                full_response = ""
                input_query = f"{system_prompt}\n{context}\n指令：{prompt}"
                
                for chunk in llm.stream(input_query):
                    converted_chunk = cc.convert(chunk)
                    full_response += converted_chunk
                    # 在容器中即時渲染
                    response_container.markdown(full_response + "▌")
                
                # 最終完成版本
                response_container.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"🛰️ 通訊異常：{e}")