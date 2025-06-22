# ACME Corp — Security Workflow Bot • Home Assignment
==================================================

## Context
-------
You are joining ACME Corp’s Security Engineering group.  The team relies on Slack as its primary front‑door
for security requests (network changes, vendor approvals, permission escalations, etc.).  Your task is to create the
first internal Slack App that can triage these requests automatically, drive any missing-data conversation with the
requester, and produce a final decision consistent with ACME’s historical “tribal knowledge”.

## Part 1 – Build the Bot
----------------------
1. **Slack interface** – A slash‑command or app‑mention that accepts free‑text requests.
2. **classification** – Parse the message, classify the request type, and estimate the security‑risk score.
3. **Adaptive questioning** – If mandatory fields are missing (see dataset), ask follow‑up questions in the
   same Slack thread until you have all required inputs.
4. **Decision engine** – Using the supplied `acme_security_tickets.csv` (1 000 past tickets), infer the organisation’s
   common practices and return one of: *Approved*, *Rejected*, or *Needs More Info* plus a short rationale.
5. **Persistence & transparency** – Log every interaction and decision to a local JSON/SQLite store so that the
   history can be audited.

## Part 2 – What to Deliver
------------------------
* Source code
* BackEnd should run locally on your computer. bonus: in a docker or cloud environment
* Active Slack app. We will chat with your Slack app.
* A **README** containing:
  - Design decisions & algorithm description (max 300 words).

## Part 3 - Excellence
------------------------
* To show your uniqueness, we ask you to choose one spect of this assignment and excel in it.
* It could be amazing DevOps, Product, Code architecture, Data analysis, AI, Crazy slack integration, UI, ...  
* Please choose which ever your most fluent with. 

## Non‑Functional Expectations
---------------------------
* You may use any language or framework you are comfortable with (Python/TypeScript preferred).
* Use which ever LLM engine you find best.
* Focus on clean, working code rather than perfect coverage.

## Evaluation Criteria
-------------------
* Correctness of data analysis & decision logic.
* Quality and robustness of code (structure, tests, error handling).
* Clarity of written explanations.
* Thoughtfulness of follow‑up questions asked by the bot.

Good luck – we are excited to review your work!