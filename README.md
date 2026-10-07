# 技能书架

公开的插件与技能资料目录，支持三级任务分类、搜索、完整原文阅读、单文件下载及原 ZIP 下载。

覆盖 1761 个目录记录；当前 1761 个原包已复制并核验。未取回的文件明确标记。

## 运行

Python 3.12：`pip install -r requirements.txt`，然后 `streamlit run streamlit_app.py`。

静态前端来自既有目录，原始包按 SHA-256 命名，仅做静态内容浏览，不执行包内代码。文本以纯文本方式显示，HTML/SVG 不作为页面运行。 ZIP 下载和单文件下载保留原始字节。

第三方 ZIP 文件中的声明与许可由原作者保留；fflate 0.8.2 为 MIT，许可见 `site/vendor/fflate-LICENSE.txt`。

验证记录见 `verification.json`。如目录元数据已读取而原包仍是 iCloud 占位文件，站点仍显示目录说明，但下载入口禁用。
