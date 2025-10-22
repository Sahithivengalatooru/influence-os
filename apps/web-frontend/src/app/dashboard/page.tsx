import dynamic from "next/dynamic";

const ContentCalendar = dynamic(() => import("@/components/ContentCalendar"), {
  ssr: false,
});
const AnalyticsCharts = dynamic(() => import("@/components/AnalyticsCharts"), {
  ssr: false,
});

export default function Dashboard() {
  return (
    <div className="grid gap-8">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border p-4">
          <h3 className="mb-2 font-medium">Content Calendar</h3>
          <ContentCalendar />
        </div>
        <div className="rounded-xl border p-4">
          <h3 className="mb-2 font-medium">Analytics</h3>
          <AnalyticsCharts />
        </div>
      </section>
    </div>
  );
}
