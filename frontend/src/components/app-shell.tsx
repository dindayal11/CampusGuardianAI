
"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";

type User = {
  subject: string;
  name: string;
  role: string;
  email?: string | null;
  institute_id?: number | null;
  institute_code?: string | null;
};

type Auth = {
  authenticated: boolean;
  user: User;
};

type Notification = {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
};

const common = [
  ["/dashboard", "Overview"],
  ["/dashboard/complaints", "Complaints"],
  ["/dashboard/notifications", "Notifications"],
  ["/dashboard/announcements", "Announcements"],
  ["/dashboard/profile", "Profile & security"],
];

const admin = [
  ["/dashboard/students", "Students"],
  ["/dashboard/departments", "Departments"],
  ["/dashboard/campus", "Campus safety"],
  ["/dashboard/reports", "Reports & exports"],
  ["/dashboard/analytics", "Analytics"],
  ["/dashboard/audit", "Security & audit"],
];

const platform = [
  ["/dashboard/platform", "Platform control"],
  ["/dashboard/health", "System health"],
];

export default function AppShell({
  children,
  title = "Campus Guardian AI",
}: {
  children: ReactNode;
  title?: string;
}) {
  const pathname = usePathname();
  const router = useRouter();

  const [auth, setAuth] = useState<Auth | null>(null);
  const [unread, setUnread] = useState(0);
  const [announcementUnread, setAnnouncementUnread] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadWorkspace() {
      try {
        const a = await apiFetch<Auth>("/auth/me");

        if (!mounted) return;

        setAuth(a);

        if (a.user.role === "Student") {
          try {
            const result = await apiFetch<{ unread: number }>(
              "/announcements/unread-count"
            );

            if (mounted) {
              setAnnouncementUnread(result.unread);
            }
          } catch {
            if (mounted) setAnnouncementUnread(0);
          }
        }

        const ns = await apiFetch<{
          items: Notification[];
          unread: number;
        }>("/notifications");

        if (mounted) {
          setUnread(ns.unread);
        }
      } catch {
        if (mounted) {
          router.replace("/login");
        }
      }
    }

    loadWorkspace();

    return () => {
      mounted = false;
    };
  }, [router]);

  useEffect(() => {
    if (auth?.user.role !== "Student") return;

    let mounted = true;

    async function refreshAnnouncementCount() {
      try {
        const result = await apiFetch<{ unread: number }>(
          "/announcements/unread-count"
        );

        if (mounted) {
          setAnnouncementUnread(result.unread);
        }
      } catch {
        // Keep the existing count if the request temporarily fails.
      }
    }

    window.addEventListener(
      "announcements-read-updated",
      refreshAnnouncementCount
    );

    return () => {
      mounted = false;
      window.removeEventListener(
        "announcements-read-updated",
        refreshAnnouncementCount
      );
    };
  }, [auth]);

  const links = useMemo(() => {
    if (!auth) return [];

    
if (auth.user.role === "Platform Admin") {
  return [
    ["/dashboard", "Platform Overview"],
    ["/dashboard/platform", "Institute Management"],
    ["/dashboard/health", "System Health"],
    ["/dashboard/audit", "Security & audit"],
    ["/dashboard/profile", "Profile & security"],
  ];
}


    if (auth.user.role === "Institute Admin") {
      return [...common, ...admin];
    }

    return [
      ["/dashboard", "Overview"],
      ["/dashboard/report", "Report an issue"],
      ...common.slice(1, 4),
      ["/dashboard/profile", "Profile & security"],
      ["/dashboard/campus", "Campus safety"],
    ];
  }, [auth]);

  async function logout() {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch {
      // Continue to login even if the logout request fails.
    }

    router.replace("/login");
  }

  if (!auth) {
    return (
      <main className="page">
        <div className="container">
          <div className="loading-card">
            {error || "Loading secure workspace…"}
          </div>
        </div>
      </main>
    );
  }

  const current = auth.user.role;

  return (
    <main className="dashboard">
      <div className="container dash-layout">
        <aside className="side">
          
<Link href="/dashboard" className="side-brand">
  <img
    src="/campus-guardian-logo-v2.png"
    alt="Campus Guardian AI"
    className="side-brand-logo"
  />
</Link>


          <div className="user-card">
            <strong>{auth.user.name}</strong>
            <span>{current}</span>
            <small>{auth.user.institute_code || "Platform scope"}</small>
          </div>

          <nav className="side-nav">
            {links.map(([href, label]) => (
              <Link
                key={href}
                className={
                  pathname === href ||
                  (href !== "/dashboard" &&
                    pathname.startsWith(href + "/"))
                    ? "active"
                    : ""
                }
                href={href}
              >
                <span>{label}</span>

                {label === "Notifications" && unread > 0 ? (
                  <b className="nav-badge">{unread}</b>
                ) : null}

                {label === "Announcements" &&
                current === "Student" &&
                announcementUnread > 0 ? (
                  <b className="nav-badge">{announcementUnread}</b>
                ) : null}
              </Link>
            ))}
          </nav>

          <button
            className="btn danger ghost full"
            onClick={logout}
          >
            Log out
          </button>
        </aside>

        <section className="workspace">{children}</section>
      </div>
    </main>
  );
}
