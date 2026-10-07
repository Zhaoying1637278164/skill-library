"""Evidence-based, multi-label task navigation. Package text remains untrusted data."""
import re
import json
from pathlib import Path
CURATED=json.loads((Path(__file__).parent/"精细分类校正.json").read_text())
RULES=[]
def add(cat,scene,rows):
 for task,pattern in rows:
  for stem in ['bookkeep','invoic','vulnerabil','transcri','fine.tun','recruit','advertis','refactor','debug']:
   pattern=pattern.replace(stem,stem+r'\w*')
  RULES.append((cat,scene,task,re.compile(r'(?<![a-z0-9])(?:'+pattern+r')(?![a-z0-9])',re.I)))

add('财务与投资','月结与对账',[
 ('银行流水提取',r'bankstatemently|convert.statement|extract.{0,40}(bank|statement)|bank statements?.{0,60}(structured|pdf)|银行流水提取'),
 ('银行流水核对',r'reconcile.statements|bank.{0,25}reconcil|银行.*核对'),
 ('总账差异追踪',r'gl.reconciler|general ledger|ledger reconcil|总账'),
 ('月结与记账',r'bookkeep|month.end|monthly close|quickbooks|superbooks|robosystems|granatum|accounting|月结|记账'),
 ('财务报表编制',r'trial balance|statutory reporting|balance sheet|cash.flow statement|试算平衡表|财报')])
add('财务与投资','收付款与资金',[
 ('发票与应收应付',r'invoic|accounts (receivable|payable)|发票|应收'),
 ('支付与跨境资金',r'airwallex|paypal|stripe|paymob|payment processing|cross.border|跨币种|付款'),
 ('银行账户与现金流',r'cashflow|banking|bank account|cash burn|cash flow|plaid|企业银行|现金流'),
 ('费用与交易分类',r'categorize.transactions|categoris.{0,20}transaction|expense management|spending analysis|支出分类')])
add('财务与投资','财务模型与估值',[
 ('DCF与企业估值',r'\bdcf\b|discounted cash|valuation|估值'),
 ('LBO与三表建模',r'\blbo\b|3.statement|three.statement|financial model|财务建模'),
 ('尽调与盈利质量',r'due diligence|\bqoe\b|earnings quality|ololand.dd|尽调'),
 ('股权结构与收益分配',r'cap table|carta|\b409a\b|waterfall|股权'),
 ('预算与经营预测',r'financial planning|budget|fp&a|pigment|预算|经营数据分析'),
 ('情景模拟与风险分析',r'monte carlo|monte.carlo|wealthstoryline|scenario analysis|情景模拟')])
add('财务与投资','投资与金融研究',[
 ('证券行情与基本面',r'eodhd|stock price|financial data|financial analysis|market data|股票|金融行情'),
 ('基金筛选与比较',r'morningstar|fund.screener|fund.comparison|fund research|基金'),
 ('债券、外汇与衍生品',r'\blseg\b|yield curve|bonds?|forex|derivatives|option pric|债券'),
 ('公司研究与宏观数据',r'economic mind|privco|company research|macroeconomic|企业财务|公司资料'),
 ('投资组合分析',r'investment portfolio|portfolio analy|roboinvestor|投资组合'),
 ('云成本与FinOps',r'finops|cloud cost|cloud spend|doit cloud|云成本|资源费用')])
add('数据、数据库与BI','数据库与SQL',[
 ('本地文件与DuckDB',r'duckdb|ducklake|csv.{0,30}parquet|本地数据读取'),
 ('关系数据库查询',r'postgres(?:ql)?|alloydb|mysql|sqlite|sql server|sql queries|sql query|数据库查询'),
 ('云数仓与大数据',r'snowflake|bigquery|databricks|redshift|clickhouse|spanner|数仓'),
 ('NoSQL与缓存',r'mongodb|firestore|dynamodb|redis|nosql'),
 ('数据库运维与迁移',r'database migration|database administrator|query optimization|database performance|数据库迁移')])
add('数据、数据库与BI','数据治理',[
 ('数据目录与资产搜索',r'atlan|datahub|informatica|data catalog|data assets|数据目录|数据资产'),
 ('数据血缘追踪',r'lineage|血缘'),
 ('数据质量与落地核对',r'data quality|pipeline reconcile|data validation|数据质量|落地核对'),
 ('业务术语与语义层',r'glossary|semantic layer|business terms|业务术语|语义层')])
