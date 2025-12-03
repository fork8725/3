from fastapi import FastAPI, Depends, HTTPException, Request, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal, Any
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone, date

# Import models
from models import Base, User, Client, ProductionOrder, ComponentPartRelation

# Auth settings
SECRET_KEY = "change-this-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Database setup (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed an admin user if none exists
with SessionLocal() as db:
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        hashed = pwd_context.hash("admin123")
        admin = User(username="admin", hashed_password=hashed, role="admin")
        db.add(admin)
        db.commit()

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UserRead(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True

# 5.2.1 Client schemas and CRUD
class ClientCreate(BaseModel):
    clientid: str = Field(min_length=1, max_length=30)
    clientname: str = Field(min_length=1, max_length=100)
    clienttype: Literal['整机厂','维修厂','运营商']
    contactperson: str = Field(min_length=1, max_length=50)
    contactphone: str = Field(min_length=1, max_length=20)
    email: EmailStr
    cooperationstartdate: date
    qualificationlevel: Literal['S','A','B','C'] = 'C'

class ClientRead(BaseModel):
    clientid: str
    clientname: str
    clienttype: str
    contactperson: str
    contactphone: str
    email: EmailStr
    cooperationstartdate: date
    qualificationlevel: str
    class Config:
        from_attributes = True

# 5.2.2 ProductionOrder schemas and CRUD
class ProductionOrderCreate(BaseModel):
    orderid: str = Field(min_length=1, max_length=30)
    clientid: str = Field(min_length=1, max_length=30)
    ordertype: Literal['机身组件','机翼组件','定制组件']
    orderstatus: Literal['设计中','生产中','检测中','已交付','已取消']
    ordertime: Optional[datetime] = None
    requiredfinishtime: datetime
    actualfinishtime: Optional[datetime] = None
    orderamount: float = Field(gt=0)
    priority: int = Field(ge=1, le=5, default=3)

class ProductionOrderRead(BaseModel):
    orderid: str
    clientid: str
    ordertype: str
    orderstatus: str
    ordertime: datetime
    requiredfinishtime: datetime
    actualfinishtime: Optional[datetime]
    orderamount: float
    priority: int
    class Config:
        from_attributes = True

# 5.2.3 ComponentPartRelation schemas and CRUD
class ComponentPartRelationCreate(BaseModel):
    relationid: str = Field(min_length=1, max_length=30)
    componentid: str = Field(min_length=1, max_length=30)
    partid: str = Field(min_length=1, max_length=30)
    requiredquantity: int = Field(gt=0)
    assemblyposition: str = Field(min_length=1, max_length=50)
    processrequirement: str = Field(min_length=1, max_length=200)

class ComponentPartRelationRead(BaseModel):
    relationid: str
    componentid: str
    partid: str
    requiredquantity: int
    assemblyposition: str
    processrequirement: str
    class Config:
        from_attributes = True

app = FastAPI()

# Mount static files and set up templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_model=dict)
async def root():
    return {"message": "Hello World"}

# Auth helpers
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Any:
    token = (authorization or "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(user: Any = Depends(get_current_user)) -> Any:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return current

# Dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/clients", response_model=ClientRead, status_code=201)
def create_client(payload: ClientCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(Client).filter(Client.clientid == payload.clientid).first():
        raise HTTPException(status_code=400, detail="clientid already exists")
    if db.query(Client).filter(Client.email == payload.email).first():
        raise HTTPException(status_code=400, detail="email already exists")
    c = Client(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@app.get("/clients", response_model=List[ClientRead])
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).order_by(Client.clientname.asc()).all()

@app.get("/clients/{clientid}", response_model=ClientRead)
def get_client(clientid: str, db: Session = Depends(get_db)):
    c = db.query(Client).filter(Client.clientid == clientid).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    return c

@app.delete("/clients/{clientid}", status_code=204)
def delete_client(clientid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    c = db.query(Client).filter(Client.clientid == clientid).first()
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(c)
    db.commit()
    return None

@app.post("/production-orders", response_model=ProductionOrderRead, status_code=201)
def create_production_order(payload: ProductionOrderCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(ProductionOrder).filter(ProductionOrder.orderid == payload.orderid).first():
        raise HTTPException(status_code=400, detail="orderid already exists")
    # FK check
    if not db.query(Client).filter(Client.clientid == payload.clientid).first():
        raise HTTPException(status_code=400, detail="clientid not found")
    ordertime = payload.ordertime or datetime.now(timezone.utc)
    po = ProductionOrder(
        orderid=payload.orderid,
        clientid=payload.clientid,
        ordertype=payload.ordertype,
        orderstatus=payload.orderstatus,
        ordertime=ordertime,
        requiredfinishtime=payload.requiredfinishtime,
        actualfinishtime=payload.actualfinishtime,
        orderamount=payload.orderamount,
        priority=payload.priority,
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po

@app.get("/production-orders", response_model=List[ProductionOrderRead])
def list_production_orders(db: Session = Depends(get_db)):
    return db.query(ProductionOrder).order_by(ProductionOrder.ordertime.desc()).all()

@app.get("/production-orders/{orderid}", response_model=ProductionOrderRead)
def get_production_order(orderid: str, db: Session = Depends(get_db)):
    po = db.query(ProductionOrder).filter(ProductionOrder.orderid == orderid).first()
    if not po:
        raise HTTPException(status_code=404, detail="ProductionOrder not found")
    return po

@app.delete("/production-orders/{orderid}", status_code=204)
def delete_production_order(orderid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    po = db.query(ProductionOrder).filter(ProductionOrder.orderid == orderid).first()
    if not po:
        raise HTTPException(status_code=404, detail="ProductionOrder not found")
    db.delete(po)
    db.commit()
    return None

@app.post("/component-part-relations", response_model=ComponentPartRelationRead, status_code=201)
def create_component_part_relation(payload: ComponentPartRelationCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(ComponentPartRelation).filter(ComponentPartRelation.relationid == payload.relationid).first():
        raise HTTPException(status_code=400, detail="relationid already exists")
    cpr = ComponentPartRelation(**payload.model_dump())
    db.add(cpr)
    db.commit()
    db.refresh(cpr)
    return cpr

@app.get("/component-part-relations", response_model=List[ComponentPartRelationRead])
def list_component_part_relations(db: Session = Depends(get_db)):
    return db.query(ComponentPartRelation).order_by(ComponentPartRelation.relationid.asc()).all()

@app.get("/component-part-relations/{relationid}", response_model=ComponentPartRelationRead)
def get_component_part_relation(relationid: str, db: Session = Depends(get_db)):
    cpr = db.query(ComponentPartRelation).filter(ComponentPartRelation.relationid == relationid).first()
    if not cpr:
        raise HTTPException(status_code=404, detail="ComponentPartRelation not found")
    return cpr

@app.delete("/component-part-relations/{relationid}", status_code=204)
def delete_component_part_relation(relationid: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    cpr = db.query(ComponentPartRelation).filter(ComponentPartRelation.relationid == relationid).first()
    if not cpr:
        raise HTTPException(status_code=404, detail="ComponentPartRelation not found")
    db.delete(cpr)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
