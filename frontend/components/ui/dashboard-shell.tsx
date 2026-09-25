"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  LayoutDashboard,
  ListChecks,
  Sparkles,
} from "lucide-react";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  {
    label: "Overview",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Exceptions",
    href: "/exceptions",
    icon: AlertTriangle,
  },
  {
    label: "Approvals",
    href: "/approvals",
    icon: ListChecks,
  },
  {
    label: "Activity",
    href: "/activity",
    icon: Activity,
  },
];

export default function DashboardShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <main className="min-h-screen bg-[#edf4f9] text-slate-900">
      <div className="flex min-h-screen">

        {/* ================= SIDEBAR ================= */}

        <aside className="hidden w-[248px] shrink-0 bg-[#002970] text-white lg:flex lg:flex-col">

          {/* Brand */}
          <div className="px-6 py-7">
            <Link href="/" className="flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#00baf2] shadow-lg shadow-cyan-950/20">
                <Sparkles className="h-4 w-4" />
              </div>

              <div>
                <div className="text-[15px] font-semibold">
                  ReconcileAI
                </div>

                <div className="text-[11px] text-blue-200/70">
                  Merchant Operations
                </div>
              </div>

            </Link>
          </div>

          <div className="h-px bg-[#17458c]" />

          {/* Navigation */}
          <nav className="flex-1 px-3 py-6">

            <div className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-200/50">
              Workspace
            </div>

            <div className="space-y-1">

              {navigation.map((item) => {

                const Icon = item.icon;

                const active =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname.startsWith(item.href);

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition-all ${
                      active
                        ? "bg-[#00baf2] text-white shadow-md shadow-cyan-950/20"
                        : "text-blue-100/70 hover:bg-white/10 hover:text-white"
                    }`}
                  >

                    <Icon className="h-4 w-4" />

                    <span className="font-medium">
                      {item.label}
                    </span>

                    {item.label === "Exceptions" && (
                      <span
                        className={`ml-auto rounded-full px-2 py-0.5 text-[10px] ${
                          active
                            ? "bg-white/20"
                            : "bg-[#17458c] text-blue-100"
                        }`}
                      >
                        3
                      </span>
                    )}

                  </Link>
                );
              })}

            </div>
          </nav>

          {/* System status */}
          <div className="border-t border-[#17458c] p-4">

            <div className="rounded-xl border border-white/10 bg-[#001f55] p-4">

              <div className="flex items-center gap-2">

                <span className="h-2 w-2 rounded-full bg-emerald-400" />

                <span className="text-xs font-semibold">
                  System operational
                </span>

              </div>

              <p className="mt-2 text-[11px] leading-5 text-blue-200/60">
                Reconciliation services are connected and responding normally.
              </p>

            </div>

          </div>
        </aside>

        {/* ================= MAIN ================= */}

        <section className="min-w-0 flex-1">

          {/* Header */}
          <header className="border-b border-[#dce8f0] bg-white">

            <div className="flex h-[72px] items-center justify-between px-5 sm:px-8">

              <div>

                <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                  Merchant workspace
                </div>

                <div className="mt-1 text-sm font-semibold text-slate-950">
                  Demo Merchant
                </div>

              </div>

              <div className="flex items-center gap-3">

                <div className="hidden items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1.5 sm:flex">

                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />

                  <span className="text-[11px] font-medium text-emerald-700">
                    Connected
                  </span>

                </div>

                <div className="rounded-full border border-[#c5eaf7] bg-[#f0fbfe] px-3 py-1 text-xs font-semibold text-[#0077b6]">
                  M101
                </div>

                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#dff6fc] text-xs font-bold text-[#0077b6]">
                  DA
                </div>

              </div>

            </div>

          </header>

          {children}

        </section>

      </div>
    </main>
  );
}