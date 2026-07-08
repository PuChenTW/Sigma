"use client";

import { Check, ClipboardList, FileText, LibraryBig, Play, Plus, Send, ShieldCheck, X } from "lucide-react";
import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import {
  ActivityEvent,
  CreateEvidenceRequest,
  DecisionProposal,
  EvidenceDesk,
  EvidenceSourceType,
  Evidence,
  EvidenceCitation,
  InvestmentDecision,
  ResearchArtifact,
  ResearchProject,
  ResearchTask,
  ResearchWorkflowResponse,
  Thesis,
  apiRequest,
} from "../lib/api";

type Step = "idle" | "creating" | "addingEvidence" | "running" | "evaluating" | "deciding";

type EvidenceFormState = {
  source_type: EvidenceSourceType;
  desk: EvidenceDesk;
  title: string;
  url: string;
  summary: string;
  label: string;
  excerpt: string;
  location: string;
};

const initialEvidenceForm: EvidenceFormState = {
  source_type: "note",
  desk: "industry",
  title: "",
  url: "",
  summary: "",
  label: "",
  excerpt: "",
  location: "manual note",
};

export default function StudioWorkflowPage() {
  const [topic, setTopic] = useState("Small modular reactors and investable advanced nuclear exposure");
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [project, setProject] = useState<ResearchProject | null>(null);
  const [tasks, setTasks] = useState<ResearchTask[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [citations, setCitations] = useState<EvidenceCitation[]>([]);
  const [artifacts, setArtifacts] = useState<ResearchArtifact[]>([]);
  const [thesis, setThesis] = useState<Thesis | null>(null);
  const [proposal, setProposal] = useState<DecisionProposal | null>(null);
  const [decision, setDecision] = useState<InvestmentDecision | null>(null);
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [note, setNote] = useState("");
  const [evidenceForm, setEvidenceForm] = useState<EvidenceFormState>(initialEvidenceForm);
  const [step, setStep] = useState<Step>("idle");
  const [error, setError] = useState<string | null>(null);

  const selectedProjectId = project?.id;

  useEffect(() => {
    void loadProjects();
  }, []);

  useEffect(() => {
    if (!selectedProjectId) {
      return;
    }
    void loadProjectState(selectedProjectId);
  }, [selectedProjectId]);

  const citationById = useMemo(() => new Map(citations.map((citation) => [citation.id, citation])), [citations]);
  const evidenceById = useMemo(() => new Map(evidence.map((item) => [item.id, item])), [evidence]);

  async function loadProjects() {
    try {
      const loaded = await apiRequest<ResearchProject[]>("/research-projects");
      setProjects(loaded);
      if (!project && loaded.length > 0) {
        setProject(loaded.at(-1) ?? null);
      }
    } catch (loadError) {
      setError(errorMessage(loadError));
    }
  }

  async function loadProjectState(projectId: string) {
    setProposal(null);
    setDecision(null);
    setNote("");

    try {
      const [loadedProject, loadedTasks, loadedEvents, loadedEvidence, loadedCitations, loadedArtifacts, loadedProposals, loadedDecisions] = await Promise.all([
        apiRequest<ResearchProject>(`/research-projects/${projectId}`),
        apiRequest<ResearchTask[]>(`/research-projects/${projectId}/tasks`),
        apiRequest<ActivityEvent[]>(`/research-projects/${projectId}/activity-events`),
        apiRequest<Evidence[]>(`/research-projects/${projectId}/evidence`),
        apiRequest<EvidenceCitation[]>(`/research-projects/${projectId}/citations`),
        apiRequest<ResearchArtifact[]>(`/research-projects/${projectId}/artifacts`),
        apiRequest<DecisionProposal[]>(`/research-projects/${projectId}/decision-proposals`),
        apiRequest<InvestmentDecision[]>(`/research-projects/${projectId}/investment-decisions`),
      ]);

      setProject(loadedProject);
      setTasks(loadedTasks);
      setEvents(loadedEvents);
      setEvidence(loadedEvidence);
      setCitations(loadedCitations);
      setArtifacts(loadedArtifacts);
      setProposal(loadedProposals.at(-1) ?? null);
      setDecision(loadedDecisions.at(-1) ?? null);
      setNote(loadedDecisions.at(-1)?.user_note ?? "");

      try {
        setThesis(await apiRequest<Thesis>(`/research-projects/${projectId}/thesis`));
      } catch {
        setThesis(null);
      }
    } catch (loadError) {
      setError(errorMessage(loadError));
    }
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStep("creating");
    setError(null);
    setProposal(null);
    setDecision(null);

    try {
      const created = await apiRequest<ResearchProject>("/research-projects", {
        method: "POST",
        body: JSON.stringify({ topic }),
      });
      setProject(created);
      await loadProjects();
      await loadProjectState(created.id);
    } catch (createError) {
      setError(errorMessage(createError));
    } finally {
      setStep("idle");
    }
  }

  async function runResearch() {
    if (!project) {
      return;
    }

    setStep("running");
    setError(null);
    setProposal(null);
    setDecision(null);

    try {
      const result = await apiRequest<ResearchWorkflowResponse>(`/research-projects/${project.id}/run-research`, {
        method: "POST",
      });
      setProject(result.project);
      setTasks(result.tasks);
      setEvidence(result.evidence);
      setCitations(result.citations);
      setArtifacts(result.artifacts);
      setThesis(result.thesis);
      setEvents(result.activity_events);
      await loadProjectState(result.project.id);
    } catch (runError) {
      setError(errorMessage(runError));
    } finally {
      setStep("idle");
    }
  }

  async function addEvidence(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!project) {
      return;
    }

    setStep("addingEvidence");
    setError(null);

    const request: CreateEvidenceRequest = {
      source_type: evidenceForm.source_type,
      desk: evidenceForm.desk,
      title: evidenceForm.title,
      url: evidenceForm.url.trim() || null,
      summary: evidenceForm.summary,
      citations: [
        {
          label: evidenceForm.label.trim() || null,
          excerpt: evidenceForm.excerpt,
          location: evidenceForm.location,
        },
      ],
    };

    try {
      await apiRequest(`/research-projects/${project.id}/evidence`, {
        method: "POST",
        body: JSON.stringify(request),
      });
      setEvidenceForm((current) => ({
        ...current,
        title: "",
        url: "",
        summary: "",
        label: "",
        excerpt: "",
      }));
      await loadProjectState(project.id);
    } catch (evidenceError) {
      setError(errorMessage(evidenceError));
    } finally {
      setStep("idle");
    }
  }

  async function evaluateCommittee() {
    if (!project) {
      return;
    }

    setStep("evaluating");
    setError(null);
    setDecision(null);

    try {
      const createdProposal = await apiRequest<DecisionProposal>(`/research-projects/${project.id}/committee/evaluate`, {
        method: "POST",
      });
      setProposal(createdProposal);
      await loadProjectState(project.id);
    } catch (evaluateError) {
      setError(errorMessage(evaluateError));
    } finally {
      setStep("idle");
    }
  }

  async function decide(decisionType: "approve" | "reject") {
    if (!proposal) {
      return;
    }

    setStep("deciding");
    setError(null);

    try {
      const recorded = await apiRequest<InvestmentDecision>(`/decision-proposals/${proposal.id}/${decisionType}`, {
        method: "POST",
        body: JSON.stringify({ user_note: note || null }),
      });
      setDecision(recorded);
      setProposal(await apiRequest<DecisionProposal>(`/decision-proposals/${proposal.id}`));
      if (project) {
        await loadProjectState(project.id);
      }
    } catch (decisionError) {
      setError(errorMessage(decisionError));
    } finally {
      setStep("idle");
    }
  }

  function selectProject(item: ResearchProject) {
    setProject(item);
    setProposal(null);
    setDecision(null);
    setNote("");
  }

  return (
    <main className="shell">
      <section className="workspace">
        <aside className="left-pane">
          <header className="app-title">
            <p>AI Investment Research Studio</p>
            <h1>Research to decision</h1>
          </header>

          <form className="topic-form" onSubmit={createProject}>
            <label htmlFor="topic">Topic</label>
            <textarea id="topic" value={topic} onChange={(event) => setTopic(event.target.value)} rows={4} />
            <button type="submit" disabled={step !== "idle"}>
              <Send size={18} />
              Create project
            </button>
          </form>

          <div className="project-list" aria-label="Projects">
            {projects.map((item) => (
              <button key={item.id} className={item.id === project?.id ? "project-row selected" : "project-row"} onClick={() => selectProject(item)} type="button">
                <span>{item.title}</span>
                <StatusBadge value={item.status} />
              </button>
            ))}
          </div>
        </aside>

        <section className="main-pane">
          {error ? <div className="error-banner">{error}</div> : null}

          <div className="toolbar">
            <div>
              <p className="eyebrow">Current project</p>
              <h2>{project?.title ?? "No project selected"}</h2>
            </div>
            <div className="actions">
              <button type="button" onClick={runResearch} disabled={!project || step !== "idle"}>
                <Play size={18} />
                Run research
              </button>
              <button type="button" onClick={evaluateCommittee} disabled={!thesis || step !== "idle"}>
                <ShieldCheck size={18} />
                Committee
              </button>
            </div>
          </div>

          <div className="content-grid">
            <section className="panel tasks-panel">
              <PanelTitle icon={<ClipboardList size={18} />} title="Tasks" />
              <div className="task-list">
                {tasks.map((task) => (
                  <article key={task.id} className="task-row">
                    <div>
                      <h3>{task.title}</h3>
                      <p>{task.description}</p>
                    </div>
                    <StatusBadge value={task.status} />
                  </article>
                ))}
              </div>
            </section>

            <section className="panel evidence-panel">
              <PanelTitle icon={<LibraryBig size={18} />} title="Evidence workbench" />
              <form className="evidence-form" onSubmit={addEvidence}>
                <div className="field-row">
                  <label>
                    <span>Source</span>
                    <select
                      value={evidenceForm.source_type}
                      onChange={(event) => setEvidenceForm((current) => ({ ...current, source_type: event.target.value as EvidenceSourceType }))}
                    >
                      <option value="note">Note</option>
                      <option value="article">Article</option>
                    </select>
                  </label>
                  <label>
                    <span>Desk</span>
                    <select value={evidenceForm.desk} onChange={(event) => setEvidenceForm((current) => ({ ...current, desk: event.target.value as EvidenceDesk }))}>
                      <option value="industry">Industry</option>
                      <option value="macro_policy">Macro / policy</option>
                      <option value="fundamental">Fundamental</option>
                    </select>
                  </label>
                </div>
                <label>
                  <span>Title</span>
                  <input value={evidenceForm.title} onChange={(event) => setEvidenceForm((current) => ({ ...current, title: event.target.value }))} />
                </label>
                <label>
                  <span>URL</span>
                  <input value={evidenceForm.url} onChange={(event) => setEvidenceForm((current) => ({ ...current, url: event.target.value }))} />
                </label>
                <label>
                  <span>Summary</span>
                  <textarea value={evidenceForm.summary} onChange={(event) => setEvidenceForm((current) => ({ ...current, summary: event.target.value }))} rows={3} />
                </label>
                <div className="field-row">
                  <label>
                    <span>Citation label</span>
                    <input value={evidenceForm.label} onChange={(event) => setEvidenceForm((current) => ({ ...current, label: event.target.value }))} />
                  </label>
                  <label>
                    <span>Location</span>
                    <input value={evidenceForm.location} onChange={(event) => setEvidenceForm((current) => ({ ...current, location: event.target.value }))} />
                  </label>
                </div>
                <label>
                  <span>Excerpt</span>
                  <textarea value={evidenceForm.excerpt} onChange={(event) => setEvidenceForm((current) => ({ ...current, excerpt: event.target.value }))} rows={3} />
                </label>
                <button type="submit" disabled={!project || step !== "idle"}>
                  <Plus size={18} />
                  Add evidence
                </button>
              </form>

              <div className="evidence-library">
                {evidence.length > 0 ? (
                  evidence.map((item) => {
                    const itemCitations = citations.filter((citation) => citation.evidence_id === item.id);
                    return (
                      <article key={item.id} className="evidence-item">
                        <div className="evidence-heading">
                          <div>
                            <h3>{item.title}</h3>
                            <span>{String(item.metadata.desk ?? item.source_type).replaceAll("_", " ")}</span>
                          </div>
                          <StatusBadge value={String(item.metadata.origin ?? item.source_type)} />
                        </div>
                        <p>{item.summary}</p>
                        {itemCitations[0] ? (
                          <div className="citation-preview">
                            <strong>{itemCitations[0].label}</strong>
                            <span>{itemCitations[0].excerpt}</span>
                          </div>
                        ) : null}
                      </article>
                    );
                  })
                ) : (
                  <EmptyState label="Add evidence before running research, or run research to attach fixtures." />
                )}
              </div>
            </section>

            <section className="panel thesis-panel">
              <PanelTitle icon={<FileText size={18} />} title="Thesis" />
              {thesis ? (
                <div className="thesis-block">
                  <div className="asset-strip">
                    <strong>{thesis.candidate_asset.symbol}</strong>
                    <span>{thesis.candidate_asset.name}</span>
                    <StatusBadge value={thesis.confidence} />
                  </div>
                  <p className="claim">{thesis.claim}</p>
                  <List title="Evidence for" items={thesis.evidence_for} />
                  <List title="Invalidation" items={thesis.invalidation_conditions} />
                  <div className="trace-strip">
                    <span>{artifacts.length} artifacts</span>
                    <span>{citations.length} citations</span>
                  </div>
                </div>
              ) : (
                <EmptyState label="Run research to create the thesis." />
              )}
            </section>

            <section className="panel proposal-panel">
              <PanelTitle icon={<ShieldCheck size={18} />} title="Proposal review" />
              {proposal ? (
                <div className="proposal-block">
                  <div className="proposal-header">
                    <div>
                      <p className="eyebrow">{proposal.action}</p>
                      <h3>{proposal.asset}</h3>
                    </div>
                    <StatusBadge value={proposal.status} />
                  </div>
                  <dl className="proposal-facts">
                    <div>
                      <dt>Size</dt>
                      <dd>{proposal.suggested_position_size}</dd>
                    </div>
                    <div>
                      <dt>Horizon</dt>
                      <dd>{proposal.horizon}</dd>
                    </div>
                    <div>
                      <dt>Conviction</dt>
                      <dd>{proposal.conviction}</dd>
                    </div>
                  </dl>
                  <p>{proposal.rationale}</p>
                  <p className="trace-line">Thesis {proposal.thesis_id} · {proposal.citation_ids.length} citations</p>
                  <List title="Risks" items={proposal.primary_risks} />
                  <textarea aria-label="Decision note" value={note} onChange={(event) => setNote(event.target.value)} rows={3} placeholder="Decision note" />
                  <div className="decision-actions">
                    <button type="button" onClick={() => void decide("approve")} disabled={proposal.status !== "pending_review" || step !== "idle"}>
                      <Check size={18} />
                      Approve
                    </button>
                    <button type="button" className="secondary-danger" onClick={() => void decide("reject")} disabled={proposal.status !== "pending_review" || step !== "idle"}>
                      <X size={18} />
                      Reject
                    </button>
                  </div>
                  {decision ? <p className="decision-result">Decision recorded: {decision.decision}</p> : null}
                </div>
              ) : (
                <EmptyState label="Send the active thesis to committee." />
              )}
            </section>

            <section className="panel artifacts-panel">
              <PanelTitle icon={<FileText size={18} />} title="Artifacts and citations" />
              {artifacts.length > 0 ? (
                <div className="artifact-list">
                  {artifacts.map((artifact) => (
                    <article key={artifact.id} className="artifact-card">
                      <h3>{artifact.title}</h3>
                      <p>{artifact.summary}</p>
                      <List title="Findings" items={artifact.findings} />
                      <CitationList citationIds={artifact.citation_ids} citationById={citationById} evidenceById={evidenceById} />
                    </article>
                  ))}
                </div>
              ) : (
                <EmptyState label="Artifacts and citations appear after research runs." />
              )}
            </section>

            <section className="panel activity-panel">
              <PanelTitle icon={<ClipboardList size={18} />} title="Activity" />
              <ol className="activity-list">
                {events.slice(-8).map((event) => (
                  <li key={event.id}>
                    <span>{event.event_type.replaceAll("_", " ")}</span>
                    <p>{event.message}</p>
                  </li>
                ))}
              </ol>
            </section>
          </div>
        </section>
      </section>
    </main>
  );
}

