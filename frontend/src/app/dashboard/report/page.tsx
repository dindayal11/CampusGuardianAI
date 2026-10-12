
"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { apiFetch, uploadFile } from "@/lib/api";
import AppShell from "@/components/app-shell";


type AIAnalysis = {
  provider?: string;
  mode?: string;
  summary?: string;
  reasoning?: string;
  recommended_actions?: string[];
  safety_flags?: string[];
  confidence?: string;
};

type Complaint = {
  complaint_id: string;
  title: string;
  category: string | null;
  priority: string | null;
  status: string;
  department?: string | null;
  risk_score?: number | null;
  recommended_action?: string | null;
  ai_analysis?: AIAnalysis | null;
};

export default function Report() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [anonymous, setAnonymous] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Complaint | null>(null);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");

    try {
      const complaint = await apiFetch<Complaint>("/complaints", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          location: location.trim(),
          anonymous,
        }),
      });

      if (file) {
        await uploadFile(
          `/complaints/${complaint.complaint_id}/attachment`,
          file
        );
      }

      setResult(complaint);
      setTitle("");
      setDescription("");
      setLocation("");
      setAnonymous(false);
      setFile(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not submit complaint."
      );
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    return (
      <AppShell>
        <section className="success-card">
          <span className="success-icon">✓</span>
          <span className="eyebrow">Submitted</span>

          <h1>Complaint received.</h1>

          <p className="muted">
            Your report <strong>{result.complaint_id}</strong> is now
            in the institute workflow.
          </p>

          
{result.recommended_action && (
  <div className="notice">
    <strong>Recommended action</strong>
    <p>{result.recommended_action}</p>
  </div>
)}


{result.ai_analysis && (
  <section className="guardian-ai-card">
    <div className="guardian-ai-header">
      <div className="guardian-ai-icon">✦</div>
      <div className="guardian-ai-title">
        <span className="guardian-ai-eyebrow">
          INTELLIGENT SAFETY SYSTEM
        </span>
        <h2>Guardian AI Analysis</h2>
        <p>
          AI-powered insights to help assess your reported concern.
        </p>
      </div>
      <span className="guardian-ai-status">ANALYSIS</span>
    </div>

    <div className="guardian-ai-divider" />

    {result.ai_analysis.summary && (
      <div className="guardian-ai-summary">
        <span className="guardian-ai-label">✦ GUARDIAN AI SUMMARY</span>
        <p>{result.ai_analysis.summary}</p>
      </div>
    )}

    {result.ai_analysis.reasoning && (
      <div className="guardian-ai-section">
        <h3>Analysis &amp; reasoning</h3>
        <p>{result.ai_analysis.reasoning}</p>
      </div>
    )}

    {!!result.ai_analysis.recommended_actions?.length && (
      <div className="guardian-ai-section">
        <h3>Recommended actions</h3>
        <div className="guardian-ai-actions">
          {result.ai_analysis.recommended_actions.map((action, index) => (
            <div
              className="guardian-ai-action"
              key={`${index}-${action}`}
            >
              <span className="guardian-ai-action-number">
                {String(index + 1).padStart(2, "0")}
              </span>
              <p>{action}</p>
            </div>
          ))}
        </div>
      </div>
    )}

    {!!result.ai_analysis.safety_flags?.length && (
      <div className="guardian-ai-flags">
        <h3>Safety flags</h3>
        <div className="guardian-ai-flag-list">
          {result.ai_analysis.safety_flags.map((flag, index) => (
            <span
              className="guardian-ai-flag"
              key={`${index}-${flag}`}
            >
              <span aria-hidden="true">!</span>
              {flag}
            </span>
          ))}
        </div>
      </div>
    )}

    {result.ai_analysis.confidence && (
      <div className="guardian-ai-footer">
        <span>Assessment confidence</span>
        <strong>{result.ai_analysis.confidence}</strong>
      </div>
    )}

    <p className="guardian-ai-disclaimer">
      AI-generated assessment for decision support. Institute staff
      should review the report before taking action.
    </p>
  </section>
)}


          <div className="result-grid">
            <div>
              <span>Category</span>
              <strong>{result.category || "General"}</strong>
            </div>

            <div>
              <span>Priority</span>
              <strong>{result.priority || "Unspecified"}</strong>
            </div>

            <div>
              <span>Department</span>
              <strong>{result.department || "Auto-assigned"}</strong>
            </div>

            <div>
              <span>Risk score</span>
              <strong>
                {result.risk_score ?? "—"}/100
              </strong>
            </div>

            <div>
              <span>Status</span>
              <strong>{result.status}</strong>
            </div>
          </div>

          <div className="cta">
            <Link
              className="btn primary"
              href={`/dashboard/complaints/${result.complaint_id}`}
            >
              Track complaint
            </Link>

            <button
              className="btn"
              onClick={() => setResult(null)}
            >
              Report another
            </button>
          </div>
        </section>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <header className="workspace-head">
        <div>
          <span className="eyebrow">Student workflow</span>
          <h1>Report an issue</h1>
          <p className="muted">
            Describe the problem clearly. AI analysis can help
            identify category, priority and similar complaints.
          </p>
        </div>
      </header>

      <form className="card form-card" onSubmit={submit}>
        <div className="form-grid">
          <div className="field full-span">
            <label htmlFor="title">Title</label>
            <input
              id="title"
              required
              minLength={3}
              maxLength={255}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Water leakage in hostel bathroom"
            />
          </div>

          <div className="field full-span">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              required
              minLength={5}
              maxLength={5000}
              rows={7}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Explain what happened, where it is and why it needs attention."
            />
          </div>

          <div className="field">
            <label htmlFor="location">Campus location</label>
            <input
              id="location"
              required
              maxLength={255}
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Hostel Block A, 2nd floor"
            />
            <small>
              Enter the building, block, floor or other campus location.
            </small>
          </div>

          <div className="field">
            <label htmlFor="file">Photo (optional)</label>
            <input
              id="file"
              type="file"
              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
              onChange={(e) => {
                const selected = e.target.files?.[0] || null;
                setFile(selected);
                setError("");
              }}
            />
            <small>JPG/JPEG/PNG, maximum 5 MB.</small>
          </div>
        </div>

        <label className="check">
          <input
            type="checkbox"
            checked={anonymous}
            onChange={(e) => setAnonymous(e.target.checked)}
          />
          <span>
            <strong>Submit anonymously</strong>
            <small>
              Your identity will be hidden where supported by the
              backend and complaint-viewing permissions.
            </small>
          </span>
        </label>

        {error && <div className="notice">{error}</div>}

        <div className="form-actions">
          <button
            className="btn primary"
            type="submit"
            disabled={busy}
          >
            {busy ? "Submitting…" : "Submit complaint"}
          </button>

          <Link className="btn" href="/dashboard">
            Cancel
          </Link>
        </div>
      </form>
    </AppShell>
  );
}

