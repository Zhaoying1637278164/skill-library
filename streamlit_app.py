from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='技能书架 · 原文与下载',page_icon='📚',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
[data-testid="stHeader"], [data-testid="stToolbar"], footer {display:none}
.block-container{padding:0!important;max-width:100%!important}
[data-testid="stMainBlockContainer"]{padding:0!important}
iframe[title="streamlit_app.skill_library"]{width:100%;height:100vh!important;min-height:0;border:0}
html,body,[data-testid="stAppViewContainer"]{background:#f6f7f2}
</style>''',unsafe_allow_html=True)
library=components.declare_component('skill_library',path=str(Path(__file__).parent/'site'))
library(key='skill-library',package=st.query_params.get('package'),file=st.query_params.get('file'))
