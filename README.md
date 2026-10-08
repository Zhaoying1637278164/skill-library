# 技能书架

公开的第三方插件与技能资料目录。2026-10-08 更新为应用商店式发现、分类、详情、搜索、原文阅读和新手指南，支持手机布局。

## 运行

`pip install -r requirements.txt`，然后 `streamlit run streamlit_app.py`。

首页通过 `site/data/list.json` 加载轻量目录；搜索索引与单包详情按需加载。1761 个目录记录，按 SHA-256 去重显示 1748 个包。首页资源约 1.81 MB。原始 ZIP 和单文件保留原字节，下载前核验 SHA-256；包内代码不执行，HTML/SVG 只作为文本阅读。

## 中文编辑状态

879 个摘要与 10364 条技能中文说明仍待完善，页面顶部保留提示。本次明确授权发布现有页面，未将中文编辑宣称为完成。专题与领域介绍为待确认配置；126 个未声明许可证包保持既有下载策略。

`python3 tools/build_site.py` 的默认编辑校验仍拒绝未完成内容；经负责人明确批准发布当前界面时，可使用 `python3 tools/build_site.py --allow-incomplete-editorial`，该模式保留完善中提示，仍拒绝伪技能。构建只静态扫描现有 ZIP。

第三方作者许可保持原样。fflate（MIT）、Marked（MIT）和 Lucide（ISC）的许可证随文件保存。发布标识在 `site/release.json`，构建数字在 `site/构建验收.json`。
