import streamlit as st
import pandas as pd
from database.database import get_platform_overview, get_all_institutes, get_audit_logs
from utils.advanced_features import require_role, base_style
st.set_page_config(page_title='Platform Intelligence',page_icon='🧠',layout='wide'); base_style(); admin=require_role('Platform Admin')
st.title('🧠 Platform Intelligence'); st.caption('Phase 16 — platform-level intelligence and health overview')
o=get_platform_overview(); cols=st.columns(8)
for c,label,key in zip(cols,['Institutes','Approved','Students','Admins','Complaints','Resolved','Pending','Critical'],['institutes','approved_institutes','students','admins','complaints','resolved','pending','critical']): c.metric(label,o[key])
inst=get_all_institutes(); df=pd.DataFrame(inst,columns=['ID','Code','Name','Type','Email','Phone','Address','City','State','Status','Created','Approved']) if inst else pd.DataFrame()
if not df.empty:
    st.subheader('Institute Portfolio'); st.dataframe(df[['Code','Name','Type','City','State','Status','Created']],use_container_width=True,hide_index=True)
logs=get_audit_logs(None,100); st.subheader('Recent Platform Activity'); st.dataframe(pd.DataFrame(logs,columns=['ID','Institute','Actor','Role','Action','Entity','Entity ID','Details','Created']),use_container_width=True,hide_index=True)
