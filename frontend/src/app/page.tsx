
import Link from "next/link";

const capabilities = [
  {
    number: "01",
    title: "Structured complaint reporting",
    description:
      "Provide a clear way to describe campus concerns, share relevant details, and submit information for review.",
    href: "/features#reporting",
  },
  {
    number: "02",
    title: "Organized complaint workflow",
    description:
      "Help authorized institute staff review complaints, manage available status updates, and coordinate follow-up.",
    href: "/features#management",
  },
  {
    number: "03",
    title: "Campus announcements",
    description:
      "Make relevant institute updates and announcements accessible through the platform's available communication features.",
    href: "/features#communication",
  },
  {
    number: "04",
    title: "AI-assisted review",
    description:
      "Where enabled, keyword and similarity analysis can help identify complaints that may need closer review.",
    href: "/features#intelligence",
  },
];

const audiences = [
  {
    label: "01 / STUDENTS",
    title: "A clearer way to raise campus concerns.",
    description:
      "Use the available complaint reporting process to describe an issue and check the status information provided by the platform.",
    points: [
      "Structured issue reporting",
      "Access to relevant announcements",
      "Complaint status information, where available",
    ],
  },
  {
    label: "02 / INSTITUTE ADMINISTRATORS",
    title: "A more organized approach to complaint handling.",
    description:
      "Use the administrative functions available to your account to review complaints and coordinate the next steps.",
    points: [
      "Complaint review and management",
      "Student and department administration, where enabled",
      "Available complaint history and oversight",
    ],
  },
];

const faqs = [
  {
    question: "What is Campus Guardian AI?",
    answer:
      "Campus Guardian AI is a campus issue reporting, complaint management, and institute communication platform designed to help organize campus-related concerns and their follow-up.",
  },
  {
    question: "Who can use the platform?",
    answer:
      "The platform is designed for students, institute administrators, and platform administrators. The functions available to each person depend on their assigned role and permissions.",
  },
  {
    question: "Does AI guarantee that a complaint is genuine or resolved?",
    answer:
      "No. AI-assisted keyword or similarity analysis can support review, but it can make mistakes. Appropriate human review and the institute's handling process remain important.",
  },
  {
    question: "How can I get help?",
    answer:
      "Visit the Contact page to find the available email and phone contact options for Campus Guardian AI.",
  },
];

