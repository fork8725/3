# AeroNetB Aerospace 公司数据库设计方案

# 一、标题页

学生姓名：［请填写姓名］

学生ID:［请填写ID］

课程名称：［请填写课程名称］

提交日期：［请填写提交日期］

# 二、项目概述

## 2.1业务定位

AeroNetB Aerospace 是商用飞机关键部件的专业制造商，核心产品涵盖机身部分和机翼组件等高精度航空结构件。为支撑全球化业务布局，公司构建了庞大的全球供应链体系，合作网络中包含数百家专业零件供应商，这些供应商为公司提供各类配套航空零件，所有零件均需严格遵循详细的规格标准与严苛的认证要求，以契合航空工业对安全性与可靠性的极致追求。凭借专业的制造能力，公司服务于全球范围内的飞机制造商及相关航空企业，为其提供符合行业标准的关键部件支持。

## 2.2数据管理现状与挑战

随着业务规模扩张与客户需求多元化，AeroNetB现有的数据管理模式已难以支撑高效运营。当前数据分散存储于legacy系统（如老旧ERP的Oracle数据库）、部门级Excel表格、纸质档案及本地共享文件夹中，形成严重的数据孤岛。这种碎片化管理导致三大核心问题：一是供应链协同滞后，供应商生产进度、零件交付状态等关键信息需人工汇总，常出现生产计划与物料供应脱节；二是质量追溯困难，零件批次信息、检测数据与装配记录无法快速关联，一旦出现质量问题需耗费数天排查源头；三是实时决策缺失，生产设备运行状态、车间产能负荷等数据更新不及时，管理层难以精准调整生产策略。

## 2.3设计目标

本次数据库设计旨在构建一套＂全域数据集成、实时智能响应、安全合规可控”的多模态数据管理体系，设计范围全面覆盖公司核心业务流程，涵盖供应商全生命周期管理（准入、评估、合作记录）、航空零件与组件管理（规格、认证、库存、装配关系）、生产过程管理（订单拆解、任务分配、设备监控）、质量检测管理（检测记录、问题追溯）、交付管理（交付进度、验收结果）。同时，将基于角色的权限管控机制深度融入各业务模块，形成数据驱动的业务管理闭环，彻底解决效率低下、数据重复、可见性不足等问题。

# 三、需求分析

## 3.1功能性需求

### 3.1.1核心业务流程需求

**1．供应商管理**：支持供应商准入申请、资质审核、动态评估全流程管理，需存储供应商认证文件、履约记录、风险评级等数据，实现资质到期自动提醒；

**2．生产管控**：承接客户订单后自动拆解为生产任务，关联所需零件清单与设备资源，实时采集生产进度数据，支持任务优先级调整与异常预警；

**3．质量检测**：记录零件／组件各检测环节的标准参数、实际检测值、检测设备信息，支持不合格品的原因分析与整改跟踪；

**4．库存管理**：实时更新零件库存状态，支持入库、出库、调拨等操作记录，触发最低安全库存预警，关联采购订单实现自动补货；

**5．交付管理**：跟踪交付批次的运输状态、验收结果，存储签收凭证与客户反馈，形成交付全流程档案。

### 3.1.2数据处理需求

·结构化数据：包括客户信息、订单数据、零件规格等，需支持复杂查询、多表关联与事务一致性；

·半结构化数据：如供应商认证证书元数据、生产工艺参数配置等，需支持灵活的字段扩展；

·非结构化数据：设计图纸（CAD格式）、检测影像、合同扫描件等，需实现与业务数据的精准关联与安全存储；

·实时流数据：生产设备运行参数、传感器数据（如温度、转速），采集频率最高达每秒1次，需支持低延迟写入与时间范围查询。

## 3.2非功能性需求

**·性能要求**：结构化数据查询响应时间≤500ms，实时流数据写入吞吐量≥1000条／秒，订单状态更新并发支持≥50用户同时操作；

