
import Link from "next/link";

const principles = [
  {
    number: "01",
    title: "Clarity over complexity",
    description:
      "Reporting a campus issue should be straightforward. Clear forms and structured information help users explain what needs attention.",
  },
  {
    number: "02",
    title: "Responsible AI assistance",
    description:
      "Keyword and similarity signals can help organize complaints. AI-assisted suggestions should support review, not replace human judgment.",
  },
  {
    number: "03",
    title: "Accountability through workflow",
    description:
      "Complaint status, assignment, and available history can help authorized users follow an issue through its handling process.",
  },
  {
    number: "04",
    title: "Privacy-conscious design",
    description:
      "Access to campus information should be managed through appropriate roles and permissions. Sensitive information deserves careful handling.",
  },
];

const capabilities = [
  {
    icon: "01",
    title: "Structured issue reporting",
    description:
      "Give students a dedicated way to describe a campus problem, provide relevant details, and attach supporting evidence where enabled.",
  },
  {
    icon: "02",
    title: "Organized complaint handling",
    description:
      "Help authorized staff review submissions, manage complaint status, and coordinate follow-up through the available workflow.",
  },
  {
    icon: "03",
    title: "Campus communication",
    description:
      "Support announcements and relevant updates so users can access important information through the platform.",
  },
  {
    icon: "04",
    title: "Administrative visibility",
    description:
      "Provide role-based views for students, institute administrators, and platform administrators according to their permissions.",
  },
];

export default function AboutPage() {
  return (
    <main className="cg-about">
      {/* Hero */}
      <section className="cg-about-hero">
        <div className="cg-about-hero-inner">
          <div className="cg-about-hero-copy">
            <span className="cg-about-eyebrow">
              ABOUT CAMPUS GUARDIAN AI
            </span>

            <h1>
              A more organized way to address
              <span> campus concerns.</span>
            </h1>

            <p>
              Campus Guardian AI is a campus issue reporting and complaint
              management platform designed to help students and educational
              institutions organize concerns, communicate more clearly, and
              manage follow-up in one place.
            </p>

            <div className="cg-about-hero-actions">
              <Link
                href="/features"
                className="cg-about-button cg-about-button-primary"
              >
                Explore features <span aria-hidden="true">↗</span>
              </Link>

              <Link
                href="/contact"
                className="cg-about-button cg-about-button-secondary"
              >
                Contact us <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>

          <div className="cg-about-hero-art" aria-hidden="true">
            <div className="cg-about-art-orbit cg-about-art-orbit-one" />
            <div className="cg-about-art-orbit cg-about-art-orbit-two" />

            <div className="cg-about-art-card">
              <div className="cg-about-art-card-head">
                <span className="cg-about-art-symbol">CG</span>
                <div>
                  <strong>Campus Guardian AI</strong>
                  <span>Issue management</span>
                </div>
              </div>

              <div className="cg-about-art-line" />

              <div className="cg-about-art-item">
                <span className="cg-about-art-check">✓</span>
                <div>
                  <strong>Report an issue</strong>
                  <span>Capture relevant details</span>
                </div>
              </div>

              <div className="cg-about-art-item">
                <span className="cg-about-art-check">↗</span>
                <div>
                  <strong>Review and assign</strong>
                  <span>Support organized follow-up</span>
                </div>
              </div>

              <div className="cg-about-art-item">
                <span className="cg-about-art-check">◎</span>
                <div>
                  <strong>Track progress</strong>
                  <span>Follow available status updates</span>
                </div>
              </div>

              <div className="cg-about-art-foot">
                <span className="cg-about-art-dot" />
                A connected campus workflow
              </div>
            </div>

            <div className="cg-about-art-float cg-about-art-float-top">
              Structured reporting
            </div>

            <div className="cg-about-art-float cg-about-art-float-bottom">
              <span>✓</span> Clearer follow-up
            </div>
          </div>
        </div>
      </section>

      {/* Why the platform exists */}
      <section className="cg-about-intro">
        <div className="cg-about-section-label">
          <span className="cg-about-eyebrow">WHY IT EXISTS</span>
          <h2>Campus concerns deserve a clear process.</h2>
        </div>

        <div className="cg-about-intro-copy">
          <p>
            Campus-related problems can involve different people, departments,
            and stages of resolution. When information is scattered, it can
            become harder to understand what was reported and what needs to
            happen next.
          </p>

          <p>
            Campus Guardian AI aims to bring issue reporting, complaint
            management, communication, and administrative oversight into a
            more structured digital workflow.
          </p>
        </div>
      </section>

      {/* Capabilities */}
      <section className="cg-about-capabilities">
        <div className="cg-about-section-heading">
          <span className="cg-about-eyebrow">WHAT THE PLATFORM DOES</span>
          <h2>Built around practical campus needs.</h2>
          <p>
            The platform brings together key activities involved in reporting
            and managing campus concerns.
          </p>
        </div>

        <div className="cg-about-capability-grid">
          {capabilities.map((item) => (
            <article
              className="cg-about-capability"
              key={item.title}
            >
              <span className="cg-about-capability-number">
                {item.icon}
              </span>

              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Principles */}
      <section className="cg-about-principles">
        <div className="cg-about-section-heading">
          <span className="cg-about-eyebrow">OUR APPROACH</span>
          <h2>Technology with responsibility.</h2>
          <p>
            Useful software should make processes easier to understand without
            making promises it cannot guarantee.
          </p>
        </div>

        <div className="cg-about-principle-list">
          {principles.map((item) => (
            <article
              className="cg-about-principle"
              key={item.number}
            >
              <span className="cg-about-principle-number">
                {item.number}
              </span>

              <div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>

              <span
                className="cg-about-principle-arrow"
                aria-hidden="true"
              >
                ↗
              </span>
            </article>
          ))}
        </div>
      </section>

      {/* Transparency */}
      <section className="cg-about-transparency">
        <div
          className="cg-about-transparency-icon"
          aria-hidden="true"
        >
          i
        </div>

        <div>
          <span className="cg-about-eyebrow">OUR COMMITMENT</span>
          <h2>Clear about what technology can do.</h2>
          <p>
            AI-assisted categorization and similarity checks can support
            complaint review, but they are not infallible. Actual outcomes
            depend on the information provided, the available platform
            features, and the people responsible for handling each issue.
            Campus Guardian AI is designed to support campus processes, not
            guarantee that every complaint will be resolved.
          </p>
        </div>
      </section>

      {/* Call to action */}
      <section className="cg-about-cta">
        <span className="cg-about-eyebrow">GET STARTED</span>

        <h2>Make campus issue management more organized.</h2>

        <p>
          Explore the platform, learn how it works, or contact us if you have
          a question.
        </p>

        <div className="cg-about-hero-actions">
          <Link
            href="/register"
            className="cg-about-button cg-about-button-white"
          >
            Institute registration <span aria-hidden="true">↗</span>
          </Link>

          <Link
            href="/contact"
            className="cg-about-button cg-about-button-outline"
          >
            Get in touch <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>
    </main>
  );
}
