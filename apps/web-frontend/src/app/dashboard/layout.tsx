export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section className="grid gap-4">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      {children}
    </section>
  );
}
