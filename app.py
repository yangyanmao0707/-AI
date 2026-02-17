import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_community.tools import DuckDuckGoSearchRun
from opencc import OpenCC

# ==========================================
# 1. 核心初始化
# ==========================================
cc = OpenCC('s2twp')
search = DuckDuckGoSearchRun()

# 網頁基本設定 (標題改為較中性的系統名稱)
st.set_page_config(page_title="Terminal | System 12B", layout="wide")

# CSS 全域置中與美化注入
st.markdown("""
    <style>
    /* 讓所有文字與對話框置中 */
    .stApp h1, .stApp h2, .stApp h3, .stApp p {
        text-align: center !important;
    }
    .stChatMessage {
        display: flex !important;
        justify-content: center !important;
    }
    .stChatMessageContent {
        max-width: 800px !important;
        text-align: left !important; 
        margin: 0 auto !important;
    }
    /* 隱藏上方裝飾條 */
    header {visibility: hidden;}
    /* 讓 spinner 置中 */
    .stSpinner {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 側邊欄 (System Settings)
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ SYSTEM CONTROL")
    st.divider()
    internet_on = st.toggle("🌐 全球連網模式", value=True)
    st.divider()
    st.subheader("Hardware Status")
    st.code("GPU: RTX 4060 8GB\nCore: Mistral NeMo 12B\nType: Local Edge Computing")
    
    if st.button("🗑️ CLEAR MEMORY", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. 加載 Ollama 模型
# ==========================================
@st.cache_resource
def load_llm():
    return OllamaLLM(model="mistral-nemo")

try:
    llm = load_llm()
except Exception:
    st.error("❌ 核心引擎未啟動，請確認 Ollama 是否執行中")

# ==========================================
# 4. 授權鎖 (極簡登入介面)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-weight: 200; letter-spacing: 5px;'>SYSTEM ENCRYPTION</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888;'>此連線受端對端加密保護，請輸入驗證金鑰</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        auth_code = st.text_input("Access Key", type="password", label_visibility="collapsed")
        if st.button("ENTER", use_container_width=True):
            if auth_code == "12345":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Key.")
    st.stop()

# ==========================================
# 5. 主對話介面
# ==========================================
# 極簡頂部標示
st.markdown("<h3 style='font-weight: 300; color: #444;'>TERMINAL_LOG_v1.0</h3>", unsafe_allow_html=True)
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 處理輸入指令
if prompt := st.chat_input("Waiting for instruction..."):
    # 紀錄使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 回應部分
    with st.chat_message("assistant"):
        response_container = st.empty()
        
        try:
            with st.spinner("📡 正在擷取衛星數據並進行 12B 運算..."):
                context = ""
                # 如果開啟聯網功能
                if internet_on:
                    search_result = search.run(f"latest news about {prompt}")
                    context = f"\n【即時參考資訊】：{search_result}\n"

                # 系統 Prompt 設定
                system_prompt = (
                    "你是由 yangyanmao0707 開發的專業 AI 助手。\n"
                    "1. 必須完全使用臺灣繁體中文回應。\n"
                    "2. 嚴禁使用大陸用語（例如：視頻、軟件、打印）。\n"
                    "3. 語氣保持專業、簡潔、科學化。"
                )
                
                # 執行串流輸出
                full_response = ""
                input_query = f"{system_prompt}\n{context}\nUser Instruction: {prompt}"
                
                for chunk in llm.stream(input_query):
                    # 簡體轉繁體
                    converted_chunk = cc.convert(chunk)
                    full_response += converted_chunk
                    # 即時顯示動態打字效果
                    response_container.markdown(full_response + "▌")
                
                # 最終完成版本去除游標
                response_container.markdown(full_response)
                # 儲存對話紀錄
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"🛰️ 連線異常：{str(e)}")
