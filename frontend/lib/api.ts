export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export interface DashboardOverview {
  merchant_id: string;
  merchant_name: string;
  transactions: number;
  exceptions: number;
  open_exceptions: number;
  resolved_exceptions: number;
  pending_approvals: number;
  system_status: string;
}

export interface DashboardException {
  id: number;
  case_id: string;
  transaction_id: string | null;
  case_type: string;
  expected_amount: string;
  actual_amount: string;
  difference: string;
  status: string;
  priority: string;
  description: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface DashboardActivity {
  id: number;
  case_id: number | null;
  action_type: string;
  status: string;
  description: string | null;
  tool_name: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string | null;
}

export async function getDashboardOverview(): Promise<DashboardOverview> {
  const response = await fetch(
    `${API_BASE_URL}/api/dashboard/overview`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load dashboard overview.");
  }

  return response.json();
}

export async function getDashboardExceptions(): Promise<{
  count: number;
  exceptions: DashboardException[];
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/dashboard/exceptions`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load exceptions.");
  }

  return response.json();
}

export async function getDashboardActivity(): Promise<{
  count: number;
  actions: DashboardActivity[];
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/dashboard/activity`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load activity.");
  }

  return response.json();
}

export interface PendingApproval {
  id: number;
  case_id: number;
  requested_action: string;
  status: string;
  reason: string | null;
  created_at: string | null;
}

export async function getPendingApprovals(): Promise<{
  count: number;
  approvals: PendingApproval[];
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/approvals/pending`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load pending approvals.");
  }

  const data = await response.json();

  return {
    ...data,
    approvals: (data.approvals ?? []).map((approval: any) => ({
      ...approval,
      id: approval.id ?? approval.approval_id,
    })),
  };
}

export async function resolveApproval(
  approvalId: number,
  decision: "approved" | "rejected",
  approvedBy: string = "demo_admin"
): Promise<PendingApproval> {
  const response = await fetch(
    `${API_BASE_URL}/api/approvals/${approvalId}/resolve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        decision,
        approved_by: approvedBy,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to resolve approval.");
  }

  return response.json();
}

export async function approveAndExecute(
  approvalId: number
) {
  const response = await fetch(
    `${API_BASE_URL}/api/approvals/${approvalId}/approve-and-execute`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    }
  );

  let data: any = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  /*
   * The backend intentionally returns HTTP 200 even when
   * a financial action is safely blocked or fails verification.
   *
   * Therefore we inspect `data.success`, not only response.ok.
   */

  if (!response.ok) {
    throw new Error(
      data?.error ??
        data?.message ??
        `Approval request failed with HTTP ${response.status}.`
    );
  }

  return data;
}

export type ReconciliationRunResponse = {
  success: boolean;
  status: string;
  merchant_id: string;
  current_step: string;
  error: string | null;

  reconciliation: {
    merchant_id: string;
    total_transactions: number;
    discrepancy_count: number;
    discrepancies: Array<{
      transaction_id: string;
      transaction_amount: number;
      settlement_id: string | null;
      settled_amount: number;
      difference: number;
      transaction_status: string;
      settlement_status: string | null;
    }>;
  };

  investigations: Array<{
    transaction_id: string;
    classification: string;
    reason: string;
    transaction_amount: number;
    refund_amount: number;
    refund_count: number;
    difference: number;
    settlement_id: string | null;
    settled_amount: number;
  }>;

  planned_actions: Array<{
    transaction_id: string;
    action_type: string;
    reason: string;
    approval_required: boolean;
  }>;

  execution_results: Array<{
    success: boolean;
    status: string;
    action_type: string;
    result?: Record<string, unknown>;
  }>;

  case_results: Array<{
    success: boolean;
    case_id: string;
    case_db_id: number;
    status: string;
    transaction_id: string;
    case_type: string;
    priority: string;
  }>;

  approval_requests: Array<{
    success: boolean;
    approval_id: number;
    case_id: number;
    requested_action: string;
    status: string;
    reason: string;
  }>;
};


export async function runReconciliation(
  merchantId: string,
): Promise<ReconciliationRunResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/reconciliation/run/${merchantId}`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail?.error ??
      data?.error ??
      "Failed to run reconciliation.",
    );
  }

  return data;
}

export interface ActivityItem {
  id: number;
  action_type: string;
  status: string;
  description: string | null;
  tool_name: string | null;
  case_id: number | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface ActivityResponse {
  success: boolean;
  count: number;
  activities: ActivityItem[];
}

export async function getActivity(
  limit: number = 50
): Promise<ActivityResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/activity?limit=${limit}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load agent activity.");
  }

  return response.json();
}