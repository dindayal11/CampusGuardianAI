
"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import AppShell from "@/components/app-shell";

type C = {
  complaint_id: string;
  title: string;
  description: string;
  location: string;
  category: string | null;
  priority: string | null;
  status: string;
  department: string | null;
  created_at: string | null;
  student_id?: string | null;
};

type Auth = {
  user: {
    role: string;
  };
};

const STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"];

function Complaints() {
  const [items, setItems] = useState<C[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("All");
  const [priority, setPriority] = useState("All");
  const [search, setSearch] = useState("");
  const [selectedStatuses, setSelectedStatuses] = useState<
    Record<string, string>
  >({});
  const [savingId, setSavingId] = useState<string | null>(null);

  const isAdmin = role !== "" && role !== "Student";

  const load = useCallback(async () => {
    try {
      setError("");

      const q = new URLSearchParams();

      if (status !== "All") q.set("status", status);
      if (priority !== "All") q.set("priority", priority);

      const query = q.toString();
      const result = await apiFetch<{ items: C[] }>(
        `/complaints${query ? `?${query}` : ""}`
      );

      setItems(result.items);

      setSelectedStatuses((previous) => {
        const next = { ...previous };

        for (const complaint of result.items) {
          next[complaint.complaint_id] =
            next[complaint.complaint_id] ?? complaint.status;
        }

        return next;
      });
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not load complaints."
      );
    }
  }, [status, priority]);

  useEffect(() => {
    async function loadUser() {
      try {
        const auth = await apiFetch<Auth>("/auth/me");
        setRole(auth.user.role);
      } catch {
        setRole("");
      }
    }

    void loadUser();
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(
    () =>
      items.filter((item) =>
        `${item.title} ${item.complaint_id} ${item.location}`
          .toLowerCase()
          .includes(search.toLowerCase())
      ),
    [items, search]
  );

  async function updateStatus(complaint: C) {
    const newStatus = selectedStatuses[complaint.complaint_id];

    if (!newStatus || newStatus === complaint.status) {
      setNotice("Select a different status before updating.");
      return;
    }

    const confirmed = window.confirm(
      `Change complaint status from "${complaint.status}" to "${newStatus}"?`
    );

    if (!confirmed) return;

    setSavingId(complaint.complaint_id);
    setError("");
    setNotice("");

    try {
      await apiFetch(
        `/complaints/${encodeURIComponent(complaint.complaint_id)}`,
        {
          method: "PATCH",
          body: JSON.stringify({ status: newStatus }),
        }
      );

      setNotice(`Status updated to "${newStatus}".`);
      await load();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not update complaint status."
      );
    } finally {
      setSavingId(null);
    }
  }

  return (
    <AppShell>
      <header className="workspace-head">
        <div>
          <span className="eyebrow">Complaint management</span>
          <h1>Complaints</h1>
          <p className="muted">
            Filter, inspect and follow every visible complaint.
          </p>
        </div>

        <Link className="btn primary" href="/dashboard/report">
          + Report issue
        </Link>
      </header>

      {error && (
        <div className="notice" role="alert">
          {error}
        </div>
      )}

      {notice && (
        <div className="notice" role="status">
          {notice}
        </div>
      )}

      <div className="filters">
        <input
          placeholder="Search complaint, ID or location…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          aria-label="Filter by status"
        >
          <option>All</option>
          {STATUSES.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>

        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          aria-label="Filter by priority"
        >
          <option>All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </div>

      <section className="card table-card">
        <div className="table-head">
          <strong>
            {filtered.length} visible complaint
            {filtered.length === 1 ? "" : "s"}
          </strong>
          <span className="muted">
            Select a complaint to inspect its workflow and history.
          </span>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Complaint</th>
                <th>Priority</th>
                <th>Status</th>
                {isAdmin && <th>Update status</th>}
                <th>Department</th>
                <th>Location</th>
                <th>Created</th>
              </tr>
            </thead>

            <tbody>
              {filtered.map((complaint) => {
                const selected =
                  selectedStatuses[complaint.complaint_id] ??
                  complaint.status;
                const saving = savingId === complaint.complaint_id;

                return (
                  <tr key={complaint.complaint_id}>
                    <td>
                      <Link
                        className="table-link"
                        href={`/dashboard/complaints/${complaint.complaint_id}`}
                      >
                        <strong>{complaint.title}</strong>
                        <small>{complaint.complaint_id}</small>
                      </Link>
                    </td>

                    <td>
                      <span
                        className={`pill ${String(
                          complaint.priority || ""
                        ).toLowerCase()}`}
                      >
                        {complaint.priority || "—"}
                      </span>
                    </td>

                    <td>
                      <span className="pill">{complaint.status}</span>
                    </td>

                    {isAdmin && (
                      <td>
                        <div className="complaint-status-editor">
                          <select
                            value={selected}
                            disabled={saving}
                            onChange={(e) =>
                              setSelectedStatuses((previous) => ({
                                ...previous,
                                [complaint.complaint_id]: e.target.value,
                              }))
                            }
                            aria-label={`New status for ${complaint.title}`}
                          >
                            {STATUSES.map((item) => (
                              <option key={item} value={item}>
                                {item}
                              </option>
                            ))}
                          </select>

                          <button
                            type="button"
                            className="btn primary complaint-status-save"
                            disabled={
                              saving || selected === complaint.status
                            }
                            onClick={() => void updateStatus(complaint)}
                          >
                            {saving ? "Saving…" : "Update"}
                          </button>
                        </div>
                      </td>
                    )}

                    <td>{complaint.department || "Unassigned"}</td>
                    <td>{complaint.location}</td>
                    <td>{complaint.created_at || "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <p className="muted empty">No matching complaints.</p>
        )}
      </section>
    </AppShell>
  );
}

export default Complaints;
