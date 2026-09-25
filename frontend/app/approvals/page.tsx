"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from "lucide-react";

import { useEffect, useState } from "react";

import DashboardShell from "@/components/ui/dashboard-shell";

import {
  approveAndExecute,
  getPendingApprovals,
  PendingApproval,
  resolveApproval,
} from "@/lib/api";

import { Badge } from "@/components/ui/badge";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";


export default function ApprovalsPage() {

  const [approvals, setApprovals] = useState<
    PendingApproval[]
  >([]);

  const [loading, setLoading] = useState(true);

  const [processingId, setProcessingId] =
    useState<number | null>(null);

  const [error, setError] =
    useState<string | null>(null);


  async function loadApprovals() {

    try {

      setLoading(true);
      setError(null);

      const data =
        await getPendingApprovals();

        const uniqueApprovals = Array.from(
  new Map(
    data.approvals.map((approval) => [
      approval.id,
      approval,
    ])
  ).values()
);

setApprovals(uniqueApprovals);

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load pending approvals."
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    loadApprovals();

    const interval =
      setInterval(
        loadApprovals,
        10000
      );

    return () =>
      clearInterval(interval);

  }, []);


  async function handleDecision(
  approvalId: number,
  decision: "approved" | "rejected"
) {
  try {
    setProcessingId(approvalId);
    setError(null);

    if (decision === "approved") {
      const result =
        await approveAndExecute(approvalId);

      console.log(
        "Approved action result:",
        result
      );

      if (!result.success) {
        setError(
          result.message ??
            result.execution?.error ??
            "The approved action could not be executed."
        );

        return;
      }
    } else {
      await resolveApproval(
        approvalId,
        "rejected"
      );
    }

    await loadApprovals();

  } catch (err) {
    console.error(err);

    setError(
      err instanceof Error
        ? err.message
        : "The approval decision could not be completed."
    );

  } finally {
    setProcessingId(null);
  }
}


  return (
    <DashboardShell>

      <div className="mx-auto max-w-[1200px] px-5 py-7 sm:px-8 lg:px-10">

        {/* HEADER */}

        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">

          <div>

            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#0077b6]">
              Human-in-the-loop
            </p>

            <h1 className="mt-2 text-2xl font-semibold">
              Approvals
            </h1>

            <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-500">
              Review financially consequential actions
              before your AI teammate executes them.
            </p>

          </div>


          <button
            onClick={loadApprovals}
            className="flex w-fit items-center gap-2 rounded-lg border border-[#b9e7f4] bg-white px-4 py-2 text-xs font-semibold text-[#0077b6] shadow-sm transition hover:bg-[#f4fcfe]"
          >

            <RefreshCw className="h-3.5 w-3.5" />

            Refresh

          </button>

        </div>


        {/* ERROR */}

        {error && (

          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700">

            {error}

          </div>

        )}


        {/* STATUS BANNER */}

        <div className="mt-6 rounded-2xl border border-[#bde8f5] bg-[#eaf9fd] p-5">

          <div className="flex gap-4">

            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#00baf2] text-white">

              <ShieldCheck className="h-5 w-5" />

            </div>

            <div>

              <p className="text-sm font-semibold text-slate-900">

                Financial actions require human approval

              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">

                ReconcileAI can investigate and verify
                discrepancies autonomously, but consequential
                financial changes remain behind an approval gate.

              </p>

            </div>

          </div>

        </div>


        {/* SUMMARY */}

        <div className="mt-5 grid gap-4 md:grid-cols-3">

          <SummaryCard
            title="Pending"
            value={
              loading
                ? "—"
                : String(approvals.length)
            }
            icon={
              <Clock3 className="h-4 w-4" />
            }
          />

          <SummaryCard
            title="Approval policy"
            value="Human"
            icon={
              <ShieldCheck className="h-4 w-4" />
            }
          />

          <SummaryCard
            title="Automation"
            value="Active"
            icon={
              <CheckCircle2 className="h-4 w-4" />
            }
          />

        </div>


        {/* APPROVAL LIST */}

        <Card className="mt-6 border-slate-200 shadow-sm">

          <CardHeader className="border-b border-slate-100">

            <div className="flex items-center justify-between">

              <div>

                <CardTitle className="text-sm">
                  Pending decisions
                </CardTitle>

                <p className="mt-1 text-xs text-slate-400">
                  Actions waiting for an authorized human decision.
                </p>

              </div>

              <Badge className="border-0 bg-[#eaf9fd] text-[#0077b6]">

                {approvals.length} pending

              </Badge>

            </div>

          </CardHeader>


          <CardContent className="p-0">

            {loading ? (

              <div className="px-5 py-14 text-center text-xs text-slate-400">

                Loading approvals...

              </div>

            ) : approvals.length === 0 ? (

              <div className="px-5 py-16 text-center">

                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">

                  <CheckCircle2 className="h-6 w-6 text-emerald-500" />

                </div>

                <p className="mt-4 text-sm font-semibold">

                  No pending approvals

                </p>

                <p className="mx-auto mt-1 max-w-md text-xs leading-5 text-slate-400">

                  Your AI teammate has no financially consequential
                  actions waiting for a human decision.

                </p>

              </div>

            ) : (

              <div className="divide-y divide-slate-100">

                {approvals.map(
  (approval, index) => (
    <ApprovalRow
      key={`${approval.id}-${approval.case_id}-${index}`}
      approval={approval}
      processing={
        processingId === approval.id
      }
      onDecision={
        handleDecision
      }
    />
  )
)}

              </div>

            )}

          </CardContent>

        </Card>

      </div>

    </DashboardShell>
  );
}


