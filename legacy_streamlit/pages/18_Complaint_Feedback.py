import streamlit as st
from database.database import get_complaints_by_student,get_complaint_workflow,submit_complaint_feedback
from utils.advanced_features import require_role,base_style
st.set_page_config(page_title='Complaint Feedback',page_icon='⭐',layout='wide'); base_style(); student=require_role('Student'); iid=student[1]; sid=student[2]
st.title('⭐ Complaint Feedback'); st.caption('Phase 14 — resolution feedback and service quality')
rows=get_complaints_by_student(sid,iid); resolved=[r for r in rows if r[11]=='Resolved']
if not resolved: st.info('Feedback becomes available after a complaint is resolved.'); st.stop()
for r in resolved:
    cid=r[1]; wf=get_complaint_workflow(cid,iid); current=wf[8]
    with st.container(border=True):
        st.markdown(f'### {cid} — {r[4]}'); st.caption(f'Resolved on: {wf[7] or "—"}')
        if current: st.success(f'Already rated: {current}/5')
        with st.form(f'fb_{cid}'):
            rating=st.slider('Rating',1,5,int(current or 5)); comment=st.text_area('Comment',value=wf[9] or '')
            if st.form_submit_button('⭐ Submit Feedback'):
                if submit_complaint_feedback(cid,iid,sid,rating,comment): st.success('Thank you for your feedback.'); st.rerun()
                else: st.error('Feedback could not be saved.')
