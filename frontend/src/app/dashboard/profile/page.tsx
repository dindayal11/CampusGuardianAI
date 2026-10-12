
"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
} from "react";
import AppShell from "@/components/app-shell";
import { apiFetch, uploadFile } from "@/lib/api";

type Account = {
  name: string;
  user_id: string;
  email: string | null;
  institute_name: string | null;
};

type ProfileResponse = {
  account_type: string;
  user: Account;
  profile: {
    photo_url: string | null;
  };
};

type InstituteDetails = {
  name: string;
  phone: string;
  registration_date: string | null;
};

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8000/api/v1"
).replace(/\/$/, "");

export default function Profile() {
  const [account, setAccount] = useState<Account | null>(null);
  const [role, setRole] = useState("");
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [savingInstitute, setSavingInstitute] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [institute, setInstitute] = useState<InstituteDetails>({
    name: "",
    phone: "",
    registration_date: null,
  });

  const [oldPass, setOldPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [confirm, setConfirm] = useState("");

  const refreshPhoto = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/profile/photo`, {
        method: "GET",
        credentials: "include",
        cache: "no-store",
      });

      if (!response.ok) {
        setPhotoUrl(null);
        return;
      }

      const imageBlob = await response.blob();
      const nextUrl = URL.createObjectURL(imageBlob);

      setPhotoUrl((previousUrl) => {
        if (previousUrl) URL.revokeObjectURL(previousUrl);
        return nextUrl;
      });
    } catch {
      setPhotoUrl(null);
    }
  }, []);

  const loadInstitute = useCallback(async () => {
    const result = await apiFetch<InstituteDetails>("/profile/institute");

    setInstitute({
      name: result.name || "",
      phone: result.phone || "",
      registration_date: result.registration_date || null,
    });
  }, []);

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      try {
        setLoading(true);
        setError("");

        const result = await apiFetch<ProfileResponse>("/profile");

        if (!active) return;

        setAccount(result.user);
        setRole(result.account_type);

        if (result.profile?.photo_url) {
          await refreshPhoto();
        }

        if (result.account_type === "Institute Admin") {
          const details = await apiFetch<InstituteDetails>(
            "/profile/institute"
          );

          if (!active) return;

          setInstitute({
            name: details.name || "",
            phone: details.phone || "",
            registration_date: details.registration_date || null,
          });
        }
      } catch (e) {
        if (active) {
          setError(
            e instanceof Error
              ? e.message
              : "Could not load your profile."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadProfile();

    return () => {
      active = false;
    };
  }, [refreshPhoto]);

  useEffect(() => {
    return () => {
      if (photoUrl) URL.revokeObjectURL(photoUrl);
    };
  }, [photoUrl]);

  async function handlePhotoChange(
    event: FormEvent<HTMLInputElement>
  ) {
    const input = event.currentTarget;
    const file = input.files?.[0];

    if (!file) return;

    setMessage("");
    setError("");

    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setError("Please select a JPG or PNG image.");
      input.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("Photo must be 5 MB or smaller.");
      input.value = "";
      return;
    }

    try {
      setUploading(true);

      await uploadFile("/profile/photo", file);
      await refreshPhoto();

      setMessage("Profile photo updated successfully.");
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not upload your profile photo."
      );
    } finally {
      setUploading(false);
      input.value = "";
    }
  }

  async function saveInstituteDetails(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    setMessage("");
    setError("");

    const name = institute.name.trim();
    const phone = institute.phone.trim();

    if (!name) {
      setError("Institute name cannot be empty.");
      return;
    }

    try {
      setSavingInstitute(true);

      const result = await apiFetch<{
        success: boolean;
        message: string;
        name: string;
        phone: string;
        registration_date: string | null;
      }>("/profile/institute", {
        method: "PUT",
        body: JSON.stringify({ name, phone }),
      });

      setInstitute((previous) => ({
        ...previous,
        name: result.name,
        phone: result.phone || "",
        registration_date: result.registration_date,
      }));

      setAccount((previous) =>
        previous
          ? { ...previous, institute_name: result.name }
          : previous
      );

      setMessage(result.message || "Institute details updated successfully.");
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not update institute details."
      );
    } finally {
      setSavingInstitute(false);
    }
  }

  async function changePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError("");

    if (newPass !== confirm) {
      setError("New password and confirmation do not match.");
      return;
    }

    try {
      const result = await apiFetch<{ message: string }>(
        "/auth/change-password",
        {
          method: "POST",
          body: JSON.stringify({
            current_password: oldPass,
            new_password: newPass,
            confirm_password: confirm,
          }),
        }
      );

      setMessage(result.message || "Password changed successfully.");
      setOldPass("");
      setNewPass("");
      setConfirm("");
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Could not change your password."
      );
    }
  }

  function formatRegistrationDate(value: string | null) {
    if (!value) return "Not available";

    const date = new Date(value.replace(/([+-]\d{2})(\d{2})$/, "$1:$2"));

    if (Number.isNaN(date.getTime())) return value;

    return new Intl.DateTimeFormat("en-IN", {
      day: "2-digit",
      month: "long",
      year: "numeric",
      timeZone: "Asia/Kolkata",
    }).format(date);
  }

  const initials = (account?.name || "U")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");

  return (
    <AppShell>
      <header className="workspace-head">
        <div>
          <span className="eyebrow">Account</span>
          <h1>Profile &amp; security</h1>
          <p className="muted">
            Manage your profile and keep your account secure.
          </p>
        </div>
      </header>

      {message && (
        <div className="success-note" role="status">
          {message}
        </div>
      )}

      {error && (
        <div className="notice" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <section className="card">
          <p className="muted">Loading your profile...</p>
        </section>
      ) : (
        <div className="section-grid">
          <div className="card form-card">
            <h2>Personal information</h2>
            <p className="muted">
              Your account details are read-only.
            </p>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                flexWrap: "wrap",
                margin: "22px 0 28px",
              }}
            >
              {photoUrl ? (
                <img
                  src={photoUrl}
                  alt="Your profile"
                  style={{
                    width: 112,
                    height: 112,
                    borderRadius: "50%",
                    objectFit: "cover",
                    border: "2px solid var(--border)",
                  }}
                />
              ) : (
                <div
                  aria-label="Profile photo placeholder"
                  style={{
                    width: 112,
                    height: 112,
                    borderRadius: "50%",
                    display: "grid",
                    placeItems: "center",
                    background: "var(--surface-secondary, #e5e7eb)",
                    color: "var(--foreground, #1f2937)",
                    fontSize: 32,
                    fontWeight: 700,
                    border: "2px solid var(--border)",
                  }}
                >
                  {initials || "U"}
                </div>
              )}

              <div>
                <strong>
                  {photoUrl ? "Profile photo" : "Add a profile photo"}
                </strong>
                <p className="muted">JPG or PNG, maximum 5 MB.</p>

                {role !== "Platform Admin" && (
                  <label
                    className="btn primary"
                    style={{
                      display: "inline-block",
                      cursor: uploading ? "wait" : "pointer",
                      opacity: uploading ? 0.65 : 1,
                    }}
                  >
                    {uploading
                      ? "Uploading..."
                      : photoUrl
                        ? "Change photo"
                        : "Upload photo"}

                    <input
                      type="file"
                      accept="image/jpeg,image/png"
                      disabled={uploading}
                      onChange={handlePhotoChange}
                      style={{ display: "none" }}
                    />
                  </label>
                )}

                {role === "Platform Admin" && (
                  <p className="muted">
                    Photo upload is not enabled for this account.
                  </p>
                )}
              </div>
            </div>

            <div className="form-grid">
              <div className="field">
                <label htmlFor="profile-name">Full name</label>
                <input
                  id="profile-name"
                  value={account?.name || ""}
                  readOnly
                  aria-readonly="true"
                />
              </div>

              <div className="field">
                <label htmlFor="profile-user-id">
                  {role === "Student" ? "Student ID" : "User ID"}
                </label>
                <input
                  id="profile-user-id"
                  value={account?.user_id || ""}
                  readOnly
                  aria-readonly="true"
                />
              </div>

              <div className="field full-span">
                <label htmlFor="profile-email">Email address</label>
                <input
                  id="profile-email"
                  value={account?.email || "Not available"}
                  readOnly
                  aria-readonly="true"
                />
              </div>

              {role !== "Platform Admin" && (
                <div className="field full-span">
                  <label htmlFor="profile-institute-name">
                    Institute / College
                  </label>
                  <input
                    id="profile-institute-name"
                    value={account?.institute_name || "Not available"}
                    readOnly
                    aria-readonly="true"
                  />
                </div>
              )}
            </div>
          </div>

          {role === "Institute Admin" && (
            <form
              className="card form-card"
              onSubmit={saveInstituteDetails}
            >
              <h2>Institute Details</h2>
              <p className="muted">
                Update your institute contact information. Registration date
                cannot be changed.
              </p>

              <div className="field">
                <label htmlFor="institute-name">Institute Name</label>
                <input
                  id="institute-name"
                  required
                  maxLength={255}
                  value={institute.name}
                  onChange={(e) =>
                    setInstitute((previous) => ({
                      ...previous,
                      name: e.target.value,
                    }))
                  }
                  placeholder="Enter institute name"
                />
              </div>

              <div className="field">
                <label htmlFor="institute-phone">Mobile Number</label>
                <input
                  id="institute-phone"
                  type="tel"
                  maxLength={50}
                  value={institute.phone}
                  onChange={(e) =>
                    setInstitute((previous) => ({
                      ...previous,
                      phone: e.target.value,
                    }))
                  }
                  placeholder="Enter mobile number"
                  autoComplete="tel"
                />
              </div>

              <div className="field">
                <label htmlFor="institute-registration-date">
                  Registration Date
                </label>
                <input
                  id="institute-registration-date"
                  value={formatRegistrationDate(
                    institute.registration_date
                  )}
                  readOnly
                  aria-readonly="true"
                />
              </div>

              <button
                className="btn primary"
                type="submit"
                disabled={savingInstitute}
              >
                {savingInstitute ? "Saving..." : "Save Institute Details"}
              </button>
            </form>
          )}

          <form className="card form-card" onSubmit={changePassword}>
            <h2>Change password</h2>
            <p className="muted">
              Use a strong password to keep your account secure.
            </p>

            <div className="field">
              <label htmlFor="current-password">Current password</label>
              <input
                id="current-password"
                type="password"
                autoComplete="current-password"
                required
                value={oldPass}
                onChange={(e) => setOldPass(e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="new-password">New password</label>
              <input
                id="new-password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                value={newPass}
                onChange={(e) => setNewPass(e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="confirm-password">
                Confirm new password
              </label>
              <input
                id="confirm-password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </div>

            <button className="btn primary" type="submit">
              Change password
            </button>
          </form>
        </div>
      )}
    </AppShell>
  );
}
