import os
import asyncio
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_generic_api_key_here":
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# -----------------
# 1. DB Setup & Models
# -----------------
DATABASE_URL = "sqlite:///./chatbot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class ChatSession(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String)  # 'user', 'assistant', 'system'
    content = Column(String)
    media_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key = Column(String)
    value = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------
# 2. FastAPI Initialization
# -----------------
app = FastAPI(title="Antigravity Chatbot")

if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

app.mount("/static", StaticFiles(directory="static"), name="static")

# If templates dir doesn't exist, this line could fail, but our frontend file is generated via LLM so it's fine.
templates = Jinja2Templates(directory="templates")

# Global dict to hold stop events for streaming control
stop_events = {}

# -----------------
# 3. Core Logic & API
# -----------------

@app.on_event("startup")
def startup_db():
    # Insert default test user 'Antigravity' during startup
    db = SessionLocal()
    user = db.query(User).filter(User.username == "Antigravity").first()
    if not user:
        user = User(username="Antigravity")
        db.add(user)
        db.commit()
    db.close()

def get_current_user(db: Session = Depends(get_db)):
    return db.query(User).filter(User.username == "Antigravity").first()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/sessions")
def get_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """獲取特定使用者的所有聊天室"""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return [{"id": s.id, "title": s.title} for s in sessions]

@app.post("/api/sessions")
def create_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """新建一個對話室"""
    new_session = ChatSession(user_id=current_user.id, title="New Conversation")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"id": new_session.id, "title": new_session.title}

@app.get("/api/sessions/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    """獲取該聊天室的所有歷史訊息"""
    msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return [{"id": m.id, "role": m.role, "content": m.content, "media_path": m.media_path} for m in msgs]


class ChatRequest(BaseModel):
    session_id: int
    content: str
    media_path: Optional[str] = None

@app.post("/api/chat")
async def chat(request: Request, chat_req: ChatRequest, db: Session = Depends(get_db)):
    """對話邏輯 (實作 SSE Chunked Streaming)"""
    
    # 1. 儲存使用者送來的對話
    user_msg = Message(session_id=chat_req.session_id, role="user", content=chat_req.content, media_path=chat_req.media_path)
    db.add(user_msg)
    db.commit()
    
    # 2. 修改標題（若為第一個對話區）
    session = db.query(ChatSession).filter(ChatSession.id == chat_req.session_id).first()
    if session and session.title == "New Conversation":
        session.title = chat_req.content[:15] + "..."
        db.commit()
        
    # 3. 預留 Assistant 的位置
    ai_msg = Message(session_id=chat_req.session_id, role="assistant", content="")
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    # 4. 準備 Streaming 邏輯與終止控制
    stop_event = asyncio.Event()
    stop_events[chat_req.session_id] = stop_event

    async def event_generator():
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_generic_api_key_here":
            msg = f"[提示] 目前尚未填寫您的 GEMINI_API_KEY 於 `.env` 中，所以系統仍為模擬模式喔！請至本機的 .env 檔案更換 API 金鑰即可啟動真正的 AI！\n\n您說了：{chat_req.content}"
            db_conn = SessionLocal()
            final_msg = db_conn.query(Message).filter(Message.id == ai_msg.id).first()
            if final_msg:
                final_msg.content = msg
                db_conn.commit()
            db_conn.close()
            for char in msg:
                if stop_event.is_set(): break
                yield f"data: {'<br>' if char == '\\n' else char}\n\n"
                await asyncio.sleep(0.02)
            yield "data: [DONE]\n\n"
            return

        db_conn = SessionLocal()
        history_msgs = db_conn.query(Message).filter(Message.session_id == chat_req.session_id).order_by(Message.created_at.asc()).all()
        # 準備給模型的對話格式
        gemini_history = []
        for m in history_msgs[:-2]: # 去除剛新增的一對空白
            role = "user" if m.role == "user" else "model"
            if m.content and m.content.strip():
                gemini_history.append({"role": role, "parts": [m.content]})
        db_conn.close()

        # 執行 LLM
        model = genai.GenerativeModel("gemini-2.5-flash")
        chat_session = model.start_chat()
        if gemini_history:
            try:
                chat_session = model.start_chat(history=gemini_history)
            except:
                chat_session = model.start_chat()
        
        prompt = chat_req.content
        if chat_req.media_path:
            prompt += f"\n[使用者有附加上傳檔案，路徑為: {chat_req.media_path}]"

        full_response = ""
        try:
            response = chat_session.send_message(prompt, stream=True)
            for chunk in response:
                if stop_event.is_set():
                    full_response += " [(系統) 生成已由使用者中止]"
                    yield f"data: [(系統) 生成已由使用者中止]\n\n"
                    break
                if chunk.text:
                    full_response += chunk.text
                    chunk_text = chunk.text.replace("\n", "<br>")
                    yield f"data: {chunk_text}\n\n"
                    await asyncio.sleep(0.01)
        except Exception as e:
            full_response = f"API 發生錯誤：{str(e)}"
            yield f"data: {full_response}\n\n"
            
        # 儲存
        db_conn = SessionLocal()
        final_msg = db_conn.query(Message).filter(Message.id == ai_msg.id).first()
        if final_msg:
            final_msg.content = full_response
            db_conn.commit()
        db_conn.close()
        
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/chat/stop/{session_id}")
async def stop_chat(session_id: int):
    """使用者點擊停止按鈕時呼叫：觸發 stop_event 使迴圈中斷"""
    if session_id in stop_events:
        stop_events[session_id].set()
    return {"status": "stopped"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """處理多模態檔案上傳，存入 static 資料夾並回傳路徑"""
    file_location = f"static/uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"filename": file.filename, "path": f"/{file_location}"}
