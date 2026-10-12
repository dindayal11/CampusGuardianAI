"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import AppShell from "@/components/app-shell";
import { apiFetch } from "@/lib/api";

const CampusMap = dynamic(() => import("@/components/campus-map"), { ssr: false });

type MapData = {
  settings: {
    center_latitude: number | null;
    center_longitude: number | null;
    default_zoom: number;
    heatmap_enabled: boolean;
    complaint_markers_enabled: boolean;
    hotspots_enabled: boolean;
    campus_locations_enabled: boolean;
  };
  locations: Array<{ id:number; location_name:string; latitude:number; longitude:number; location_type:string }>;
  complaints: Array<{ complaint_id:string; location:string; category:string|null; priority:string|null; status:string }>;
};

export default function Campus() {
  const [data,setData] = useState<MapData|null>(null);
  const [role,setRole] = useState("");
  const [name,setName] = useState("");
  const [lat,setLat] = useState("");
  const [lng,setLng] = useState("");
  const [type,setType] = useState("General");
  const [error,setError] = useState("");
  const [centerLat,setCenterLat] = useState("");
  const [centerLng,setCenterLng] = useState("");
  const [zoom,setZoom] = useState("17");
  const [saving,setSaving] = useState(false);

  async function load() {
    try {
      setError("");
      const a = await apiFetch<{user:{role:string}}>("/auth/me");
      setRole(a.user.role);
      const m = await apiFetch<MapData>("/management/campus-map");
      setData(m);
      setCenterLat(m.settings.center_latitude == null ? "" : String(m.settings.center_latitude));
      setCenterLng(m.settings.center_longitude == null ? "" : String(m.settings.center_longitude));
      setZoom(String(m.settings.default_zoom));
    } catch(e) {
      setError(e instanceof Error ? e.message : "Could not load campus safety.");
    }
  }

  useEffect(() => { load(); }, []);

  async function add() {
    try {
      setSaving(true);
      await apiFetch("/management/campus-locations", {
        method:"POST",
        body:JSON.stringify({
          location_name:name,
          latitude:Number(lat),
          longitude:Number(lng),
          location_type:type,
        })
      });
      setName(""); setLat(""); setLng("");
      await load();
    } catch(e) {
      setError(e instanceof Error ? e.message : "Could not add campus location.");
    } finally {
      setSaving(false);
    }
  }

  async function saveSettings() {
    try {
      setSaving(true);
      await apiFetch("/management/campus-map/settings", {
        method:"PUT",
        body:JSON.stringify({
          center_latitude:Number(centerLat),
          center_longitude:Number(centerLng),
          default_zoom:Number(zoom),
          heatmap_enabled:true,
          complaint_markers_enabled:true,
          hotspots_enabled:true,
          campus_locations_enabled:true,
        })
      });
      await load();
    } catch(e) {
      setError(e instanceof Error ? e.message : "Could not save map settings.");
    } finally {
      setSaving(false);
    }
  }

  async function remove(id:number) {
    if(!confirm("Archive this campus location?")) return;
    try {
      await apiFetch(`/management/campus-locations/${id}`,{method:"DELETE"});
      await load();
    } catch(e) {
      setError(e instanceof Error ? e.message : "Could not archive location.");
    }
  }

  const mapCenter: [number,number] =
    data?.settings.center_latitude != null && data?.settings.center_longitude != null
      ? [data.settings.center_latitude, data.settings.center_longitude]
      : data?.locations[0]
        ? [data.locations[0].latitude, data.locations[0].longitude]
        : [20.5937,78.9629];

  return <AppShell>
    <header className="workspace-head">
      <div>
<span className="eyebrow">
  {role === "Student" ? "Your Campus" : "Campus safety intelligence"}
</span>

<h1>{role === "Student" ? "Campus Map" : "Campus Safety"}</h1>

<p className="muted">
  {role === "Student"
    ? "View campus locations configured by your institute."
    : "Manage trusted campus locations and review complaint risk signals."}
</p>
      </div>
    </header>

    {error && <div className="notice">{error}</div>}

    {data && <section className="card map-card">
      <div className="section-head">
        <div><h2>Campus map</h2><p className="muted">Locations configured by the institute.</p></div>
        <span className="pill">{data.locations.length} locations</span>
      </div>
      <CampusMap center={mapCenter} zoom={data.settings.default_zoom} locations={data.locations} />
    </section>}

    {role==="Institute Admin" && <section className="card form-card">
      <h2>Add campus location</h2>
      <div className="form-grid">
        <div className="field"><label>Name</label><input value={name} onChange={e=>setName(e.target.value)} placeholder="Main Gate"/></div>
        <div className="field"><label>Latitude</label><input type="number" step="any" value={lat} onChange={e=>setLat(e.target.value)}/></div>
        <div className="field"><label>Longitude</label><input type="number" step="any" value={lng} onChange={e=>setLng(e.target.value)}/></div>
        <div className="field"><label>Type</label><input value={type} onChange={e=>setType(e.target.value)}/></div>
      </div>
      <button className="btn primary" disabled={saving || !name.trim() || !lat || !lng} onClick={add}>
        {saving ? "Saving…" : "Add location"}
      </button>
    </section>}

    {role==="Institute Admin" && <section className="card form-card">
      <h2>Map settings</h2>
      <div className="form-grid">
        <div className="field"><label>Center latitude</label><input type="number" step="any" value={centerLat} onChange={e=>setCenterLat(e.target.value)}/></div>
        <div className="field"><label>Center longitude</label><input type="number" step="any" value={centerLng} onChange={e=>setCenterLng(e.target.value)}/></div>
        <div className="field"><label>Default zoom</label><input type="number" min="1" max="22" value={zoom} onChange={e=>setZoom(e.target.value)}/></div>
      </div>
      <button className="btn" disabled={saving || !centerLat || !centerLng} onClick={saveSettings}>Save map settings</button>
    </section>}

    
<div className="section-grid">
  <section className="card">
    <h2>Configured locations</h2>
    {data?.locations.length ? (
      data.locations.map((l) => (
        <div className="list-row" key={l.id}>
          <div>
            <strong>{l.location_name}</strong>
            <span>
              {l.location_type} · {l.latitude}, {l.longitude}
            </span>
          </div>
          {role === "Institute Admin" && (
            <button
              className="btn danger ghost"
              onClick={() => remove(l.id)}
            >
              Archive
            </button>
          )}
        </div>
      ))
    ) : (
      <p className="muted">No campus locations configured.</p>
    )}
  </section>

  {role === "Institute Admin" && (
    <section className="card">
      <h2>Risk signal</h2>
      <div className="mini-grid">
        <div>
          <span className="muted">Visible complaints</span>
          <strong>{data?.complaints.length ?? 0}</strong>
        </div>
        <div>
          <span className="muted">Critical</span>
          <strong>
            {data?.complaints.filter((c) => c.priority === "Critical").length ?? 0}
          </strong>
        </div>
        <div>
          <span className="muted">High</span>
          <strong>
            {data?.complaints.filter((c) => c.priority === "High").length ?? 0}
          </strong>
        </div>
      </div>

      <div className="risk-list">
        {data?.complaints.slice(0, 12).map((c) => (
          <div className="risk-row" key={c.complaint_id}>
            <div>
              <strong>{c.location}</strong>
              <span>
                {c.complaint_id} · {c.category || "General"}
              </span>
            </div>
            <span className={`pill ${String(c.priority || "").toLowerCase()}`}>
              {c.priority || "—"}
            </span>
          </div>
        ))}
      </div>
    </section>
  )}
</div>

  </AppShell>;
}