add('数据、数据库与BI','数据工程',[
 ('dbt模型开发',r'\bdbt\b|数据转换'),
 ('ETL与数据连接器',r'\betl\b|\belt\b|fivetran|airbyte|data pipeline|数据管道'),
 ('任务编排与调度',r'airflow|dagster|prefect|kestra|data orchestration'),
 ('流式数据处理',r'\bkafka\b|apache spark|stream processing|流式数据')])
add('数据、数据库与BI','分析与展示',[
 ('Excel与表格处理',r'\bexcel\b|spreadsheet|workbook|表格处理'),
 ('探索分析与统计',r'data analysis|statistical|\beda\b|jupyter|数据分析|统计'),
 ('需求预测与建模',r'demand.insight|forecasting|demand forecast|machine learning|需求预测'),
 ('BI与指标看板',r'tableau|power.?bi|superset|preset|looker|dashboards?|看板'),
 ('图表与数据可视化',r'data visuali[sz]ation|plotly|matplotlib|chart generation|图表|数据可视化')])
add('销售、营销与电商','客户与销售',[
 ('CRM与客户资料',r'\bcrm\b|hubspot|salesforce|pipedrive|freshsales|客户资料'),
 ('线索发现与客户研究',r'prospecting|sales intelligence|lead generation|lead enrichment|apollo.io|线索'),
 ('商机与销售跟进',r'deal pipeline|sales pipeline|sales enablement|gong|销售跟进'),
 ('客户支持与反馈',r'customer support|customer success|zendesk|intercom|freshdesk|客户服务|客户反馈')])
add('销售、营销与电商','广告与增长',[
 ('广告账户与投放',r'google ads|meta ads|amazon ads|advertis|ppc|adspirer|adology|广告'),
 ('SEO与关键词研究',r'\bseo\b|semrush|ahrefs|keyword research|search console|搜索优化'),
 ('AI搜索可见度',r'\baeo\b|generative engine optimization|ai search|search visibility|AI搜索'),
 ('营销活动与邮件触达',r'email marketing|marketing campaign|customer.io|mailchimp|activecampaign|营销'),
 ('网站流量与转化',r'google analytics|web analytics|conversion optimization|conversion rate|网站流量')])
add('销售、营销与电商','内容与电商',[
 ('社交媒体内容与排期',r'social media|social content|instagram|tiktok|linkedin|bluesky|hootsuite|buffer|社交'),
 ('商品、订单与店铺',r'shopify|woocommerce|e.commerce|ecommerce|etsy|merchant|店铺|订单'),
 ('库存与履约',r'inventory|fulfillment|库存|履约'),
 ('营销文案与品牌',r'copywriting|brand strategy|marketing content|品牌|营销文案')])
add('产品、设计与创作','产品与体验',[
 ('需求与产品规划',r'product management|product discovery|\bprd\b|productboard|roadmap|产品需求'),
 ('用户研究与体验评审',r'user research|ux research|usability|user experience|体验|用户研究'),
 ('界面与组件设计',r'figma|penpot|ui design|interface design|21st|gemdesign|界面|组件'),
 ('设计系统与无障碍',r'design system|design tokens|accessibility|\ba11y\b|设计规范|无障碍')])
add('产品、设计与创作','图像与视觉',[
 ('图像生成与编辑',r'image generation|image editing|images?|adobe|canva|图片|图像'),
 ('摄影、插画与素材',r'photograph|illustration|stock photos|visual assets|插画|摄影'),
 ('品牌视觉与版式',r'visual identity|typography|graphic design|layout design|品牌视觉|版式')])
add('产品、设计与创作','视频与音频',[
 ('视频制作与剪辑',r'video|remotion|视频|剪辑'),
 ('动画、3D与渲染',r'animation|blender|3d model|rendering|动画|渲染'),
 ('语音合成与转录',r'speech|transcri|elevenlabs|text.to.speech|语音|转录'),
 ('音乐与播客',r'music|podcast|suno|音频|音乐|播客')])
