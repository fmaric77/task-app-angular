Support Agent Demo Presenter Script

About fifteen to twenty minutes for one ticket, thirty to forty if you run all three. Audience is stakeholders evaluating agentic support for app development. Repo is fmaric77/task-app-angular on GitHub.

Welcome, about one minute. Say this when you open.

Say: Welcome to the demo. Thanks for being here. Today I am going to show you an autonomous support agent for application development. The idea is simple. A user reports a problem in Jira the way they normally would. An agent picks it up, finds the right internal runbook, fixes the code, opens a pull request, and closes the ticket when that PR is merged. You will see the whole loop live. We have a real Angular app in production on Vercel, real Jira tickets written like user reports, and runbooks that hold the engineering knowledge. The agent reads the ticket and the runbook, but it does not get the fix handed to it in the ticket itself. At the end I am happy to take questions on how this would fit your support workflow.

The story in one sentence: a user reports a bug in Jira, an autonomous agent reads the ticket, finds the matching runbook, fixes the code, opens a pull request, and closes the ticket when it merges. No engineer in the loop for the fix itself.

Before the room, about fifteen minutes ahead. Go to the project folder, set JIRA_API_TOKEN, run ./scripts/demo-reset.sh --push. Confirm main is at demo-baseline with bugs still unresolved. Confirm Jira tickets TEST-1, TEST-2, and TEST-3 are in Backlog with no comments. Confirm the production app at task-app-angular-tau.vercel.app still shows the bugs.

Open these tabs: the production app at task-app-angular-tau.vercel.app, the Jira board at iolap-inc.atlassian.net for project TEST, the GitHub repo fmaric77/task-app-angular, the runbooks folder in the repo, and an empty terminal for the watcher.

Start the watcher with JIRA_API_TOKEN set, then run python3 automation/agent_watcher.py automation/agent_watcher_config.json. Keep that terminal visible. You should see Sleeping 15s every poll cycle.

Scene one, about two minutes. Show the production app.

Say: This is a simple Angular task app deployed on Vercel. It has three known issues we deliberately left in for this demo.

Do the live repro. Add a task, mark it complete, click Clear completed. Nothing happens. That is TEST-1, an empty clearCompleted stub. Point at the Added date. The month is off by one. That is TEST-3, getMonth without plus one. Mention that priority levels do not exist yet. That is TEST-2, a feature not built.

Say: In a real support flow, a user would not file a GitHub issue. They would open a Jira ticket describing what they see. That is what we have next.

Scene two, about two minutes. Show the Jira board. Open TEST-1, TEST-2, and TEST-3.

Say: These tickets are written like real user reports. Symptoms and expected behavior only. No file paths, no root cause, no fix instructions.

Open TEST-1 and read the What I am seeing section aloud.

Say: The agent does not get the answer from the ticket. It has to figure out what is wrong. The engineering knowledge lives separately, in runbooks.

Scene three, about two minutes. Show runbooks/clear-completed-noop.md in GitHub or the IDE.

Say: Runbooks are our internal playbooks. Symptoms, diagnosis, exact fix, verification steps. They are markdown in the repo today. In production these could live in Confluence and be fetched via Atlassian MCP.

Scroll to the root cause and fix sections. Show that the agent gets this, the user does not.

Say: The agent can read the code and the runbook, but it cannot edit runbooks. It only touches src.

Scene four, about one minute. Show the watcher terminal.

Say: Locally we run a lightweight watcher. It polls Jira every fifteen seconds, picks up support-agent tickets in Backlog, and invokes Cursor Agent. In production this could be a Cursor Cloud Automation or a Jira webhook instead of polling.

Point out: poll interval is fifteen seconds, one ticket at a time because we share one git workspace, and labels route tickets to runbooks like clear-completed, date, and priority.

Scene five, about five to eight minutes. Live run on TEST-1. This is the recommended first demo because it is the fastest bug with the clearest before and after.

Make sure only TEST-1 is actionable, or let the watcher pick the oldest ticket which should be TEST-1.

Say: Watch Jira. Within about fifteen seconds the watcher should pick this up.

Show in order. In Jira, TEST-1 moves to In Progress and gets an agent comment with a PR link. On GitHub, a new branch fix/test-1-something appears and a pull request opens with title starting TEST-1. In the PR diff, show the one-line fix in task.service.ts. In the watcher log, show Running cursor-agent, then Ticket TEST-1 processed.

Say: That took about forty to sixty seconds end to end. The agent read the ticket, matched the runbook, fixed the code, verified the build, and opened a PR. It did not merge. A human still reviews.

Merge the PR on GitHub, or ask someone in the room to approve.

Show that within one poll cycle the watcher detects the merge and TEST-1 moves to Done with a close comment that includes justification, PR link, and merged by and merged at.

Say: Ticket closed automatically when the fix landed in main. That is the full loop.

Scene six, about one minute. Show the production app again. Vercel auto-deploys on merge to main, so refresh or wait for redeploy.

Click Clear completed. Tasks disappear.

Say: User-reported bug, agent fix, human merge, production. Done.

Optional second ticket, about five to eight minutes each. TEST-3 is another small bug, a one-line date fix, good for showing the same pipeline again. TEST-2 is a feature request, about twelve files, priority dots, sort toggle, persistence. For TEST-2 say: Not every ticket is a bug. This one is a feature request. The runbook is a full spec with acceptance criteria. Same pipeline, ticket to runbook to PR. Note that if all three tickets are in Backlog they run one after another in a single poll cycle, about three minutes total agent time. For a tight demo, reset between tickets or leave only one in Backlog.

Optional PR feedback loop. Leave a comment on the open PR, not from CodeRabbit because the watcher ignores those. Example: Please add a unit test for clearCompleted. Show the watcher picking up feedback and the agent pushing a commit to the same branch. Say: The agent can also respond to human review comments on the PR and update Jira.

Architecture in thirty seconds if you need it. User opens a Jira ticket with symptoms only. Watcher or automation picks it up via poll or webhook. Cursor Agent reads the ticket as a user report, reads the runbook as engineer knowledge, edits src, runs npm run build, opens a PR on GitHub. A human merges the PR. Watcher closes the Jira ticket.

If asked why runbooks in repo: small set, Cursor indexes them, scale to Confluence or RAG later. If asked why not fix from Jira alone: real tickets do not contain root cause, this tests realistic triage. If asked why sequential: single workspace, parallel would need isolated worktrees per ticket. If asked why not merge automatically: human review gate, agent opens PR only. If asked cloud versus local: same flow via Cursor Cloud Automations and Jira MCP, see docs/cursor-automation-setup.md. If asked what if agent fails: check watcher logs, re-run after reset, ticket stays In Progress.

If something goes wrong. Watcher not running: python3 automation/agent_watcher.py automation/agent_watcher_config.json. Ticket stuck In Progress: ./scripts/demo-reset.sh --push. Agent slow over two minutes: talk through the runbook while waiting or show a previous PR from GitHub history. Wrong runbook matched: labels drive routing, check support-agent plus symptom labels. Build fails on Vercel: check the Vercel deploy tab.

Quick reset between runs: ./scripts/demo-reset.sh --push, then python3 automation/agent_watcher.py automation/agent_watcher_config.json.

URLs cheat sheet. Production app: task-app-angular-tau.vercel.app. Jira project: iolap-inc.atlassian.net/browse/TEST. GitHub: github.com/fmaric77/task-app-angular. Vercel dashboard: vercel.com/goldenarchangels-projects/task-app-angular.
