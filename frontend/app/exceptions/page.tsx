"use client";

import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Clock3,
  RefreshCw,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";

import type React from "react";
import { useEffect, useMemo, useState } from "react";

import DashboardShell from "@/components/ui/dashboard-shell";

import {
  DashboardException,
  getDashboardExceptions,
} from "@/lib/api";

import { Badge } from "@/components/ui/badge";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";


type FilterType = "all" | "open" | "resolved";


export default function ExceptionsPage() {
  const [exceptions, setExceptions] = useState<
    DashboardException[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");

  const [filter, setFilter] =
    useState<FilterType>("all");

  const [selectedException, setSelectedException] =
    useState<DashboardException | null>(null);


  async function loadExceptions(
    showRefreshing = false,
  ) {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError(null);

      const data = await getDashboardExceptions();

      setExceptions(data.exceptions);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to load reconciliation exceptions.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }


  useEffect(() => {
    loadExceptions();

    const interval = setInterval(() => {
      loadExceptions();
    }, 10000);

    return () => clearInterval(interval);
  }, []);


  const filteredExceptions = useMemo(() => {
    const query = search.trim().toLowerCase();

    return exceptions.filter((item) => {
      const matchesSearch =
        !query ||
        item.case_id
          .toLowerCase()
          .includes(query) ||
        item.transaction_id
          ?.toString()
          .toLowerCase()
          .includes(query) ||
        item.case_type
          .toLowerCase()
          .includes(query) ||
        item.description
          ?.toLowerCase()
          .includes(query);

      const status =
        item.status.toLowerCase();

      const matchesFilter =
        filter === "all" ||
        status === filter;

      return matchesSearch && matchesFilter;
    });
  }, [exceptions, search, filter]);


  const total = exceptions.length;

  const resolved = exceptions.filter(
    (item) =>
      item.status.toLowerCase() ===
      "resolved",
  ).length;

  const open = exceptions.filter(
    (item) =>
      item.status.toLowerCase() ===
      "open",
  ).length;


  return (
    <DashboardShell>
      <div className="min-h-full bg-[#eef7fc]">
        <div className="mx-auto max-w-[1500px] px-5 py-7 sm:px-8 lg:px-10">

          {/* HEADER */}
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">

            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#0077b6]">
                Merchant operations
              </p>

              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[#10243e]">
                Exceptions
              </h1>

              <p className="mt-2 text-sm text-[#5f7692]">
                Review discrepancies identified during
                reconciliation.
              </p>
            </div>


            <button
              type="button"
              onClick={() => loadExceptions(true)}
              disabled={refreshing}
              className="
                inline-flex
                items-center
                justify-center
                gap-2
                rounded-xl
                border
                border-[#b9e7f4]
                bg-white
                px-4
                py-2.5
                text-xs
                font-semibold
                text-[#0077b6]
                shadow-sm
                transition
                hover:border-[#00baf2]
                hover:bg-[#f5fcff]
                disabled:cursor-not-allowed
                disabled:opacity-60
              "
            >
              <RefreshCw
                className={`h-3.5 w-3.5 ${
                  refreshing
                    ? "animate-spin"
                    : ""
                }`}
              />

              {refreshing
                ? "Refreshing..."
                : "Refresh"}
            </button>
          </div>


          {/* ERROR */}
          {error && (
            <div className="mt-5 flex items-center justify-between rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700">
              <span>{error}</span>

              <button
                type="button"
                onClick={() => loadExceptions(true)}
                className="font-semibold underline"
              >
                Retry
              </button>
            </div>
          )}


          {/* SUMMARY */}
          <div className="mt-7 grid gap-4 md:grid-cols-3">

            <SummaryCard
              title="Total exceptions"
              value={
                loading
                  ? "—"
                  : String(total)
              }
              icon={
                <AlertTriangle className="h-4 w-4" />
              }
            />

            <SummaryCard
              title="Resolved"
              value={
                loading
                  ? "—"
                  : String(resolved)
              }
              valueClass="text-emerald-600"
              icon={
                <CheckCircle2 className="h-4 w-4" />
              }
              iconClass="bg-emerald-50 text-emerald-600"
            />

            <SummaryCard
              title="Needs review"
              value={
                loading
                  ? "—"
                  : String(open)
              }
              valueClass={
                open > 0
                  ? "text-amber-600"
                  : "text-slate-900"
              }
              icon={
                <Clock3 className="h-4 w-4" />
              }
              iconClass="bg-amber-50 text-amber-600"
            />

          </div>


          {/* FILTER BAR */}
          <Card className="mt-6 border-[#d7e5ef] bg-white shadow-[0_4px_18px_rgba(20,70,100,0.04)]">

            <CardContent className="flex flex-col gap-4 p-4 md:flex-row md:items-center md:justify-between">

              {/* SEARCH */}
              <div className="flex w-full max-w-[360px] items-center gap-2 rounded-xl border border-[#d8e5ee] bg-[#f9fcfe] px-3 py-2.5 transition focus-within:border-[#00baf2] focus-within:bg-white">

                <Search className="h-4 w-4 text-[#7f96ac]" />

                <input
                  value={search}
                  onChange={(event) =>
                    setSearch(
                      event.target.value,
                    )
                  }
                  placeholder="Search case or transaction..."
                  className="
                    w-full
                    bg-transparent
                    text-xs
                    text-[#243b53]
                    outline-none
                    placeholder:text-[#8ca0b3]
                  "
                />

                {search && (
                  <button
                    type="button"
                    onClick={() =>
                      setSearch("")
                    }
                    className="text-[#8ca0b3] hover:text-[#243b53]"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>


              {/* FILTERS */}
              <div className="flex items-center gap-2">

                <SlidersHorizontal className="mr-1 h-4 w-4 text-[#8ca0b3]" />

                <FilterButton
                  active={filter === "all"}
                  onClick={() =>
                    setFilter("all")
                  }
                >
                  All
                </FilterButton>

                <FilterButton
                  active={filter === "open"}
                  onClick={() =>
                    setFilter("open")
                  }
                >
                  Open
                  {open > 0 && (
                    <span className="ml-1.5 opacity-70">
                      {open}
                    </span>
                  )}
                </FilterButton>

                <FilterButton
                  active={filter === "resolved"}
                  onClick={() =>
                    setFilter("resolved")
                  }
                >
                  Resolved
                </FilterButton>

              </div>

            </CardContent>
          </Card>


          {/* TABLE */}
          <Card className="mt-4 overflow-hidden border-[#d7e5ef] bg-white shadow-[0_4px_18px_rgba(20,70,100,0.04)]">

            <CardHeader className="border-b border-[#e8f0f5] bg-[#fbfdff]">

              <div className="flex items-center justify-between">

                <div>
                  <CardTitle className="text-sm font-semibold text-[#172b4d]">
                    Reconciliation exceptions
                  </CardTitle>

                  <p className="mt-1 text-xs text-[#8298ad]">
                    Live data from the reconciliation backend
                  </p>
                </div>

                <span className="rounded-full bg-[#edf9fd] px-2.5 py-1 text-[11px] font-medium text-[#0077b6]">
                  {filteredExceptions.length} shown
                </span>

              </div>

            </CardHeader>


            <CardContent className="p-0">

              {loading ? (

                <div className="px-5 py-16 text-center">

                  <div className="mx-auto h-7 w-7 animate-spin rounded-full border-2 border-[#d9edf4] border-t-[#00baf2]" />

                  <p className="mt-4 text-sm font-medium text-[#40566d]">
                    Loading reconciliation cases...
                  </p>

                  <p className="mt-1 text-xs text-[#8ca0b3]">
                    Fetching the latest backend state
                  </p>

                </div>

              ) : filteredExceptions.length === 0 ? (

                <div className="px-5 py-16 text-center">

                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">
                    <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                  </div>

                  <p className="mt-4 text-sm font-semibold text-[#172b4d]">
                    No matching exceptions
                  </p>

                  <p className="mt-1 text-xs text-[#8ca0b3]">
                    Try changing your search or filter.
                  </p>

                </div>

              ) : (

                <div className="overflow-x-auto">

                  <table className="w-full min-w-[950px]">

                    <thead className="bg-[#f7fafc] text-left text-[11px] text-[#7890a5]">

                      <tr>

                        <th className="px-5 py-4 font-medium">
                          Case
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Transaction
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Exception
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Expected
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Settled
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Difference
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Priority
                        </th>

                        <th className="px-5 py-4 font-medium">
                          Status
                        </th>

                        <th className="w-10 px-3 py-4" />

                      </tr>

                    </thead>


                    <tbody className="divide-y divide-[#edf2f6]">

                      {filteredExceptions.map(
                        (item) => {

                          const isResolved =
                            item.status.toLowerCase() ===
                            "resolved";

                          const difference =
                            Number(
                              item.difference,
                            );

                          return (
                            <tr
                              key={item.id}
                              onClick={() =>
                                setSelectedException(
                                  item,
                                )
                              }
                              className="
                                group
                                cursor-pointer
                                transition
                                hover:bg-[#f4fbfd]
                              "
                            >

                              {/* CASE */}
                              <td className="px-5 py-5">

                                <div className="flex items-center gap-3">

                                  <div
                                    className={`
                                      flex
                                      h-9
                                      w-9
                                      shrink-0
                                      items-center
                                      justify-center
                                      rounded-xl
                                      ${
                                        isResolved
                                          ? "bg-emerald-50 text-emerald-600"
                                          : "bg-amber-50 text-amber-600"
                                      }
                                    `}
                                  >
                                    {isResolved ? (
                                      <CheckCircle2 className="h-4 w-4" />
                                    ) : (
                                      <AlertTriangle className="h-4 w-4" />
                                    )}
                                  </div>

                                  <div>
                                    <p className="text-sm font-semibold text-[#172b4d]">
                                      {item.case_id}
                                    </p>

                                    <p className="mt-0.5 text-[10px] text-[#94a7b8]">
                                      ID #{item.id}
                                    </p>
                                  </div>

                                </div>

                              </td>


                              {/* TRANSACTION */}
                              <td className="px-5 py-5">

                                <span className="rounded-md bg-[#f1f6fa] px-2 py-1 text-xs font-medium text-[#40566d]">
                                  {item.transaction_id ??
                                    "—"}
                                </span>

                              </td>


                              {/* TYPE */}
                              <td className="px-5 py-5">

                                <p className="text-sm font-medium text-[#34495e]">
                                  {formatCaseType(
                                    item.case_type,
                                  )}
                                </p>

                                <p className="mt-1 max-w-[270px] text-[11px] leading-4 text-[#8a9cad]">
                                  {item.description}
                                </p>

                              </td>


                              {/* EXPECTED */}
                              <td className="px-5 py-5 text-sm font-medium text-[#243b53]">
                                ₹
                                {Number(
                                  item.expected_amount,
                                ).toLocaleString(
                                  "en-IN",
                                )}
                              </td>


                              {/* SETTLED */}
                              <td className="px-5 py-5 text-sm text-[#536b80]">
                                ₹
                                {Number(
                                  item.actual_amount,
                                ).toLocaleString(
                                  "en-IN",
                                )}
                              </td>


                              {/* DIFFERENCE */}
                              <td className="px-5 py-5">

                                <span
                                  className={`
                                    text-sm
                                    font-semibold
                                    ${
                                      difference === 0
                                        ? "text-emerald-600"
                                        : "text-[#172b4d]"
                                    }
                                  `}
                                >
                                  ₹
                                  {difference.toLocaleString(
                                    "en-IN",
                                  )}
                                </span>

                              </td>


                              {/* PRIORITY */}
                              <td className="px-5 py-5">

                                <PriorityBadge
                                  priority={
                                    item.priority
                                  }
                                />

                              </td>


                              {/* STATUS */}
                              <td className="px-5 py-5">

                                <Badge
                                  className={
                                    isResolved
                                      ? "border-0 bg-emerald-50 text-emerald-700"
                                      : "border-0 bg-amber-50 text-amber-700"
                                  }
                                >
                                  {formatStatus(
                                    item.status,
                                  )}
                                </Badge>

                              </td>


                              {/* ARROW */}
                              <td className="px-3 py-5">

                                <ChevronRight
                                  className="
                                    h-4
                                    w-4
                                    text-[#a7bac9]
                                    transition
                                    group-hover:translate-x-0.5
                                    group-hover:text-[#00a8dc]
                                  "
                                />

                              </td>

                            </tr>
                          );
                        },
                      )}

                    </tbody>

                  </table>

                </div>

              )}

            </CardContent>
          </Card>

        </div>
      </div>


      {/* DETAIL DRAWER */}
      {selectedException && (
        <ExceptionDrawer
          exception={selectedException}
          onClose={() =>
            setSelectedException(null)
          }
        />
      )}

    </DashboardShell>
  );
}


/* =========================================================
   SUMMARY CARD
========================================================= */

function SummaryCard({
  title,
  value,
  icon,
  valueClass = "text-[#172b4d]",
  iconClass = "bg-[#eef9fd] text-[#00a8dc]",
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  valueClass?: string;
  iconClass?: string;
}) {
  return (
    <Card className="border-[#d7e5ef] bg-white shadow-[0_4px_18px_rgba(20,70,100,0.04)]">

      <CardContent className="flex items-start justify-between p-5">

        <div>
          <p className="text-xs font-medium text-[#8298ad]">
            {title}
          </p>

          <p
            className={`mt-2 text-3xl font-semibold tracking-tight ${valueClass}`}
          >
            {value}
          </p>
        </div>

        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl ${iconClass}`}
        >
          {icon}
        </div>

      </CardContent>

    </Card>
  );
}


/* =========================================================
   FILTER BUTTON
========================================================= */

function FilterButton({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        rounded-lg
        px-3
        py-2
        text-xs
        font-medium
        transition
        ${
          active
            ? "bg-[#00baf2] text-white shadow-sm"
            : "bg-[#f4f8fb] text-[#637b91] hover:bg-[#eaf5fa] hover:text-[#0077b6]"
        }
      `}
    >
      {children}
    </button>
  );
}


/* =========================================================
   PRIORITY BADGE
========================================================= */

function PriorityBadge({
  priority,
}: {
  priority: string;
}) {
  const value =
    priority.toLowerCase();

  if (value === "high") {
    return (
      <Badge className="border-0 bg-red-50 text-red-700">
        High
      </Badge>
    );
  }

  if (value === "low") {
    return (
      <Badge className="border-0 bg-slate-100 text-slate-600">
        Low
      </Badge>
    );
  }

  return (
    <Badge className="border-0 bg-amber-50 text-amber-700">
      Medium
    </Badge>
  );
}


/* =========================================================
   DETAIL DRAWER
========================================================= */

function ExceptionDrawer({
  exception,
  onClose,
}: {
  exception: DashboardException;
  onClose: () => void;
}) {
  const isResolved =
    exception.status.toLowerCase() ===
    "resolved";

  const difference =
    Number(exception.difference);

  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        justify-end
        bg-[#0b1d2d]/35
        backdrop-blur-[2px]
      "
      onClick={onClose}
    >

      <div
        className="
          h-full
          w-full
          max-w-[520px]
          overflow-y-auto
          bg-white
          shadow-2xl
        "
        onClick={(event) =>
          event.stopPropagation()
        }
      >

        {/* DRAWER HEADER */}
        <div className="sticky top-0 z-10 border-b border-[#e5edf3] bg-white/95 px-6 py-5 backdrop-blur">

          <div className="flex items-start justify-between">

            <div>

              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#0077b6]">
                Reconciliation case
              </p>

              <h2 className="mt-1 text-xl font-semibold text-[#172b4d]">
                {exception.case_id}
              </h2>

              <p className="mt-1 text-xs text-[#8196aa]">
                Case ID #{exception.id}
              </p>

            </div>

            <button
              type="button"
              onClick={onClose}
              className="
                flex
                h-9
                w-9
                items-center
                justify-center
                rounded-lg
                bg-[#f4f8fb]
                text-[#637b91]
                transition
                hover:bg-[#eaf5fa]
                hover:text-[#0077b6]
              "
            >
              <X className="h-4 w-4" />
            </button>

          </div>

        </div>


        {/* DRAWER CONTENT */}
        <div className="space-y-6 p-6">

          {/* STATUS */}
          <div className="rounded-2xl border border-[#dceaf2] bg-[#f6fbfe] p-5">

            <div className="flex items-center justify-between">

              <div className="flex items-center gap-3">

                <div
                  className={`
                    flex
                    h-10
                    w-10
                    items-center
                    justify-center
                    rounded-xl
                    ${
                      isResolved
                        ? "bg-emerald-50 text-emerald-600"
                        : "bg-amber-50 text-amber-600"
                    }
                  `}
                >
                  {isResolved ? (
                    <CheckCircle2 className="h-5 w-5" />
                  ) : (
                    <AlertTriangle className="h-5 w-5" />
                  )}
                </div>

                <div>

                  <p className="text-sm font-semibold text-[#172b4d]">
                    {isResolved
                      ? "Exception resolved"
                      : "Exception needs review"}
                  </p>

                  <p className="mt-0.5 text-xs text-[#8196aa]">
                    {formatStatus(
                      exception.status,
                    )}
                  </p>

                </div>

              </div>

              <PriorityBadge
                priority={
                  exception.priority
                }
              />

            </div>

          </div>


          {/* TRANSACTION */}
          <DetailSection title="Transaction">

            <DetailRow
              label="Transaction ID"
              value={
                exception.transaction_id ??
                "—"
              }
            />

            <DetailRow
              label="Exception type"
              value={formatCaseType(
                exception.case_type,
              )}
            />

          </DetailSection>


          {/* MONEY */}
          <DetailSection title="Settlement details">

            <div className="grid grid-cols-2 gap-3">

              <MoneyCard
                label="Expected"
                value={Number(
                  exception.expected_amount,
                )}
              />

              <MoneyCard
                label="Settled"
                value={Number(
                  exception.actual_amount,
                )}
              />

            </div>


            <div className="mt-3 rounded-xl border border-[#e4edf3] bg-white p-4">

              <div className="flex items-center justify-between">

                <span className="text-xs text-[#8298ad]">
                  Remaining difference
                </span>

                <span
                  className={`
                    text-lg
                    font-semibold
                    ${
                      difference === 0
                        ? "text-emerald-600"
                        : "text-[#172b4d]"
                    }
                  `}
                >
                  ₹
                  {difference.toLocaleString(
                    "en-IN",
                  )}
                </span>

              </div>

            </div>

          </DetailSection>


          {/* DESCRIPTION */}
          <DetailSection title="Why this case exists">

            <div className="rounded-xl border border-[#e4edf3] bg-[#f9fcfe] p-4">

              <p className="text-sm leading-6 text-[#536b80]">
                {exception.description ||
                  "No additional description is available."}
              </p>

            </div>

          </DetailSection>


          {/* WORKFLOW */}
          <DetailSection title="AI teammate state">

            <div className="space-y-3">

              <WorkflowStep
                title="Exception detected"
                description="The reconciliation engine identified a settlement discrepancy."
                done
              />

              <WorkflowStep
                title="Investigation"
                description="The transaction and settlement records were inspected."
                done
              />

              <WorkflowStep
                title={
                  isResolved
                    ? "Resolution verified"
                    : "Human review required"
                }
                description={
                  isResolved
                    ? "The settlement now matches the expected amount."
                    : "A consequential resolution requires an authorized human decision."
                }
                done={isResolved}
                active={!isResolved}
              />

            </div>

          </DetailSection>

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   DETAIL HELPERS
========================================================= */

function DetailSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>

      <h3 className="mb-3 text-xs font-bold uppercase tracking-[0.12em] text-[#71889d]">
        {title}
      </h3>

      {children}

    </section>
  );
}


function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between border-b border-[#edf2f6] py-3 last:border-0">

      <span className="text-xs text-[#8298ad]">
        {label}
      </span>

      <span className="text-sm font-medium text-[#243b53]">
        {value}
      </span>

    </div>
  );
}


function MoneyCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-[#e4edf3] bg-[#fbfdff] p-4">

      <p className="text-[11px] text-[#8298ad]">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold text-[#172b4d]">
        ₹
        {value.toLocaleString(
          "en-IN",
        )}
      </p>

    </div>
  );
}


function WorkflowStep({
  title,
  description,
  done,
  active = false,
}: {
  title: string;
  description: string;
  done: boolean;
  active?: boolean;
}) {
  return (
    <div className="flex gap-3">

      <div className="relative flex flex-col items-center">

        <div
          className={`
            flex
            h-7
            w-7
            shrink-0
            items-center
            justify-center
            rounded-full
            ${
              done
                ? "bg-emerald-50 text-emerald-600"
                : active
                  ? "bg-[#eaf9fd] text-[#00a8dc]"
                  : "bg-slate-100 text-slate-400"
            }
          `}
        >
          {done ? (
            <CheckCircle2 className="h-3.5 w-3.5" />
          ) : (
            <Clock3 className="h-3.5 w-3.5" />
          )}
        </div>

      </div>

      <div className="pb-4">

        <p className="text-sm font-medium text-[#243b53]">
          {title}
        </p>

        <p className="mt-1 text-xs leading-5 text-[#8298ad]">
          {description}
        </p>

      </div>

    </div>
  );
}


/* =========================================================
   FORMATTERS
========================================================= */

function formatCaseType(type: string) {
  return type
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    );
}


function formatStatus(status: string) {
  return status
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    );
}