add('文档、知识与办公','文档与写作',[
 ('PDF读取与处理',r'\bpdf\b|pdfs|PDF'),
 ('Word与文档生成',r'\bdocx\b|word document|document generation|document editing|文档生成'),
 ('合同与电子签名',r'e.signature|esign|docusign|pandadoc|contract management|电子签名'),
 ('文字润色与翻译',r'writing|translation|translate|proofread|文字|润色|翻译'),
 ('幻灯片与汇报材料',r'slides|presentations?|powerpoint|pptx|marp|slidev|演示文稿|汇报'),
 ('事实、引用与来源核验',r'citation|fact.check|source verification|事实|引用核验')])
add('文档、知识与办公','知识与资料',[
 ('笔记与知识库',r'obsidian|notion|knowledge base|notes|wiki|笔记|知识库'),
 ('企业知识搜索',r'glean|enterprise search|semantic search|enterprise knowledge|企业知识'),
 ('网页采集与资料归档',r'web scrap|crawl|firecrawl|archive|web research|网页采集|归档'),
 ('阅读与资料整理',r'ebook|reading|literature organiz|电子阅读|资料整理')])
add('文档、知识与办公','邮件与会议',[
 ('邮件收发与收件箱',r'email|gmail|outlook|agentmail|inboxes|邮件'),
 ('日历与预约安排',r'calendar|scheduling|appointment|日历|预约'),
 ('会议纪要与准备',r'meeting|会议|纪要'),
 ('聊天与团队沟通',r'slack|microsoft teams|sms|text messaging|短信|聊天')])
add('文档、知识与办公','任务与协作',[
 ('任务与项目管理',r'project management|task management|asana|trello|clickup|monday|jira|linear|todo|任务|项目管理'),
 ('跨应用流程自动化',r'n8n|zapier|make.com|workflow automation|办公自动化|流程自动化'),
 ('文件与云盘管理',r'google drive|dropbox|onedrive|file management|云盘|文件管理')])
add('AI与智能体','记忆与上下文',[
 ('长期记忆与检索',r'memory|memories|recall|记忆'),
 ('上下文压缩与Token',r'context compress|context management|token budget|token inspector|context window|上下文|指令格式压缩'),
 ('会话交接与恢复',r'handoff|session restor|session history|conversation history|交接|会话'),
 ('决策与知识留存',r'decision log|decision record|决策记录|知识保存')])
add('AI与智能体','智能体与工作流',[
 ('多智能体协作',r'multi.agent|agent orchestration|ag2|crew.?ai|多模型|多视角|分工'),
 ('智能体开发框架',r'agent framework|agents sdk|agent development|agentic framework|langchain|langgraph|agentforce|智能体开发'),
 ('MCP开发与工具连接',r'mcp server development|build.{0,15}mcp|mcp builder|mcp gateway|mcp management|tool routing|工具路由'),
 ('RAG与向量检索',r'\brag\b|retrieval.augmented|vector search|embedding|向量'),
 ('工作流编排',r'ai workflow|agent workflow|workflow orchestration|agent automation|工作流组织|AI工作流')])
add('AI与智能体','模型与质量',[
 ('提示词设计与管理',r'prompt engineering|prompt management|prompt optim|prompt templates|提示词'),
 ('AI评测与效果检查',r'llm eval|ai eval|deepeval|giskard|model evaluat|agent eval|ai benchmark|评测'),
 ('LLM追踪与可观测性',r'langfuse|langsmith|braintrust|helicone|arize|llm observability|phoenix|AI.*追踪'),
 ('模型训练与推理',r'hugging face|huggingface|fine.tun|model training|model inference|推理|模型训练')])
add('AI与智能体','助手配置与技能',[
 ('Claude、Codex与Cursor配置',r'claude code.{0,25}(config|settings)|codex.{0,25}(config|settings)|cursor.{0,25}(config|rules)|statusline|statusbar|助手配置'),
 ('插件与技能管理',r'skill.{0,15}(install|creat|manag|discover)|plugin.{0,15}(install|manag|discover)|skills?.{0,20}marketplace|插件与技能|技能选择'),
 ('助手规则与行为控制',r'guardrails|assistant behavior|agent instructions|claude.md|agents.md|助手行为|回答去重复'),
 ('AI使用与思考方法',r'ai adoption|ai mentor|ai productivity|critical thinking|mental model|AI改造|思考框架|需求澄清')])
