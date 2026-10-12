import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import "./globals.css";
import "leaflet/dist/leaflet.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
    icons: {
    icon: "/favicon.png",
    shortcut: "/favicon.png",
    apple: "/favicon.png",
  },
  title: {
    default: "Campus Guardian AI",
    template: "%s | Campus Guardian AI",
  },
  description:
    "Campus safety reporting, complaint management and institute communication platform for education teams.",
  robots: { index: true, follow: true },
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    siteName: "Campus Guardian AI",
    title: "Campus Guardian AI",
    description:
      "Campus safety reporting, complaint management and institute communication platform.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="nav">
          <div className="container nav-inner">
            <Link href="/" className="brand">
             <Image
  src="/campus-guardian-logo-v2.png"
  alt="Campus Guardian AI"
  width={180}
  height={145}
  priority
  style={{
    width: "auto",
    height: "48px",
    objectFit: "contain",
  }}
/>
            </Link>

            <nav className="nav-links" aria-label="Primary">
              <Link href="/features">Features</Link>
              <Link href="/about">About</Link>
              <Link href="/faq">FAQ</Link>
              <Link href="/contact">Contact</Link>
            </nav>

            <div className="nav-actions">
              <Link className="btn" href="/login">
                Login
              </Link>
              <Link className="btn primary" href="/register">
                Register institute
              </Link>
            </div>
          </div>
        </header>

        {children}

        <footer className="footer">
          <div className="container footer-grid">
            <div>
              <h3>Campus Guardian AI</h3>
              <p>
                Organize campus issue reporting, complaint workflows,
                communication and safety operations through one focused
                platform.
              </p>
            </div>

            <div>
              <strong>Explore</strong>
              <p>
                <Link href="/features">Features</Link>
              </p>
              <p>
                <Link href="/about">About</Link>
              </p>
              <p>
                <Link href="/faq">FAQ</Link>
              </p>
              <p>
                <Link href="/contact">Contact</Link>
              </p>
            </div>

            <div>
              <strong>Trust</strong>
              <p>
                <Link href="/privacy">Privacy</Link>
              </p>
              <p>
                <Link href="/terms">Terms</Link>
              </p>
              <p>
                <Link href="/register">Institute registration</Link>
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}