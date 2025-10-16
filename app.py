import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import uuid
import shutil
import plotly.express as px

# ---------- Configuration ----------
DB_PATH = "homework_tracker.db"
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ---------- Database helpers ----------
@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id TEXT PRIMARY KEY,
            subject TEXT,
            title TEXT,
            due_date TEXT,
            status TEXT,
            priority TEXT,
            notes TEXT,
            file_path TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn

conn = get_conn()

# ---------- CRUD functions ----------
def add_assignment(subject, title, due_date, status, priority, notes, file_path):
    aid = str(uuid.uuid4())
    created = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO assignments (id, subject, title, due_date, status, priority, notes, file_path, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (aid, subject, title, due_date, status, priority, notes, file_path, created)
    )
    conn.commit()
    return aid

def update_assignment(aid, **fields):
    set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values())
    values.append(aid)
    conn.execute(f"UPDATE assignments SET {set_clause} WHERE id = ?", values)
    conn.commit()

def delete_assignment(aid):
    cur = conn.execute("SELECT file_path FROM assignments WHERE id = ?", (aid,))
    row = cur.fetchone()
    if row and row[0]:
        try:
            os.remove(row[0])
        except Exception:
            pass
    conn.execute("DELETE FROM assignments WHERE id = ?", (aid,))
    conn.commit()

def fetch_assignments():
    cur = conn.execute("SELECT id, subject, title, due_date, status, priority, notes, file_path, created_at FROM assignments")
    rows = cur.fetchall()
    cols = ["id", "subject", "title", "due_date", "status", "priority", "notes", "file_path", "created_at"]
    df = pd.DataFrame(rows, columns=cols)
    if not df.empty:
        df["due_date"] = pd.to_datetime(df["due_date"])
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df

# ---------- UI setup ----------
st.set_page_config(page_title="作業追蹤器", layout="wide")

# 導覽區
st.title("📚 作業追蹤器 Homework Tracker")
st.info("這是一個幫助學生記錄與追蹤作業進度的應用程式。你可以：\n- 新增每一科作業\n- 標記狀態（待完成 / 進行中 / 已完成）\n- 上傳附件（如照片或 PDF）\n- 查看統計圖表\n- 匯出紀錄與檔案備份")

# ---------- Sidebar：新增作業 ----------
with st.sidebar.expander("✚ 新增作業", expanded=True):
    st.subheader("新增一筆作業")
    with st.form("add_form"):
        subject = st.text_input("科目")
        title = st.text_input("標題 / 題目")
        due_date = st.date_input("截止日期", value=datetime.now().date())
        status = st.selectbox("狀態", ["Pending", "In Progress", "Completed"])
        priority = st.selectbox("優先度", ["Low", "Medium", "High"])
        notes = st.text_area("備註（可選）")
        uploaded_file = st.file_uploader("上傳作業檔案（可選）", type=["png","jpg","jpeg","pdf","txt"], accept_multiple_files=False)
        submitted = st.form_submit_button("新增作業")
        if submitted:
            file_path = None
            if uploaded_file is not None:
                filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                dest = os.path.join(UPLOADS_DIR, filename)
                with open(dest, "wb") as f:
                    shutil.copyfileobj(uploaded_file, f)
                file_path = dest
            add_assignment(subject, title, due_date.isoformat(), status, priority, notes, file_path)
            st.success("✅ 新增成功！")

# ---------- Main：作業表格 ----------
df = fetch_assignments()

if df.empty:
    st.warning("目前沒有任何作業，請從側邊欄新增一筆。")
else:
    st.subheader("📋 所有作業清單")
    df_display = df.copy()
    df_display["due_date"] = df_display["due_date"].dt.strftime("%Y-%m-%d")
    st.dataframe(df_display[["subject", "title", "due_date", "status", "priority", "notes"]], use_container_width=True)

    st.markdown("---")
    st.subheader("📊 作業統計圖表")

    # 統計圖：各狀態數量
    status_chart = df.groupby("status").size().reset_index(name="count")
    fig1 = px.bar(status_chart, x="status", y="count", color="status", title="作業狀態分佈")
    st.plotly_chart(fig1, use_container_width=True)

    # 統計圖：各科目未完成數
    subject_chart = df[df["status"] != "Completed"].groupby("subject").size().reset_index(name="count")
    if not subject_chart.empty:
        fig2 = px.pie(subject_chart, names="subject", values="count", title="各科未完成作業比例")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("💾 提示：請定期備份 homework_tracker.db 和 uploads 資料夾以保護你的作業資料。")
