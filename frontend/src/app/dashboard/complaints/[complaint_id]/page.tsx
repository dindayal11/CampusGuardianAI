
"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
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
  image_path?: string | null;
  anonymous?: boolean | null;
};

type H = {
  id: number;
  action: string;
  actor_user_id: string | null;
  old_value: string | null;
  new_value: string | null;
  note: string | null;
  created_at: string | null;
};

type W = {
  assigned_to: string | null;
  sla_hours: number;
  due_at: string | null;
  escalation_level: number;
  resolution_notes: string | null;
  resolved_at: string | null;
  feedback_rating: number | null;
  feedback_comment: string | null;
  feedback_at: string | null;
  is_overdue: boolean;
  remaining_hours: number | null;
};

type D = {
  complaint: C;
  workflow: W;
  history: H[];
  duplicate: {
    is_duplicate: boolean;
    similarity_score: number;
    similar_complaints: Array<{
      complaint_id: string;
      title: string;
      similarity: number;
    }>;
  } | null;
};

export default function Detail({
  params,
}: {
  params: Promise<{ complaint_id: string }>;
}) {
  const { complaint_id } = use(params);

  const [detail, setDetail] = useState<D | null>(null);
  const [authRole, setAuthRole] = useState("");
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [department, setDepartment] = useState("");
  const [assigned, setAssigned] = useState("");
  const [sla, setSla] = useState("48");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");

  // Complaint photo state
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [photoError, setPhotoError] = useState("");

  const load = async () => {
    try {
      setError("");

      const a = await apiFetch<{ user: { role: string } }>("/auth/me");
      setAuthRole(a.user.role);

      const d = await apiFetch<D>(
        `/complaints/${complaint_id}/detail`
      );

      setDetail(d);
      setStatus(d.complaint.status);
      setDepartment(d.complaint.department || "");
      setAssigned(d.workflow.assigned_to || "");
      setSla(String(d.workflow.sla_hours || 48));
      setNotes(d.workflow.resolution_notes || "");
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not load complaint."
      );
    }
  };

  useEffect(() => {
    void load();
  }, [complaint_id]);

  // Load complaint photos using the authenticated session.
  // Platform Admin must never request or display complaint photos.
  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;

    async function loadPhoto() {
      setPhotoUrl(null);
      setPhotoError("");

      const imagePath = detail?.complaint.image_path;

      if (
        !authRole ||
        authRole === "Platform Admin" ||
        !imagePath
      ) {
        setPhotoLoading(false);
        return;
      }

      setPhotoLoading(true);

      try {
        const baseUrl = (
          process.env.NEXT_PUBLIC_API_BASE_URL ||
          "http://localhost:8000/api/v1"
        ).replace(/\/$/, "");

        // The API path comes from the complaint response.
        // It should be the relative attachment URL returned by the backend.
        if (
          !imagePath.startsWith(
            `/complaints/${encodeURIComponent(complaint_id)}/attachment`
          ) &&
          imagePath !== `/complaints/${complaint_id}/attachment`
        ) {
          throw new Error("Invalid complaint photo URL.");
        }

        const response = await fetch(`${baseUrl}${imagePath}`, {
          method: "GET",
          credentials: "include",
          cache: "no-store",
        });

        if (!response.ok) {
          if (response.status === 403) {
            throw new Error(
              "You are not allowed to view this complaint photo."
            );
          }

          if (response.status === 404) {
            throw new Error(
              "The attached photo could not be found."
            );
          }

          throw new Error("Could not load the complaint photo.");
        }

        const blob = await response.blob();

        if (
          blob.type &&
          !["image/jpeg", "image/png"].includes(blob.type)
        ) {
          throw new Error("The server returned an unsupported image.");
        }

        objectUrl = URL.createObjectURL(blob);

        if (!cancelled) {
          setPhotoUrl(objectUrl);
        } else {
          URL.revokeObjectURL(objectUrl);
        }
      } catch (e) {
        if (!cancelled) {
          setPhotoError(
            e instanceof Error
              ? e.message
              : "Could not load the complaint photo."
          );
        }
      } finally {
        if (!cancelled) {
          setPhotoLoading(false);
        }
      }
    }

    void loadPhoto();

    return () => {
      cancelled = true;

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [
    authRole,
    complaint_id,
    detail?.complaint.image_path,
  ]);

  async function save() {
    setBusy(true);
    setError("");

    try {
      await apiFetch(`/complaints/${complaint_id}`, {
        method: "PATCH",
        body: JSON.stringify({
          status,
          department: department || null,
          assigned_to: assigned || null,
          sla_hours: Number(sla) || 48,
          resolution_notes: notes || null,
        }),
      });

      await load();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not update complaint."
      );
    } finally {
      setBusy(false);
    }
  }

  async function escalate() {
    setBusy(true);
    setError("");

    try {
      await apiFetch(`/complaints/${complaint_id}/escalate`, {
        method: "POST",
      });

      await load();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not escalate complaint."
      );
    } finally {
      setBusy(false);
    }
  }

  async function feedback() {
    setBusy(true);
    setError("");

    try {
      await apiFetch(`/complaints/${complaint_id}/feedback`, {
        method: "POST",
        body: JSON.stringify({ rating, comment }),
      });

      await load();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not submit feedback."
      );
    } finally {
      setBusy(false);
    }
  }

  const canViewPhoto =
    authRole === "Student" || authRole === "Institute Admin";

  return (
    <AppShell>
      <Link className="muted" href="/dashboard/complaints">
        ← Complaints
      </Link>

      {error && <div className="notice">{error}</div>}

      {!detail ? (
        <div className="loading-card">Loading complaint…</div>
      ) : (
        <>
          <header className="workspace-head">
            <div>
              <span className="eyebrow">
                {detail.complaint.complaint_id}
              </span>

              <h1>{detail.complaint.title}</h1>

              <p className="muted">
                {detail.complaint.location} ·{" "}
                {detail.complaint.created_at || "—"}
              </p>
            </div>

            <span className="pill">
              {detail.complaint.status}
            </span>
          </header>

          <div className="detail-grid">
            <section className="card">
              <h2>Complaint</h2>

              <p>{detail.complaint.description}</p>

              {/* Complaint photo: only Student and Institute Admin */}
              {canViewPhoto && detail.complaint.image_path && (
                <section
                  className="complaint-photo"
                  aria-label="Complaint attachment"
                  style={{ marginTop: "20px" }}
                >
                  <h3>Attached Photo</h3>

                  {photoLoading && (
                    <p className="muted">Loading photo…</p>
                  )}

                  {photoError && (
                    <p className="notice" role="alert">
                      {photoError}
                    </p>
                  )}

                  {photoUrl && (
                    <a
                      href={photoUrl}
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Open complaint photo in a new tab"
                    >
                      <img
                        src={photoUrl}
                        alt="Photo attached to this complaint"
                        style={{
                          display: "block",
                          width: "100%",
                          maxWidth: "560px",
                          maxHeight: "420px",
                          objectFit: "contain",
                          borderRadius: "12px",
                          marginTop: "12px",
                          border: "1px solid var(--border, #ddd)",
                        }}
                      />
                    </a>
                  )}
                </section>
              )}

              <div className="tag-row">
                <span className="pill">
                  {detail.complaint.category || "General"}
                </span>

                <span
                  className={`pill ${String(
                    detail.complaint.priority || ""
                  ).toLowerCase()}`}
                >
                  {detail.complaint.priority || "Unspecified"}
                </span>

                <span className="pill">
                  {detail.complaint.department || "Unassigned"}
                </span>
              </div>

              {detail.complaint.student_id && (
                <p className="muted">
                  Submitted by:{" "}
                  {detail.complaint.anonymous
                    ? "Anonymous"
                    : detail.complaint.student_id}
                </p>
              )}
            </section>

            <section className="card">
              <h2>Workflow</h2>

              {authRole !== "Student" ? (
                <>
                  <div className="form-grid">
                    <div className="field">
                      <label>Status</label>

                      <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                      >
                        <option>Pending</option>
                        <option>In Progress</option>
                        <option>Resolved</option>
                        <option>Rejected</option>
                      </select>
                    </div>

                    <div className="field">
                      <label>Department</label>

                      <input
                        value={department}
                        onChange={(e) =>
                          setDepartment(e.target.value)
                        }
                        placeholder="Maintenance"
                      />
                    </div>

                    <div className="field">
                      <label>Assigned to</label>

                      <input
                        value={assigned}
                        onChange={(e) =>
                          setAssigned(e.target.value)
                        }
                        placeholder="Maintenance team"
                      />
                    </div>

                    <div className="field">
                      <label>SLA hours</label>

                      <input
                        type="number"
                        min="1"
                        max="720"
                        value={sla}
                        onChange={(e) => setSla(e.target.value)}
                      />
                    </div>

                    <div className="field full-span">
                      <label>Resolution / internal notes</label>

                      <textarea
                        rows={4}
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                      />
                    </div>
                  </div>

                  <button
                    className="btn primary"
                    onClick={save}
                    disabled={busy}
                  >
                    {busy ? "Saving…" : "Save workflow"}
                  </button>
                </>
              ) : (
                <>
                  <div className="result-grid">
                    <div>
                      <span>Department</span>
                      <strong>
                        {detail.complaint.department || "Unassigned"}
                      </strong>
                    </div>

                    <div>
                      <span>SLA</span>
                      <strong>
                        {detail.workflow.sla_hours} hours
                      </strong>
                    </div>

                    <div>
                      <span>Due</span>
                      <strong>
                        {detail.workflow.due_at || "Not set"}
                      </strong>
                    </div>

                    <div>
                      <span>SLA state</span>
                      <strong>
                        {detail.workflow.is_overdue
                          ? `Overdue by ${Math.abs(
                              detail.workflow.remaining_hours ?? 0
                            )}h`
                          : detail.workflow.remaining_hours != null
                            ? `${detail.workflow.remaining_hours}h remaining`
                            : "—"}
                      </strong>
                    </div>

                    <div>
                      <span>Escalation</span>
                      <strong>
                        Level {detail.workflow.escalation_level}
                      </strong>
                    </div>
                  </div>

                  {detail.complaint.status === "Resolved" &&
                    detail.workflow.feedback_rating == null && (
                      <div className="feedback">
                        <h3>How was the resolution?</h3>

                        <label>
                          Rating{" "}
                          <select
                            value={rating}
                            onChange={(e) =>
                              setRating(Number(e.target.value))
                            }
                          >
                            {[1, 2, 3, 4, 5].map((x) => (
                              <option key={x} value={x}>
                                {x}
                              </option>
                            ))}
                          </select>
                        </label>

                        <textarea
                          rows={3}
                          placeholder="Optional comment"
                          value={comment}
                          onChange={(e) => setComment(e.target.value)}
                        />

                        <button
                          className="btn primary"
                          onClick={feedback}
                          disabled={busy}
                        >
                          {busy ? "Submitting…" : "Send feedback"}
                        </button>
                      </div>
                    )}

                  {detail.workflow.feedback_rating != null && (
                    <p className="muted">
                      Feedback submitted:{" "}
                      {detail.workflow.feedback_rating}/5.
                    </p>
                  )}
                </>
              )}

              {detail.workflow.is_overdue &&
                authRole !== "Student" && (
                  <div className="notice">
                    <strong>SLA overdue.</strong> Escalate this complaint
                    to raise its priority for admin attention.{" "}
                    <button
                      className="btn"
                      onClick={escalate}
                      disabled={busy}
                    >
                      Escalate
                    </button>
                  </div>
                )}
            </section>
          </div>

          {detail.duplicate &&
            detail.duplicate.similar_complaints?.length > 0 &&
            authRole !== "Student" && (
              <section className="card">
                <h2>Similarity signal</h2>

                <p className="muted">
                  Highest similarity:{" "}
                  <strong>
                    {detail.duplicate.similarity_score}%
                  </strong>
                  . Review related complaints before duplicating work.
                </p>

                {detail.duplicate.similar_complaints
                  .slice(0, 5)
                  .map((x) => (
                    <div
                      className="list-row"
                      key={x.complaint_id}
                    >
                      <div>
                        <strong>{x.title}</strong>
                        <span>{x.complaint_id}</span>
                      </div>

                      <span className="pill">
                        {x.similarity}%
                      </span>
                    </div>
                  ))}
              </section>
            )}

          <section className="card">
            <h2>History</h2>

            {detail.history.length === 0 ? (
              <p className="muted">No history recorded.</p>
            ) : (
              <div className="timeline">
                {detail.history.map((x) => (
                  <div className="timeline-item" key={x.id}>
                    <div className="timeline-dot" />

                    <div>
                      <strong>{x.action}</strong>

                      <span>
                        {x.created_at || "—"} ·{" "}
                        {x.actor_user_id || "System"}
                      </span>

                      {x.old_value || x.new_value ? (
                        <small>
                          {x.old_value || "—"} → {x.new_value || "—"}
                        </small>
                      ) : null}

                      {x.note && (
                        <p className="muted">{x.note}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </AppShell>
  );
}