add('软件开发与测试','需求与架构',[
 ('规格与需求拆解',r'spec.driven|specification|requirements|需求|规格'),
 ('系统架构与技术方案',r'architecture|architect|system design|technical design|架构'),
 ('工程方法与交付',r'sdlc|superpowers|engineering workflow|development workflow|工程流程|交付|10x.team')])
add('软件开发与测试','代码质量',[
 ('代码审查与规范',r'code review|code quality|static analysis|lint|代码质量|代码审查'),
 ('调试与故障定位',r'debug|troubleshoot|调试|排错'),
 ('单元测试与覆盖率',r'unit test|test.driven|test coverage|testing|单元测试'),
 ('浏览器与端到端测试',r'playwright|cypress|selenium|end.to.end|browser automation|浏览器'),
 ('代码检索、讲解与重构',r'code search|codebase|code navigation|refactor|代码库|代码讲解|代码变更')])
add('软件开发与测试','版本与协作开发',[
 ('Git与分支管理',r'\bgit\b|worktree|rebase|git branch|分支'),
 ('PR、合并与发布',r'pull request|merge request|github|gitlab|bitbucket|release|发布准备'),
 ('CI与构建流程',r'buildkite|ci/cd|continuous integration|build pipeline|CI')])
add('软件开发与测试','应用开发',[
 ('前端与网页应用',r'react|vue|angular|svelte|next.js|nextjs|frontend|front.end|网页表格|前端'),
 ('移动端与桌面应用',r'ios|swift|android|flutter|react native|electron|tauri|slint|macos|移动端|桌面'),
 ('后端与接口集成',r'backend|back.end|fastapi|django|spring|laravel|rails|api integration|sdk integration|API集成|后端'),
 ('语言与开发环境',r'python|typescript|javascript|rust|golang|clojure|julia|language server|本地开发环境|语言服务'),
 ('游戏与实时交互',r'unity|unreal|game development|real.time (audio|video)|音视频|游戏'),
 ('低代码与平台应用',r'tooljet|modelence|workiom|atlassian forge|low.code|应用构建|应用开发')])
add('云平台、运维与安全','云与基础设施',[
 ('AWS、Azure与GCP',r'\baws\b|\bazure\b|\bgcp\b|google cloud|oracle cloud|云平台'),
 ('容器与Kubernetes',r'docker|kubernetes|\bk8s\b|容器'),
 ('基础设施即代码',r'terraform|pulumi|infrastructure as code|upbound|基础设施'),
 ('应用部署与托管',r'deploy|vercel|netlify|hosting|fastly|部署|托管')])
add('云平台、运维与安全','监控与运维',[
 ('日志与可观测性',r'grafana|datadog|new relic|sumo.logic|observability|log analy|日志|可观测性'),
 ('告警与事故处理',r'pagerduty|incident|sentry|alert|root cause|告警|事故'),
 ('备份、恢复与设备维护',r'backup|restore|disk space|device management|备份|磁盘')])
add('云平台、运维与安全','安全检查',[
 ('API与应用安全',r'api security|42crunch|aikido|application security|security scan|API安全'),
 ('漏洞与威胁分析',r'vulnerabil|threat|penetration|security audit|above security|安全检查'),
 ('密钥与访问控制',r'1password|secret management|identity|authentication|authorization|oauth|oidc|auth0|身份|访问控制'),
 ('安全策略与合规',r'security compliance|governance|governor|policy enforce|security policy|合规|操作边界')])
add('行业、研究与生活','法律与公共事务',[
 ('法规检索与合规研究',r'legal|regulatory|regulation|westlaw|lexis|gdpr|nis2|法律|法规'),
 ('诉讼与法律文书',r'litigation|诉讼|法律文书'),
 ('公共部门与采购',r'government|public sector|arckit|public procurement|公共采购|公共部门'),
 ('税务、关税与贸易',r'taxation|tax law|tariff|customs|税务|关税')])
add('行业、研究与生活','研究与学习',[
 ('学术论文与文献检索',r'scholar|academic|pubmed|wiley|springer|literature|research papers|学术|文献'),
 ('学习、教学与课程',r'education|study|learning|teaching|tutor|课表|学习|课程'),
 ('专家、导师与咨询',r'adplist|mentoring|mentor|expert search|consultant|导师|咨询'),
 ('科学论断与研究核验',r'stem|scientific|research validation|科学|论断')])
