#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a local, offline, evidence-linked ZIP catalog. No package execution."""
import collections
import csv
import html
import json
import re
import hashlib
from pathlib import Path
from taxonomy import refine

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tools/catalog/generated'

# Chinese navigation labels are editorial aids; exact capabilities remain tied
# to the source manifest and skill descriptions shown alongside them.
THEMES = [
('财务与投资', '总账、月结与对账', r'\b(bookkeep\w*|accounting|reconcil\w*|general ledger|month.end|trial balance|quickbooks|netsuite|superbooks|robosystems|granatum|gl-reconciler|statutory reporting)\b', '围绕账务、总账、月结或对账工作提供指导或服务连接'),
('财务与投资', '发票与收付款', r'\b(invoice\w*|invoic\w*|billing|payment\w*|paypal|stripe|airwallex|paymob|yofacturo|waybill)\b', '围绕发票、账单、支付或收付款业务提供操作能力或集成指南'),
('财务与投资', '财务模型、估值与尽调', r'\b(valuation|dcf|lbo|cap table|due diligence|investment.banking|financial model\w*|model-builder|npv|qoe|financial advisors?)\b', '支持财务模型、估值、交易材料或尽职调查相关工作'),
('财务与投资', '金融行情与公司研究', r'\b(financial data|financial analysis|financial statements?|market data|stock\w*|equities|bonds?|yield curves?|investment|portfolio\w*|morningstar|lseg|eodhd|economic mind|privco|wealthstoryline|boersi|financ\w*)\b', '围绕金融数据、企业财务、市场或投资主题提供资料、分析流程或服务连接'),
('财务与投资', '云成本与资源费用', r'\b(finops|cloud cost\w*|azure subscription cost|cloud spend|doit cloud|amg-toolkit)\b', '支持云资源费用分析、成本监测或资源优化相关工作'),
('数据、数据库与BI', 'Excel、表格与办公计算', r'\b(excel|spreadsheets?|workbooks?|handsontable|hyperformula|worker k)\b', '支持表格处理、工作簿操作、计算或办公数据自动化'),
('数据、数据库与BI', '数据目录、血缘与质量', r'\b(datahub|atlan|informatica|data catalog|lineage|data quality|data governance|pipeline reconcile)\b', '支持查找数据资产、理解字段和血缘、检查数据质量或管理业务术语'),
('数据、数据库与BI', 'SQL、数据库与数仓', r'\b(sql|databases?|warehouse\w*|duckdb|snowflake|bigquery|postgres\w*|mysql|mongodb|redis|sqlite|clickhouse|databricks|supabase|planetscale|alloydb|aiven|whodb)\b', '支持数据库查询、数据探查、SQL 开发或数据平台集成'),
('数据、数据库与BI', '数据管道与转换', r'\b(dbt|etl|elt|data pipeline\w*|data engineering|fivetran|airbyte|spark|kafka|airflow|dagster|prefect|kestra)\b', '支持数据转换、管道开发、连接器或任务编排'),
('数据、数据库与BI', 'BI、图表与看板', r'\b(tableau|power.?bi|superset|preset|dashboards?|visualization|visualisation|chart\w*|plot\w*)\b', '围绕 BI、图表或看板提供分析展示和管理流程'),
('数据、数据库与BI', '数据分析与预测', r'\b(analytics|data analysis|forecast\w*|statistics|statistical|eda|jupyter|demand-insight|machine.learning)\b', '支持数据分析、指标解释、统计建模或预测流程'),
('销售、营销与电商', 'CRM、客户与销售', r'\b(crm|salesforce|hubspot|pipedrive|sales enablement|sales intelligence|lead\w*|prospecting|customer success|customer support|zendesk|intercom|freshdesk|freshsales|gong|zocks)\b', '支持客户资料查询、线索管理、销售跟进或客户服务'),
('销售、营销与电商', '广告投放与优化', r'\b(advertis\w*|google ads|meta ads|amazon ads|campaign\w*|adspirer|adwhispr|advisorppc|adology|adlane|adplane|scaleskus|ryze|ppc)\b', '支持广告研究、账户分析、投放管理或广告效果优化'),
('销售、营销与电商', 'SEO与搜索可见度', r'\b(seo|aeo|geo|search engine|search console|search visibility|keyword research|semrush|ahrefs|serp\w*)\b', '支持搜索优化、关键词研究、网站检查或品牌在 AI 搜索中的可见度分析'),
('销售、营销与电商', '社交媒体与内容运营', r'\b(social media|social content|social post\w*|instagram|tiktok|linkedin|facebook|pinterest|bluesky|adaptlypost|8digit planner|ayrshare|hootsuite|buffer)\b', '支持社交内容策划、排期、发布流程或效果分析'),
('销售、营销与电商', '电商、订单与商品', r'\b(e.commerce|ecommerce|shopify|woocommerce|selling partner|merchant|storefront|inventory|fulfillment|marketplace|etsy|amazon selling)\b', '支持商品、订单、库存、店铺或电商业务流程'),
('产品、设计与创作', '产品规划与用户研究', r'\b(product discovery|product management|prd|productboard|user research|ux research|product strategy|roadmap|pragmatic pm|agile product|stride.ideation)\b', '支持产品需求、产品策略、路线图或用户研究相关工作'),
('产品、设计与创作', 'UI、UX与设计系统', r'\b(figma|penpot|design system|ui design|ux|user interface|design tokens?|component library|accessibility|a11y|gemdesign)\b', '支持界面设计、设计系统、组件规范或体验检查'),
('产品、设计与创作', '图片、视频与动画', r'\b(images?|video\w*|animation\w*|creative cloud|adobe|canva|render\w*|illustrat\w*|photograph\w*|background removal|anidoodle|apiai|pixinsight)\b', '支持图片、视频、动画或视觉素材的创作和处理'),
('产品、设计与创作', '音频、音乐与语音', r'\b(audio|music|speech|voice|podcast\w*|sound\w*|elevenlabs|suno|transcrib\w*|transcription)\b', '支持音频、音乐、语音或转录相关工作'),
('文档、知识与办公', '文档、PDF与电子签名', r'\b(pdf|docx|word processing|documents?|contracts?|e.signature|esign|signing|formify|pandadoc|docusign|devexpress)\b', '支持文档阅读和生成、PDF 处理、合同或签名流程'),
('文档、知识与办公', '演示文稿与汇报', r'\b(slides?|presentations?|powerpoint|pptx|decks?|marp|slidev|arcdeck)\b', '支持演示文稿、汇报材料或幻灯片相关工作'),
('文档、知识与办公', '知识库、笔记与搜索', r'\b(knowledge base|knowledge graph|semantic search|obsidian|notion|wiki|notes?|knowmine|agent archive|alexandria|wikipedia)\b', '支持知识整理、笔记保存、知识库检索或资料归档'),
('文档、知识与办公', '邮件、日历与会议', r'\b(email|gmail|outlook|calendar|meeting\w*|scheduling|office.365|microsoft.365|google workspace|slack|teams|agentmail|higgs hub|anson)\b', '支持邮件、日程、会议准备、纪要或协作平台操作'),
('文档、知识与办公', '任务、项目与流程', r'\b(project management|task management|asana|trello|clickup|monday|jira|confluence|linear|todo\w*|workflow automation|n8n|zapier|make\.com)\b', '支持任务、项目、协作事项或跨应用流程管理'),
('AI与智能体', '记忆、上下文与会话交接', r'\b(memory|memories|context|handoff|recall|token budget|tokenbudget|token inspector|ai passport|anamnese|anchor-memory|active memory|adaptive agent)\b', '支持保存会话信息、管理上下文、检索历史或交接 AI 工作'),
('AI与智能体', '智能体设计、编排与集成', r'\b(agents?|agentic|ag2|multi.agent|orchestrat\w*|mcp servers?|mcp connector|integration|rag|langchain|llamaindex|agentforce|ai employees|soulz)\b', '支持智能体设计、工作流编排、工具连接或 AI 系统集成'),
('AI与智能体', '提示词、评测与可观测性', r'\b(prompts?|evaluat\w*|deepeval|langfuse|langsmith|tracing|llm engineering|benchmark\w*|arize|braintrust|helicone|phoenix)\b', '支持提示词管理、AI 评测、运行追踪或效果改进'),
('AI与智能体', 'AI工具配置与使用', r'\b(claude|codex|cursor|gemini|copilot|ai adoption|ai mentor|statusline|statusbar|ai-hp|claude meter)\b', '支持 AI 工具配置、使用方法或开发助手工作流程'),
('软件开发与测试', '架构、需求与工程流程', r'\b(architecture|architect\w*|sdlc|engineering|superpowers|protocol\w*|design review|specification|spec-driven|shipwright|takshak|10x-team|cto-toolkit|backend design)\b', '支持软件架构、需求拆解、开发规范或工程交付流程'),
('软件开发与测试', '代码审查、调试与测试', r'\b(code review|review\w*|debug\w*|test\w*|qa|playwright|cypress|selenium|coverage|critique|agile merge|agile sprint)\b', '支持代码审查、故障排查、自动化测试或质量验证'),
('软件开发与测试', 'Git、PR与协作开发', r'\b(github|gitlab|bitbucket|git |pull request\w*|merge request\w*|rebase|worktree\w*|commit\w*|buildkite)\b', '支持代码仓库、分支、PR 或协作开发流程'),
('软件开发与测试', '前端、移动端与应用开发', r'\b(react|vue|angular|svelte|nextjs|next.js|frontend|front.end|swift|ios|android|flutter|react native|slint|mobile|capacitor|unity|unreal|game\w*)\b', '支持前端、移动端、桌面应用或游戏开发相关工作'),
('软件开发与测试', '后端、API与SDK', r'\b(api|sdk|backend|back.end|python|typescript|javascript|node.js|rust|golang| go |java|\.net|spring|fastapi|django|rails|laravel|watermill)\b', '支持后端、接口、SDK 或特定编程语言的开发与集成'),
('云平台、运维与安全', '安全、身份与合规', r'\b(security|compliance|vulnerabilit\w*|secrets?|identity|authentication|authorization|oauth|oidc|auth0|1password|ar[m]?o ctrl|aikido|42crunch|above security|governance|governor)\b', '支持安全检查、身份认证、访问控制或合规相关工作'),
('云平台、运维与安全', '云平台、部署与基础设施', r'\b(cloud|aws|azure|gcp|google cloud|oci|oracle|deployment|deploy\w*|devops|kubernetes|docker|terraform|infrastructure|ci/cd|vercel|netlify|upbound)\b', '支持云平台、基础设施配置、部署或运维自动化'),
('云平台、运维与安全', '监控、日志与故障诊断', r'\b(monitor\w*|observability|incidents?|telemetry|logs?|grafana|datadog|sentry|new relic|sumo.?logic|pagerduty|root cause)\b', '支持系统监控、日志查询、告警或故障诊断'),
('行业、研究与生活', '法规、法律与公共部门', r'\b(legal|law\w*|regulatory|regulation\w*|government|public sector|arckit|ansvar|lexis|westlaw|gdpr|nis2)\b', '提供法律、监管、公共部门或行业规范相关资料和流程'),
('行业、研究与生活', '医药、医疗与生命科学', r'\b(healthcare|medical|clinical|trials?|drug\w*|biotech|fhir|adisinsight|phasefolio|anamnese core|nhs)\b', '支持医药研发、医疗数据、临床研究或生命科学资料工作'),
('行业、研究与生活', '学术、研究与学习', r'\b(research|scholar\w*|papers?|academic|thesis|learning|study|education|teach\w*|coach|adplist|adhd|wiley|springer|pubmed)\b', '支持资料研究、学术检索、学习辅导或课程相关工作'),
('行业、研究与生活', '人力、招聘与薪酬', r'\b(hr|human resources|recruit\w*|hiring|payroll|employee\w*|remote.com|workday|bamboohr|people management)\b', '支持人员管理、招聘、薪酬或员工事务相关工作'),
('行业、研究与生活', '供应链、物流与制造', r'\b(supply chain|logistics|manufactur\w*|procurement|shipping|waybill|metafloor|cargo|warehouse management)\b', '支持采购、供应链、物流或制造业务流程'),
('行业、研究与生活', '区块链与数字资产', r'\b(blockchain|crypto\w*|web3|ethereum|solana|on.chain|defi|allium|coin\w*|tres finance)\b', '支持链上数据查询、数字资产或区块链应用工作'),
('行业、研究与生活', '旅游、地图与个人生活', r'\b(travel|airport|lounges?|flights?|hotel\w*|maps?|geospatial|geocod\w*|location service|personal|life edit|planner|restaurant\w*|booking|reservation)\b', '支持旅行、地图、预约或个人生活规划相关工作'),
]