**·安全要求**：基于岗位角色实现数据访问权限管控，敏感数据（如客户合同金额、供应商报价）加密存储，操作日志留存≥3年；

**·可靠性要求**：数据库系统可用性≥99.9%，数据备份采用＂实时增量＋每日全量＋异地容灾＂策略，故障恢复时间≤1小时；

**·合规要求**：满足航空行业FAA 21 CFR Part 183、EASA CS-25等规范，确保质量数据、认证信息的完整性与可追溯性。

# 四、概念数据模型设计

## 4.1核心实体识别

基于业务流程与数据需求，提取18个核心实体，覆盖供应商、生产、质量、库存等全业务域，核心实体包括：客户（Client）、生产订单（ProductionOrder）、航空零件（AviationPart）、飞机组件（AircraftComponent）、供应商（Supplier）、生产车间（ProductionWorkshop）、物联网设备（loTDevice）、生产任务（ManufacturingTask）、员工（Employee）、质量检测记录（QualitylnspectionRecord）等。

## 4.2实体属性定义

选取关键实体进行属性详细定义，确保属性完整性与业务关联性：

**1．航空零件（AviationPart)**：零件ID(PK）、零件名称、类型（标准件／定制件）、规格型号、材质标准（如TC4钛合金）、精度等级（如IT5）、认证编号、单位重量、单位成本、当前库存、最低安全库存、所属仓库ID(FK）、核心供应商ID(FK）、备用供应商ID列表、生命周期状态（在产／停产／淘汰）、创建时间、更新时间；

**2．生产任务（ManufacturingTask)：**任务ID(PK）、订单ID(FK）、组件ID （FK）、任务类型（加工／组装／检测）、任务状态（待分配／执行中／完成／异常）、分配员工ID(FK）、分配设备ID(FK）、计划开始时间、计划完成时间、实际开始时间、实际完成时间、任务进度、工艺要求、异常描述（若有）；

**3．物联网设备（IoTDevice)**：设备ID(PK）、设备名称、类型（数控机床／三坐标测量仪／温湿度传感器）、所属车间ID(FK）、安装位置、型号规格、制造商、校准周期、实时监控指标、运行状态（在线／离线／故障）、最后校准时间、下次校准提醒时间。

## 4.3实体关系构建

采用ER模型梳理实体间关联关系，明确关系类型与关联依据，核心关系如下：

**1．客户与生产订单**：一对多（1:N)，一个客户可下达多个订单，每个订单归属唯一客户，通过＂客户ID＂关联；

**2．飞机组件与航空零件**：多对多（M:N)，一个组件由多种零件组成，一种零件可用于多个组件，通过“组件零件关联表”存储零件数量、装配工艺等关联信息；

**3．生产订单与生产任务**：一对多（1:N)，一个订单拆解为多个任务，每个任务关联唯一订单；

**4．物联网设备与生产任务**：一对多（1:N)，一台设备可执行多个连续任务，一个任务指定一台设备执行，通过＂设备ID＂关联；

**5．员工与角色权限**：多对一（M:1)，多个员工可拥有同一角色，一个员工对应核心角色，通过＂角色ID＂关联，支持权限叠加。

## 4.4概念ER图

# 五、逻辑数据模型设计

## 5.1数据库选型策略

针对多类型数据特性与业务需求，采用“主从协同”的多数据库架构，各数据库各司其职并通过关联键实现数据一致性：

**1．主数据库：MS** **SQL** Server-存储核心结构化业务数据，如客户、订单、零件、任务等。优势在于支持ACID事务、复杂JOIN查询与严格的数据约束，满足航空制造业务中订单处理、库存更新等事务完整性要求；

**2．从数据库1:**MongoDB-存储半结构化与非结构化数据关联信息，如供应商认证文档元数据、设计图纸属性、检测报告详情等。支持JSON格式与灵活schema，适配数据结构多变的场景，通过“业务ID＂与主库关联；

**3．从数据库2:**InfluxDB-专门存储物联网时序数据，如设备运行参数、传感器采集数据。针对时间戳优化存储与查询性能，支持高吞吐量写入与按时间范围的聚合分析，

为生产监控提供支撑。

## 5.2关系型数据库表结构（MS SQL Server）

基于第三范式设计，消除数据冗余，核心表结构如下（含字段、类型、约束）：

**5.2.1客户表（Client）**

<table border="1" ><tr>
<td>字段名</td>
<td>数据类型</td>
<td>约束</td>
<td>说明</td>
</tr><tr>
<td>ClientID</td>
<td>VARCHAR(30)</td>
<td>PK, NOT NULL, UNIQUE</td>
<td>客户唯一标识，<br>格式＂CL-<br>YYYYMM-XXX"</td>
</tr><tr>
<td>ClientName</td>
<td>VARCHAR(100)</td>
<td>NOT NULL</td>
<td>客户名称（如＂空中客车公司＂）</td>
</tr><tr>
<td>ClientType</td>
<td>VARCHAR(20)</td>
<td>CHECK IN(＇整机厂＇,＇维修厂，<br>运营商＇）</td>
<td>客户类型</td>
</tr><tr>
<td>ContactPerson</td>
<td>VARCHAR(50)</td>
<td>NOT NULL</td>
<td>联系人姓名</td>
</tr><tr>
<td>ContactPhone</td>
<td>VARCHAR(20)</td>
<td>NOT NULL</td>
<td>联系电话</td>
</tr><tr>
<td>Email</td>
<td>VARCHAR(100)</td>
<td>NOT NULL,<br>UNIQUE</td>
<td>电子邮箱</td>
</tr><tr>
<td>CooperationStartDate</td>
<td>DATE</td>
<td>NOT NULL</td>
<td>合作起始日期</td>
</tr><tr>
<td>QualificationLevel</td>
<td>VARCHAR(10)</td>
<td>CHECK IN<br>('S','A','B','C')</td>
<td>资质等级，S 级最高</td>
</tr></table>

**5.2.2生产订单表（ProductionOrder）**

<table border="1" ><tr>
<td>字段名</td>
<td>数据类型</td>
<td>约束</td>
<td>说明</td>
</tr><tr>
<td>OrderID</td>
<td>VARCHAR(30)</td>
<td>PK, NOT NULL,<br>UNIQUE</td>
<td>订单标识，格式"PO-YYYYMM-</td>
</tr><tr>
<td></td>
<td></td>
<td></td>
<td>XXX"</td>
</tr><tr>
<td>ClientID</td>
<td>VARCHAR(30)</td>
<td>FK(Client.ClientID),<br>NOT NULL</td>
<td>关联客户</td>
</tr><tr>
<td>OrderType</td>
<td>VARCHAR(30)</td>
<td>CHECK IN(＇机身组件＇，<br>机翼组件＇,＇定制组件＇）</td>
<td>订单类型</td>
</tr><tr>
<td>OrderStatus</td>
<td>VARCHAR(20)</td>
<td>CHECK IN(＇设计中＇,＇生产中＇,＇检测中＇,＇已交付＇,＇已取消＇）</td>
<td>订单状态</td>
</tr><tr>
<td>OrderTime</td>
<td>DATETIME</td>
<td>NOT NULL, DEFAULT GETDATE()</td>
<td>下单时间</td>
</tr><tr>
<td>RequiredFinishTime</td>
<td>DATETIME</td>
<td>NOT NULL</td>
<td>要求完成时间</td>
</tr><tr>
<td>ActualFinish Time</td>
<td>DATETIME</td>
<td>NULL</td>
<td>实际完成时间<br>（交付后更新）</td>
</tr><tr>
<td>OrderAmount</td>
<td>DECIMAL(18,2)</td>
<td>NOT NULL,<br>CHECK(OrderAmount&gt;0)</td>
<td>订单金额（元）</td>
</tr><tr>
<td>Priority</td>
<td>INT</td>
<td>CHECK(Priority<br>BETWEEN 1 AND 5)</td>
<td>优先级，5 级最高</td>
</tr></table>

**5.2.3多对多关联表示例**

组件零件关联表（ComponentPartRelation)：解决飞机组件与航空零件的多对多关系

<table border="1" ><tr>
<td>字段名</td>
<td>数据类型</td>
<td>约束</td>
<td>说明</td>
</tr><tr>
<td>RelationID</td>
<td>VARCHAR(30)</td>
<td>PK, NOT NULL</td>
<td>关联标识</td>
</tr><tr>
<td>ComponentID</td>
<td>VARCHAR(30)</td>
<td>FK(AircraftComp onent.Componen tID), NOT NULL</td>
<td>关联组件</td>
</tr><tr>
<td>PartID</td>
<td>VARCHAR(30)</td>
<td>FK(AviationPart. PartID), NOT</td>
<td>关联零件</td>
</tr><tr>
<td rowspan="2">RequiredQuantity</td>
<td rowspan="2">INT</td>
<td>NULL</td>
<td rowspan="2">所需零件数量</td>
</tr><tr>
<td>NOT NULL,<br>CHECK(Required Quantity&gt;0)</td>
</tr><tr>
<td>AssemblyPosition</td>
<td>VARCHAR(50)</td>
<td>NOT NULL</td>
<td>装配位置（如＂机翼前缘第3 段＂）</td>
</tr><tr>
<td>ProcessRequirement</td>
<td>VARCHAR(200)</td>
<td>NOT NULL</td>
<td>装配工艺要求</td>
</tr></table>

## 5.3文档型数据库结构（MongoDB）

以JSON文档形式存储半结构化数据，核心集合设计如下：

### 5.3.1供应商集合（Supplier）

json

{

＂id": "SU-2025001",/／对应主库 SupplierID

＂supplierName":＂华航精密制造有限公司”，

"qualificationLevel": "A",

＂country":＂中国＂，

＂address":＂广东省深圳市宝安区航空产业园8号＂，

"contactInfo": {

＂contactPerson":＂李四＂，

"contactPhone": "13900139000",

"email": "lisi@huahang-aero.com"

},

＂corePartTypes":[＂机身连接螺栓＂，“复合材料蒙皮＂]，

＂certifications": [/／嵌入认证信息子文档

{

＂certName": "AS9100航空质量管理体系认证＂，

"certNo": "AS-2025-0012",

"issueDate": "2024-03-05",

"expireDate": "2027-03-04",

＂certFileId": "FR-20250011"/／关联文件资源ID

},

{し

＂certName": "ISO 9001质量管理体系认证＂，

"certNo": "ISO-2025-0036",

"issueDate": "2023-09-12",

"expireDate": "2026-09-11",

"certFileId": "FR-20250012"

}

],

"cooperationData": {

"startDate": "2022-05-20",

＂performanceRate":0.97,/／履约率

"qualityRate": 0.992,

／／质量合格率

"latestCooperationTime": "2025-11-22"

},

＂riskLevel":＂低”，

＂evaluationRecords": ["SE-2025Q3002", "SE-2025Q2003"],/／关联评估记录ID

"createTime": ISODate("2022-05-20T09:30:00Z"),

"updateTime": ISODate("2025-11-22T16:45:00Z")

}

### 5.3.2文件资源集合（FileResource）

json

{

"id": "FR-20250011",

＂businessType": "Supplier",/／关联业务类型

＂businessId":"SU-2025001",/／关联业务ID

＂resourceType":＂认证证书＂，

＂fileName":＂华航精密AS9100认证证书．pdf"，

"fileInfo":{

"format": "PDF",

"sizeKB": 3240,

"storagePath": "https://aeronetb-cloud/files/supplier/cert/SU-20250011AS9100.pdf"

},

"uploadInfo": {

"uploadUserId": "EMP-2025012",

"uploadTime": ISODate("2025-11-22T16:30:00Z"),

"fileVersion": "V1.0"

},

＂description":＂华航精密制造有限公司AS9100认证证书，有效期至2027年3月＂，

＂accessRoles":[＂管理员＂,＂采购专员＂，“质量总监＂]/／允许访问的角色

}

## 5.4时序数据库结构（InfluxDB）

采用＂测量值-标签-字段-时间戳”结构，优化时序数据存储，核心测量值设计：

**5.4.1设备实时数据测量值（IoTRealTimeData）**

<table border="1" ><tr>
<td>组成部分</td>
<td>字段名称</td>
<td>数据类型</td>
<td>说明</td>
</tr><tr>
<td>Measurement</td>
<td>loTRealTimeData</td>
<td>-</td>
<td>测量值名称</td>
</tr><tr>
<td rowspan="3">Tag （索引字段）</td>
<td>DeviceID</td>
<td>字符串</td>
<td>设备唯一标识<br>（对应主库设备<br>ID)</td>
</tr><tr>
<td>DeviceType</td>
<td>字符串</td>
<td>设备类型（如＂数控机床＂）</td>
</tr><tr>
<td>WorkshopID</td>
<td>字符串</td>
<td>所属车间ID （对应主库车间ID ）</td>
</tr><tr>
<td rowspan="4">Field（值字段）</td>
<td>MetricName</td>
<td>字符串</td>
<td>监控指标（如＂转<br>速＂、＂温度”）</td>
</tr><tr>
<td>MetricValue</td>
<td>浮点数</td>
<td>指标数值（如<br>3200.0)</td>
</tr><tr>
<td>Unit</td>
<td>字符串</td>
<td>指标单位（如<br>"rpm"、"C")</td>
</tr><tr>
<td>DataStatus</td>
<td>字符串</td>
<td>数据状态（＂正常＂/＂异常＂）</td>
</tr><tr>
<td>Timestamp</td>
<td>Time</td>
<td>时间戳</td>
<td>采集时间（精确<br>到毫秒）</td>
</tr></table>

