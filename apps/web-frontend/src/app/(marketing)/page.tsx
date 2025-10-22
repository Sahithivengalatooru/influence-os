import Image from "next/image";
import Link from "next/link";

export default function MarketingPage() {
  const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/compose", label: "Compose" },
    { href: "/calendar", label: "Calendar" },
    { href: "/trends", label: "Trends" },
    { href: "/profile", label: "Profile" },
    { href: "/strategy", label: "Strategy" },
    { href: "/ab-tests", label: "A/B Tests" },
    { href: "/competitors", label: "Competitors" },
    { href: "/images", label: "Images" },
    { href: "/growth", label: "Growth" },
    { href: "/settings", label: "Settings" },
  ];
  return (
    <section className="grid gap-8 lg:grid-cols-2 items-center">
      <div className="space-y-4">
        <h1 className="text-3xl font-bold tracking-tight">Grow your LinkedIn, automatically.</h1>
        <p className="text-gray-600">
          Research topics, generate on-brand posts, schedule, publish, and measure impact —
          all powered by open-source models (with graceful fallbacks for this prototype).
        </p>
        <div className="flex gap-3 flex-wrap">
          {links.map(l => (
            <Link key={l.href} href={l.href} className="rounded-lg border px-4 py-2">{l.label}</Link>
          ))}
        </div>
      </div>
      <div className="flex justify-center">
        <Image src="/icons/logo.svg" alt="logo" width={160} height={160} />
      </div>
    </section>
  );
}
