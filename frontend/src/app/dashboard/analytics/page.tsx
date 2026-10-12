"use client";
import { useEffect,useState } from "react";
import AppShell from "@/components/app-shell";
import { apiFetch } from "@/lib/api";

type Item={label:string;count:number};
type A={total:number;by_status:Item[];by_priority:Item[];by_category:Item[];by_department:Item[];monthly:{month:string;count:number}[]};

function Block({title,items}:{title:string;items:Item[]}) {
  const max=Math.max(1,...items.map(x=>x.count));
  return <section className="card">
    <h2>{title}</h2>
    <div className="bars">
      {items.length===0?<p className="muted">No data.</p>:items.slice(0,10).map(x=><div className="bar-row" key={`${title}-${x.label}`}>
        <div className="bar-label"><span>{x.label}</span><strong>{x.count}</strong></div>
        <div className="bar-track"><div className="bar-fill" style={{width:`${Math.max(4,(x.count/max)*100)}%`}}/></div>
      </div>)}
    </div>
  </section>;
}

export default function Analytics() {
  const [data,setData]=useState<A|null>(null);
  const [error,setError]=useState("");
  useEffect(()=>{apiFetch<A>("/management/analytics").then(setData).catch(e=>setError(e instanceof Error?e.message:"Could not load analytics."));},[]);
  return <AppShell>
    <header className="workspace-head">
      <div><span className="eyebrow">Advanced analytics</span><h1>Analytics</h1><p className="muted">Understand complaint volume, status, priorities and routing demand.</p></div>
    </header>
    {error&&<div className="notice">{error}</div>}
    {data && <>
      <div className="kpis five"><div className="kpi"><span className="muted">Total complaints</span><strong>{data.total}</strong></div><div className="kpi"><span className="muted">Categories</span><strong>{data.by_category.length}</strong></div><div className="kpi"><span className="muted">Departments</span><strong>{data.by_department.length}</strong></div><div className="kpi"><span className="muted">Priority groups</span><strong>{data.by_priority.length}</strong></div><div className="kpi"><span className="muted">Months</span><strong>{data.monthly.length}</strong></div></div>
      <div className="section-grid">
        <Block title="By status" items={data.by_status}/>
        <Block title="By priority" items={data.by_priority}/>
        <Block title="By category" items={data.by_category}/>
        <Block title="By department" items={data.by_department}/>
      </div>
      <section className="card">
        <h2>Monthly volume</h2>
        {data.monthly.length===0?<p className="muted">No monthly data yet.</p>:<div className="monthly-list">{data.monthly.map(x=><div className="monthly-row" key={x.month}><span>{x.month}</span><strong>{x.count}</strong></div>)}</div>}
      </section>
    </>}
  </AppShell>;
}
