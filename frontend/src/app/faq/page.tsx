
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Frequently Asked Questions",
  description:
    "Answers about institute registration, student complaints, account access, privacy and Campus Guardian AI workflows.",
};

const faqs = [
  [
    "What is Campus Guardian AI?",
    "Campus Guardian AI is a web platform for campus issue reporting, complaint management, institute announcements and campus safety operations.",
  ],
  [
    "Who can use the platform?",
    "The application has separate workflows for Students, Institute Admins and Platform Admins. The actions available to each user depend on their assigned role and permissions.",
  ],
  [
    "How does an institute register?",
    "Use the Institute Registration page and submit the requested details. Registration is subject to the platform's review and approval process. Submitting a registration does not itself guarantee approval.",
  ],
  [
    "How do students get access?",
    "Student access is managed through the institute's account and student-management workflow. Contact your institute administrator if you need help with access.",
  ],
  [
    "How do I submit a complaint?",
    "Sign in to your student workspace, open the issue-reporting page and provide the requested description and location details. Add supporting evidence if the form offers that option.",
  ],
  [
    "Can I track a complaint?",
    "The application supports complaint status and workflow updates. The details visible to a user depend on their permissions and the information recorded by the institute team.",
  ],
  [
    "Can I report an issue anonymously?",
    "The complaint workflow includes an anonymous-reporting option where available. Review the reporting form and the applicable privacy information before submitting. Do not assume that every detail or uploaded attachment is automatically anonymous.",
  ],
  [
    "Does AI make the final complaint decision?",
    "Available local analysis can suggest categories or priority and flag similar complaints. These signals support review; they should not be treated as a substitute for authorized staff decisions.",
  ],
  [
    "How are complaints assigned and resolved?",
    "Authorized institute staff can use the available workflow to update status, assign departments or users, manage SLA targets and record resolution notes.",
  ],
  [
    "Who can see institute information?",
    "The application uses role-based access and institute-scoped workflows. Users should access only the information permitted for their account. For a specific data-access question, contact the responsible institute or platform team.",
  ],
  [
    "Is a mobile application available?",
    "This website provides the web application. Do not assume a separate Android or iOS app is available unless an official release link is published.",
  ],
  [
    "What does the platform cost?",
    "Pricing and commercial terms should be confirmed with the platform team. Do not assume that registration guarantees a free or paid plan.",
  ],
  [
    "How can I get support?",
    "Use the Contact page to see the contact method configured for this deployment. Students can also contact their institute administrator about institute-managed accounts.",
  ],
];

export default function FAQ() {
  return (
    <main className="page">
      <div className="container prose">
        <span className="eyebrow">Help and information</span>
        <h1>Frequently asked questions</h1>
        <p>
          Find answers about institute onboarding, student reporting, complaint
          workflows and account access. If a question depends on your
          institute's configuration, contact its administrator.
        </p>

        {faqs.map(([question, answer]) => (
          <section key={question}>
            <h2>{question}</h2>
            <p>{answer}</p>
          </section>
        ))}

        <section>
          <h2>Still need help?</h2>
          <p>
            <a href="/contact">View contact options</a>
            {" · "}
            <a href="/register">Institute registration</a>
            {" · "}
            <a href="/login">Login</a>
          </p>
        </section>
      </div>
    </main>
  );
}