OVERRIDES = {
'aiplus_finance_codex_pack_2026-09-30': ('财务与投资','财务工具产品设计','规划 12 个财务业务分类和 1 个通用数据区，共 64 款独立工具候选；列出输入、输出、规则、参考来源，并给出 D02 双表核对助手的需求、验收与 Codex 启动任务。只有研究和设计资料，未包含实现应用。'),
'duckdb-skills': ('数据、数据库与BI','本地数据读取与SQL','读取 CSV、JSON、Parquet 等数据文件，挂接和查询 DuckDB 数据库，查找 DuckDB／DuckLake 文档及历史会话，并安装或更新扩展。'),
'atlan': ('数据、数据库与BI','数据目录与血缘','通过 Atlan 服务搜索和探查数据资产、追踪血缘、管理业务术语和数据质量规则，为理解企业数据提供上下文。'),
'datahub cloud': ('数据、数据库与BI','数据目录与血缘','通过 DataHub Cloud 检索数据目录、追踪血缘、检查数据质量，并依据实际元数据编写 SQL。'),
'informatica': ('数据、数据库与BI','企业数据治理','通过 Informatica 数据目录与治理能力发现、探索、丰富和管理数据资产，支持遵守治理边界的数据问答。'),
'intuit quickbooks': ('财务与投资','会计与经营分析','围绕 QuickBooks 提供财务健康简报、行业对标、发票、工资和融资相关技能；通常需要连接相应业务账户。'),
'morningstar': ('财务与投资','金融数据与投资研究','通过 Morningstar MCP 服务使用晨星专有数据和研究资料，支持财务与投资分析。'),
'eodhd financial data apis': ('财务与投资','金融行情数据','通过 EODHD API／MCP 获取证券价格、历史行情、基本面、期权、技术指标、新闻、情绪、宏观指标和 ESG 等数据。覆盖规模为包内作者描述，未实时核实。'),
'lseg': ('财务与投资','债券、外汇与衍生品分析','使用 LSEG 金融数据开展债券定价、收益率曲线分析、外汇套息交易分析、期权估值和宏观看板工作。'),
'bankstatemently': ('财务与投资','银行流水结构化','把 PDF 银行对账单中的交易、账户和余额提取为结构化数据，再对已上传的多份对账单进行查询分析。'),
'cashflow': ('财务与投资','个人现金流与记账','通过 Plaid 连接银行账户，查询支出、跟踪周期性账单、分类交易并生成个人财务回顾。'),
'found': ('财务与投资','银行、记账与月结','读取 Found 业务银行和账簿数据，查看余额、导出交易、辅助月结与账户对账、查看损益及未付发票；包内声明为只读。'),
'gl-reconciler': ('财务与投资','总账对账','发现对账差异、追踪根因，并把需要签核的问题提交到相应审核流程。具体输入和操作步骤以包内技能说明为准。'),
'model-builder': ('财务与投资','Excel财务建模','围绕 Excel 中的 DCF、LBO、三表联动和可比公司分析提供财务建模技能。'),
'valuation-reviewer': ('财务与投资','估值复核与LP报告','接收 GP 提供的资料包、运行估值模板，并准备面向 LP 的报告材料。'),
'netsuite finance analyst': ('财务与投资','NetSuite财务分析','基于实时 NetSuite 数据提供财务管理分析工作流；是否可直接使用取决于连接器和账户权限。'),
'netsuite ai companion': ('财务与投资','NetSuite连接器使用指南','指导 AI 助手正确使用 NetSuite AI Connector，理解工具和业务操作的使用方法。'),
'airwallex agentos': ('财务与投资','跨币种资金与付款业务','连接 Airwallex 账户，围绕采购订单开票、供应商入驻和跨币种资金余额查询等工作提供预置财务技能与服务工具。'),
'airwallex-dev': ('软件开发与测试','支付API集成','生成、配置并接入 Airwallex API 的项目代码和集成工作流。'),
'apollo invoicing': ('财务与投资','客户与发票草稿','通过按业务实体划定范围的 OAuth 访问查找 Apollo 客户、查看发票并创建发票草稿。'),
'economic mind': ('财务与投资','企业财务与市场规模分析','基于 Economic Mind 连接器数据生成企业财务概览、竞争对标和自下而上的市场规模分析，强调数字来源与交叉核验。'),
'robosystems': ('财务与投资','财报与财务知识图谱','通过 MCP 使用 SEC EDGAR XBRL 披露、RoboLedger 总账和 RoboInvestor 投资组合知识图谱，辅助披露分析、月结、董事会报告和图谱探索。'),
'statutory reporting plugin': ('财务与投资','试算平衡表转财报','从试算平衡表分类科目，生成资产负债表、损益表、现金流量表、权益变动表和附注；作者声明支持印度 Ind AS、IFRS、印度 GAAP 和美国 GAAP，不等于已适配中国准则。'),
'superbooks': ('财务与投资','记账、发票与现金消耗','连接 SuperBooks，准备发票、查询应收、分类交易与匹配凭证，查看损益、现金消耗率和资金可用期限。'),
'granatum financeiro': ('财务与投资','损益与现金流','连接 Granatum，查看损益和现金流报告、查询交易分录，并在确认后创建分录。'),
'mosofin': ('财务与投资','跨SaaS财务数据读取','通过认证连接 MosoFin，在工作区权限范围内只读查询已连接 SaaS 平台的财务数据。'),
'tres finance plugin': ('财务与投资','区块链会计','连接 TRES Finance 的托管 MCP 服务，支持区块链会计、账簿管理和交易分析流程。'),
'wealthstoryline': ('财务与投资','家庭财务情景模拟','对收入、支出、储蓄、投资、房产和贷款进行蒙特卡洛情景模拟，考虑通胀、工资增长、利率和市场回报的不确定性。'),
'ololand-dd': ('财务与投资','投资尽调与情景分析','提供 DCF、LBO、蒙特卡洛等分析引擎，以及风险分类、盈利质量、跨文档核对、假设控制、情景分析和交易材料工作流；包内宣称的能力未实际运行验证。'),
'carta cap table': ('财务与投资','股权结构与交易情景','查询股权表、授予权益、SAFE、409A 估值及收益分配情景，配有对应技能与钩子。'),
'phasefolio': ('财务与投资','生物医药资产估值','通过 MCP 支持风险调整净现值、临床资产估值、成功概率基准、可比试验研究和签名导出核验。'),
'worker k': ('文档、知识与办公','财务办公自动化','面向会计和专业服务机构，提供 Excel、Word、PDF、研究与银行对账等办公自动化技能。'),
'altimate code': ('数据、数据库与BI','数仓与dbt开发','将数仓和 dbt 工作交给 altimate-code 命令行助手，支持 SQL 分析、列级血缘、dbt 构建测试、数仓探查、云成本分析和多类数据平台连接。'),
'pipeline reconcile': ('数据、数据库与BI','数据管道落地核对','核对管道报告已交付的数据是否真正到达目标端，发现运行状态正常但数据缺失的问题。'),
'snowflake-cortex-code': ('数据、数据库与BI','Snowflake开发助手路由','将 Claude Code 中的 Snowflake 相关请求转交 Cortex Code 执行，包内包含路由、运行与设置技能。'),
'preset cli skills': ('数据、数据库与BI','Superset命令行管理','使用 sup 命令行工具管理 Preset／Superset，支持明确要求命令行、脚本和 CI/CD 的工作流。'),
'demand-insight': ('数据、数据库与BI','需求预测与数据分析','按业务访谈、数据探查、特征、建模、误差分析和报告的流程做需求预测；强调防止数据泄漏、滚动验证、业务成本和 Excel 报告，并可生成实现材料。'),
'handsontable-skills': ('软件开发与测试','网页表格与公式计算','帮助开发 Handsontable JavaScript 表格组件和 HyperFormula 公式计算引擎。'),
'doit cloud intelligence': ('财务与投资','云成本管理','连接 DoiT Cloud Intelligence，使用云成本管理、报告、异常检测、预算和告警等服务工具。'),
'amg-toolkit': ('云平台、运维与安全','Azure监控与成本诊断','通过 Azure Managed Grafana 和 AMG-MCP 做健康检查、成本分析与诊断；包内技能还覆盖 Azure 订阅费用等分析。'),
'claude2figma': ('产品、设计与创作','Figma设计规范检查','约束 AI 设计优先使用组件库、绑定设计变量，并执行质量检查，使 Figma 产物遵循设计规范。'),
'dbt-toolkit': ('数据、数据库与BI','dbt项目管理','围绕 dbt 项目提供产物检查、审计、设计、代码审查、调试、依赖、开发与文档工作流。'),
}

