import "@/styles/globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Influence OS (Prototype)",
  description: "Open-source social growth assistant",
};

const nav = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/compose", label: "Compose" },
  { href: "/calendar", label: "Calendar" },
  { href: "/trends", label: "Trends" },
  { href: "/profile", label: "Profile" },
  { href: "/strategy", label: "Strategy" },
  { href: "/ab-tests", label: "A/B" },
  { href: "/competitors", label: "Competitors" },
  { href: "/images", label: "Images" },
  { href: "/growth", label: "Growth" },
  { href: "/settings", label: "Settings" },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b">
          <nav className="mx-auto flex max-w-7xl items-center gap-4 p-4">
            <Link href="/" className="font-semibold">
              Influence OS
            </Link>
            <div className="ml-auto flex flex-wrap gap-3 text-sm">
              {nav.map((n) => (
                <Link key={n.href} href={n.href} className="hover:underline">
                  {n.label}
                </Link>
              ))}
            </div>
          </nav>
        </header>
        <main className="mx-auto max-w-7xl p-6">{children}</main>
        <footer className="border-t mt-12">
          <div className="mx-auto max-w-7xl p-4 text-xs text-gray-500">
            © {new Date().getFullYear()} Influence OS — Prototype
          </div>
        </footer>
      </body>
    </html>
  );
}
