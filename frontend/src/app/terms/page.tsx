
import Link from "next/link";

const terms = [
  {
    title: "1. Eligibility and Accounts",
    body: (
      <>
        <p>
          You must provide accurate information when registering or using the
          platform. Accounts may be subject to institute verification,
          approval and role-based access.
        </p>
        <p>
          You are responsible for protecting your credentials and for activity
          performed through your account, except where applicable law provides
          otherwise. Do not impersonate another person or access an account
          without authorization.
        </p>
      </>
    ),
  },
  {
    title: "2. User Roles and Responsibilities",
    body: (
      <>
        <p><strong>Students:</strong> Submit genuine, relevant and respectful reports. Provide accurate information and upload only material you are permitted to share.</p>
        <p><strong>Institute Administrators:</strong> Use administrative access only for legitimate institute purposes. Handle complaints fairly, protect personal information and avoid unauthorized disclosure.</p>
        <p><strong>Platform Administrators:</strong> Use platform-level access only for authorized operational, security and support purposes.</p>
      </>
    ),
  },
  {
    title: "3. Complaints and Reports",
    body: (
      <>
        <p>
          Campus Guardian AI provides tools for submitting and tracking campus
          complaints. Submission does not guarantee acceptance, a particular
          resolution, a specific response time or a particular outcome.
        </p>
        <p>
          Complaints may be reviewed, categorized, routed, marked as duplicate,
          updated, escalated or closed according to platform functionality and
          institute procedures. Statuses, due times and escalation indicators
          are provided to support workflow management and should not be
          interpreted as a guarantee of resolution.
        </p>
        <p>
          Do not submit knowingly false, malicious, threatening or deliberately
          misleading reports. Do not use the complaint process to harass,
          threaten or target another person.
        </p>
      </>
    ),
  },
  {
    title: "4. Photos, Attachments and Personal Information",
    body: (
      <>
        <p>
          Where uploads are available, you must have the right or permission
          needed to submit the attached content. Avoid uploading unnecessary
          personal, confidential, medical, financial or identity information.
        </p>
        <p>
          Information submitted in a complaint may be visible to authorized
          personnel who need it to review or resolve the issue. Do not assume
          that a report or attachment is private from the institute or
          administrators responsible for handling it.
        </p>
      </>
    ),
  },
  {
    title: "5. Acceptable Use",
    body: (
      <>
        <p>You must not:</p>
        <ul>
          <li>Use the platform for unlawful activity, fraud, harassment or threats.</li>
          <li>Submit false reports or knowingly misuse complaint workflows.</li>
          <li>Attempt unauthorized access, bypass access controls or interfere with service security.</li>
          <li>Upload malware or content intended to damage systems or compromise users.</li>
          <li>Scrape, copy, redistribute or exploit platform data without authorization.</li>
          <li>Use the service in a way that violates another person’s rights or applicable law.</li>
        </ul>
      </>
    ),
  },
  {
    title: "6. AI-Assisted Features",
    body: (
      <p>
        Where enabled, automated or AI-assisted tools may help organize
        complaints, identify possible similarities or suggest categories,
        priorities or actions. These outputs may be incomplete or incorrect
        and are not a substitute for human judgment. Authorized personnel
        should review important decisions and consider the actual circumstances
        before acting on a suggestion.
      </p>
    ),
  },
  {
    title: "7. Notifications and Communications",
    body: (
      <p>
        The platform may send service-related communications, such as account,
        complaint-status or institute notifications, using available channels.
        Delivery may be delayed, blocked or unavailable due to network,
        provider, device or configuration issues. Users should not rely on a
        notification as the only source of information about an urgent matter.
      </p>
    ),
  },
  {
    title: "8. Availability and Changes to the Service",
    body: (
      <p>
        We aim to maintain a useful and reliable service, but uninterrupted
        availability is not guaranteed. Features may be updated, restricted,
        suspended or discontinued for maintenance, security, operational,
        legal or other legitimate reasons. We may also correct errors and
        improve functionality over time.
      </p>
    ),
  },
  {
    title: "9. Intellectual Property",
    body: (
      <p>
        Unless stated otherwise, the platform’s design, branding, software and
        original content are owned by or used with permission by the relevant
        rights holder. You may not copy, modify, redistribute or commercially
        exploit these materials without authorization. You retain any rights
        you already hold in content you submit, subject to the permissions
        necessary to operate and provide the service.
      </p>
    ),
  },
  {
    title: "10. Privacy",
    body: (
      <p>
        Your use of the platform is also subject to our{" "}
        <Link href="/privacy-policy">Privacy Policy</Link>, which explains
        information handling practices. You should avoid submitting
        unnecessary sensitive information and follow your institute’s
        applicable policies.
      </p>
    ),
  },
  {
    title: "11. Suspension and Termination",
    body: (
      <p>
        Access may be restricted or suspended where reasonably necessary to
        protect users, investigate suspected misuse, maintain security, comply
        with law or enforce these Terms. Where appropriate and legally
        permitted, the relevant user or institute may be informed. Account
        closure does not necessarily remove records that must be retained for
        legitimate operational, security or legal reasons.
      </p>
    ),
  },
  {
    title: "12. Disclaimers and Limitation of Liability",
    body: (
      <>
        <p>
          To the extent permitted by applicable law, the platform is provided
          on an “as available” basis. We do not guarantee that every report
          will be accurate, reviewed within a particular time or resolved to a
          user’s satisfaction.
        </p>
        <p>
          Campus Guardian AI is a complaint-management and communication tool;
          it is not an emergency-response service and does not replace
          emergency services, campus security, medical care, law enforcement
          or other appropriate authorities.
        </p>
        <p>
          Nothing in these Terms excludes or limits liability that cannot
          lawfully be excluded or limited. Any permitted limitation must be
          interpreted under applicable law.
        </p>
      </>
    ),
  },
  {
    title: "13. Changes to These Terms",
    body: (
      <p>
        These Terms may be updated as the service or applicable requirements
        change. The latest version will be published on this page with a
        revised “Last updated” date. Continued use after an update takes effect
        may be subject to the revised Terms, to the extent permitted by law.
      </p>
    ),
  },
  {
    title: "14. Governing Law",
    body: (
      <p>
        These Terms are intended to be interpreted in accordance with the laws
        of India, subject to applicable mandatory legal protections and
        requirements. Any dispute will be handled by a competent forum as
        determined under applicable law.
      </p>
    ),
  },
];