export default function HomePage() {
  return (
    <main className="cg-home">
      {/* Hero */}
      <section className="cg-home-hero">
        <div className="cg-home-hero-inner">
          <div className="cg-home-hero-copy">
            <span className="cg-home-eyebrow">
              CAMPUS ISSUE REPORTING & MANAGEMENT
            </span>

            <h1>
              Better organized campuses start with
              <span> being heard.</span>
            </h1>

            <p>
              Campus Guardian AI brings campus issue reporting, complaint
              management, and institute communication into a structured
              digital workflow.
            </p>

            <div className="cg-home-actions">
              <Link
                href="/features"
                className="cg-home-button cg-home-button-primary"
              >
                Explore platform <span aria-hidden="true">↗</span>
              </Link>

              <Link
                href="/about"
                className="cg-home-button cg-home-button-secondary"
              >
                Learn about us <span aria-hidden="true">→</span>
              </Link>
            </div>

            <div className="cg-home-trust-note">
              <span aria-hidden="true">✓</span>
              Clear processes. Role-based access. Responsible AI assistance.
            </div>
          </div>

          <div className="cg-home-hero-visual" aria-hidden="true">
            <div className="cg-home-orbit cg-home-orbit-one" />
            <div className="cg-home-orbit cg-home-orbit-two" />

            <div className="cg-home-dashboard-preview">
              <div className="cg-home-preview-header">
                <div className="cg-home-preview-brand">
                  <span className="cg-home-preview-logo">CG</span>
                  <div>
                    <strong>Campus Guardian AI</strong>
                    <span>Campus workspace</span>
                  </div>
                </div>

                <span className="cg-home-preview-menu">•••</span>
              </div>

              <div className="cg-home-preview-divider" />

              <div className="cg-home-preview-heading">
                <span>COMPLAINT WORKFLOW</span>
                <strong>From report to review</strong>
              </div>

              <div className="cg-home-workflow">
                <div className="cg-home-workflow-step">
                  <span className="cg-home-step-icon">01</span>
                  <div>
                    <strong>Report a concern</strong>
                    <span>Record relevant details</span>
                  </div>
                  <span className="cg-home-step-arrow">↗</span>
                </div>

                <div className="cg-home-workflow-connector" />

                <div className="cg-home-workflow-step">
                  <span className="cg-home-step-icon">02</span>
                  <div>
                    <strong>Review the report</strong>
                    <span>Support organized handling</span>
                  </div>
                  <span className="cg-home-step-arrow">↗</span>
                </div>

                <div className="cg-home-workflow-connector" />

                <div className="cg-home-workflow-step">
                  <span className="cg-home-step-icon">03</span>
                  <div>
                    <strong>Follow up</strong>
                    <span>Use available status updates</span>
                  </div>
                  <span className="cg-home-step-arrow">↗</span>
                </div>
              </div>

              <div className="cg-home-preview-footer">
                <span className="cg-home-preview-dot" />
                A structured approach to campus concerns
              </div>
            </div>

            <div className="cg-home-floating cg-home-floating-top">
              <span>✓</span> Organized reporting
            </div>

            <div className="cg-home-floating cg-home-floating-bottom">
              Responsible AI assistance
            </div>
          </div>
        </div>
      </section>

      {/* Product introduction */}
      <section className="cg-home-intro">
        <div className="cg-home-intro-heading">
          <span className="cg-home-eyebrow">WHY CAMPUS GUARDIAN AI</span>
          <h2>Campus concerns deserve a process, not confusion.</h2>
        </div>

        <div className="cg-home-intro-copy">
          <p>
            A campus issue may need to be reported, reviewed, assigned, and
            followed up by different people. When information is scattered,
            understanding the next step can become difficult.
          </p>

          <p>
            Campus Guardian AI is designed to bring these activities into a
            more structured workflow, helping authorized users access relevant
            complaint information and communication in one platform.
          </p>

          <Link href="/about" className="cg-home-text-link">
            Learn about our approach <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="cg-home-capabilities">
        <div className="cg-home-section-heading">
          <span className="cg-home-eyebrow">PLATFORM CAPABILITIES</span>
          <h2>Tools designed around campus needs.</h2>
          <p>
            Explore the main areas of the platform and how they support
            reporting, administration, and communication.
          </p>
        </div>

        <div className="cg-home-capability-grid">
          {capabilities.map((item) => (
            <article
              className="cg-home-capability-card"
              key={item.title}
            >
              <div className="cg-home-capability-top">
                <span className="cg-home-capability-number">
                  {item.number}
                </span>

                <span className="cg-home-capability-arrow" aria-hidden="true">
                  ↗
                </span>
              </div>

              <h3>{item.title}</h3>
              <p>{item.description}</p>

              <Link href={item.href} className="cg-home-card-link">
                Explore feature <span aria-hidden="true">→</span>
              </Link>
            </article>
          ))}
        </div>

        <div className="cg-home-centered-link">
          <Link href="/features" className="cg-home-button cg-home-button-secondary">
            View all features <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>

      {/* User roles */}
      <section className="cg-home-audiences">
        <div className="cg-home-section-heading">
          <span className="cg-home-eyebrow">BUILT FOR CAMPUS WORKFLOWS</span>
          <h2>Different roles. Clearer responsibilities.</h2>
          <p>
            Platform access and available actions depend on the user's assigned
            role and permissions.
          </p>
        </div>

        <div className="cg-home-audience-grid">
          {audiences.map((item) => (
            <article className="cg-home-audience-card" key={item.label}>
              <span className="cg-home-audience-label">{item.label}</span>

              <h3>{item.title}</h3>
              <p>{item.description}</p>

              <ul>
                {item.points.map((point) => (
                  <li key={point}>
                    <span aria-hidden="true">✓</span>
                    {point}
                  </li>
                ))}
              </ul>

              <Link href="/features" className="cg-home-text-link">
                Explore capabilities <span aria-hidden="true">→</span>
              </Link>
            </article>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="cg-home-process">
        <div className="cg-home-process-heading">
          <span className="cg-home-eyebrow">HOW THE WORKFLOW FITS TOGETHER</span>
          <h2>Three stages. One more organized process.</h2>
          <p>
            The exact steps depend on the complaint type, permissions, and
            workflow configured for the institute.
          </p>
        </div>

        <div className="cg-home-process-grid">
          <article className="cg-home-process-step">
            <span className="cg-home-process-number">01</span>
            <h3>Report</h3>
            <p>
              Provide the relevant information through the available reporting
              process.
            </p>
          </article>

          <article className="cg-home-process-step">
            <span className="cg-home-process-number">02</span>
            <h3>Review</h3>
            <p>
              Authorized staff review the information and use the available
              tools to manage the complaint.
            </p>
          </article>

          <article className="cg-home-process-step">
            <span className="cg-home-process-number">03</span>
            <h3>Follow up</h3>
            <p>
              Use available status information and communication features to
              follow the next steps.
            </p>
          </article>
        </div>
      </section>

      {/* Responsible use */}
      <section className="cg-home-responsibility">
        <div className="cg-home-responsibility-icon" aria-hidden="true">
          i
        </div>

        <div>
          <span className="cg-home-eyebrow">RESPONSIBLE BY DESIGN</span>
          <h2>AI can assist review. People remain important.</h2>
          <p>
            Keyword and similarity analysis can help organize complaint
            information, but automated signals may be incorrect. They should
            not be treated as proof that a complaint is valid, invalid, or
            resolved. Appropriate human review remains essential.
          </p>

          <Link href="/features#intelligence" className="cg-home-text-link">
            Learn about AI-assisted review <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>

      {/* Useful FAQ content */}
      <section className="cg-home-faq">
        <div className="cg-home-faq-heading">
          <span className="cg-home-eyebrow">HELPFUL INFORMATION</span>
          <h2>Questions about the platform?</h2>
          <p>
            Read the answers below or visit the full FAQ page for more
            information.
          </p>

          <Link href="/faq" className="cg-home-text-link">
            Visit all FAQs <span aria-hidden="true">→</span>
          </Link>
        </div>

        <div className="cg-home-faq-list">
          {faqs.map((item) => (
            <details className="cg-home-faq-item" key={item.question}>
              <summary>
                <span>{item.question}</span>
                <span className="cg-home-faq-plus" aria-hidden="true">
                  +
                </span>
              </summary>

              <p>{item.answer}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Final call to action */}
      <section className="cg-home-cta">
        <span className="cg-home-eyebrow">EXPLORE THE PLATFORM</span>
        <h2>Take the next step toward a more organized campus workflow.</h2>
        <p>
          Explore the available features, learn more about the platform, or
          contact us with your questions.
        </p>

        <div className="cg-home-actions cg-home-actions-center">
          <Link
            href="/features"
            className="cg-home-button cg-home-button-white"
          >
            Explore features <span aria-hidden="true">↗</span>
          </Link>

          <Link
            href="/contact"
            className="cg-home-button cg-home-button-outline"
          >
            Contact us <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>
    </main>
  );
}
