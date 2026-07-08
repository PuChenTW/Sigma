"use client";

import { ChartNoAxesColumn, Check, LayoutDashboard, NotebookTabs, Play, Plus, Send, ShieldCheck, X } from "lucide-react";
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
type WorkspaceView = "dashboard" | "decision" | "positions" | "research" | "assign";

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

const teamMembers = [
  { tag: "TR", name: "Trader", role: "Trading Committee", status: "deciding", focus: "Reviewing thesis-backed proposals and risk controls." },
  { tag: "IN", name: "Industry", role: "Industry desk", status: "research", focus: "Supply chains, demand curves, and bottlenecks." },
  { tag: "MA", name: "Macro", role: "Macro policy desk", status: "done", focus: "Policy setup, rates, energy security, and fiscal support." },
  { tag: "FN", name: "Fundamental", role: "Fundamental desk", status: "research", focus: "Business quality, capital intensity, and financing runway." },
  { tag: "MI", name: "Market Intel", role: "Market intelligence", status: "idle", focus: "Positioning, sentiment, and catalyst timing." },
];

const previewPositions = [
  {
    symbol: "OKLO",
    name: "Oklo Inc.",
    direction: "Watchlist",
    pnl: "Pending",
    status: "manual record pending",
    narrative: "Approved decisions can become manual or paper positions once the outcome loop is implemented.",
  },
  {
    symbol: "XLU",
    name: "US Utilities ETF",
    direction: "Long idea",
    pnl: "Preview",
    status: "mock-backed",
    narrative: "Prototype parity placeholder for power infrastructure exposure linked to AI and electrification theses.",
  },
];