数据写入示例：车间ID"WS-02＂、设备ID"loT-015＂的三坐标测量仪，每2秒采集一次数据，MetricName为＂测量精度＂,MetricValue为0.002,Unit为＂mm", DataStatus 为＂正常”，Timestamp为采集时刻。该设计支持快速查询设备在特定时间段的指标变化趋势。

# 六、安全与访问控制设计

## 6.1 RBAC权限体系设计

结合企业组织架构，设计五级角色权限体系，实现数据访问与操作的精细化管控：

<table border="1" ><tr>
<td>角色ID</td>
<td>角色名称</td>
<td>对应岗位</td>
<td>核心权限</td>
</tr><tr>
<td>R-001</td>
<td>系统管理员</td>
<td>IT 运维</td>
<td>全量数据访问；用户／角色管理；系统配置；数据备<br>份恢复</td>
</tr><tr>
<td>R-002</td>
<td>企业高管</td>
<td>总经理、总监</td>
<td>全量业务数据访问；订单／供应商审批；经营报表查<br>看</td>
</tr><tr>
<td>R-003</td>
<td>车间主任</td>
<td>车间负责人</td>
<td>本车间数据访问；任务分<br>配；设备调度；生产计划<br>审批</td>
</tr><tr>
<td>R-004</td>
<td>质检员</td>
<td>质量检测员</td>
<td>检测数据访问；检测记录<br>录入；不合格品上报</td>
</tr><tr>
<td>R-005</td>
<td>一线技工</td>
<td>生产员工</td>
<td>个人任务数据访问；任务<br>状态更新；设备运行数据<br>上报</td>
</tr></table>

