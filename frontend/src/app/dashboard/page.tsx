"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import AppShell from "@/components/app-shell";

type User = { subject: string; name: string; role: string; email?: string | null; institute_code?: string | null };
type Auth = { user: User };
type Overview = {
  complaints:number; pending:number; in_progress:number; resolved:number; rejected:number; critical:number; high:number;
  departments?:number; students?:number; overdue?:number; institutes?:number; users?:number;
};
type Complaint = { complaint_id:string; title:string; priority:string|null; status:string; department:string|null; created_at:string|null };
type Intelligence = { recommendations:string[]; hotspots:{location:string;risk_score:number;risk_level:string;total_complaints:number}[]; complaint_count:number };

function OverviewPage() {
  const [auth,setAuth]=useState<Auth|null>(null);
  const [stats,setStats]=useState<Overview|null>(null);
  const [recent,setRecent]=useState<Complaint[]>([]);
  const [error,setError]=useState("");
  const [intelligence,setIntelligence]=useState<Intelligence|null>(null);

  useEffect(() => {
    (async () => {
      try {
        const a=await apiFetch<Auth>("/auth/me"); setAuth(a);
        const s=a.user.role==="Student"
          ? await apiFetch<{items:Complaint[];total:number}>("/complaints")
          : await apiFetch<Overview>("/admin/overview");
        if (a.user.role==="Student") {
          const items=(s as {items:Complaint[];total:number}).items;
          setStats({
            complaints:(s as {total:number}).total,pending:items.filter(x=>x.status==="Pending").length,
            in_progress:items.filter(x=>x.status==="In Progress").length,resolved:items.filter(x=>x.status==="Resolved").length,
            rejected:items.filter(x=>x.status==="Rejected").length,critical:items.filter(x=>x.priority==="Critical").length,
            high:items.filter(x=>x.priority==="High").length
          });
          setRecent(items.slice(0,5));
        } else {
          setStats(s as Overview);
          const intel=await apiFetch<Intelligence>("/management/intelligence");
          setIntelligence(intel);
          const c=await apiFetch<{items:Complaint[]}>("/complaints");
          setRecent(c.items.slice(0,5));
        }
      } catch(e) { setError(e instanceof Error?e.message:"Could not load dashboard."); }
    })();
  },[]);

  const isStudent=auth?.user.role==="Student";
  return (
    <AppShell>
      <header className="workspace-head">
        <div><span className="eyebrow">Secure workspace</span><h1>{isStudent ? "Your campus updates" : "Institute operations"}</h1><p className="muted">{isStudent ? "Report an issue, track progress and stay informed." : "Monitor complaints, teams, communication and safety signals in one place."}</p></div>
        {isStudent ? <Link className="btn primary" href="/dashboard/report">+ Report an issue</Link> : <Link className="btn primary" href="/dashboard/complaints">Manage complaints</Link>}
      </header>
      {error && <div className="notice" role="alert">{error}</div>}
      {stats ? (
        <>
          <div className="kpis five">
            {[
              ["Complaints",stats.complaints],["Pending",stats.pending],["In progress",stats.in_progress],
              ["Resolved",stats.resolved],["Critical",stats.critical]
            ].map(([label,value])=><div className="kpi" key={label as string}><span className="muted">{label}</span><strong>{value as number}</strong></div>)}
          </div>
          <div className="section-grid">
            <section className="card">
              <div className="section-head"><div><h2>Recent complaints</h2><p className="muted">Latest activity in your visible scope.</p></div><Link href="/dashboard/complaints" className="text-link">View all →</Link></div>
              {recent.length===0?<p className="muted">No complaints yet.</p>:recent.map(c=><Link className="list-row" key={c.complaint_id} href={`/dashboard/complaints/${c.complaint_id}`}><div><strong>{c.title}</strong><span>{c.complaint_id} · {c.department||"Unassigned"}</span></div><span className={`status ${c.status.toLowerCase().replaceAll(" ","-")}`}>{c.status}</span></Link>)}
            </section>
            <section className="card">
              <h2>Quick actions</h2><p className="muted">Keep the next task one click away.</p>
              <div className="quick-grid">
                {isStudent ? <>
                  <Link className="quick" href="/dashboard/report"><strong>Report issue</strong><span>Create a structured complaint with local AI analysis.</span></Link>
                  <Link className="quick" href="/dashboard/campus">
  <strong>Campus Map</strong>
  <span>View campus locations configured by your institute.</span>
</Link>
                </> : <>
                  <Link className="quick" href="/dashboard/students"><strong>Manage students</strong><span>Create accounts and control student access.</span></Link>
                  <Link className="quick" href="/dashboard/departments"><strong>Departments</strong><span>Maintain routing teams and assignments.</span></Link>
                  <Link className="quick" href="/dashboard/campus"><strong>Safety map</strong><span>Manage locations and campus safety settings.</span></Link>
                  <Link className="quick" href="/dashboard/reports"><strong>Reports</strong><span>Filter and export operational complaint data.</span></Link>
                </>}
              </div>
            </section>
          </div>
          
{!isStudent && intelligence && (
  <section className="guardian-admin-ai">
    <div className="guardian-admin-ai-header">
      <div className="guardian-admin-ai-icon">
        ✦
      </div>

      <div className="guardian-admin-ai-heading">
        <span className="guardian-admin-ai-eyebrow">
          INTELLIGENCE &amp; PREVENTION
        </span>
        <h2>Guardian AI Analysis</h2>
        <p>
          AI-assisted campus safety insights and actionable
          recommendations based on available complaint data.
        </p>
      </div>

      <span className="guardian-admin-ai-count">
        {intelligence.complaint_count} analysed
      </span>
    </div>

    <div className="guardian-admin-ai-divider" />

    {intelligence.recommendations.length === 0 ? (
      <div className="guardian-admin-ai-empty">
        No safety recommendations available at this time.
      </div>
    ) : (
      <div className="guardian-admin-ai-recommendations">
        {intelligence.recommendations.slice(0, 6).map((item, i) => (
          <div className="guardian-admin-ai-recommendation" key={i}>
            <div className="guardian-admin-ai-number">
              {String(i + 1).padStart(2, "0")}
            </div>

            <div>
              <h3>Recommendation {i + 1}</h3>
              <p>{item}</p>
            </div>
          </div>
        ))}
      </div>
    )}

    {intelligence.hotspots.length > 0 && (
      <div className="guardian-admin-hotspots">
        <h3>Campus Risk Hotspots</h3>

        <div className="guardian-admin-hotspot-grid">
          {intelligence.hotspots.slice(0, 3).map((hotspot) => (
            <div
              className="guardian-admin-hotspot"
              key={hotspot.location}
            >
              <span>{hotspot.location}</span>
              <strong>
                {hotspot.risk_score}/100
              </strong>
              <small>{hotspot.risk_level} risk</small>
            </div>
          ))}
        </div>
      </div>
    )}

    <p className="guardian-admin-ai-note">
      Guardian AI provides decision-support recommendations.
      Institute administrators should review findings before
      taking action.
    </p>
  </section>
)}

          
{!isStudent && (
  <section className="guardian-operations">
    <div className="guardian-operations-header">
      <div>
        <span className="eyebrow">OPERATIONAL OVERVIEW</span>
        <h2>Operations Snapshot</h2>
        <p className="muted">
          Current institute activity and complaint management metrics.
        </p>
      </div>
    </div>

    <div className="guardian-operations-grid">
      {[
        { label: "High priority", value: stats.high },
        { label: "Rejected", value: stats.rejected },
        { label: "Departments", value: stats.departments ?? 0 },
        { label: "Students", value: stats.students ?? 0 },
        { label: "Overdue", value: stats.overdue ?? 0 },
      ].map((item) => (
        <div className="guardian-operation-item" key={item.label}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
        </div>
      ))}
    </div>
  </section>
)}

        </>
      ) : <div className="loading-card">Loading dashboard…</div>}
    </AppShell>
  );
}
export default function Dashboard(){ return <OverviewPage/>; }