const previewReports = [
  {
    facet: "Industry",
    title: "AI power scarcity reshapes advanced nuclear and utility capex",
    confidence: "medium",
    summary: "Prototype-backed library item showing how durable theses will sit beside API-backed research artifacts.",
  },
  {
    facet: "Macro",
    title: "Energy security policy keeps nuclear optionality alive",
    confidence: "medium",
    summary: "Policy support and permitting remain catalysts, but timelines and first-of-a-kind execution risk cap conviction.",
  },
];

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
  const [view, setView] = useState<WorkspaceView>("dashboard");
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
        setView("research");
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
      setView("research");
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
      setView("decision");
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
    setView("research");
    setProposal(null);
    setDecision(null);
    setNote("");
  }

  const pendingProposalCount = proposal?.status === "pending_review" ? 1 : 0;
  const totalDashboardItems = projects.length + artifacts.length + (proposal ? 1 : 0);
  const topbarCopy = {
    dashboard: ["綜合儀表板", "Research projects, desk status, proposals, and outcome previews"],
    decision: ["決策台", "Thesis-backed proposals awaiting your final call"],
    positions: ["交易部位", "Approved decisions will become manual or paper positions here"],
    research: [project?.title ?? "No project selected", "Research to decision · you keep the final call"],
    assign: ["派研究任務", "Assign a topic, seed evidence, and route desk work"],
  } satisfies Record<WorkspaceView, [string, string]>;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <p className="brand-name">Studio</p>
            <p className="brand-sub">AI Investment Research</p>
          </div>
        </div>

        <nav className="side-nav" aria-label="Workspace">
          <NavButton active={view === "dashboard"} icon={<LayoutDashboard size={17} />} label="綜合儀表板" onClick={() => setView("dashboard")} />
          <NavButton
            active={view === "decision"}
            badge={pendingProposalCount > 0 ? String(pendingProposalCount) : null}
            icon={<ShieldCheck size={17} />}
            label="決策台"
            onClick={() => setView("decision")}
          />
          <NavButton active={view === "positions"} icon={<ChartNoAxesColumn size={17} />} label="交易部位" onClick={() => setView("positions")} />
          <NavButton active={view === "research"} icon={<NotebookTabs size={17} />} label="研究報告" onClick={() => setView("research")} />
          <NavButton active={view === "assign"} icon={<Send size={17} />} label="派研究任務" onClick={() => setView("assign")} />
        </nav>

        <form className="topic-form" onSubmit={createProject}>
          <label htmlFor="topic">Topic</label>
          <textarea id="topic" value={topic} onChange={(event) => setTopic(event.target.value)} rows={4} />
          <button type="submit" disabled={step !== "idle"}>
            <Send size={15} />
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

        <div className="team-mini">
          <span>TEAM ONLINE · {teamMembers.length}</span>
          {teamMembers.map((member) => (
            <div key={member.tag} className="team-mini-row">
              <span className={`live-dot live-dot-${member.status}`} />
              <span>{member.role}</span>
              <strong>{statusLabel(member.status)}</strong>
            </div>
          ))}
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="topbar-heading">
            <h2>{topbarCopy[view][0]}</h2>
            <p>{topbarCopy[view][1]}</p>
          </div>
          <div className="pnl-pill">
            <span>Prototype parity</span>
            <strong>{totalDashboardItems} records</strong>
          </div>
          <div className="actions">
            <button type="button" onClick={runResearch} disabled={!project || step !== "idle"}>
              <Play size={15} />
              Run research
            </button>
            <button type="button" className="ghost" onClick={evaluateCommittee} disabled={!thesis || step !== "idle"}>
              <ShieldCheck size={15} />
              Committee
            </button>
          </div>
        </header>

        <div className="pagepad">
          {error ? <div className="error-banner">{error}</div> : null}

          {view === "dashboard" ? (
            <DashboardView
              artifacts={artifacts}
              events={events}
              pendingProposalCount={pendingProposalCount}
              projects={projects}
              setView={setView}
              thesis={thesis}
            />
          ) : null}

          {view === "positions" ? <PositionsView /> : null}

          {view === "assign" ? (
            <AssignView
              createProject={createProject}
              setTopic={setTopic}
              step={step}
              topic={topic}
            />
          ) : null}

          {view === "decision" ? (
            <DecisionDeskView
              decision={decision}
              decide={decide}
              events={events}
              note={note}
              proposal={proposal}
              setNote={setNote}
              step={step}
            />
          ) : null}

          {view === "research" ? (
          <div className="content-grid">
            <div className="col">
            <section className="panel tasks-panel">
              <PanelTitle eyebrow="TASKS" title="Tasks" />
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


            <section className="panel thesis-panel">
              <PanelTitle eyebrow="RESEARCH" title="Thesis" />
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


            <section className="panel artifacts-panel">
              <PanelTitle eyebrow="TRACE" title="Artifacts and citations" />
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
              <PanelTitle eyebrow="ACTIVITY" title="Activity" />
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

            <div className="col">
            <section className="panel evidence-panel">
              <PanelTitle eyebrow="EVIDENCE" title="Evidence workbench" />
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
                  <Plus size={15} />
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

            <section className="panel proposal-panel">
              <PanelTitle eyebrow="DESK" title="Proposal review" />
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
                      <Check size={15} />
                      Approve
                    </button>
                    <button type="button" className="secondary-danger" onClick={() => void decide("reject")} disabled={proposal.status !== "pending_review" || step !== "idle"}>
                      <X size={15} />
                      Reject
                    </button>
                  </div>
                  {decision ? <p className="decision-result">Decision recorded: {decision.decision}</p> : null}
                </div>
              ) : (
                <EmptyState label="Send the active thesis to committee." />
              )}
            </section>
            </div>
          </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}

function NavButton({
  active,
  badge,
  icon,
  label,
  onClick,
}: {
  active: boolean;
  badge?: string | null;
  icon: ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button className={active ? "nav-item active" : "nav-item"} onClick={onClick} type="button">
      {icon}
      <span>{label}</span>
      {badge ? <strong>{badge}</strong> : null}
    </button>
  );
}

