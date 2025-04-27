import streamlit as st
import requests
import json
import time

# ---------- API 設定 ----------
API_ENDPOINT = "https://42t2q26m2a.execute-api.us-west-2.amazonaws.com/dev/idol"

# ---------- 頁面設定 ----------
st.set_page_config(page_title="偶像故事啟動", page_icon="🎬")

# ---------- 初始化會話狀態 ----------
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
    st.session_state.scene = ""
    st.session_state.is_typing = False
    st.session_state.full_response = ""
    st.session_state.affinity = 0
    st.session_state.first_story_done = False
    st.session_state.user_input = ""
    st.session_state.auto_send_flag = True  # 🚀 初次載入自動送「開始故事」

# ---------- 顯示文字動畫函數 ----------
def display_text_animation():
    story_container = st.empty()
    full_text = st.session_state.full_response

    if not isinstance(full_text, str):
        full_text = str(full_text)

    displayed_text = ""
    for char in full_text:
        displayed_text += char
        story_container.markdown(displayed_text)
        time.sleep(0.01)

    st.session_state.story_text = full_text
    st.session_state.is_typing = False

# ---------- 處理 API 回應的函數 ----------
def process_api_response(response_json):
    if not isinstance(response_json, dict):
        try:
            response_json = json.loads(response_json)
        except:
            return str(response_json)

    if "document" in response_json:
        content = response_json["document"]
    else:
        for key in ["story", "content", "text"]:
            if key in response_json:
                content = response_json[key]
                break
        else:
            content = json.dumps(response_json, ensure_ascii=False)

    if isinstance(content, dict):
        st.session_state.scene = content.get("scene", "")
        st.session_state.affinity = content.get("affinity", st.session_state.affinity)
        return content.get("document", "")

    return content

# ---------- 清理文本函數 ----------
def clean_text(text):
    if not isinstance(text, str):
        try:
            text = json.dumps(text, ensure_ascii=False)
        except:
            text = str(text)
    cleaned = text.replace('{"response": "', '')
    cleaned = cleaned.replace('"}', '')
    cleaned = cleaned.replace('\\"', '"')
    cleaned = cleaned.strip('"')
    return cleaned

# 發送訊息函數
def send_message(user_text):
    if user_text.strip():
        try:
            with st.spinner("思考中..."):
                response = requests.post(
                    API_ENDPOINT,
                    json={"user_input": user_text},
                    headers={"Content-Type": "application/json"}
                )
            if response.status_code == 200:
                result = response.json()
                reply_text = process_api_response(result)
                reply_text = clean_text(reply_text)
                st.session_state.full_response = reply_text
                st.session_state.is_typing = True
            else:
                st.error(f"API 請求失敗: {response.status_code}")
        except Exception as e:
            st.error(f"連接 API 失敗: {str(e)}")

# ---------- 畫面開始 ----------
# 頂部標題 + 好感度
top_container = st.container()
with top_container:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎬 偶像故事開始！")
    with col2:
        st.metric("好感度", st.session_state.affinity)

# 自動送出「開始故事」
if st.session_state.auto_send_flag:
    send_message("開始故事")
    st.session_state.auto_send_flag = False
    st.session_state.first_story_done = True

# 中間故事區域
story_container = st.container()
with story_container:
    if st.session_state.scene:
        st.write(f"**當前場景**: {st.session_state.scene}")
    if st.session_state.is_typing:
        display_text_animation()
    else:
        st.write(st.session_state.story_text)

# 輸入框固定在底部
bottom_input_container = st.container()
with bottom_input_container:
    st.subheader("✏️ 你的回應")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("輸入你的訊息:", key="user_input_field")
    with col2:
        send = st.button("發送")
    
    if send and user_input:
        send_message(user_input)
        st.session_state.user_input = ""  # 重置輸入框