add('行业、研究与生活','行业业务',[
 ('医疗、临床与生命科学',r'healthcare|medical|clinical|biotech|fhir|adisinsight|nhs|医疗|医药|临床'),
 ('招聘、人员与薪酬',r'human resources|recruit|hiring|payroll|workday|bamboohr|招聘|薪酬|求职'),
 ('供应链、采购与物流',r'supply chain|logistics|procurement|shipping|cargo|制造|供应链|物流|发货'),
 ('建筑、地产与工程估算',r'real estate|construction project|building construction|scaffolding|property listings|房源|场地|工程估算'),
 ('区块链与数字资产',r'blockchain|crypto|web3|ethereum|solana|on.chain|defi|区块链')])
add('行业、研究与生活','生活与个人事务',[
 ('旅行、地图与出行',r'travel|airport|flights|hotels|maps|geospatial|geocod|旅行|地图'),
 ('预约、收藏与个人管理',r'booking|reservation|personal planner|life edit|collection management|收藏|个人生活'),
 ('阅读、文化与经典',r'orthodox|religious|scripture|manga|宗教|经典|漫画'),
 ('车辆、设备与其他查询',r'carsxe|vehicle|automotive|robotics|车辆|机器人')])

add('AI与智能体','助手配置与技能',[
 ('用量、额度与成本跟踪',r'usage limits|usage cost|quota|rate limit|token usage|status.line|statusline|claude stats|ai.hp|brizz|burn'),
 ('会话与通知管理',r'claude code sessions|session manager|conversation|desktop notification|notify|afkswitch|chat.namer|codeman'),
 ('助手初始化与环境配置',r'claude.code.setup|claude code automations|bootstrap|claudify|claude.time|claude.tab.fix|opus.*migration')])
add('AI与智能体','智能体与工作流',[
 ('多视角讨论与决策',r'16minds|agents to debate|agent negotiation|concordia|personality.type|team of ai agents|companyforge'),
 ('自动研究与实验迭代',r'autoresearch|autonomous experiment|autonomous skill improvement|optimize.measure|auto research'),
 ('智能体设计与服务开发',r'agent system|ai agents|agentstudio|agent garden|agentic atlas|agent architecture'),
 ('MCP服务集成',r'mcp integration|mcp connector|model context protocol|building integrations|boomi.integration|boomi.marketplace')])
add('AI与智能体','模型与质量',[
 ('智能体运行诊断',r'agent traces|trace triage|tool loops|agent observability|instrumenting an ai agent'),
 ('工具可信度与行为检查',r'agentavow|safety grades|trust score|verify before asserting|assurance|candy.plugin'),
 ('基准测试与推理路由',r'benchmarks|benchmarking|typesafe|calibrated.confidence|llm performance'),
 ('问题澄清与推理方法',r'first.principles|hidden assumptions|claude.deconstruct|decision framework')])
add('文档、知识与办公','任务与协作',[
 ('工时与工作记录',r'timesheets|time tracking|work logs|工时'),
 ('短链接、二维码与域名',r'qr codes|short links|domain management|二维码|短链接')])
add('文档、知识与办公','邮件与会议',[
 ('电话与语音提醒',r'telephonist|voice call|phone call|callremind|benaiah'),
 ('即时通讯与消息渠道',r'imessage|bluebubbles|messaging channel|telegram|discord|whatsapp')])
add('文档、知识与办公','知识与资料',[
 ('协作文档与页面管理',r'confluence|cloud pages|shared pages|cflio|char'),
 ('文档检索与技术参考',r'documentation lookup|context7|code examples|technical documentation')])
add('销售、营销与电商','广告与增长',[
 ('A/B测试与增长实验',r'a/b test|ab test|landing.page|accelerate|growth experiments|conversion'),
 ('应用商店优化',r'aso atlas|app store optimization|app store connect'),
 ('品牌曝光与AI推荐追踪',r'aska irank|askairank|ai engines|mention your brand|botify'),
 ('广告素材与竞品研究',r'ad library|ad accounts|creative intelligence|atria'),
 ('内容页面与博客发布',r'link.in.bio|blog publishing|bioflow|post publishing')])