## 6.2安全保障机制

**1．数据传输安全**：应用与数据库间通信采用SSL/TLS 1.3加密；物联网设备数据通过MQTT 3.1.1协议加密传输，防止数据被窃取或篡改；

**2．数据存储安全**：MS SQL Server 对敏感字段（如订单金额、供应商报价）采用AES-256加密；MongoDB启用存储加密功能；备份数据采用独立密钥加密，实现＂本地＋异地＂双备份；

**3．操作审计**：设计操作日志表，记录操作人、操作时间、操作内容、IP地址等信息，日志不可篡改，支持按角色、时间范围追溯；

**4．异常监控**：系统实时监控异常行为，如多次密码错误、批量下载敏感数据、异地登录等，触发预警并临时锁定账户，保障数据安全。

# 七、数据集成与实时处理

## 7.1多数据库集成架构

构建＂接入-转换-关联-服务＂四层数据集成架构，实现多类型数据协同：

**1．数据接入层**：结构化数据通过JDBC接入MS SQL Server；半结构化数据通过API接入MongoDB；非结构化数据通过文件上传接口存入云存储，元数据写入MongoDB；物联网数据通过MQTT网关接入InfluxDB；

**2．数据转换层**：采用Talend ETL 工具进行数据清洗，如标准化零件规格单位、过滤设备数据异常值、去重重复订单记录；