/* -------------------------------- */
/* APPROVAL ROW */
/* -------------------------------- */

function ApprovalRow({
  approval,
  processing,
  onDecision,
}: {
  approval: PendingApproval;
  processing: boolean;
  onDecision: (
    id: number,
    decision: "approved" | "rejected"
  ) => void;
}) {

  return (

    <div className="p-5 transition hover:bg-[#f8fcfe]">

      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

        {/* LEFT */}

        <div className="flex gap-4">

          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-600">

            <AlertTriangle className="h-5 w-5" />

          </div>


          <div>

            <div className="flex flex-wrap items-center gap-2">

              <p className="text-sm font-semibold">

                Approval #{approval.id}

              </p>

              <Badge className="border-0 bg-amber-50 text-[10px] text-amber-700">

                Pending

              </Badge>

            </div>


            <p className="mt-1 text-xs text-slate-400">

              Case #{approval.case_id}

            </p>


            <div className="mt-3">

              <p className="text-xs font-semibold text-slate-700">

                {formatAction(
                  approval.requested_action
                )}

              </p>

              <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-500">

                {approval.reason ??
                  "Human review is required before this action can proceed."}

              </p>

            </div>

          </div>

        </div>


        {/* ACTIONS */}

        <div className="flex shrink-0 gap-2">

          <button
            disabled={processing}
            onClick={() =>
              onDecision(
                approval.id,
                "rejected"
              )
            }
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >

            <XCircle className="h-3.5 w-3.5" />

            Reject

          </button>


          <button
            disabled={processing}
            onClick={() =>
              onDecision(
                approval.id,
                "approved"
              )
            }
            className="flex items-center gap-2 rounded-lg bg-[#00baf2] px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-[#009ed0] disabled:cursor-not-allowed disabled:opacity-50"
          >

            <CheckCircle2 className="h-3.5 w-3.5" />

            {processing
  ? "Executing..."
  : "Approve & execute"}

          </button>

        </div>

      </div>

    </div>
  );
}


/* -------------------------------- */
/* SUMMARY CARD */
/* -------------------------------- */

function SummaryCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
}) {

  return (

    <Card className="border-slate-200 bg-white shadow-sm">

      <CardContent className="flex items-center justify-between p-5">

        <div>

          <p className="text-xs text-slate-400">
            {title}
          </p>

          <p className="mt-2 text-2xl font-semibold">
            {value}
          </p>

        </div>

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#eefaff] text-[#008bc2]">

          {icon}

        </div>

      </CardContent>

    </Card>
  );
}


/* -------------------------------- */
/* HELPERS */
/* -------------------------------- */

function formatAction(action: string) {

  return action
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}