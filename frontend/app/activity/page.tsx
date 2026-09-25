"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ActivityItem,
  getActivity,
} from "@/lib/api";

function formatActionType(value: string) {
  return value
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatTime(value: string) {
  const date = new Date(value);

  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getActionIcon(actionType: string) {
  if (actionType.includes("INVESTIGATE")) {
    return "⌕";
  }

  if (actionType.includes("VERIFY")) {
    return "✓";
  }

  if (actionType.includes("ADJUST")) {
    return "↗";
  }

  if (actionType.includes("REFUND")) {
    return "↩";
  }

  if (actionType.includes("APPROVAL")) {
    return "◉";
  }

  return "✦";
}

function getStatusClass(status: string) {
  switch (status.toLowerCase()) {
    case "completed":
    case "verified":
    case "approved":
      return "activity-status success";

    case "failed":
      return "activity-status failed";

    case "planned":
    case "pending":
      return "activity-status pending";

    default:
      return "activity-status";
  }
}

export default function ActivityPage() {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadActivity = useCallback(async () => {
    try {
      setError("");

      const result = await getActivity(50);

      if (result.success) {
        setActivities(result.activities);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load agent activity."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadActivity();
  }, [loadActivity]);

  async function handleRefresh() {
    setRefreshing(true);
    await loadActivity();
  }

  const completedCount = activities.filter(
    (item) =>
      item.status === "completed" ||
      item.status === "verified" ||
      item.status === "approved"
  ).length;

  const failedCount = activities.filter(
    (item) => item.status === "failed"
  ).length;

  return (
    <main className="min-h-screen bg-[#eef7fb]">
      <div className="mx-auto max-w-[1450px] px-6 py-8">

        {/* HEADER */}
        <section className="mb-7 flex items-end justify-between">
          <div>
            <p className="mb-2 text-[12px] font-semibold uppercase tracking-[0.18em] text-[#0077b6]">
              Agent observability
            </p>

            <h1 className="text-[30px] font-semibold tracking-tight text-[#10233f]">
              AI teammate activity
            </h1>

            <p className="mt-2 text-[14px] text-[#66809c]">
              A live record of actions performed by the reconciliation
              teammate.
            </p>
          </div>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="rounded-xl border border-[#c9e1ed] bg-white px-5 py-2.5 text-[13px] font-semibold text-[#0077b6] shadow-sm transition hover:border-[#00b9f2] hover:bg-[#f4fcff] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {refreshing ? "Refreshing..." : "↻ Refresh"}
          </button>
        </section>

        {/* ERROR */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* SUMMARY */}
        <section className="mb-7 grid grid-cols-1 gap-4 md:grid-cols-3">

          <div className="rounded-2xl border border-[#c9dce8] bg-white p-5 shadow-[0_4px_18px_rgba(19,63,92,0.04)]">
            <p className="text-[12px] font-medium text-[#7890a8]">
              Total actions
            </p>

            <p className="mt-2 text-[28px] font-semibold text-[#10233f]">
              {loading ? "—" : activities.length}
            </p>

            <p className="mt-1 text-[12px] text-[#7890a8]">
              Recorded by the agent
            </p>
          </div>

          <div className="rounded-2xl border border-[#c9dce8] bg-white p-5 shadow-[0_4px_18px_rgba(19,63,92,0.04)]">
            <p className="text-[12px] font-medium text-[#7890a8]">
              Completed
            </p>

            <p className="mt-2 text-[28px] font-semibold text-[#059669]">
              {loading ? "—" : completedCount}
            </p>

            <p className="mt-1 text-[12px] text-[#7890a8]">
              Successful agent actions
            </p>
          </div>

          <div className="rounded-2xl border border-[#c9dce8] bg-white p-5 shadow-[0_4px_18px_rgba(19,63,92,0.04)]">
            <p className="text-[12px] font-medium text-[#7890a8]">
              Failed actions
            </p>

            <p
              className={`mt-2 text-[28px] font-semibold ${
                failedCount > 0
                  ? "text-[#dc2626]"
                  : "text-[#10233f]"
              }`}
            >
              {loading ? "—" : failedCount}
            </p>

            <p className="mt-1 text-[12px] text-[#7890a8]">
              Require investigation
            </p>
          </div>
        </section>

        {/* ACTIVITY PANEL */}
        <section className="overflow-hidden rounded-2xl border border-[#c9dce8] bg-white shadow-[0_5px_24px_rgba(19,63,92,0.05)]">

          <div className="border-b border-[#e5edf2] px-6 py-5">
            <div className="flex items-center justify-between">

              <div>
                <h2 className="text-[17px] font-semibold text-[#10233f]">
                  Agent timeline
                </h2>

                <p className="mt-1 text-[12px] text-[#7890a8]">
                  Every tool execution and operational decision is recorded.
                </p>
              </div>

              <div className="rounded-full bg-[#e8f8fd] px-3 py-1 text-[11px] font-semibold text-[#0077b6]">
                LIVE BACKEND DATA
              </div>
            </div>
          </div>

          {loading ? (
            <div className="px-6 py-16 text-center text-sm text-[#7890a8]">
              Loading agent activity...
            </div>
          ) : activities.length === 0 ? (
            <div className="px-6 py-16 text-center">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[#e8f8fd] text-xl text-[#00a8df]">
                ✦
              </div>

              <p className="font-semibold text-[#10233f]">
                No activity recorded
              </p>

              <p className="mt-1 text-sm text-[#7890a8]">
                Agent actions will appear here when the teammate performs
                work.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-[#edf2f5]">

              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="group flex gap-5 px-6 py-5 transition hover:bg-[#f8fcfe]"
                >

                  {/* ICON */}
                  <div className="relative">

                    <div
                      className={`flex h-11 w-11 items-center justify-center rounded-full border text-[17px] ${
                        activity.status === "failed"
                          ? "border-red-200 bg-red-50 text-red-600"
                          : "border-[#bfe8f5] bg-[#eafaff] text-[#009ed0]"
                      }`}
                    >
                      {getActionIcon(activity.action_type)}
                    </div>

                    <div className="absolute left-[21px] top-12 h-[calc(100%+20px)] w-px bg-[#e5edf2] group-last:hidden" />
                  </div>

                  {/* CONTENT */}
                  <div className="min-w-0 flex-1">

                    <div className="flex flex-wrap items-center justify-between gap-3">

                      <div className="flex flex-wrap items-center gap-2">

                        <h3 className="text-[14px] font-semibold text-[#10233f]">
                          {formatActionType(
                            activity.action_type
                          )}
                        </h3>

                        <span
                          className={getStatusClass(
                            activity.status
                          )}
                        >
                          {activity.status}
                        </span>
                      </div>

                      <span className="text-[11px] text-[#8aa0b5]">
                        {formatTime(activity.created_at)}
                      </span>
                    </div>

                    <p className="mt-1.5 text-[13px] leading-6 text-[#637d96]">
                      {activity.description ||
                        "Agent action recorded."}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2">

                      {activity.tool_name && (
                        <span className="rounded-md bg-[#f1f6f9] px-2.5 py-1 text-[10px] font-medium text-[#6d8499]">
                          Tool: {activity.tool_name}
                        </span>
                      )}

                      {activity.case_id !== null && (
                        <span className="rounded-md bg-[#f1f6f9] px-2.5 py-1 text-[10px] font-medium text-[#6d8499]">
                          Case #{activity.case_id}
                        </span>
                      )}

                      {typeof activity.metadata?.transaction_id ===
                        "string" && (
                        <span className="rounded-md bg-[#eafaff] px-2.5 py-1 text-[10px] font-semibold text-[#0077b6]">
                          {
                            activity.metadata
                              .transaction_id
                          }
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* FOOTNOTE */}
        <div className="mt-5 flex items-center gap-2 text-[11px] text-[#8298ab]">
          <span className="h-2 w-2 rounded-full bg-[#16a34a]" />
          Activity is sourced directly from the ReconcileAI backend.
        </div>
      </div>
    </main>
  );
}