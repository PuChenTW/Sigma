from studio_schemas import Desk, ResearchProject, ResearchTask


def plan_tasks(project: ResearchProject) -> list[ResearchTask]:
    return [
        ResearchTask(
            id=f"task_{project.id}_industry",
            project_id=project.id,
            desk=Desk.INDUSTRY,
            title="Industry demand and supply chain",
            description=f"Assess whether '{project.topic}' has durable demand, credible supply chain support, and investable industry structure.",
        ),
        ResearchTask(
            id=f"task_{project.id}_macro_policy",
            project_id=project.id,
            desk=Desk.MACRO_POLICY,
            title="Macro and policy setup",
            description=f"Assess policy support, financing conditions, and macro constraints that affect '{project.topic}'.",
        ),
        ResearchTask(
            id=f"task_{project.id}_fundamental",
            project_id=project.id,
            desk=Desk.FUNDAMENTAL,
            title="Candidate asset fundamentals",
            description=f"Identify one candidate asset for '{project.topic}' and summarize the fundamental trade-offs.",
        ),
    ]