**3．数据关联层**：以MS SQL Server的核心业务ID（如 OrderlD、PartID）为关联键，同步至MongoDB与InfluxDB，确保跨库数据一致性；

**4．数据服务层**：封装统一API接口，应用系统通过API调用数据，无需关注数据存储位置，实现“一站式”数据访问。

## 7.2实时数据处理流程

针对物联网设备高频数据，设计“采集-预处理-存储-监控”全流程实时处理方案：

**1．数据采集**：设备按预设频率采集数据，通过Kafka消息队列异步传输，避免数据库直接接入压力；

**2．实时预处理**：采用Flink流处理引擎，实时解析数据格式、检测异常值（如温度超过阈值），将处理后的数据分发给对应数据库；

**3．存储与监控**：正常数据写入InfluxDB，支持实时查询与趋势分析；异常数据触发预警（短信／邮件通知运维人员），同时写入MS SQL Server异常记录表；

4．可视化展示：通过监控大屏实时展示设备运行状态、生产进度等数据，支持钻取查询详细信息。

# 八、实施与维护计划

## 8.1实施阶段划分

**1．需求确认与环境搭建（1个月）**：最终确认业务需求，部署MS SQL Server、MongoDB、InfluxDB环境，配置网络与安全策略；

**2．数据模型落地与开发（2个月）**：创建数据库表与集合，开发数据集成接口、权限管理模块、实时处理引擎；

**3．数据迁移与测试（1个月）**：迁移历史数据至新数据库，进行功能测试、性能测试、安全测试；

**4．上线与培训（2周）**：系统上线试运行，开展员工操作培训，建立运维手册；

**5．运维与优化（长期）**：实时监控系统运行状态，根据业务变化优化数据模型与性能。

## 8.2维护保障措施

·建立7x24小时运维值班制度，快速响应系统故障；

·每月进行一次数据库性能优化，包括索引调整、查询语句优化；

·每季度开展安全审计，检查权限配置与数据加密情况；

·每年根据业务发展需求，迭代更新数据模型与功能模块。

# 九、结论

本次设计的多模态数据库体系，通过MS SQL Server、MongoDB、InfluxDB的协同架构，实现了AeroNetB Aerospace公司结构化、半结构化、实时流数据的统一管理。基于RBAC的权限管控与全流程安全保障机制，确保数据安全合规；高效的数据集成与实时处理能力，解决了传统数据管理中效率低、追溯难、决策滞后的问题。系统上线后，将有力支撑公司供应链协同、生产管控与质量追溯等核心业务，提升市场竞争力，为航空制造业务的数字化转型奠定坚实基础。