function DashboardView({
  artifacts,
  events,
  pendingProposalCount,
  projects,
  setView,
  thesis,
}: {
  artifacts: ResearchArtifact[];
  events: ActivityEvent[];
  pendingProposalCount: number;
  projects: ResearchProject[];
  setView: (view: WorkspaceView) => void;
  thesis: Thesis | null;
}) {
  return (
    <div className="workspace-stack">
      {pendingProposalCount > 0 ? (
        <button className="decision-callout" onClick={() => setView("decision")} type="button">
          <span className="callout-mark">TR</span>
          <span>
            <strong>{pendingProposalCount} strategy proposal is waiting for review</strong>
            <em>You keep the final investment decision.</em>
          </span>
          <b>Open desk</b>
        </button>
      ) : null}

      <div className="kpi-grid">
        <MetricCard label="Active research" value={String(projects.length)} delta="API-backed projects" />
        <MetricCard label="Pending proposals" value={String(pendingProposalCount)} delta="Committee review queue" />
        <MetricCard label="Artifacts" value={String(artifacts.length)} delta="Traceable research output" />
        <MetricCard label="Current thesis" value={thesis ? "1" : "0"} delta={thesis ? thesis.confidence : "Run research to synthesize"} />
      </div>

      <section>
        <SectionHeading eyebrow="TEAM" title="研究團隊狀態" />
        <div className="team-grid">
          {teamMembers.map((member) => (
            <article key={member.tag} className="team-card">
              <div>
                <span className={`avatar avatar-${member.status}`}>{member.tag}</span>
                <StatusBadge value={statusLabel(member.status)} />
              </div>
              <h3>{member.name}</h3>
              <p className="role">{member.role}</p>
              <p>{member.focus}</p>
            </article>
          ))}
        </div>
      </section>

      <div className="two-col">
        <section>
          <SectionHeading eyebrow="RESEARCH" title="進行中的研究" />
          <div className="library-list">
            {projects.length > 0 ? (
              projects.slice(-4).reverse().map((item) => (
                <button key={item.id} className="library-card" onClick={() => setView("research")} type="button">
                  <StatusBadge value={item.status} />
                  <h3>{item.title}</h3>
                  <p>{item.objective}</p>
                  <span>{item.updated_at.slice(0, 10)}</span>
                </button>
              ))
            ) : (
              previewReports.map((report) => <PreviewReport key={report.title} report={report} />)
            )}
          </div>
        </section>

        <section>
          <SectionHeading eyebrow="ACTIVITY" title="最新進度" />
          <ol className="activity-list panel-lite">
            {events.length > 0 ? (
              events.slice(-5).map((event) => (
                <li key={event.id}>
                  <span>{event.event_type.replaceAll("_", " ")}</span>
                  <p>{event.message}</p>
                </li>
              ))
            ) : (
              <li>
                <span>preview</span>
                <p>Create or select a project to see API-backed research activity.</p>
              </li>
            )}
          </ol>
        </section>
      </div>
    </div>
  );
}

