export type ResearchProject = {
  id: string;
  title: string;
  topic: string;
  objective: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type ResearchTask = {
  id: string;
  project_id: string;
  desk: string;
  title: string;
  description: string;
  status: string;
};

export type ResearchArtifact = {
  id: string;
  project_id: string;
  task_id: string;
  title: string;
  summary: string;
  findings: string[];
  risks: string[];
  citation_ids: string[];
};

export type Evidence = {
  id: string;
  project_id: string;
  source_type: string;
  title: string;
  url: string | null;
  published_at: string | null;
  summary: string;
  metadata: Record<string, unknown>;
};

export type EvidenceCitation = {
  id: string;
  evidence_id: string;
  label: string;
  excerpt: string;
  location: string;
};

export type Thesis = {
  id: string;
  project_id: string;
  claim: string;
  evidence_for: string[];
  evidence_against: string[];
  catalysts: string[];
  invalidation_conditions: string[];
  horizon: string;
  confidence: string;
  candidate_asset: {
    symbol: string;
    name: string;
    rationale: string;
  };
  citation_ids: string[];
  artifact_ids: string[];
};

export type DecisionProposal = {
  id: string;
  project_id: string;
  thesis_id: string;
  asset: string;
  action: string;
  status: string;
  conviction: string;
  suggested_position_size: string;
  horizon: string;
  entry_conditions: string[];
  invalidation_conditions: string[];
  primary_risks: string[];
  rationale: string;
  citation_ids: string[];
};

export type InvestmentDecision = {
  id: string;
  project_id: string;
  proposal_id: string;
  thesis_id: string;
  decision: string;
  user_note: string | null;
  created_at: string;
};

export type ActivityEvent = {
  id: string;
  project_id: string;
  task_id: string | null;
  event_type: string;
  message: string;
  created_at: string;
};

export type ResearchWorkflowResponse = {
  project: ResearchProject;
  tasks: ResearchTask[];
  evidence: Evidence[];
  citations: EvidenceCitation[];
  artifacts: ResearchArtifact[];
  thesis: Thesis;
  activity_events: ActivityEvent[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}