export default function TermsPage() {
  return (
    <main className="cg-legal">
      <header className="cg-legal-hero">
        <span className="cg-legal-eyebrow">CAMPUS GUARDIAN AI · LEGAL</span>
        <h1>Terms &amp; Conditions</h1>
        <p>
          The rules and responsibilities that apply when accessing or using
          Campus Guardian AI.
        </p>
        <span className="cg-legal-updated">Last updated: October 12, 2026</span>
      </header>

      <div className="cg-legal-layout">
        <aside className="cg-legal-toc">
          <h2>On this page</h2>
          <nav aria-label="Terms and Conditions sections">
            {terms.map((term, index) => (
              <a href={`#term-${index + 1}`} key={term.title}>
                {term.title}
              </a>
            ))}
            <a href="#acceptance">Acceptance</a>
          </nav>
        </aside>

        <article className="cg-legal-content">
          <div className="cg-legal-notice">
            These Terms explain general platform rules. They should be reviewed
            against the final production features, operating arrangements and
            applicable legal requirements before launch.
          </div>

          <section id="acceptance">
            <h2>Acceptance of These Terms</h2>
            <p>
              By accessing or using Campus Guardian AI, you agree to follow
              these Terms &amp; Conditions and applicable laws. If you do not
              agree, do not use the service. An institute may also have
              additional policies or procedures that apply to its users.
            </p>
          </section>

          {terms.map((term, index) => (
            <section id={`term-${index + 1}`} key={term.title}>
              <h2>{term.title}</h2>
              {term.body}
            </section>
          ))}

          <section id="contact">
            <h2>15. Contact</h2>
            <p>
              For questions about these Terms, contact Campus Guardian AI:
            </p>
            <div className="cg-legal-contact">
              <p>
                <strong>Email</strong>
                <a href="mailto:dindayal8456@gmail.com">
                  dindayal8456@gmail.com
                </a>
              </p>
              <p>
                <strong>Phone</strong>
                <a href="tel:+916201628456">+91 62016 28456</a>
              </p>
              <Link className="cg-legal-link" href="/contact">
                Visit Contact page →
              </Link>
            </div>
          </section>

          <div className="cg-legal-bottom-links">
            <Link href="/privacy-policy">Read Privacy Policy →</Link>
            <Link href="/">Return to Home →</Link>
          </div>
        </article>
      </div>
    </main>
  );
}
