import streamlit as st
from database.database import get_user_profile, upsert_user_profile, change_user_password, log_audit, get_institute_by_code
from utils.advanced_features import require_role, base_style
st.set_page_config(page_title='My Profile',page_icon='👤',layout='wide'); base_style()
student=require_role('Student'); institute_id=student[1]; uid=student[2]
st.title('👤 My Profile'); st.caption('Phase 12 — profile, contact details and account security')
inst=None
for row in []: pass
profile=get_user_profile(uid,institute_id) or ('','','','','','','')
col1,col2=st.columns(2)
with col1:
    st.subheader('Account')
    st.write(f'**Name:** {student[3]}'); st.write(f'**Student ID:** {uid}'); st.write(f'**Email:** {student[4] or "Not provided"}'); st.write(f'**Status:** {student[7]}'); st.write(f'**Last login:** {student[9] or "First login"}')
with col2:
    st.subheader('Profile details')
    with st.form('profile'):
        phone=st.text_input('Phone',value=profile[0] or '')
        department=st.text_input('Department',value=profile[1] or '')
        designation=st.text_input('Designation',value=profile[2] or '')
        address=st.text_area('Address',value=profile[3] or '')
        emergency=st.text_input('Emergency contact',value=profile[4] or '')
        bio=st.text_area('Bio',value=profile[5] or '')
        if st.form_submit_button('💾 Save Profile'):
            upsert_user_profile(uid,institute_id,phone,department,designation,address,emergency,bio); log_audit(institute_id,uid,student[6],'Profile Updated','User',uid); st.success('Profile updated.')
st.divider(); st.subheader('🔐 Change Password')
with st.form('password'):
    current=st.text_input('Current password',type='password'); new=st.text_input('New password',type='password'); confirm=st.text_input('Confirm new password',type='password')
    if st.form_submit_button('Change Password'):
        if new!=confirm: st.error('New passwords do not match.')
        else:
            result=change_user_password(uid,institute_id,current,new)
            (st.success if result['success'] else st.error)(result['message'])
            if result['success']: log_audit(institute_id,uid,student[6],'Password Changed','User',uid)