def identity(name):
    name = re.sub(r' \(\d+\)(?=\.zip$)', '', name)
    name = re.sub(r'\.zip$', '', name, flags=re.I)
    name = re.sub(r'-(?:\d[\w.]*-)?v\d+$', '', name)
    return name.casefold()

OVERRIDES.update({k.casefold(): tuple(v) for k,v in json.loads((Path(__file__).parent / '补充中文说明.json').read_text(encoding='utf-8')).items()})

def text_desc(r):
    for p in r['plugins']:
        if p.get('description'): return str(p['description'])
    if r['skills'] and r['skills'][0].get('description'): return r['skills'][0]['description']
    if r['readmes']:
        t = r['readmes'][0]['text']
        lines = [l.strip() for l in t.splitlines() if l.strip() and not l.strip().startswith(('#', '|', '!', '```', '<'))]
        return '\n'.join(lines[:6])[:1600]
    return ''

def decode_description(value):
    # Interpret escapes inherited from quoted YAML description scalars only
    # when they form a valid JSON string; otherwise preserve the source text.
    if isinstance(value,str) and ('\\n' in value or '\\"' in value):
        try: return json.loads('"'+value+'"').strip()
        except json.JSONDecodeError: pass
    return value

def human_name(s):
    translations = {'read':'读取','query':'查询','search':'搜索','find':'查找','explore':'探查','analyze':'分析','analyse':'分析','analysis':'分析','audit':'审查','review':'评审','debug':'排错','test':'测试','validate':'核验','verify':'核验','create':'创建','build':'构建','generate':'生成','write':'编写','edit':'编辑','update':'更新','delete':'删除','remove':'移除','list':'列举','get':'获取','fetch':'获取','export':'导出','import':'导入','convert':'转换','attach':'挂接','install':'安装','setup':'设置','configure':'配置','deploy':'部署','monitor':'监控','report':'报告','reporting':'报告','plan':'规划','planning':'规划','design':'设计','docs':'文档','document':'文档','documents':'文档','file':'文件','files':'文件','data':'数据','database':'数据库','databases':'数据库','table':'表','tables':'表','schema':'结构','lineage':'血缘','quality':'质量','finance':'财务','financial':'财务','accounting':'会计','invoice':'发票','invoices':'发票','payroll':'工资','reconciliation':'对账','reconcile':'核对','valuation':'估值','statement':'报表','statements':'报表','cash':'现金','flow':'流量','balance':'余额','budget':'预算','cost':'成本','spend':'费用','revenue':'收入','sales':'销售','customer':'客户','customers':'客户','campaign':'活动','campaigns':'活动','email':'邮件','calendar':'日历','meeting':'会议','meetings':'会议','task':'任务','tasks':'任务','project':'项目','projects':'项目','memory':'记忆','memories':'记忆','context':'上下文','handoff':'交接','skill':'技能','skills':'技能','agent':'智能体','agents':'智能体','prompt':'提示词','prompts':'提示词','evaluation':'评测','eval':'评测','security':'安全','compliance':'合规','code':'代码','coding':'编程','git':'Git','commit':'提交','commits':'提交','branch':'分支','branches':'分支','pull':'拉取','request':'请求','merge':'合并','frontend':'前端','backend':'后端','component':'组件','components':'组件','style':'样式','styles':'样式','token':'变量/Token','tokens':'变量/Token','image':'图片','images':'图片','video':'视频','audio':'音频','slides':'幻灯片','presentation':'演示文稿','presentations':'演示文稿','chart':'图表','charts':'图表','dashboard':'看板','dashboards':'看板','research':'研究','market':'市场','model':'模型','models':'模型','forecast':'预测','forecasting':'预测','workbook':'工作簿','spreadsheet':'表格','learning':'学习','close':'结账/关闭','month':'月份','monthly':'月度','health':'健康状态','check':'检查','checks':'检查','fix':'修复','troubleshoot':'排查','troubleshooting':'排查','optimize':'优化','optimization':'优化','performance':'性能/表现','tracking':'跟踪','trace':'追踪','tracing':'追踪','logs':'日志','log':'日志','pipeline':'管道','pipelines':'管道','workflow':'流程','workflows':'流程','integration':'集成','integrations':'集成','sync':'同步','connect':'连接','connector':'连接器','connections':'连接','secrets':'密钥','auth':'认证','authentication':'认证','permissions':'权限','browser':'浏览器','web':'网页','scrape':'抓取','scraping':'抓取','crawl':'爬取','crawling':'爬取','notes':'笔记','note':'笔记','knowledge':'知识','base':'库','wiki':'知识库','onboarding':'入门/入职','discovery':'发现','insights':'洞察','insight':'洞察','metrics':'指标','metric':'指标','benchmark':'对标','benchmarks':'对标','inventory':'库存','supply':'供应','chain':'链','rules':'规则','rule':'规则','retrospective':'复盘','incident':'事件','incidents':'事件','backups':'备份','backup':'备份','restore':'恢复'}
    words = re.split(r'[-_ ]+', s)
    matched = [translations.get(w.lower(), w) for w in words]
    return ' · '.join(matched)

