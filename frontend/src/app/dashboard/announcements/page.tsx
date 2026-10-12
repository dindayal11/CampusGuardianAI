
"use client";
import PushNotificationSettings from "@/components/push-notification-settings";
import { useEffect, useState } from "react";
import AppShell from "@/components/app-shell";
import { apiFetch } from "@/lib/api";

type A = {
  id: number;
  title: string;
  message: string;
  audience: string;
  priority: string;
  created_at: string | null;
  expires_at?: string | null;
};

export default function Announcements() {
  const [items, setItems] = useState<A[]>([]);
  const [role, setRole] = useState("");
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [audience, setAudience] = useState("All");
  const [priority, setPriority] = useState("Normal");
  const [error, setError] = useState("");

  const [readIds, setReadIds] = useState<number[]>([]);
  const [markingId, setMarkingId] = useState<number | null>(null);

  async function load() {
    try {
      setError("");

      const auth = await apiFetch<{ user: { role: string } }>("/auth/me");
      setRole(auth.user.role);

      const announcements = await apiFetch<A[]>("/announcements");
      setItems(announcements);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not load announcements."
      );
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function create() {
    setError("");

    try {
      await apiFetch("/announcements", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          message: message.trim(),
          audience,
          priority,
          expires_at: null,
        }),
      });

      setTitle("");
      setMessage("");

      await load();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not publish announcement."
      );
    }
  }

  async function remove(id: number) {
    if (!confirm("Delete this announcement?")) return;

    setError("");

    try {
      await apiFetch(`/announcements/${id}`, {
        method: "DELETE",
      });

      setReadIds((previous) => previous.filter((readId) => readId !== id));
      await load();
      window.dispatchEvent(new Event("announcements-read-updated"));
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not delete announcement."
      );
    }
  }

  async function markRead(id: number) {
    if (readIds.includes(id) || markingId !== null) return;

    setMarkingId(id);
    setError("");

    try {
      await apiFetch(`/announcements/${id}/read`, {
        method: "POST",
      });

      setReadIds((previous) =>
        previous.includes(id) ? previous : [...previous, id]
      );

      window.dispatchEvent(new Event("announcements-read-updated"));
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not mark announcement as read."
      );
    } finally {
      setMarkingId(null);
    }
  }

  return (
    <AppShell>
      <header className="workspace-head">
        <div>
          <span className="eyebrow">Institute communication</span>
          <h1>Announcements</h1>
          <p className="muted">
            Publish useful updates to the right audience without clutter.
          </p>
        </div>
      </header>

      {error && <div className="notice">{error}</div>}
      <PushNotificationSettings />

      {role === "Institute Admin" && (
        <section className="card form-card">
          <h2>Publish</h2>

          <div className="form-grid">
            <div className="field">
              <label>Title</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={255}
              />
            </div>

            <div className="field">
              <label>Audience</label>
              <select
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
              >
                <option>All</option>
                <option>Students</option>
                <option>Institute Admins</option>
              </select>
            </div>

            <div className="field full-span">
              <label>Message</label>
              <textarea
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
            </div>

            <div className="field">
              <label>Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option>Normal</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </div>
          </div>

          <button
            className="btn primary"
            disabled={!title.trim() || !message.trim()}
            onClick={create}
          >
            Publish announcement
          </button>
        </section>
      )}

      <section className="announcement-list">
        {items.length === 0 ? (
          <div className="card">
            <p className="muted">No active announcements.</p>
          </div>
        ) : (
          items.map((a) => (
            <article key={a.id} className="card announcement">
              <div className="section-head">
                <div>
                  <span className={`pill ${a.priority.toLowerCase()}`}>
                    {a.priority}
                  </span>
                  <h2>{a.title}</h2>
                </div>

                {role === "Institute Admin" && (
                  <button
                    className="btn danger ghost"
                    onClick={() => remove(a.id)}
                  >
                    Delete
                  </button>
                )}
              </div>

              <p>{a.message}</p>

              <small>
                {a.audience} · {a.created_at || "—"}
                {a.expires_at ? ` · Expires ${a.expires_at}` : ""}
              </small>

              {role === "Student" && (
                <div style={{ marginTop: 12 }}>
                  <button
                    className="btn secondary"
                    disabled={
                      readIds.includes(a.id) || markingId !== null
                    }
                    onClick={() => markRead(a.id)}
                  >
                    {readIds.includes(a.id)
                      ? "Read"
                      : markingId === a.id
                        ? "Saving..."
                        : "Mark as read"}
                  </button>
                </div>
              )}
            </article>
          ))
        )}
      </section>
    </AppShell>
  );
}
