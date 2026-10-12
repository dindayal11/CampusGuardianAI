"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
type PublicKeyResponse = {
  publicKey: string;
};
type SubscriptionResponse = {
  success: boolean;
};
function urlBase64ToUint8Array(base64String: string): Uint8Array<ArrayBuffer> {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, "+")
    .replace(/_/g, "/");
  const raw = window.atob(base64);
  const output = new Uint8Array(new ArrayBuffer(raw.length));
  for (let i = 0; i < raw.length; i++) {
    output[i] = raw.charCodeAt(i);
  }
  return output;
}
export default function PushNotificationSettings() {
  const [supported, setSupported] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  useEffect(() => {
    let cancelled = false;
    async function checkSupport() {
      const available =
        "serviceWorker" in navigator &&
        "PushManager" in window &&
        "Notification" in window &&
        window.isSecureContext;
      if (!available) {
        if (!cancelled) setSupported(false);
        return;
      }
      try {
        const registration = await navigator.serviceWorker.register("/sw.js");
        const subscription = await registration.pushManager.getSubscription();
        if (!cancelled) {
          setSupported(true);
          setEnabled(
            Notification.permission === "granted" && subscription !== null
          );
        }
      } catch {
        if (!cancelled) {
          setSupported(false);
          setMessage("Browser notifications could not be initialized.");
        }
      }
    }
    void checkSupport();
    return () => {
      cancelled = true;
    };
  }, []);
  async function enableNotifications() {
    setBusy(true);
    setMessage("");
    try {
      if (
        !("serviceWorker" in navigator) ||
        !("PushManager" in window) ||
        !("Notification" in window) ||
        !window.isSecureContext
      ) {
        throw new Error("Push notifications require a supported browser and HTTPS.");
      }
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        throw new Error(
          permission === "denied"
            ? "Notifications are blocked in browser settings."
            : "Notification permission was not granted."
        );
      }
      const keyResponse = await apiFetch<PublicKeyResponse>("/push/public-key");
      if (!keyResponse.publicKey) {
        throw new Error("Push notifications are not configured on the server.");
      }
      const registration = await navigator.serviceWorker.register("/sw.js");
      await navigator.serviceWorker.ready;
      let subscription = await registration.pushManager.getSubscription();
      if (!subscription) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(
            keyResponse.publicKey
          ),
        });
      }
      const json = subscription.toJSON();
      const endpoint = json.endpoint;
      const p256dh = json.keys?.p256dh;
      const auth = json.keys?.auth;
      if (!endpoint || !p256dh || !auth) {
        throw new Error("The browser returned an incomplete subscription.");
      }
      await apiFetch<SubscriptionResponse>("/push/subscribe", {
        method: "POST",
        body: JSON.stringify({
          endpoint,
          keys: { p256dh, auth },
        }),
      });
      setEnabled(true);
      setMessage("Browser notifications enabled successfully.");
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Could not enable browser notifications."
      );
    } finally {
      setBusy(false);
    }
  }
  async function disableNotifications() {
    setBusy(true);
    setMessage("");
    try {
      const registration = await navigator.serviceWorker.getRegistration("/");
      if (registration) {
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          const json = subscription.toJSON();
const endpoint = json.endpoint;
const p256dh = json.keys?.p256dh;
const auth = json.keys?.auth;

if (!endpoint || !p256dh || !auth) {
  throw new Error("The browser returned an incomplete subscription.");
}

await apiFetch<SubscriptionResponse>("/push/unsubscribe", {
  method: "POST",
  body: JSON.stringify({
    endpoint,
    keys: {
      p256dh,
      auth,
    },
  }),
});

await subscription.unsubscribe();
        }
      }
      setEnabled(false);
      setMessage("Browser notifications disabled for this browser.");
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Could not disable browser notifications."
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="card">
      <h2>Browser notifications</h2>
      <p className="muted">
        Receive institute announcements even when Campus Guardian AI is not
        open, provided your browser and device allow background notifications.
      </p>
      {!supported && (
        <p className="muted">
          Notification support is unavailable or could not be initialized.
          Use a supported browser over HTTPS, or localhost for development.
        </p>
      )}
      {supported && (
        <p>
          Status: <strong>{enabled ? "Enabled" : "Not enabled"}</strong>
        </p>
      )}
      {supported && (
        <button
          type="button"
          className={`btn ${enabled ? "secondary" : "primary"}`}
          disabled={busy}
          onClick={() =>
            enabled
              ? void disableNotifications()
              : void enableNotifications()
          }
        >
          {busy
            ? "Please wait..."
            : enabled
              ? "Disable notifications"
              : "Enable notifications"}
        </button>
      )}
      {message && (
        <p role="status" aria-live="polite" className="muted">
          {message}
        </p>
      )}
    </section>
  );
}