add('软件开发与测试','应用开发',[
 ('API契约与接口模拟',r'api contract|contract artifacts|http apis|beeceptor|mock api'),
 ('企业框架与模块开发',r'abp framework|ef core|microservices|ddd|\.net|cap applications|cds.mcp'),
 ('电子电路与PCB设计',r'pcb|kicad|schematic|boardrepo'),
 ('游戏设备与运行维护',r'batocera|retro.gaming|roms|arcade|accelbyte')])
add('软件开发与测试','代码质量',[
 ('代码简化与遗留系统改造',r'code.simplifier|legacy code|modernization|simplifies and refines|codehog|codedna'),
 ('方案评审与开发助手反馈',r'codex.review|implementation plan|bug reports|feature requests|beer and code')])
add('产品、设计与创作','图像与视觉',[
 ('视觉素材与程序绘画',r'asset generator|anidoodle|code.drawn|drawing timelapses|blueprint studio')])
add('财务与投资','投资与金融研究',[
 ('信用指标与投资风险',r'aci risk|credit intelligence|risk indicators|credit risk'),
 ('财富规划与组合建议',r'blackrock|wealth projections|portfolio building|portfolio review')])
add('行业、研究与生活','行业业务',[
 ('分子、蛋白与药物研究',r'chembl|boltz|molecules|proteins|bioactive|drug.like compounds'),
 ('员工认可与奖励',r'bonusly|employee rewards|recognition and rewards'),
 ('职业辅导与发展',r'career coaching|careervillage|career guidance')])
add('行业、研究与生活','法律与公共事务',[
 ('立法与议案研究',r'legislation|legislators|bill text|voting records|cicada')])

# Override prose is individually curated and safely strengthens its own domain;
# it never supplies capabilities for an unread package.
def refine(r,override=None):
 name=r['name']; desc=r['description']; known=r['status']=='已读取'
 prose=(override[2] if override and known else '')
 skills=r['skills'] if known else []
 hits=[]
 for cat,scene,task,rx in RULES:
  n=bool(rx.search(name)); d=len(rx.findall(desc)) if known else 0
  z=bool(rx.search(prose)); sk=sum(bool(rx.search(s['name']+' '+s['description'])) for s in skills)
  sn=sum(bool(rx.search(s['name'])) for s in skills)
  if not (n or d or z or sn or (sk>=2 and sk/max(1,len(skills))>=0.25)):continue
  # Specific package name / stated purpose beats incidental mentions in skills.
  score=12*n+min(d,3)*4+6*z+min(4,sk)*1.3+min(sn,2)*5+(sk/max(1,len(skills)))*2
  if override and known and cat==override[0]:score+=4
  if cat=='AI与智能体' and not (n or z):score-=2
  if not(n or d or z or sn) and sk<2:score-=3
  if score>=3:hits.append((score,cat,scene,task))
 hits.sort(key=lambda h:-h[0])
 if override and known:
  own=[h for h in hits if h[1]==override[0]]
  if own:
   chosen=own[0]; hits=[chosen]+[h for h in hits if h!=chosen]
  else:
   hits.insert(0,(20,override[0],'专项工作',override[1]))
 if hits:
  _,cat,scene,task=hits[0]
  threshold=max(3,hits[0][0]*0.22)
  selected=[h for h in hits if h[0]>=threshold][:16]
  r['taxons']=[[h[1],h[2],h[3]] for h in selected]
 elif known and re.search(r'claude|codex|cursor|ai agent|mcp server|llm|gemini',name+' '+desc,re.I):
  cat,scene,task='AI与智能体','助手配置与技能','专项助手工具与服务'
  r['taxons']=[[cat,scene,task]]
 else:
  cat,scene,task='其他与待确认','用途待确认','查看原始说明' if known else '等待内容下载'
  r['taxons']=[[cat,scene,task]]
 if known and name in CURATED:
  c=CURATED[name];cat,scene,task=c['path']
  r['taxons']=[c['path']]
  r['summary_zh']=c['summary']
 r.update(category=cat,scene=scene,task=task,classification_basis='说明与技能匹配，支持多用途标签' if known else '文件名导航，内容待确认')
 r['themes']=list(dict.fromkeys(t[2] for t in r['taxons']))
 if not override and name not in CURATED and known and cat!='其他与待确认':
  r['summary_zh']=f'主要用于{scene}，可查找“{task}”相关技能或服务。具体操作范围见包内说明。'
 return r
