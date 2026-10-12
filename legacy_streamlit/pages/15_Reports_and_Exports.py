import streamlit as st
import pandas as pd
from database.database import get_institute_report_data, get_institute_overview, get_sla_summary, get_all_complaints, log_audit
from utils.advanced_features import require_role, base_style
st.set_page_config(page_title='Reports & Exports',page_icon='📊',layout='wide'); base_style(); admin=require_role('Institute Admin'); iid=admin[1]
st.title('📊 Reports & Exports'); st.caption('Phase 15 + Phase 18 — analytics, operational reports and downloads')
info=get_institute_overview(iid); sla=get_sla_summary(iid)
c1,c2,c3,c4=st.columns(4); c1.metric('Total Complaints',info['complaints']); c2.metric('Resolution Rate',f"{(info['resolved']/info['complaints']*100 if info['complaints'] else 0):.1f}%"); c3.metric('Overdue',sla['overdue']); c4.metric('Avg Resolution',f"{sla['avg_resolution_hours']} h")
rows=get_institute_report_data(iid); df=pd.DataFrame(rows,columns=['Complaint ID','Title','Location','Category','Priority','Status','Department','Created At','Student ID'])
if not df.empty:
    st.subheader('Complaint Report'); st.dataframe(df,use_container_width=True,hide_index=True)
    csv=df.to_csv(index=False).encode('utf-8'); st.download_button('⬇️ Download CSV',csv,'campus_guardian_complaints.csv','text/csv',use_container_width=True)
    summary=df.groupby(['Status']).size().reset_index(name='Count'); st.subheader('Status Distribution'); st.bar_chart(summary.set_index('Status'))
    dept=df.assign(Department=df['Department'].fillna('Unassigned')).groupby('Department').size().reset_index(name='Complaints'); st.subheader('Department Workload'); st.bar_chart(dept.set_index('Department'))
    log_audit(iid,admin[2],admin[6],'Report Viewed','Report','complaints')
else: st.info('No complaint data available.')
