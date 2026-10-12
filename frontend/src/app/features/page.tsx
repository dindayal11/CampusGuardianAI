
import Link from "next/link";

const featureGroups = [
  {
    id: "reporting",
    eyebrow: "FOR STUDENTS",
    title: "Report concerns with clarity.",
    description:
      "Give students a structured way to communicate campus issues and provide the information needed for review.",
    features: [
      {
        icon: "01",
        title: "Campus issue reporting",
        description:
          "Submit a complaint with relevant details so the concern can be reviewed through the platform's available workflow.",
      },
      {
        icon: "02",
        title: "Supporting evidence",
        description:
          "Attach supporting images or other permitted information where the reporting form and platform configuration allow it.",
      },
      {
        icon: "03",
        title: "Complaint status",
        description:
          "Check available complaint status information to understand how a submitted issue is progressing.",
      },
    ],
  },
  {
    id: "management",
    eyebrow: "FOR INSTITUTE ADMINISTRATORS",
    title: "Bring complaint handling into one workflow.",
    description:
      "Help authorized institute staff organize incoming concerns and coordinate the next steps.",
    features: [
      {
        icon: "04",
        title: "Complaint review and assignment",
        description:
          "Review submitted complaints and manage assignment or status updates according to the permissions available to the administrator.",
      },
      {
        icon: "05",
        title: "Complaint history",
        description:
          "Use available complaint history and activity records to understand previous actions and follow-up.",
      },
      {
        icon: "06",
        title: "Student and department management",
        description:
          "Manage student or department information through the administrative functions enabled for the institute.",
      },
    ],
  },
  {
    id: "communication",
    eyebrow: "CAMPUS COMMUNICATION",
    title: "Keep relevant information accessible.",
    description:
      "Make announcements and important updates easier to access through a dedicated campus platform.",
    features: [
      {
        icon: "07",
        title: "Announcements",
        description:
          "Publish or access campus announcements according to the user's role and the available announcement features.",
      },
      {
        icon: "08",
        title: "Notifications",
        description:
          "Help users notice relevant updates through the notification features enabled in the application.",
      },
      {
        icon: "09",
        title: "Campus safety support",
        description:
          "Use structured reporting and complaint follow-up to help authorized people organize campus-related concerns.",
      },
    ],
  },
  {
    id: "intelligence",
    eyebrow: "AI-ASSISTED REVIEW",
    title: "Support decisions with useful signals.",
    description:
      "Use available analysis features to help organize complaints while keeping human review central to the process.",
    features: [
      {
        icon: "10",
        title: "Keyword and similarity analysis",
        description:
          "Available analysis tools can identify relevant keywords or potentially similar complaints for further review.",
      },
      {
        icon: "11",
        title: "Duplicate complaint signals",
        description:
          "Similarity signals can help reviewers identify complaints that may describe the same issue. Results require appropriate review.",
      },
      {
        icon: "12",
        title: "Reports and oversight",
        description:
          "Use available reporting and administrative views to review complaint information within the user's authorized access.",
      },
    ],
  },
];

const principles = [
  {
    title: "Role-based access",
    description:
      "Student, Institute Admin, and Platform Admin experiences are organized around their assigned roles and permissions.",
  },
  {
    title: "Human review",
    description:
      "AI-assisted analysis can support complaint handling, but it should not be treated as a guarantee of accuracy or resolution.",
  },
  {
    title: "Structured records",
    description:
      "Available complaint details and history can help authorized users follow the handling process more clearly.",
  },
];

