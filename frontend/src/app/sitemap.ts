import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
  const paths = ["/","/features","/solutions","/how-it-works","/about","/faq","/contact","/privacy","/terms","/register","/login"];
  return paths.map(path => ({ url: `${base}${path}`, changeFrequency: "monthly", priority: path === "/" ? 1 : 0.7 }));
}
