
"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import AppShell from "@/components/app-shell";
import { apiFetch } from "@/lib/api";

type Institute = {
  id: number;
  institute_code: string;
  name: string;
  institute_type: string;
  email: string;
  phone: string | null;
  city: string | null;
  state: string | null;
  status: string;
  created_at: string | null;
};

type Overview = {
  pending_institutes: number;
  approved_institutes: number;
  blocked_institutes: number;
  institutes: number;
  users: number;
  complaints: number;
  resolved: number;
  critical: number;
};

type StatusFilter = "All" | "Pending" | "Approved" | "Rejected" | "Blocked";

const STATUS_OPTIONS: StatusFilter[] = [
  "All",
  "Pending",
  "Approved",
  "Rejected",
  "Blocked",
];

function statusClass(status: string) {
  switch (status) {
    case "Approved":
      return "status-approved";
    case "Pending":
      return "status-pending";
    case "Rejected":
      return "status-rejected";
    case "Blocked":
      return "status-blocked";
    default:
      return "";
  }
}

function formatDate(value: string | null) {
  if (!value) return "—";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function Platform() {
  const [rows, setRows] = useState<Institute[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("All");
  const [typeFilter, setTypeFilter] = useState("All");

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(async (showRefresh = false) => {
    setError("");

    if (showRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const [institutes, stats] = await Promise.all([
        apiFetch<Institute[]>("/management/platform/institutes"),
        apiFetch<Overview>("/management/platform/overview"),
      ]);

      setRows(institutes);
      setOverview(stats);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not load platform data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const instituteTypes = useMemo(
    () =>
      Array.from(
        new Set(rows.map((row) => row.institute_type).filter(Boolean))
      ).sort((a, b) => a.localeCompare(b)),
    [rows]
  );

  const filteredRows = useMemo(() => {
    const query = search.trim().toLowerCase();

    return rows.filter((row) => {
      const matchesSearch =
        !query ||
        [
          row.name,
          row.institute_code,
          row.email,
          row.city,
          row.state,
          row.institute_type,
        ].some((value) => value?.toLowerCase().includes(query));

      const matchesStatus =
        statusFilter === "All" || row.status === statusFilter;

      const matchesType =
        typeFilter === "All" || row.institute_type === typeFilter;

      return matchesSearch && matchesStatus && matchesType;
    });
  }, [rows, search, statusFilter, typeFilter]);

  async function setStatus(id: number, status: string) {
    const institute = rows.find((row) => row.id === id);
    if (!institute || updatingId !== null) return;

    const actionLabel =
      status === "Approved"
        ? "approve"
        : status === "Rejected"
          ? "reject"
          : "block";

    if (
      !window.confirm(
        `Are you sure you want to ${actionLabel} "${institute.name}"?`
      )
    ) {
      return;
    }

    setUpdatingId(id);
    setError("");
    setMessage("");

    try {
      await apiFetch(`/management/platform/institutes/${id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });

      setMessage(`${institute.name}: status updated to ${status}.`);
      await load(true);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not update institute status."
      );
    } finally {
      setUpdatingId(null);
    }
  }

  function renderActions(institute: Institute) {
    const busy = updatingId === institute.id || updatingId !== null;

    switch (institute.status) {
      case "Pending":
        return (
          <>
            <button
              className="btn primary"
              disabled={busy}
              onClick={() => void setStatus(institute.id, "Approved")}
            >
              {updatingId === institute.id ? "Updating…" : "Approve"}
            </button>
            <button
              className="btn danger ghost"
              disabled={busy}
              onClick={() => void setStatus(institute.id, "Rejected")}
            >
              Reject
            </button>
          </>
        );

      case "Approved":
        return (
          <button
            className="btn danger ghost"
            disabled={busy}
            onClick={() => void setStatus(institute.id, "Blocked")}
          >
            Block
          </button>
        );

      case "Blocked":
      case "Rejected":
        return (
          <button
            className="btn primary"
            disabled={busy}
            onClick={() => void setStatus(institute.id, "Approved")}
          >
            Approve
          </button>
        );

      default:
        return <span className="muted">No actions available</span>;
    }
  }

  return (
    <AppShell>
      <header className="workspace-head">
        <div>
          <span className="eyebrow">Platform administration</span>
          <h1>Institute Management</h1>
          <p className="muted">
            Review registrations, manage institute access and monitor platform
            activity.
          </p>
        </div>

        <button
          className="btn"
          disabled={loading || refreshing || updatingId !== null}
          onClick={() => void load(true)}
        >
          {refreshing ? "Refreshing…" : "Refresh data"}
        </button>
      </header>

      {error && (
        <div className="notice" role="alert">
          <strong>Something went wrong.</strong> {error}
          <button className="btn" onClick={() => void load(true)}>
            Try again
          </button>
        </div>
      )}

      {message && (
        <div className="success-note" role="status">
          {message}
          <button
            className="btn ghost"
            onClick={() => setMessage("")}
          >
            Dismiss
          </button>
        </div>
      )}

      {overview && (
        <div className="kpis five">
          <div className="kpi">
            <span className="muted">Total institutes</span>
            <strong>{overview.institutes}</strong>
          </div>
          <div className="kpi">
            <span className="muted">Pending review</span>
            <strong>{overview.pending_institutes}</strong>
          </div>
          <div className="kpi">
            <span className="muted">Approved</span>
            <strong>{overview.approved_institutes}</strong>
          </div>
          <div className="kpi">
            <span className="muted">Blocked</span>
            <strong>{overview.blocked_institutes}</strong>
          </div>
          <div className="kpi">
            <span className="muted">Platform users</span>
            <strong>{overview.users}</strong>
          </div>
        </div>
      )}

      <section className="card table-card">
        <div className="section-heading">
          <div>
            <h2>Registered institutes</h2>
            <p className="muted">
              Search, filter and manage institute access.
            </p>
          </div>
          <span className="pill">
            {loading ? "Loading…" : `${filteredRows.length} results`}
          </span>
        </div>

        <div className="form-grid">
          <div className="field">
            <label htmlFor="institute-search">Search institutes</label>
            <input
              id="institute-search"
              type="search"
              placeholder="Name, code, email, city…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="institute-status">Filter by status</label>
            <select
              id="institute-status"
              value={statusFilter}
              onChange={(e) =>
                setStatusFilter(e.target.value as StatusFilter)
              }
            >
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {status === "All" ? "All statuses" : status}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label htmlFor="institute-type">Filter by type</label>
            <select
              id="institute-type"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="All">All institute types</option>
              {instituteTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Reset filters</label>
            <button
              className="btn"
              onClick={() => {
                setSearch("");
                setStatusFilter("All");
                setTypeFilter("All");
              }}
            >
              Clear filters
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-card" role="status">
            Loading institute records…
          </div>
        ) : filteredRows.length === 0 ? (
          <div className="empty-state">
            <h3>No institutes found</h3>
            <p className="muted">
              Try changing your search or clearing the selected filters.
            </p>
            <button
              className="btn"
              onClick={() => {
                setSearch("");
                setStatusFilter("All");
                setTypeFilter("All");
              }}
            >
              Clear search and filters
            </button>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Institute</th>
                  <th>Type</th>
                  <th>Contact</th>
                  <th>Registered</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredRows.map((institute) => (
                  <tr key={institute.id}>
                    <td>
                      <strong>{institute.name}</strong>
                      <small>
                        {institute.institute_code} ·{" "}
                        {[institute.city, institute.state]
                          .filter(Boolean)
                          .join(", ") || "Location not provided"}
                      </small>
                    </td>

                    <td>{institute.institute_type || "—"}</td>

                    <td>
                      {institute.email}
                      <small>{institute.phone || "No phone provided"}</small>
                    </td>

                    <td>{formatDate(institute.created_at)}</td>

                    <td>
                      <span className={`pill ${statusClass(institute.status)}`}>
                        {institute.status}
                      </span>
                    </td>

                    <td>
                      <div className="inline-actions">
                        {renderActions(institute)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {refreshing && (
          <p className="muted" role="status">
            Updating institute records…
          </p>
        )}
      </section>
    </AppShell>
  );
}
