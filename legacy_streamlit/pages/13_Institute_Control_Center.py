import streamlit as st
import pandas as pd
from database.database import (
    get_institute_overview, get_departments_by_institute, get_campus_locations,
    get_complaint_workflow, update_complaint_workflow, get_all_complaints,
    get_complaint_history, add_complaint_history, log_audit, get_institute_by_code
)
from utils.advanced_features import require_role, base_style

st.set_page_config(page_title='Institute Control Center', page_icon='🏢', layout='wide')
base_style(); admin=require_role('Institute Admin'); institute_id=admin[1]; admin_id=admin[2]
st.title('🏢 Institute Control Center'); st.caption('Phase 13 + Phase 14 — institute operations, SLA and complaint workflow')

info=get_institute_overview(institute_id)
c1,c2,c3,c4,c5,c6=st.columns(6)
for c,label,key in [(c1,'Students','students'),(c2,'Admins','admins'),(c3,'Departments','departments'),(c4,'Complaints','complaints'),(c5,'Resolved','resolved'),(c6,'Critical','critical')]: c.metric(label,info[key])

tab1,tab2,tab3=st.tabs(['🏫 Institute Operations','⏱️ Complaint SLA','🧾 Complaint History'])
with tab1:
    st.subheader('Departments')
    deps=get_departments_by_institute(institute_id)
    st.dataframe(pd.DataFrame(deps,columns=['ID','Institute','Department','Description','Status','Created','Updated']) if deps else pd.DataFrame(columns=['Department','Status']),use_container_width=True,hide_index=True)
    st.subheader('Campus Locations')
    locs=get_campus_locations(institute_id)
    loc_df=pd.DataFrame(locs) if locs else pd.DataFrame(columns=['location_name','location_type'])
    if not loc_df.empty:
        loc_df=loc_df.rename(columns={'location_name':'Name','location_type':'Type','latitude':'Latitude','longitude':'Longitude','is_active':'Active','created_at':'Created','updated_at':'Updated'})
        st.dataframe(loc_df[['Name','Latitude','Longitude','Type','Active','Created','Updated']],use_container_width=True,hide_index=True)
    else:
        st.dataframe(loc_df,use_container_width=True,hide_index=True)
    st.info('Use Department Management and Campus Locations Management pages for detailed editing.')

with tab2:
    complaints=get_all_complaints(institute_id)
    if not complaints: st.info('No complaints available.'); st.stop()
    labels={c[1]:f"{c[1]} — {c[4]}" for c in complaints}
    cid=st.selectbox('Select complaint',list(labels),format_func=lambda x:labels[x])
    wf=get_complaint_workflow(cid,institute_id)
    _,_,assigned,sla,due,esc,res_notes,resolved_at,rating,feedback,feedback_at,_=wf
    st.metric('SLA due',due or '—')
    st.write(f'**Current escalation:** Level {esc}  |  **Current assignee:** {assigned or "Unassigned"}')
    with st.form('workflow'):
        assignee=st.text_input('Assigned staff / team',value=assigned or '')
        sla_hours=st.number_input('SLA hours',min_value=1,max_value=720,value=int(sla or 48),step=1)
        escalation=st.number_input('Escalation level',min_value=0,max_value=5,value=int(esc or 0),step=1)
        notes=st.text_area('Resolution / internal notes',value=res_notes or '')
        if st.form_submit_button('💾 Save Workflow'):
            update_complaint_workflow(cid,institute_id,assignee,sla_hours,escalation,notes)
            add_complaint_history(institute_id,cid,admin_id,'Workflow Updated',note=f'Assignee={assignee or "Unassigned"}, SLA={sla_hours}h, Escalation={escalation}')
            log_audit(institute_id,admin_id,admin[6],'Complaint workflow updated','Complaint',cid,f'SLA={sla_hours}; escalation={escalation}')
            st.success('Workflow updated successfully.'); st.rerun()

with tab3:
    complaints=get_all_complaints(institute_id)
    if complaints:
        cid=st.selectbox('Complaint for history', [c[1] for c in complaints], key='history_cid')
        hist=get_complaint_history(cid,institute_id)
        if hist:
            st.dataframe(pd.DataFrame(hist,columns=['ID','Actor','Action','Old','New','Note','Created']),use_container_width=True,hide_index=True)
        else: st.info('No workflow history recorded yet.')
