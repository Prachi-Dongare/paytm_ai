"use client";

import {
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Clock3,
  Sparkles,
  WalletCards,
} from "lucide-react";

import Link from "next/link";
import { useEffect, useState } from "react";
import { runReconciliation } from "@/lib/api";

import DashboardShell from "@/components/ui/dashboard-shell";

import { Badge } from "@/components/ui/badge";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  DashboardException,
  getDashboardActivity,
  getDashboardExceptions,
  getDashboardOverview,
} from "@/lib/api";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [refreshing, setRefreshing] = useState(false);

  const [refreshError, setRefreshError] = useState<string | null>(null);

  const [overview, setOverview] = useState<any>(null);

  const [exceptions, setExceptions] = useState<
    DashboardException[]
  >([]);

  const [activities, setActivities] = useState<any[]>([]);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError(null);

      const [
        overviewData,
        exceptionsData,
        activityData,
      ] = await Promise.all([
        getDashboardOverview(),
        getDashboardExceptions(),
        getDashboardActivity(),
      ]);

      setOverview(overviewData);

      setExceptions(
        exceptionsData.exceptions
      );

      setActivities(
        activityData.actions.slice(0, 5)
      );

    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the reconciliation backend."
      );

    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    setRefreshError(null);

    try {
      const result = await runReconciliation("M101");

      console.log("Reconciliation result:", result);

      window.location.reload();
    } catch (error) {
      setRefreshError(
        error instanceof Error
          ? error.message
          : "Failed to refresh reconciliation.",
      );
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(
      loadDashboard,
      10000
    );

    return () => clearInterval(interval);
  }, []);

  return (
    <DashboardShell>

      <div className="mx-auto max-w-[1500px] px-5 py-7 sm:px-8 lg:px-10">

        {/* HERO */}

        <div className="rounded-2xl border border-[#cdebf5] bg-[#e9f8fc] px-6 py-7 shadow-sm">

          <div className="flex items-center gap-2">

            <span className="rounded-full bg-[#00baf2]/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em] text-[#0077b6]">
              Reconciliation workspace
            </span>

            <span className="text-[11px] text-slate-400">
              Today
            </span>

          </div>

          <div className="mt-3 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">

            <div>

              <h1 className="text-2xl font-semibold tracking-tight text-slate-950">
                Operations overview
              </h1>

              <p className="mt-1.5 max-w-3xl text-sm leading-6 text-slate-500">
                Your AI teammate monitors payment reconciliation,
                investigates exceptions, and coordinates human
                approvals when required.
              </p>

            </div>

            <button
              type="button"
              onClick={handleRefresh}
              disabled={refreshing}
              className="rounded-xl border border-[#d7e4f2] bg-white px-5 py-2.5 text-sm font-semibold text-[#0070ba] shadow-sm transition hover:border-[#00baf2] hover:bg-[#f0fbff] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {refreshing ? "Reconciliation running..." : "Run reconciliation"}
            </button>

          </div>

        </div>

        {refreshError && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {refreshError}
          </div>
        )}

        {/* ERROR */}

        {error && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700">
            {error}
          </div>
        )}

        {/* METRICS */}

        <div className="mt-5 grid gap-4 md:grid-cols-3">

          <MetricCard
            label="Transactions"
            value={
              loading
                ? "—"
                : String(overview?.transactions ?? 0)
            }
            description="Today's reconciliation"
            icon={<WalletCards className="h-4 w-4" />}
          />

          <MetricCard
            label="Exceptions"
            value={
              loading
                ? "—"
                : String(overview?.exceptions ?? 0)
            }
            description={
              loading
                ? "Loading..."
                : `${overview?.open_exceptions ?? 0} unresolved`
            }
            icon={<AlertTriangle className="h-4 w-4" />}
            warning={
              (overview?.open_exceptions ?? 0) > 0
            }
          />

          <MetricCard
            label="Pending approvals"
            value={
              loading
                ? "—"
                : String(
                    overview?.pending_approvals ?? 0
                  )
            }
            description="Human decisions needed"
            icon={<Clock3 className="h-4 w-4" />}
          />

        </div>

        {/* LOWER GRID */}

        <div className="mt-5 grid gap-5 xl:grid-cols-[1.4fr_0.85fr]">

          {/* EXCEPTIONS */}

          <Card className="overflow-hidden border-[#d9e7ef] bg-white shadow-sm">

            <CardHeader className="flex flex-row items-center justify-between border-b border-slate-100">

              <div>

                <div className="flex items-center gap-2">

                  <CardTitle className="text-sm">
                    Recent exceptions
                  </CardTitle>

                  <Badge className="border-0 bg-[#fff4db] text-[10px] text-[#a96d00]">
                    {exceptions.length} detected
                  </Badge>

                </div>

                <p className="mt-1 text-xs text-slate-400">
                  Discrepancies identified during reconciliation
                </p>

              </div>

              <Link
                href="/exceptions"
                className="flex items-center gap-1 text-xs font-semibold text-[#0077b6] hover:text-[#005f91]"
              >
                View all
                <ArrowUpRight className="h-3.5 w-3.5" />
              </Link>

            </CardHeader>

            <CardContent className="p-0">

              {loading ? (

                <div className="px-5 py-10 text-center text-xs text-slate-400">
                  Loading exceptions...
                </div>

              ) : exceptions.length === 0 ? (

                <div className="px-5 py-10 text-center">

                  <CheckCircle2 className="mx-auto h-6 w-6 text-emerald-500" />

                  <p className="mt-2 text-sm font-medium">
                    No exceptions
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    All reconciliation checks are clear.
                  </p>

                </div>

              ) : (

                <div className="divide-y divide-slate-100">

                  {exceptions
                    .slice(0, 5)
                    .map((item) => (

                    <Link
                      href="/exceptions"
                      key={item.id}
                      className="group flex w-full items-center justify-between px-5 py-5 transition hover:bg-[#f4fbfd]"
                    >

                      <div className="flex items-center gap-4">

                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#fff8e8] text-[#b77900]">
                          <AlertTriangle className="h-4 w-4" />
                        </div>

                        <div>

                          <div className="flex items-center gap-2">

                            <span className="text-sm font-semibold">
                              {item.case_id}
                            </span>

                            <Badge
                              variant="outline"
                              className={
                                item.status ===
                                "resolved"
                                  ? "border-emerald-200 bg-emerald-50 text-[10px] text-emerald-700"
                                  : "border-amber-200 bg-amber-50 text-[10px] text-amber-700"
                              }
                            >
                              {item.status}
                            </Badge>

                          </div>

                          <p className="mt-1 text-xs text-slate-400">
                            {formatCaseType(
                              item.case_type
                            )}
                          </p>

                        </div>

                      </div>

                      <div className="flex items-center gap-3">

                        <div className="text-right">

                          <p className="text-sm font-semibold">
                            ₹
                            {Number(
                              item.difference
                            ).toLocaleString("en-IN")}
                          </p>

                          <p className="text-[10px] uppercase text-slate-400">
                            difference
                          </p>

                        </div>

                        <ArrowUpRight className="h-4 w-4 text-slate-300 transition group-hover:text-[#00baf2]" />

                      </div>

                    </Link>

                  ))}

                </div>

              )}

            </CardContent>

          </Card>

          {/* ACTIVITY */}

          <Card className="border-[#d9e7ef] bg-white shadow-sm">

            <CardHeader>

              <div className="flex items-center gap-3">

                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#00baf2] text-white">
                  <Sparkles className="h-4 w-4" />
                </div>

                <div>

                  <CardTitle className="text-sm">
                    AI teammate activity
                  </CardTitle>

                  <p className="mt-1 text-xs text-slate-400">
                    Recent autonomous actions
                  </p>

                </div>

              </div>

            </CardHeader>

            <CardContent>

              {loading ? (

                <p className="text-xs text-slate-400">
                  Loading activity...
                </p>

              ) : activities.length === 0 ? (

                <p className="text-xs text-slate-400">
                  No activity recorded yet.
                </p>

              ) : (

                <div className="space-y-5">

                  {activities.map((activity) => (

                    <ActivityItem
                      key={activity.id}
                      title={formatAction(
                        activity.action_type
                      )}
                      description={
                        activity.description ??
                        "AI teammate action completed."
                      }
                      time={formatTime(
                        activity.created_at
                      )}
                    />

                  ))}

                </div>

              )}

            </CardContent>

          </Card>

        </div>

      </div>

    </DashboardShell>
  );
}

