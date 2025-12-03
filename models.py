# // filepath: c:\Users\W\Desktop\py\6\models.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, DECIMAL, CheckConstraint, ForeignKey, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")

# 5.2.1 Client table
class Client(Base):
    __tablename__ = "client"
    clientid = Column(String(30), primary_key=True, nullable=False, unique=True)
    clientname = Column(String(100), nullable=False)
    clienttype = Column(String(20), nullable=False)
    contactperson = Column(String(50), nullable=False)
    contactphone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    cooperationstartdate = Column(Date, nullable=False)
    qualificationlevel = Column(String(10), nullable=False, default='C')

    __table_args__ = (
        CheckConstraint("clienttype IN ('整机厂','维修厂','运营商')", name="chk_clienttype"),
        CheckConstraint("qualificationlevel IN ('S','A','B','C')", name="chk_qualificationlevel"),
    )

# 5.2.2 ProductionOrder table
class ProductionOrder(Base):
    __tablename__ = "productionorder"
    orderid = Column(String(30), primary_key=True, nullable=False, unique=True)
    clientid = Column(String(30), ForeignKey("client.clientid"), nullable=False)
    ordertype = Column(String(30), nullable=False)
    orderstatus = Column(String(20), nullable=False)
    ordertime = Column(TIMESTAMP, nullable=False)
    requiredfinishtime = Column(TIMESTAMP, nullable=False)
    actualfinishtime = Column(TIMESTAMP, nullable=True)
    orderamount = Column(DECIMAL(18, 2), nullable=False)
    priority = Column(Integer, nullable=False, default=3)

    __table_args__ = (
        CheckConstraint("ordertype IN ('机身组件','机翼组件','定制组件')", name="chk_ordertype"),
        CheckConstraint("orderstatus IN ('设计中','生产中','检测中','已交付','已取消')", name="chk_orderstatus"),
        CheckConstraint("orderamount > 0", name="chk_orderamount_positive"),
        CheckConstraint("priority BETWEEN 1 AND 5", name="chk_priority_range"),
    )

# 5.2.3 ComponentPartRelation table (example M:N)
class ComponentPartRelation(Base):
    __tablename__ = "componentpartrelation"
    relationid = Column(String(30), primary_key=True, nullable=False)
    componentid = Column(String(30), nullable=False)
    partid = Column(String(30), nullable=False)
    requiredquantity = Column(Integer, nullable=False)
    assemblyposition = Column(String(50), nullable=False)
    processrequirement = Column(String(200), nullable=False)

    __table_args__ = (
        CheckConstraint("requiredquantity > 0", name="chk_requiredquantity_positive"),
    )
