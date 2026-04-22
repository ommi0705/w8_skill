import os
import asyncio
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
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
    return templates.TemplateResponse("index.html", {"request": request})

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
        # -- 核心邏輯模擬 --
        # 如果是真實串接，這邊將會呼叫 OpenAI 或 Gemini API 的 .stream()
        
        reply_base = f"我已收到您的訊息：「{chat_req.content}」。在這模擬模式中，我正在逐字產生回應... 這裡已經串接好工具使用架構與檔案處理。"
        if chat_req.media_path:
            reply_base += f"\n\n[系統通知] 發現您夾帶的文件/圖片：「{chat_req.media_path}」，我已能存取。"
            
        full_response = ""
        # 逐字輸出模擬
        for char in reply_base:
            if stop_event.is_set():
                full_response += " [(系統) 生成已由使用者中止]"
                yield f"data:  [(系統) 生成已由使用者中止]\n\n"
                break
            
            full_response += char
            yield f"data: {char}\n\n"
            await asyncio.sleep(0.04) # 模擬打字延遲
            
        # 生成完畢後，把完整句子寫回資料庫
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