function MetricCard({
  label,
  value,
  description,
  icon,
  warning = false,
}: {
  label: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  warning?: boolean;
}) {
  return (
    <Card className="border-[#d9e7ef] bg-white shadow-sm transition hover:-translate-y-0.5 hover:border-[#8ddcf1] hover:shadow-md">

      <CardContent className="p-5">

        <div className="flex items-start justify-between">

          <div>

            <p className="text-xs text-slate-400">
              {label}
            </p>

            <p className="mt-2 text-3xl font-semibold">
              {value}
            </p>

            <p
              className={`mt-1 text-xs ${
                warning
                  ? "font-medium text-amber-600"
                  : "text-slate-400"
              }`}
            >
              {description}
            </p>

          </div>

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#eefaff] text-[#008bc2]">
            {icon}
          </div>

        </div>

      </CardContent>

    </Card>
  );
}

function ActivityItem({
  title,
  description,
  time,
}: {
  title: string;
  description: string;
  time: string;
}) {
  return (
    <div className="flex gap-3">

      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#bfeaf7] bg-[#f0fbfe] text-[#008bc2]">
        <CheckCircle2 className="h-3.5 w-3.5" />
      </div>

      <div className="min-w-0 flex-1">

        <div className="flex justify-between gap-3">

          <p className="text-xs font-semibold">
            {title}
          </p>

          <span className="whitespace-nowrap text-[10px] text-slate-400">
            {time}
          </span>

        </div>

        <p className="mt-1 text-xs leading-5 text-slate-400">
          {description}
        </p>

      </div>

    </div>
  );
}

function formatCaseType(type: string) {
  return type
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

function formatAction(action: string) {
  return action
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

function formatTime(value: string | null) {
  if (!value) {
    return "Recently";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Recently";
  }

  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}