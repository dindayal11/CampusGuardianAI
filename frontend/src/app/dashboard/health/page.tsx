"use client";
import { useEffect,useState } from "react";
import AppShell from "@/components/app-shell";
import { apiFetch } from "@/lib/api";
type H={name:string;status:"PASS"|"WARN"|"FAIL";detail:string};
export default function Health(){
 const[checks,setChecks]=useState<H[]>([]);const[healthy,setHealthy]=useState(false);const[error,setError]=useState("");
 useEffect(()=>{apiFetch<{checks:H[];healthy:boolean}>("/management/system-health").then(x=>{setChecks(x.checks);setHealthy(x.healthy);}).catch(e=>setError(e instanceof Error?e.message:"Could not load system health."));},[]);
 return <AppShell><header className="workspace-head"><div><span className="eyebrow">Platform operations</span><h1>System health</h1><p className="muted">Live checks for the production API foundation.</p></div><span className={`health ${healthy?"good":"bad"}`}>{healthy?"Healthy":"Attention needed"}</span></header>{error&&<div className="notice">{error}</div>}<section className="health-grid">{checks.map(c=><article className="card health-card" key={c.name}><div className={`health-dot ${c.status.toLowerCase()}`}/><div><h3>{c.name}</h3><strong>{c.status}</strong><p className="muted">{c.detail}</p></div></article>)}</section></AppShell>
}
