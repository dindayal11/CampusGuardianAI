
import Link from "next/link";

const supportEmail = "dindayal8456@gmail.com";
const supportPhone = "+91 6201628456";
const phoneLink = "+916201628456";

const contactOptions = [
  {
    number: "01",
    title: "Email support",
    description:
      "Share your question, report a website issue, or ask for help with your account.",
    value: supportEmail,
    href: `mailto:${supportEmail}?subject=${encodeURIComponent(
      "Campus Guardian AI — Support Request"
    )}`,
    action: "Send an email",
    symbol: "@",
  },
  {
    number: "02",
    title: "Phone support",
    description:
      "Contact us directly if you need assistance with Campus Guardian AI.",
    value: supportPhone,
    href: `tel:${phoneLink}`,
    action: "Call now",
    symbol: "☎",
  },
];

export default function ContactPage() {
  return (
    <main className="cg-contact">
      <section className="cg-contact-hero">
        <div className="cg-contact-hero-inner">
          <div className="cg-contact-copy">
            <span className="cg-contact-eyebrow">
              CAMPUS GUARDIAN AI · CONTACT
            </span>

            <h1>
              We’re here to
              <span> help your campus.</span>
            </h1>

            <p className="cg-contact-intro">
              Have a question about reporting complaints, managing your
              institute, or using Campus Guardian AI? Reach out to us using
              the contact details below.
            </p>

            <div className="cg-contact-actions">
              <a
                className="cg-contact-button cg-contact-button-primary"
                href={`mailto:${supportEmail}`}
              >
                Email us <span aria-hidden="true">↗</span>
              </a>

              <a
                className="cg-contact-button cg-contact-button-secondary"
                href={`tel:${phoneLink}`}
              >
                Call us <span aria-hidden="true">↗</span>
              </a>
            </div>

            <p className="cg-contact-note">
              Direct contact details · No account required to reach us
            </p>
          </div>

          <div className="cg-contact-visual" aria-hidden="true">
            <div className="cg-contact-orbit cg-contact-orbit-one" />
            <div className="cg-contact-orbit cg-contact-orbit-two" />

            <div className="cg-contact-message-card">
              <div className="cg-contact-message-top">
                <span className="cg-contact-status-dot" />
                <span>Campus Guardian AI</span>
              </div>

              <div className="cg-contact-message-icon">✉</div>

              <h2>Let’s connect.</h2>
              <p>
                Questions, feedback, or help with your campus account — start
                the conversation with us.
              </p>

              <div className="cg-contact-message-footer">
                <span>Support contact</span>
                <span aria-hidden="true">↗</span>
              </div>
            </div>

            <div className="cg-contact-floating cg-contact-floating-top">
              <span>✓</span> Campus support
            </div>

            <div className="cg-contact-floating cg-contact-floating-bottom">
              <span>↗</span> Direct communication
            </div>
          </div>
        </div>
      </section>

      <section className="cg-contact-details">
        <div className="cg-contact-section-heading">
          <span className="cg-contact-eyebrow">GET IN TOUCH</span>
          <h2>Choose how to contact us</h2>
          <p>
            Use whichever contact method is most convenient for you.
          </p>
        </div>

        <div className="cg-contact-card-grid">
          {contactOptions.map((option) => (
            <article className="cg-contact-card" key={option.number}>
              <div className="cg-contact-card-top">
                <span className="cg-contact-card-symbol">
                  {option.symbol}
                </span>
                <span className="cg-contact-card-number">
                  {option.number}
                </span>
              </div>

              <h3>{option.title}</h3>
              <p>{option.description}</p>

              <a className="cg-contact-detail-link" href={option.href}>
                {option.value}
              </a>

              <a
                className="cg-contact-card-action"
                href={option.href}
              >
                {option.action} <span aria-hidden="true">→</span>
              </a>
            </article>
          ))}
        </div>
      </section>

      <section className="cg-contact-help">
        <div>
          <span className="cg-contact-eyebrow">CAMPUS GUARDIAN AI</span>
          <h2>Looking for something specific?</h2>
          <p>
            Open the relevant page to access your account or learn more about
            the platform.
          </p>
        </div>

        <div className="cg-contact-help-links">
          <Link href="/features">Explore features <span>→</span></Link>
          <Link href="/faq">Read FAQs <span>→</span></Link>
          <Link href="/register">Institute registration <span>→</span></Link>
          <Link href="/login">Sign in <span>→</span></Link>
        </div>
      </section>

      <p className="cg-contact-privacy">
        Please avoid sending passwords, OTPs, or other confidential account
        credentials by email or phone.
      </p>
    </main>
  );
}
