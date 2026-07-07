import { expect, test } from "@playwright/test";

test("runs the SMR research workflow through approval with traceability and refresh", async ({ page }) => {
  await page.goto("/");

  await page.getByLabel("Topic").fill("SMR approval path deterministic demo");
  await page.getByRole("button", { name: "Create project" }).click();

  await expect(page.getByRole("heading", { name: "SMR approval path deterministic demo" })).toBeVisible();
  await expect(page.getByText("Industry demand and supply chain")).toBeVisible();
  await expect(page.getByText("Macro and policy setup")).toBeVisible();

  await page.getByRole("button", { name: "Run research" }).click();
  await expect(page.getByText("SMR-linked equities deserve bounded committee review")).toBeVisible();
  await expect(page.getByText("OKLO", { exact: true })).toBeVisible();
  await expect(page.getByText("completed").first()).toBeVisible();
  await expect(page.getByText("Artifacts and citations")).toBeVisible();
  await expect(page.getByText("IND-1")).toBeVisible();
  await expect(page.getByText("SMR demo evidence: industry demand").first()).toBeVisible();

  await page.getByRole("button", { name: "Committee" }).click();
  await expect(page.getByRole("heading", { name: "OKLO" })).toBeVisible();
  await expect(page.getByText("watchlist", { exact: true })).toBeVisible();
  await expect(page.getByText("First-of-a-kind deployment risk").first()).toBeVisible();
  await expect(page.getByText(/Thesis thesis_project_/)).toBeVisible();

  await page.getByLabel("Decision note").fill("Approve as watchlist review.");
  await page.getByRole("button", { name: "Approve" }).click();

  await expect(page.getByText("Decision recorded: approved")).toBeVisible();
  await expect(page.getByText("decision recorded", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve" })).toBeDisabled();

  await page.reload();
  await expect(page.getByRole("heading", { name: "SMR approval path deterministic demo" })).toBeVisible();
  await expect(page.getByText("Decision recorded: approved")).toBeVisible();
  await expect(page.getByText("IND-1")).toBeVisible();

  await page.getByLabel("Topic").fill("Second project without proposal");
  await page.getByRole("button", { name: "Create project" }).click();
  await expect(page.getByRole("heading", { name: "Second project without proposal" })).toBeVisible();
  await expect(page.getByText("Send the active thesis to committee.")).toBeVisible();
  await expect(page.getByText("Decision recorded: approved")).toHaveCount(0);

  await page.getByRole("button", { name: /SMR approval path deterministic demo/ }).click();
  await expect(page.getByText("Decision recorded: approved")).toBeVisible();
});

test("runs the reject decision path", async ({ page }) => {
  await page.goto("/");

  await page.getByLabel("Topic").fill("SMR reject path deterministic demo");
  await page.getByRole("button", { name: "Create project" }).click();
  await page.getByRole("button", { name: "Run research" }).click();
  await expect(page.getByText("SMR-linked equities deserve bounded committee review")).toBeVisible();
  await page.getByRole("button", { name: "Committee" }).click();
  await expect(page.getByRole("heading", { name: "OKLO" })).toBeVisible();

  await page.getByLabel("Decision note").fill("Reject because execution risk is too high.");
  await page.getByRole("button", { name: "Reject", exact: true }).click();

  await expect(page.getByText("Decision recorded: rejected")).toBeVisible();
  await expect(page.getByRole("button", { name: "Reject", exact: true })).toBeDisabled();
});