def classify(r):
    name = identity(r['file'])
    desc = text_desc(r)
    skilltext = ' '.join(s['name']+' '+s['description'] for s in r['skills'])
    themes = []
    for cat, topic, pattern, use in THEMES:
        score = (7 if re.search(pattern,name,re.I) else 0)+(4 if re.search(pattern,desc,re.I) else 0)+(1 if re.search(pattern,skilltext,re.I) else 0)
        if score >= 4: themes.append((score,cat,topic,use))
    themes.sort(key=lambda x:-x[0])
    o = OVERRIDES.get(name)
    if o and r['status'] == '已读取':
        cat,topic,summary = o
    elif themes:
        _,cat,topic,summary = themes[0]
        summary += '。'
    else:
        cat,topic = '其他与待确认','专用工具或功能待确认'
        summary = '包内有专用技能或服务连接；请结合下方原始说明和技能清单判断用途。' if r['status']=='已读取' else '当前只有压缩包文件名，尚不能确认内部功能与使用条件。'
    if r['status'] != '已读取':
        summary = f'仅按文件名作导航：{topic}。包内容尚未读取，具体功能、技能和依赖待确认。' if themes else summary
    r.update({'name': name,'category':cat,'topic':topic,'summary_zh':summary,'description':desc,'themes':list(dict.fromkeys([topic]+[t[2] for t in themes[:5]]))})
    paths=r['paths']
    r['platforms'] = [label for label,fragment in [('Claude插件','.claude-plugin/'),('Codex插件','.codex-plugin/'),('Cursor插件','.cursor-plugin/'),('Agent技能','skills/')] if any(fragment in p for p in paths)]
    r['counts'] = {label:sum(bool(re.search(rx,p,re.I)) for p in paths) for label,rx in [('脚本与代码',r'\.(?:py|js|ts|sh|mjs|cjs|go|rs|java|cs|ps1|rb|php)$'),('参考资料',r'(?:^|/)(?:references?|docs)/'),('模板',r'(?:^|/)templates?/'),('智能体定义',r'(?:^|/)agents/'),('钩子配置',r'(?:^|/)hooks?/'),('测试文件',r'(?:^|/)(?:tests?|evals?)/|(?:test|spec)\.(?:py|js|ts)$')]}
    req=[]
    if r.get('mcp_servers'): req.append('含 MCP 服务配置：'+ '、'.join(sorted(set(r['mcp_servers']))))
    if r.get('config_names'):req.append('包内声明用户配置项：'+'、'.join(sorted(set(r['config_names']))))
    alltext=desc+' '+' '.join(m['text'] for m in r['readmes'][:2])
    for label,pattern in [('提及账号登录或 OAuth 授权',r'\boauth\b|sign.in|log.in|authenticate|authentication'),('提及 API Key、令牌或凭证配置',r'api[ _-]?keys?|access[ _-]?tokens?|credentials?|\$\{\w+(?:TOKEN|KEY)\}'),('提及命令行工具或本地运行环境',r'\bcli\b|\bpython\b|node\.js|\bnpm\b|\bnpx\b|\buvx\b|\bdocker\b'),('提及必须依赖其他插件或连接器',r'requires? .*?(plugin|connector|mcp)|prerequisites?|dependencies')]:
        if r['status']=='已读取' and re.search(pattern,alltext,re.I):req.append(label+'（根据说明文字识别，具体步骤见原文）')
    if not req: req=['未从已读取说明中识别明确前置条件；不代表无需环境或账号。'] if r['status']=='已读取' else ['内部说明未读取，前置条件待确认。']
    r['requirements']=req
    if r['skills']:r['form']='技能包'+(' + 服务连接' if r.get('mcp_servers') else '')
    elif r.get('mcp_servers'):r['form']='服务连接插件'
    elif r['status']=='已读取':r['form']='插件、命令或资料包'
    else:r['form']='包类型待确认'
    if name.startswith('aiplus_finance'):r['form']='产品设计与研究资料包'
    r['evidence_note']='基于包内静态说明；未安装、未运行，作者宣称的效果未验收。' if r['status']=='已读取' else '尚未读取包内内容；用途分类只作文件名导航。'
    refine(r, o)
    return r

