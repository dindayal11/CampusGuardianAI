
import Link from "next/link";

const sections = [
  {
    id: "information",
    title: "1. Information We May Collect",
    content: (
      <>
        <p>Depending on how you use Campus Guardian AI, information may include:</p>
        <ul>
          <li><strong>Account information:</strong> name, email address, phone number, password credentials, role and account status.</li>
          <li><strong>Institute information:</strong> institute name, type, contact details, address and registration or verification information.</li>
          <li><strong>Complaint information:</strong> complaint title and description, category, campus location, status, relevant timestamps, resolution notes and feedback.</li>
          <li><strong>Attachments:</strong> photographs or other files you choose to upload with a complaint, where uploads are available.</li>
          <li><strong>Service records:</strong> notifications, announcements, complaint history and security or audit records generated while using the service.</li>
          <li><strong>Technical information:</strong> limited device, browser, connection and diagnostic information where collected by the service or its infrastructure.</li>
        </ul>
        <p>Please do not include unnecessary sensitive personal information in complaints or attachments.</p>
      </>
    ),
  },
  {
    id: "use",
    title: "2. How We Use Information",
    content: (
      <>
        <p>Information may be used to:</p>
        <ul>
          <li>Create and manage accounts and institute registrations.</li>
          <li>Submit, review, route, track and resolve campus complaints.</li>
          <li>Send relevant account, complaint-status and institute notifications.</li>
          <li>Support institute administration, reporting and service operations.</li>
          <li>Detect duplicate reports, organize complaint information and support human review through automated or AI-assisted features, where enabled.</li>
          <li>Protect accounts, investigate misuse, maintain audit records and troubleshoot technical issues.</li>
          <li>Meet applicable legal obligations and respond to legitimate legal requests.</li>
        </ul>
        <p>Automated or AI-assisted suggestions should not be treated as a substitute for appropriate human review or emergency response.</p>
      </>
    ),
  },
  {
    id: "visibility",
    title: "3. Who May See Your Information",
    content: (
      <>
        <p>Access depends on the feature used, account role, institute and applicable permissions. For example:</p>
        <ul>
          <li>Students can access information made available to them through their own accounts.</li>
          <li>Authorized institute personnel may access complaints and related information needed to manage campus issues.</li>
          <li>Authorized platform administrators may access information needed to operate, secure and support the platform.</li>
          <li>Infrastructure, hosting, email or other service providers may process information when necessary to provide services to the platform.</li>
          <li>Information may be disclosed when required by law or when reasonably necessary to protect users, the service or others.</li>
        </ul>
        <p>Do not assume that a complaint or an attachment is confidential from authorized personnel responsible for handling it. If an anonymous reporting option is offered, it may hide your identity from certain complaint viewers, but it may not prevent all technical or administrative records from being generated.</p>
      </>
    ),
  },
  {
    id: "security",
    title: "4. Security and Passwords",
    content: (
      <>
        <p>We aim to use reasonable technical and organizational safeguards to protect information. No website, storage system or internet transmission can be guaranteed completely secure.</p>
        <p>Keep your login credentials private, use a strong password and notify the platform or your institute if you suspect unauthorized access. Passwords should not be shared with other users.</p>
      </>
    ),
  },
  {
    id: "retention",
    title: "5. Data Retention and Deletion",
    content: (
      <>
        <p>Information may be retained for as long as reasonably necessary to provide the service, manage complaints, maintain account and audit records, resolve disputes, protect security or comply with legal obligations.</p>
        <p>Retention periods may vary by record type and institute requirements. Deleting an account or requesting deletion may not immediately remove records that must be retained for legitimate operational, security or legal reasons. Contact us to ask about access, correction or deletion options.</p>
      </>
    ),
  },
  {
    id: "cookies",
    title: "6. Cookies and Similar Technologies",
    content: (
      <>
        <p>The website may use essential cookies or similar technologies to support login sessions, security and core functionality. Additional analytics, advertising or preference technologies may be used if they are enabled in the deployed service.</p>
        <p>Where required, appropriate notice or consent should be provided for non-essential cookies and advertising technologies. You can also manage cookies through your browser settings, although disabling essential cookies may affect website functionality.</p>
      </>
    ),
  },
  {
    id: "choices",
    title: "7. Your Choices and Rights",
    content: (
      <>
        <p>Subject to applicable law and legitimate record-keeping requirements, you may request to:</p>
        <ul>
          <li>Access or correct inaccurate account information.</li>
          <li>Ask questions about how your information is used.</li>
          <li>Request deletion of eligible information.</li>
          <li>Raise a privacy concern or complaint.</li>
        </ul>
        <p>We may need to verify your identity and clarify the request before acting. Some information may need to be handled through your institute if the institute controls the relevant records.</p>
      </>
    ),
  },
  {
    id: "children",
    title: "8. Children and Student Information",
    content: (
      <p>Campus Guardian AI is intended for use by institutions and their authorized users. Where a user is a minor, the relevant institute and responsible adults should ensure that account creation and personal-information processing comply with applicable law and institutional requirements. Please contact us if you believe information has been submitted improperly.</p>
    ),
  },
  {
    id: "third-party",
    title: "9. Third-Party Services and External Links",
    content: (
      <p>The platform may rely on third-party infrastructure or link to external websites. Those services may have their own privacy policies and practices. Review their policies before providing information directly to them. The privacy practices of an external service are not controlled by this policy.</p>
    ),
  },
  {
    id: "changes",
    title: "10. Changes to This Policy",
    content: (
      <p>We may update this Privacy Policy as the platform, its features or applicable requirements change. The updated version will be published on this page with a revised “Last updated” date. Where required, significant changes will be communicated through an appropriate channel.</p>
    ),
  },
];

export default function PrivacyPolicyPage() {
  return (
    <main className="cg-legal">
      <header className="cg-legal-hero">
        <span className="cg-legal-eyebrow">CAMPUS GUARDIAN AI · LEGAL</span>
        <h1>Privacy Policy</h1>
        <p>
          How Campus Guardian AI handles information when you use our campus
          complaint management and communication platform.
        </p>
        <span className="cg-legal-updated">Last updated: October 12, 2026</span>
      </header>

      <div className="cg-legal-layout">
        <aside className="cg-legal-toc">
          <h2>On this page</h2>
          <nav aria-label="Privacy Policy sections">
            {sections.map((section) => (
              <a href={`#${section.id}`} key={section.id}>
                {section.title}
              </a>
            ))}
            <a href="#contact">Contact</a>
          </nav>
        </aside>

        <article className="cg-legal-content">
          <div className="cg-legal-notice">
            Please read this policy carefully. It explains the information
            practices intended for the platform; actual practices should match
            the features and services enabled on the live website.
          </div>

          <section id="introduction">
            <h2>Introduction</h2>
            <p>
              Campus Guardian AI is a platform designed to help students and
              authorized institute personnel report, manage and track campus
              issues. This Privacy Policy describes the categories of
              information that may be processed, why it may be used and the
              choices available to users.
            </p>
          </section>

          {sections.map((section) => (
            <section id={section.id} key={section.id}>
              <h2>{section.title}</h2>
              {section.content}
            </section>
          ))}

          <section id="contact">
            <h2>11. Contact Us</h2>
            <p>
              For privacy questions, correction requests or concerns about
              information handled through Campus Guardian AI, contact us:
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
            <Link href="/terms">Read Terms &amp; Conditions →</Link>
            <Link href="/">Return to Home →</Link>
          </div>
        </article>
      </div>
    </main>
  );
}