function AssignView({
  createProject,
  setTopic,
  step,
  topic,
}: {
  createProject: (event: FormEvent<HTMLFormElement>) => void;
  setTopic: (topic: string) => void;
  step: Step;
  topic: string;
}) {
  return (
    <div className="assign-grid">
      <section className="panel">
        <PanelTitle eyebrow="ASSIGN" title="下達新研究任務" />
        <form className="assign-form" onSubmit={createProject}>
          <label htmlFor="assign-topic">
            <span>研究主題</span>
            <textarea id="assign-topic" value={topic} onChange={(event) => setTopic(event.target.value)} rows={5} />
          </label>
          <div>
            <span className="field-label">指派研究面向</span>
            <div className="facet-grid">
              <FacetCard label="Industry" text="Supply chain, demand, competition" />
              <FacetCard label="Macro" text="Policy, rates, fiscal setup" />
              <FacetCard label="Fundamental" text="Business model and valuation" />
              <FacetCard label="Market Intel" text="Positioning and catalyst timing" />
            </div>
          </div>
          <button type="submit" disabled={step !== "idle"}>
            <Send size={15} />
            Create project
          </button>
        </form>
      </section>

      <section>
        <SectionHeading eyebrow="QUEUE" title="任務佇列" />
        <div className="queue-list">
          {[
            "Route topic into desk-level research tasks",
            "Collect project evidence and citations",
            "Synthesize thesis before committee review",
          ].map((item, index) => (
            <article key={item} className="queue-item">
              <StatusBadge value={index === 0 ? "ready" : "preview"} />
              <p>{item}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function DecisionDeskView({
  decision,
  decide,
  events,
  note,
  proposal,
  setNote,
  step,
}: {
  decision: InvestmentDecision | null;
  decide: (decisionType: "approve" | "reject") => Promise<void>;
  events: ActivityEvent[];
  note: string;
  proposal: DecisionProposal | null;
  setNote: (note: string) => void;
  step: Step;
}) {
  if (!proposal) {
    return (
      <div className="workspace-stack">
        <section className="empty-desk">
          <h2>目前沒有待裁決的提案</h2>
          <p>Run research, then send the active thesis to committee.</p>
        </section>
        <DecisionHistory decision={decision} />
        <ActivityTrace events={events} />
      </div>
    );
  }

  return (
    <div className="workspace-stack">
      <section className="decision-card">
        <div className="decision-card-head">
          <div className="callout-mark">TR</div>
          <div>
            <span>Trading Committee Proposal</span>
            <h2>{proposal.asset}</h2>
          </div>
          <StatusBadge value={proposal.status} />
        </div>
        <div className="proposal-facts statgrid4">
          <div>
            <dt>Action</dt>
            <dd>{proposal.action}</dd>
          </div>
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
        </div>
        <p>{proposal.rationale}</p>
        <div className="trace-strip">
          <span>Thesis {proposal.thesis_id}</span>
          <span>{proposal.citation_ids.length} citations</span>
        </div>
        <List title="Primary risks" items={proposal.primary_risks} />
        <List title="Invalidation" items={proposal.invalidation_conditions} />
        <textarea aria-label="Decision note" value={note} onChange={(event) => setNote(event.target.value)} rows={3} placeholder="Decision note" />
        <div className="decision-actions">
          <button type="button" onClick={() => void decide("approve")} disabled={proposal.status !== "pending_review" || step !== "idle"}>
            <Check size={15} />
            Approve
          </button>
          <button type="button" className="secondary-danger" onClick={() => void decide("reject")} disabled={proposal.status !== "pending_review" || step !== "idle"}>
            <X size={15} />
            Reject
          </button>
        </div>
        {decision ? <p className="decision-result">Decision recorded: {decision.decision}</p> : null}
      </section>
      <DecisionHistory decision={decision} />
      <ActivityTrace events={events} />
    </div>
  );
}

function ActivityTrace({ events }: { events: ActivityEvent[] }) {
  return (
    <section>
      <SectionHeading eyebrow="ACTIVITY" title="Activity" />
      <ol className="activity-list panel-lite">
        {events.slice(-6).map((event) => (
          <li key={event.id}>
            <span>{event.event_type.replaceAll("_", " ")}</span>
            <p>{event.message}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

function PositionsView() {
  return (
    <div className="positions-grid">
      {previewPositions.map((position) => (
        <article key={position.symbol} className="position-card">
          <div>
            <strong className="num">{position.symbol}</strong>
            <StatusBadge value={position.direction} />
          </div>
          <span>{position.name}</span>
          <p>{position.narrative}</p>
          <dl>
            <div>
              <dt>Status</dt>
              <dd>{position.status}</dd>
            </div>
            <div>
              <dt>P/L</dt>
              <dd>{position.pnl}</dd>
            </div>
          </dl>
        </article>
      ))}
    </div>
  );
}

function DecisionHistory({ decision }: { decision: InvestmentDecision | null }) {
  return (
    <section>
      <SectionHeading eyebrow="HISTORY" title="決策紀錄" />
      <div className="history-list">
        {decision ? (
          <article>
            <StatusBadge value={decision.decision} />
            <strong>{decision.project_id}</strong>
            <span>{decision.user_note ?? "No note"}</span>
          </article>
        ) : (
          <article>
            <StatusBadge value="preview" />
            <strong>No recorded decision</strong>
            <span>Approval, rejection, and later defer actions will stay linked to thesis evidence.</span>
          </article>
        )}
      </div>
    </section>
  );
}

function MetricCard({ delta, label, value }: { delta: string; label: string; value: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong className="num">{value}</strong>
      <p>{delta}</p>
    </article>
  );
}

function PreviewReport({ report }: { report: (typeof previewReports)[number] }) {
  return (
    <article className="library-card preview-card">
      <StatusBadge value={report.facet} />
      <h3>{report.title}</h3>
      <p>{report.summary}</p>
      <span>Confidence {report.confidence}</span>
    </article>
  );
}

function FacetCard({ label, text }: { label: string; text: string }) {
  return (
    <div className="facet-card">
      <span />
      <div>
        <strong>{label}</strong>
        <p>{text}</p>
      </div>
    </div>
  );
}

function SectionHeading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="section-heading">
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
    </div>
  );
}

function PanelTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="panel-title">
      <span className="eyebrow">{eyebrow}</span>
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
  const statusClass = value.toLowerCase().replaceAll("_", "-").replaceAll(" ", "-");
  return <span className={`status status-${statusClass}`}>{value.replaceAll("_", " ")}</span>;
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    deciding: "deciding",
    done: "done",
    idle: "idle",
    research: "researching",
  };
  return labels[status] ?? status;
}

function errorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return "Unexpected error";
}