def md_escape(v):return str(v).replace('|','\\|').replace('\n','<br>')

def build_md(records,stats):
    lines=['# AI技能与插件压缩包详细目录','', '> 生成日期：2026-10-07（中国时间）。所有介绍基于本目录 ZIP 的静态内容；未安装、未执行任何包内脚本。分类与中文用途为整理者的导航说明，精确功能以附带原始说明为依据。','', f'共 **{stats["total"]}** 个 ZIP，**{stats["read"]}** 个已读取，**{stats["pending"]}** 个未读取。已读取 **{stats["skills"]}** 条技能说明。','', '## 阅读方法','', '- 先按用途分类浏览，再查看每个包的中文用途、原始说明、技能和命令。','- 每一条技能均列出名称、可读名称提示、原始 description 及其在 ZIP 中的路径。名称提示只是词语导航，不是对功能范围的翻译保证。','- 账号、授权、CLI 等条件是从说明识别的线索，不能证明已在当前电脑配置好。','- iCloud 占位包保留独立条目并标明待读取，不以文件名推测替代真实说明。','- 不同文件名对应同一产品的版本/副本，也分别列出；只对 SHA-256 完全一致的文件判定内容相同。','', '## 分类索引','', '| 分类 | 包数量 |','|---|---:|']
    cats=collections.Counter(r['category'] for r in records)
    lines += [f'| {c} | {n} |' for c,n in cats.items()]
    for cat in cats:
        lines += ['',f'## {cat}','']
        for r in [x for x in records if x['category']==cat]:
            lines += [f'### {r["id"]:04d} · {r["file"]}','',f'- **读取状态**：{r["status"]}',f'- **中文用途**：{r["summary_zh"]}',f'- **主题**：{"、".join(r["themes"])}',f'- **三级分类**：{r["category"]} → {r["scene"]} → {r["task"]}',f'- **包形态**：{r["form"]}',f'- **大小**：{r["bytes"]:,} 字节',f'- **适配线索**：{"、".join(r["platforms"]) or "未识别/待确认"}',f'- **内容规模**：{len(r["paths"])} 个文件，{len(r["skills"])} 条技能，{len(r["commands"])} 条命令',f'- **前置条件**：{"；".join(r["requirements"])}',f'- **证据边界**：{r["evidence_note"]}']
            if r.get('duplicates'):lines += [f'- **内容完全相同的副本**：{"；".join(r["duplicates"])}']
            if r.get('same_name'):lines += [f'- **同名产品的其他文件**：{"；".join(r["same_name"])}（未必内容相同）']
            if r['description']:lines += ['', '**原始功能说明**', '',r['description'],'']
            if r['plugins']:
                lines += ['**插件信息**','']
                for p in r['plugins']:
                    lines += [f'- `{p.get("name", "")}` / 版本 `{p.get("version", "未声明")}` / 许可 `{p.get("license", "未声明")}` / 来源路径 `{p["path"]}`']
                    for k,label in [('repository','仓库'),('homepage','主页')]:
                        if p.get(k):lines.append(f'  - {label}：{p[k]}')
            if r['skills']:
                lines += ['', '**全部技能**','', '| 技能名称 | 名称词语提示 | 原始用途说明 | 包内路径 |','|---|---|---|---|']
                for s in r['skills']:
                    desc=s['description'] or '未声明 description；章节：'+' / '.join(s['headings'][:8])
                    lines += ['| '+ ' | '.join(md_escape(x) for x in [s['name'],human_name(s['name']),desc,s['path']])+' |']
            if r['commands']:
                lines += ['', '**全部命令**','']
                for c in r['commands']:lines += [f'- `{c["name"]}`：{c["description"] or " / ".join(c["headings"])}（`{c["path"]}`）']
            if r['readmes']:lines += ['', '**README 位置与主要章节**','']+[f'- `{m["path"]}`：'+ ' / '.join(m['headings']) for m in r['readmes']]
            if r['paths']: lines += ['', '<details><summary>展开全部包内文件</summary>','', '```text','\n'.join(r['paths']),'```','','</details>','']
    (OUT / '详细目录.md').write_text('\n'.join(lines),encoding='utf-8')