export default function FeaturesPage() {
  return (
    <main className="cg-features">
      {/* Hero */}
      <section className="cg-features-hero">
        <div className="cg-features-hero-inner">
          <div className="cg-features-hero-copy">
            <span className="cg-features-eyebrow">
              PLATFORM FEATURES
            </span>

            <h1>
              Everything organized around
              <span> campus concerns.</span>
            </h1>

            <p>
              Explore how Campus Guardian AI brings issue reporting, complaint
              management, campus communication, and administrative oversight
              into a structured digital workflow.
            </p>

            <div className="cg-features-actions">
              <Link
                href="/register"
                className="cg-features-button cg-features-button-primary"
              >
                Institute registration <span aria-hidden="true">↗</span>
              </Link>

              <Link
                href="/contact"
                className="cg-features-button cg-features-button-secondary"
              >
                Ask a question <span aria-hidden="true">→</span>
              </Link>
            </div>

            <p className="cg-features-hero-note">
              Available functions depend on account role and platform
              configuration.
            </p>
          </div>

          <div className="cg-features-visual" aria-hidden="true">
            <div className="cg-features-orbit cg-features-orbit-one" />
            <div className="cg-features-orbit cg-features-orbit-two" />

            <div className="cg-features-preview">
              <div className="cg-features-preview-header">
                <div>
                  <span className="cg-features-preview-label">
                    PLATFORM OVERVIEW
                  </span>
                  <strong>Campus workspace</strong>
                </div>
                <span className="cg-features-preview-mark">CG</span>
              </div>

              <div className="cg-features-preview-divider" />

              <div className="cg-features-preview-row">
                <span className="cg-features-preview-icon">01</span>
                <div>
                  <strong>Issue reporting</strong>
                  <span>Capture relevant details</span>
                </div>
                <span className="cg-features-preview-arrow">↗</span>
              </div>

              <div className="cg-features-preview-row">
                <span className="cg-features-preview-icon">02</span>
                <div>
                  <strong>Complaint workflow</strong>
                  <span>Review and follow up</span>
                </div>
                <span className="cg-features-preview-arrow">↗</span>
              </div>

              <div className="cg-features-preview-row">
                <span className="cg-features-preview-icon">03</span>
                <div>
                  <strong>Campus updates</strong>
                  <span>Access relevant information</span>
                </div>
                <span className="cg-features-preview-arrow">↗</span>
              </div>

              <div className="cg-features-preview-footer">
                <span className="cg-features-preview-dot" />
                A structured campus workflow
              </div>
            </div>

            <div className="cg-features-float cg-features-float-top">
              Organized reporting
            </div>

            <div className="cg-features-float cg-features-float-bottom">
              <span>✓</span> Role-based workspace
            </div>
          </div>
        </div>
      </section>

      {/* Feature navigation */}
      <nav
        className="cg-features-nav"
        aria-label="Feature categories"
      >
        <a href="#reporting">Student reporting <span>↘</span></a>
        <a href="#management">Complaint management <span>↘</span></a>
        <a href="#communication">Communication <span>↘</span></a>
        <a href="#intelligence">AI-assisted review <span>↘</span></a>
      </nav>

      {/* Feature groups */}
      {featureGroups.map((group) => (
        <section
          className="cg-features-group"
          id={group.id}
          key={group.id}
        >
          <div className="cg-features-group-heading">
            <span className="cg-features-eyebrow">
              {group.eyebrow}
            </span>

            <h2>{group.title}</h2>
            <p>{group.description}</p>
          </div>

          <div className="cg-features-grid">
            {group.features.map((item) => (
              <article
                className="cg-features-card"
                key={item.title}
              >
                <div className="cg-features-card-top">
                  <span className="cg-features-card-icon">
                    {item.icon}
                  </span>
                  <span className="cg-features-card-arrow" aria-hidden="true">
                    ↗
                  </span>
                </div>

                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </section>
      ))}

      {/* Trust and responsible use */}
      <section className="cg-features-principles">
        <div className="cg-features-principles-heading">
          <span className="cg-features-eyebrow">
            DESIGNED FOR RESPONSIBLE USE
          </span>

          <h2>Useful tools. Clear responsibilities.</h2>

          <p>
            Digital workflows work best when access, review, and
            accountability are considered together.
          </p>
        </div>

        <div className="cg-features-principles-list">
          {principles.map((item, index) => (
            <article
              className="cg-features-principle"
              key={item.title}
            >
              <span className="cg-features-principle-number">
                {String(index + 1).padStart(2, "0")}
              </span>

              <div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>

              <span className="cg-features-principle-arrow" aria-hidden="true">
                ↗
              </span>
            </article>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cg-features-cta">
        <span className="cg-features-eyebrow">
          EXPLORE CAMPUS GUARDIAN AI
        </span>

        <h2>See how a structured campus workflow can help.</h2>

        <p>
          Learn more about the platform, register your institute, or contact
          us with your questions.
        </p>

        <div className="cg-features-actions">
          <Link
            href="/register"
            className="cg-features-button cg-features-button-white"
          >
            Get started <span aria-hidden="true">↗</span>
          </Link>

          <Link
            href="/about"
            className="cg-features-button cg-features-button-outline"
          >
            About the platform <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>
    </main>
  );
}
