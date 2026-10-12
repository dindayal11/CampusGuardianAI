"use client";
import { useEffect,useState } from "react";
import AppShell from "@/components/app-shell";
import { apiFetch } from "@/lib/api";
type N={id:number;complaint_id:string|null;notification_type:string;title:string;message:string;is_read:boolean;created_at:string|null};
type P={in_app_enabled:boolean;complaint_updates:boolean;priority_alerts:boolean;admin_alerts:boolean};
export default function Notifications(){
 const[items,setItems]=useState<N[]>([]);const[prefs,setPrefs]=useState<P|null>(null);const[error,setError]=useState("");const[saving,setSaving]=useState(false);
 async function load(){try{const [n,p]=await Promise.all([apiFetch<{items:N[];unread:number}>("/notifications"),apiFetch<P>("/notifications/preferences")]);setItems(n.items);setPrefs(p);}catch(e){setError(e instanceof Error?e.message:"Could not load notifications.");}}
 useEffect(()=>{load();},[]);
 async function read(id:number){try{await apiFetch(`/notifications/${id}/read`,{method:"PATCH"});await load();}catch(e){setError(e instanceof Error?e.message:"Could not mark notification.");}}
 async function readAll(){try{await apiFetch("/notifications/read-all",{method:"PATCH"});await load();}catch(e){setError(e instanceof Error?e.message:"Could not mark notifications.");}}
 async function savePrefs(){if(!prefs)return;setSaving(true);setError("");try{await apiFetch("/notifications/preferences",{method:"PATCH",body:JSON.stringify(prefs)});await load();}catch(e){setError(e instanceof Error?e.message:"Could not save notification preferences.");}finally{setSaving(false);}}
 return <AppShell><header className="workspace-head"><div><span className="eyebrow">Inbox</span><h1>Notifications</h1><p className="muted">Complaint updates, announcements and important account alerts.</p></div><button className="btn" onClick={readAll}>Mark all read</button></header>{error&&<div className="notice">{error}</div>}
 <div className="section-grid"><section className="card">{items.length===0?<p className="muted">You&apos;re all caught up.</p>:items.map(n=><article key={n.id} className={`notification ${n.is_read?"read":"unread"}`}><div><div className="notif-top"><strong>{n.title}</strong><span className="pill">{n.notification_type}</span></div><p>{n.message}</p><small>{n.created_at||"—"}{n.complaint_id?` · ${n.complaint_id}`:""}</small></div>{!n.is_read&&<button className="btn" onClick={()=>read(n.id)}>Mark read</button>}</article>)}</section>
 {prefs&&<section className="card"><h2>Notification preferences</h2><p className="muted">Choose which in-app events should reach this account.</p><div className="pref-list">{([['in_app_enabled','In-app notifications'],['complaint_updates','Complaint status updates'],['priority_alerts','Priority and SLA alerts'],['admin_alerts','Administrative alerts']] as const).map(([key,label])=><label className="check" key={key}><input type="checkbox" checked={prefs[key]} onChange={e=>setPrefs({...prefs,[key]:e.target.checked})}/><span><strong>{label}</strong><small>Applies to future notifications.</small></span></label>)}</div><button className="btn primary" disabled={saving} onClick={savePrefs}>{saving?'Saving…':'Save preferences'}</button></section>}</div></AppShell>
}