def build_html(records,stats):
    from web_catalog import build_html as render_web
    render_web(records,stats,OUT)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records=json.loads((OUT/'完整扫描.json').read_text())
    originals=json.loads((Path(__file__).parent/'保留中文摘要.json').read_text())
    templates=json.loads((Path(__file__).parent/'原模板摘要.json').read_text())
    evidence_file=Path(__file__).parent/'中文摘要依据.json'
    evidence=json.loads(evidence_file.read_text()) if evidence_file.exists() else {}
    if isinstance(evidence.get('records'),list):evidence={str(x['id']):x for x in evidence['records']}
    zh_file=Path(__file__).parent/'技能中文说明.json'
    zh=json.loads(zh_file.read_text()) if zh_file.exists() else {}
    corrections_path=Path(__file__).parent/'用户反馈摘要校正.json'
    corrections=json.loads(corrections_path.read_text()) if corrections_path.exists() else {}
    hashes=collections.defaultdict(list);names=collections.defaultdict(list)
    for r in records:
        if r['sha256']:hashes[r['sha256']].append(r['file'])
        names[identity(r['file'])].append(r['file'])
    for i,r in enumerate(records,1):
        for s in r['skills']+r['commands']:s['description']=decode_description(s['description'])
        classify(r);r['id']=i
        if str(i) in originals:r['summary_zh']=originals[str(i)]
        # Record-specific editorial evidence avoids confusing unrelated packages with the same name.
        e=evidence.get(str(i),{})
        if str(i) in templates and not (isinstance(e,dict) and e.get('summary_zh')):r['summary_zh']=templates[str(i)]
        if isinstance(e,dict) and e.get('summary_zh') and str(i) not in originals:r['summary_zh']=e['summary_zh']
        correction=corrections.get(str(i))
        if correction:
            if correction['file']!=r['file'] or correction['source_description']!=r['description']:
                raise ValueError('人工摘要校正的来源已变化：'+r['file'])
            r['summary_zh']=correction['summary_zh']
        r['duplicates']=[x for x in hashes.get(r['sha256'],[]) if x!=r['file']]
        r['same_name']=[x for x in names[r['name']] if x!=r['file']]
        for s in r['skills']:
            s['name_hint']=human_name(s['name'])
            key=hashlib.sha256(s['description'].encode()).hexdigest()
            entry=zh.get('by_path',{}).get(r['file']+':'+s['path']) or zh.get('by_path',{}).get(str(i)+':'+s['path']) or zh.get('translations',{}).get(key)
            if isinstance(entry,str):s['description_zh']=entry
            elif isinstance(entry,dict):
                if entry.get('method')=='本地逐条人工意译并核对适用范围' and entry.get('source_sha256')!=key:
                    raise ValueError('中文技能说明的原文已变化：'+r['file']+':'+s['path'])
                s['description_zh']=entry.get('description_zh','')
        r['counts']['参考资料']=len(r.get('references',[]))
    stats={'total':len(records),'read':sum(r['status']=='已读取' for r in records),'pending':sum(r['status']!='已读取' for r in records),'skills':sum(len(r['skills']) for r in records),'commands':sum(len(r['commands']) for r in records),'bytes':sum(r['bytes'] for r in records),'duplicate_groups':sum(len(v)>1 for v in hashes.values()),'categories':dict(collections.Counter(r['category'] for r in records))}
    stats.update(scene_count=len({t[:2][0]+' / '+t[1] for r in records for t in r['taxons']}),task_count=len({tuple(t) for r in records for t in r['taxons']}))
    (OUT/'catalog.json').write_text(json.dumps({'stats':stats,'records':records},ensure_ascii=False,separators=(',',':')))
    print(json.dumps(stats,ensure_ascii=False))

if __name__=='__main__':main()