function PanelTitle({ icon, title }: { icon: ReactNode; title: string }) {
  return (
    <div className="panel-title">
      {icon}
      <h2>{title}</h2>
    </div>
  );
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="list-block">
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return <p className="empty-state">{label}</p>;
}

function CitationList({
  citationIds,
  citationById,
  evidenceById,
}: {
  citationIds: string[];
  citationById: Map<string, EvidenceCitation>;
  evidenceById: Map<string, Evidence>;
}) {
  return (
    <div className="citation-list">
      <h4>Citations</h4>
      {citationIds.map((citationId) => {
        const citation = citationById.get(citationId);
        const source = citation ? evidenceById.get(citation.evidence_id) : null;
        return (
          <div key={citationId} className="citation-row">
            <strong>{citation?.label ?? citationId}</strong>
            <span>{source?.title ?? "Source pending"}</span>
            {source?.summary ? <p className="citation-summary">{source.summary}</p> : null}
            <p>{citation?.excerpt ?? "Citation not resolved."}</p>
          </div>
        );
      })}
    </div>
  );
}

function StatusBadge({ value }: { value: string }) {
  return <span className={`status status-${value.replaceAll("_", "-")}`}>{value.replaceAll("_", " ")}</span>;
}

function errorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return "Unexpected error";
}
