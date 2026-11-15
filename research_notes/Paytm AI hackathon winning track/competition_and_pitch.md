# Competition density by track and winning-pitch format: Paytm Build for India AI Hackathon (Chennai, devSemble, 15 Nov 2026)

Research date: 2026-11-12. Labels: [VERIFIED] = read on the cited page; [SELF-REPORTED] = a team's own README/post, unconfirmed by organizers; [INFERENCE] = my reasoning. Official winner lists, judging rubrics and per-track submission counts were NOT found anywhere for this hackathon series.

## 1. Prior editions of the Paytm x devSemble hackathon: what was presented, by track

### Takeaway
The Chennai event is one city in a multi-city 2026 series (Bengaluru, Mumbai, Delhi, Chennai) with the same 3-track, 2-stage format. No organizer has published winners or finalists by track. The best available evidence is about a dozen public GitHub READMEs and one self-reported Mumbai winner post. Those show heavy convergence on a "Saathi" merchant-agent concept in Track 3.

### Cited Findings
- Bengaluru edition is "organized by Paytm in collaboration with devSemble." It has the same three tracks as Chennai: (1) Merchant Growth AI, (2) AI-Powered Financial Journeys, (3) Autonomous AI Teammates ("complete measurable sales or customer service outcomes, not just answer questions"). [VERIFIED] — [Luma Bengaluru](https://luma.com/6afp5q46)
- Format [VERIFIED] — [Luma Bengaluru](https://luma.com/6afp5q46):
  - Stage 1 is a deck on the devSemble platform; only shortlisted teams advance.
  - Stage 2 is an on-site build of a working prototype/POC with mentor access, then a demo.
  - Stage 2 deliverables are the prototype, a demo video and a presentation.
  - The deck sections are Title, Problem, Solution, Tech stack, USP, Impact & benefits, Business model.
  - Judging criteria are "to be communicated to shortlisted teams" (not public).
  - Prizes are only "exciting prizes, rewards, and recognition."
- Bengaluru dates: deck deadline 27 Oct, offline finals 31 Oct 2026 at the Paytm office. [VERIFIED] — [Luma Bengaluru](https://luma.com/6afp5q46); [ClaimSaathi README](https://github.com/ParasAdlakha/claimsaathi); [Saathi README](https://github.com/amithrh/saathi-paytm-hackathon) (Bellandur, Bengaluru).
- An earlier or parallel "Paytm AI Hackathon" listing used two tracks (AI for Paytm Users; AI for Small Businesses). It had 143 attendees, a ₹1,00,000 prize pool, teams of up to 3, and an in-person day with 10:00-17:00 hacking and 17:00-18:00 submissions. [VERIFIED] — [Luma evm2zg68](https://luma.com/evm2zg68). A Phinite x Paytm "Agent Labs" buildathon used the same two track names; solutions had to work "as features within Paytm's current products." [VERIFIED] — [Luma Agent Labs](https://luma.com/ii0pip0d)
- A Delhi edition exists: the VoiceVyapar README says "Delhi edition, Track 1: Merchant Growth AI." [SELF-REPORTED] — [VoiceVyapar](https://github.com/smarpitm/Paytm_Ai_Hackathon)
- A devSemble Chennai page exists ("Paytm Build for India AI Hackathon – Chennai | devSemble Hackathon"), but its body content (date, deadlines, rubric) could not be retrieved. A search summary said a Mumbai post gave 31 Oct 2026 at the Paytm Mumbai office, 8 hours. [PARTIAL, unverified] — [devSemble Chennai](https://devsemble.com/hackathons/paytm-build-for-india-ai-hackathon-chennai-by-paytm)
- Mumbai winner claim: Team Swamit Labs says it won with "Paytm Saathi - Money SOS", a single button for urgent money problems.
  - The user states the problem in their own language. The worked example is a family facing an ICU deposit demand, where the goal is to avoid borrowing the full amount when insurance may cover part of it.
  - The post reports about 6,000 registrations, 100 teams in the offline finale, 10 teams on stage and one winner.
  - A team member's post thanks "Paytm and HackBriven" for the platform, which may mean the Mumbai round ran on a different platform than devSemble.
  - Jurors named: Ami Ganjawalla, Cyrus Carvalho, Prasad Nayak (Paytm).
  - [SELF-REPORTED, LinkedIn; pages return HTTP 999 to fetchers, so I relied on search-result extracts] — [LinkedIn result](https://it.linkedin.com/in/angelozabelli); [LinkedIn Tejas Bavaskar](https://www.linkedin.com/in/tejas-bavaskar-658238104/)
- Public finalist-stage/entry repos found (all 0 stars; none report a placement):
  - **Saathi (Track 3, Bengaluru finals):** Manager agent plus Diagnoser/Fixer/Seller/Compliance. It recovers lost revenue (offline Soundbox, failed settlements) via a Kannada/Hindi voice call, then offers a loan. Sarvam STT/TTS/LLM, Twilio, Paytm Payment Gateway sandbox, 20 seeded merchants. Compliance is enforced in the tool layer (TRAI calling window 9-19h, consent, Key Fact Statement, one-day cooling-off under RBI Digital Lending Directions 2025). 86 unit tests plus a number-audit check. Latency 1.5-3.2 s. Offline fallback with cached audio. [SELF-REPORTED] — [GitHub](https://github.com/amithrh/saathi-paytm-hackathon)
  - **Paytm Saathi "Kirana AI Teammate" (Track 3):** Seven agents (Resolve, Fix, Reconcile, Revive, Onboard, FieldMate, Vasooli), a LangGraph orchestrator, risk tiers R0-R4, idempotency keys and bounded loops. Seeded demo data. [SELF-REPORTED] — [GitHub](https://github.com/Karnita-Saumya/Paytm-Saathi)
  - **Wapsi (Track 3):** Re-engages dormant merchants for the field sales team. Claude Sonnet with tool calling, Bolna/Sarvam voice, 500 simulated merchants. Claims "diagnosed all 37 cases" (self-generated data, which the README itself caveats). Unit economics of about ₹3,000/yr per merchant versus about ₹12 per call. Includes an evaluate_agent.py script. [SELF-REPORTED] — [GitHub](https://github.com/amanunreal/Paytm-hack)
  - **MerchantPulse AI (Track 3):** Churn-risk detection for about 1.5 crore subscription merchants, simulated at 500 merchants calibrated to NPCI's ~0.8% decline rate. Caught problems 3 days earlier than a volume-drop alert, with 329 false alarms avoided. About ₹19.9 crore/yr business case, explicitly an assumption-based estimate. [SELF-REPORTED] — [GitHub](https://github.com/iashutoshyadav/Paytm-AI-hackathon)
  - **Paytm Commerce OS (Track 3):** Lead-to-credit agents over WhatsApp (Sarvam, Cognee, n8n); Paytm rails mocked. [SELF-REPORTED] — [GitHub](https://github.com/AryanPandey17/paytm-ai-hackathon)
  - **Pakka (Track 3):** UPI AutoPay "asks before the money moves." The LLM only writes text and a deterministic engine moves money. 6,000 synthetic users, 14 merchants, 9,400 mandates, 270 tests, red-team result of 0 of 14 attacks succeeded, 24 languages. The only consumer-side Track 3 entry I found. [SELF-REPORTED] — [GitHub](https://github.com/sneharc16/Paytm-hack)
  - **Munshi AI (Track 1):** Four "guardians" (fraud, shift leakage/QR swap, GST limit, win-back). 22,853 synthetic payments. Reports 5/5 fraud caught with no false alarms, 43/43 tax items classified correctly. The README admits thresholds are hand-tuned. [SELF-REPORTED] — [GitHub](https://github.com/23f3003609/munshi-ai-Paytm-hackathon)
  - **VoiceVyapar (Track 1, Delhi):** Voice ledger/udhaar, UPI QR reminders via Telegram, credit score. Seeded with 5 customers, no evals. [SELF-REPORTED] — [GitHub](https://github.com/smarpitm/Paytm_Ai_Hackathon)
  - **HarvestWise (Track 1):** Tamil-first voice copilot for vegetable vendors (Sarvam, n8n, Cognee), 83-test QA battery. Says it was "shortlisted in Round 1." [SELF-REPORTED] — [GitHub](https://github.com/venkatanarayana15/paytm-harvestwise)
  - **DukaanSaathi AI (merchant, track unstated):** Demand forecast (8.4% MAPE), YOLOv8 shelf scan, credit-health score; 10 synthetic merchants. [SELF-REPORTED] — [GitHub](https://github.com/Tushar040903/Paytm-Build-for-India-AI-Hackathon)
  - **ClaimSaathi (Track 2):** Health-insurance claim companion that reads the bill, predicts the payout with the policy clause behind each cut, and drafts a grievance. It has a deterministic rules engine for money, IRDAI non-payable list, BM25 clause search, Hindi/English voice, 13 tests, a 9-slide deck (Title, Problem, Solution, Product, Tech stack, USP, Impact, Business model, Team), a 2-minute demo video and a 3-minute pitch video. It lists as a limitation that estimates are not validated against settled claims. [SELF-REPORTED] — [GitHub](https://github.com/ParasAdlakha/claimsaathi)
- Unrelated: a repo for FIN-O-HACK 2026 (track "AI for Small Businesses") built a merchant-credit "agent swarm" on Paytm's Payment MCP Server. That is a different event but shows what teams build with Paytm tooling. [SELF-REPORTED] — [TrustAI](https://github.com/Pulkit7070/TrustAI)

### Inferences
- [INFERENCE] The first merchant-side Track 3 pattern is already done at least five times in public repos. It is "Saathi/Wapsi/Revive for dormant or failing Soundbox merchants plus udhaar reminders plus Hindi voice via Sarvam plus human approval". A Chennai team building the same will be one of many near-duplicates.
- [INFERENCE] Track 2 is the least visible in public repos (1 found), yet the one self-reported Mumbai winner is a Track-2-style consumer money/insurance journey. Both are weak evidence (see section 2 for bias), but together they suggest Track 2 is where fewer strong merchant-style clones exist.
- [INFERENCE] Chennai participants may have access to these public repos and the Mumbai winner idea; judges who saw Bengaluru/Mumbai/Delhi rounds may be primed to see repeats.

### Gaps
- No official winner/finalist list for Bengaluru, Delhi or Mumbai. No rubric. No Chennai page content (date, deadline, prize pool, shortlist status). Whether the Chennai Stage 1 deadline has already passed is unknown; check the devSemble page immediately.
- Could not read LinkedIn/Instagram/X posts directly (HTTP 999/403); winner details rely on search-result extracts.

## 2. Submission distribution per track in similar multi-track corporate hackathons

### Takeaway
No hard per-track submission counts exist for this series or for comparable Indian corporate hackathons. The only quantitative proxy is a skewed sample of public GitHub READMEs, where Track 3 is the most common. Treat the pattern as directional, not measured.

### Cited Findings
- Track counts from the ten READMEs a search surfaced (public GitHub only; some entries were also from different editions) — sources in section 1:
  - Track 1 Merchant Growth AI: 3 explicit (Munshi, VoiceVyapar, HarvestWise) plus DukaanSaathi (unstated, merchant-themed).
  - Track 2 Financial Journeys: 1 (ClaimSaathi).
  - Track 3 Autonomous Teammates: 6 (Saathi, Paytm Saathi, Wapsi, MerchantPulse, Commerce OS, Pakka).
- Mumbai finale (self-reported): ~6,000 registrations, 100 teams offline, 10 on stage. That is a ~1.7% registration-to-offline conversion and about 10% of the offline field reaching the stage. [SELF-REPORTED] — [LinkedIn result](https://it.linkedin.com/in/angelozabelli)
- Comparable events published no per-track submission counts:
  - MumbaiHacks 2025 had 3 tracks (Fintech, Healthtech, Misinformation) and 3,500+ participants, one winner per track. The Fintech winner "MoneyMitra" was a personal-finance and financial-literacy app with budgeting, OCR/SMS parsing and multilingual modules. The Fintech runner-up "FinOps Copilot" was an agent that automates routine operations. The source is a VMPL press release that Tribune/ANI say they did not verify. [VERIFIED as reported] — [Tribune](https://www.tribuneindia.com/news/business/mumbaihacks-2025-crowns-indias-next-gen-ai-innovators-with-inr-1-crore-cash-and-rewards-marking-the-worlds-largest-agentic-ai-hackathon)
  - Google Cloud Gen AI Exchange 2025: 270,000+ developers and a top-100 pitch to 30 judges. The article gives no category breakdown, but says winners moved from prototype-style demos to agentic and explainable systems "built for enterprise integration" with auditability. [VERIFIED as reported] — [Outlook Business](https://www.outlookbusiness.com/deeptech/artificial-intelligence/google-cloud-gen-ai-hackathon-2025-winners-use-cases-and-what-270000-developers-built)
  - OpenAI x Varun Mayya "Build What Moves India": 13,000+ registrations, 250 shortlisted, 10 finalists with working prototypes. The winner was RaktKhoj (blood-bank finder), a narrow real-world service problem rather than a generic chatbot. [VERIFIED as reported] — [T2 Online](https://t2online.in/tech/tech-news/openai-and-varun-mayya-s-build-what-moves-india-ends-with-10-finalists-in-bengaluru/2008590)
- Searches for submission-distribution data on Indian hackathons returned no published breakdowns (organizers publish winners only). — search of devfolio/Unstop/IISc pages, e.g. [IISc Gen AI 2025 results](https://cni.iisc.ac.in/hackathons/gen-AI-2025-results/)

### Inferences
- [INFERENCE] The sample is biased: only teams that publish a README with the hackathon name show up. It over-represents builders who pitch deeply technical agent stacks. Consumer chatbot and "financial literacy" ideas, which are probably common among the 6,000 registrants, would mostly die at the deck stage and never produce a repo. So the real Stage 1 pool is likely dominated by weak generic decks in all three tracks; the relevant crowd is the shortlisted strong teams.
- [INFERENCE] Track 3's name ("Autonomous AI Teammates") is the most hype-aligned with current LLM-agent buzz and with Paytm's own agentic messaging (see section 5), so it likely attracts the most technically strong builders. Track 1 likely attracts the largest number of generic voice-WhatsApp merchant bots. Track 2 likely attracts the generic consumer "loan/insurance chatbot" decks, but strong, regulation-aware entries appear scarce.

### Gaps
- No per-track registration/submission/shortlist counts for any Paytm edition. The Chennai shortlist is unknown.

## 3. Generic submissions to avoid and what differentiates winners

### Takeaway
Across all the public entries the commodity layer is the same: Sarvam voice, Hindi/Hinglish, WhatsApp, Soundbox, udhaar reminders, synthetic data, a credit score. Standing out requires a deterministic action layer, a quantified KPI tied to real Paytm numbers, measured evals (not only "tests pass"), regulation-aware escalation, and a single memorable demo moment.

### Cited Findings
- Entries in the series already cover (so are "generic" for Chennai): voice-first udhaar/ledger assistants, dormant-merchant win-back, Soundbox fault diagnosis, GST/fraud guardians, demand forecasting plus credit score, WhatsApp lead-to-loan agents. [SELF-REPORTED] — see repos in section 1.
- Differentiators observed in the stronger repos:
  - **Deterministic money layer.** The LLM only writes text and a typed tool layer or rules engine moves money (Pakka, Saathi, ClaimSaathi, Munshi). [SELF-REPORTED]
  - **Compliance enforced in code,** not in the prompt: RBI Digital Lending Directions 2025 (KFS, cooling-off), TRAI calling window, consent logs, AI disclosure, IRDAI non-payable list and the grievance chain Insurer GRO, Bima Bharosa, Ombudsman. [SELF-REPORTED] — [Saathi](https://github.com/amithrh/saathi-paytm-hackathon); [ClaimSaathi](https://github.com/ParasAdlakha/claimsaathi)
  - **Escalation logic.** Risk tiers R0-R4, approval above ₹25,000, confidence below 0.7 escalates to a human, one nudge per customer per 3 days, no-action when a whole area dips together. [SELF-REPORTED] — [Paytm Saathi](https://github.com/Karnita-Saumya/Paytm-Saathi); [Commerce OS](https://github.com/AryanPandey17/paytm-ai-hackathon); [Wapsi](https://github.com/amanunreal/Paytm-hack)
  - **Measured outcomes against planted ground truth.** Examples are 5/5 fraud caught with 0 false alarms in 22,848 normal payments, 329 false alarms avoided, 3 days earlier detection than a baseline alert, and a red-team result of 0 of 14 attacks succeeded. Also a latency budget and a "number audit" that checks every rupee figure the agent speaks against tool output. [SELF-REPORTED] — [Munshi](https://github.com/23f3003609/munshi-ai-Paytm-hackathon); [MerchantPulse](https://github.com/iashutoshyadav/Paytm-AI-hackathon); [Pakka](https://github.com/sneharc16/Paytm-hack); [Saathi](https://github.com/amithrh/saathi-paytm-hackathon)
  - **Unit economics.** About ₹3,000/yr per merchant versus about ₹12 per agent call (Wapsi) and an assumption-based ₹19.9 crore/yr (MerchantPulse). Both explicitly label their inputs. [SELF-REPORTED]
  - **Honest limitations.** Several READMEs list "synthetic data," "thresholds hand-tuned," "estimates not validated against settled claims." These are good practice but also reveal that nobody has real-data validation.
- Judge guidance (generic, not Paytm-specific): a clear demo beats a complex confusing one; check the rubric (innovation, impact, technical execution, relevance to brief, presentation); have one memorable moment; record the demo as a fallback; a team with the best demo lost because it lacked a business angle (blog anecdote). [VERIFIED as reported, blog-level, mostly 2014-2020 with a few 2025-26 pieces] — summary of results incl. [JetBrains blog, 2026](https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/) (page itself returned 403; claims taken from the search extract), [Medium judge perspective](https://medium.com/thecapital/how-to-win-a-hackathon-from-a-judge-mentor-and-participant-perspective-b7bfe9cd20a1) (403)
- Google Gen AI Exchange write-up: judges favoured domain-specific tools that plug into enterprise pipelines, provide auditability and scale. [VERIFIED as reported] — [Outlook Business](https://www.outlookbusiness.com/deeptech/artificial-intelligence/google-cloud-gen-ai-hackathon-2025-winners-use-cases-and-what-270000-developers-built)

### Inferences
- [INFERENCE] The "reply to a question" chatbot (loan-eligibility bot, financial-literacy assistant, WhatsApp merchant FAQ) is explicitly disfavored by Track 3's wording ("not just answer questions") and by Track 1's "business partner" wording. Treat both chatbot patterns as the baseline to beat.
- [INFERENCE] A Chennai-specific edge: Tamil-first, local-merchant personas (HarvestWise already did Tamil vegetable vendors, so pick a different niche, e.g. a Chennai trade like tea stalls, textile, auto-parts or gold-loan context) and a named regional sector reduces overlap with the Hindi/Kannada-heavy repos.

### Gaps
- No judge or winner interviews specific to Paytm. No evidence on how Paytm weights business model versus technical depth.

## 4. What a winning PPT pitch looks like for the required sections

### Takeaway
The required 7 sections (Title, Problem, Solution, Tech stack, USP, Impact & benefits, Business model) are fixed by the organizer. Winning means filling them with sponsor-specific numbers, one concrete worked example, and a business case framed as value to Paytm (not a startup-style market-size slide). Public evidence on winning decks is thin.

### Cited Findings
- Required deck structure [VERIFIED]: Title, Problem, Solution, Tech stack, USP, Impact & benefits, Business model, "tailored to the chosen track." — [Luma Bengaluru](https://luma.com/6afp5q46)
- Teams in the series used 7 to 9 slides (the Saathi README says 7; ClaimSaathi used 9, adding Product and Team) and supplemented the deck with a 2-minute demo video and 3-minute pitch video. [SELF-REPORTED] — [Saathi](https://github.com/amithrh/saathi-paytm-hackathon); [ClaimSaathi](https://github.com/ParasAdlakha/claimsaathi)
- A pitch closing line used by one team: "Other voice bots wait for questions. Saathi hunts for lost money and acts." (a one-sentence USP contrast). The same team's open item at submission time was a missing worked rupee example for the Impact slide and an unsupported "60%" figure. [SELF-REPORTED] — [Saathi](https://github.com/amithrh/saathi-paytm-hackathon)
- Generic judge/blog advice: one idea, one memorable moment, 2-3 minute pitches, a business model matters, backwards planning from the demo. [Blog-level, see section 3 sources]
- Sponsor context useful for the Business-model/Impact slides:
  - Paytm said all new investment goes to AI, building small language models for SMB/voice/Indian languages, and "seven times more people complete the funnel in an agentic workflow." — [LetsDataScience, May 2026 (Q4 FY26 call)](https://letsdatascience.com/news/paytm-bets-on-ai-to-drive-fy27-momentum-cfdb9749)
  - Merchant GMV was ₹6.5 lakh crore (+27% YoY) and UPI GTV +46% YoY (same source).
  - Paytm described Soundbox as evolving into a small-business operating system (same source). It launched an AI Soundbox with an assistant in 11 Indian languages and a dedicated Paytm Button for summaries and support. — [Business Today, Oct 2025](https://www.businesstoday.in/tech-today/launch/story/paytm-unveils-indias-first-ai-soundbox-for-merchants-shares-jump-25-after-launch-497139-2025-10-07)
  - Watch items named for FY27 include customer-acquisition cost and merchant activation on AI-enabled devices (LetsDataScience source).

### Inferences
- [INFERENCE] Suggested slide content that fits the rubric style of the repos above:
  - Problem: one sharp, quantified pain tied to a Paytm metric (device-offline days, T+1 settlement failures, claim deductions, drop-off in a lending funnel), with a real-world anecdote.
  - Solution: an agent loop diagram (trigger, tool calls, policy check, action, verification, escalation) rather than a feature list.
  - Tech stack: name the deterministic layer and the evals, not only the LLM.
  - USP: one contrast sentence against the obvious chatbot alternative.
  - Impact: a worked per-merchant or per-ticket rupee example plus a KPI (resolution rate, cost per ticket/call, recovered GMV, claim leakage), with assumptions visible. Do not state unsupported percentages.
  - Business model: how it makes money for Paytm (cost-to-serve reduction, retained subscriptions, take-rate on lending/insurance conversion) and a rollout path through existing surfaces (Soundbox, Paytm for Business app, Money, Check-In). Avoid a standalone-SaaS framing.
- [INFERENCE] Because Stage 2 is a build-on-site and the deck only gets you shortlisted, the deck should signal feasibility (what will be real versus simulated in the room) in addition to vision.

### Gaps
- No actual winning Paytm decks were found. No Paytm judge statements on slide weighting or business-model expectations.

## 5. Feasibility for a 3-person team in a short offline build, by track

### Takeaway
Track 1 (merchant) and Track 3 (service/sales agent) can show an end-to-end agent loop fastest on synthetic data. Track 2 is feasible but demands a credible, compliant journey and a fixed rules engine; it is rich in a single powerful demo (document in, decision out) but weaker on "autonomy." Sandbox access to Paytm-specific APIs is uncertain.

### Cited Findings
- Stage 2 gives 'on site' time with mentors; the other event listing allotted about 7 hours of hacking (10:00-13:00 and 13:30-17:00) and submissions at 17:00. The Mumbai round was reportedly 8 hours (unverified). [VERIFIED for the earlier listing] — [Luma evm2zg68](https://luma.com/evm2zg68)
- Teams are 1-3 people in the earlier listing; the Bengaluru page states no team size. [VERIFIED] — [Luma evm2zg68](https://luma.com/evm2zg68); [Luma Bengaluru](https://luma.com/6afp5q46)
- Paytm tooling: an official "Paytm MCP Server" page exists under Paytm Payments developer docs; third-party listings describe tools like create_link, fetch_link and settlement lookup, local run with PAYTM_MID/PAYTM_KEY_SECRET, and a hosted remote option requiring onboarding. The official page body could not be read. [PARTIAL] — [Paytm docs](https://paytmpayments.com/docs/mcp-server-overview); search results via [LobeHub](https://lobehub.com/en/mcp/paytm-payment-mcp-server). The Saathi team used the Paytm Payment Gateway sandbox (payment links, status, refunds). [SELF-REPORTED] — [Saathi](https://github.com/amithrh/saathi-paytm-hackathon)
- Common stack used by multiple teams: Sarvam AI (saarika STT, bulbul TTS, sarvam-105b LLM) for Indic voice, n8n and Cognee for orchestration/memory, Twilio WhatsApp sandbox, FastAPI plus React dashboard, SQLite or Postgres, and seeded synthetic data (20 to 6,000 users). Several demos run offline with cached audio and scripted fallbacks. [SELF-REPORTED] — [Saathi](https://github.com/amithrh/saathi-paytm-hackathon); [HarvestWise](https://github.com/venkatanarayana15/paytm-harvestwise); [Commerce OS](https://github.com/AryanPandey17/paytm-ai-hackathon); [Pakka](https://github.com/sneharc16/Paytm-hack)
- Entries admit real Paytm logs are internal, so all use simulated data calibrated to public figures (e.g. NPCI's ~0.8% decline rate). [SELF-REPORTED] — [MerchantPulse](https://github.com/iashutoshyadav/Paytm-AI-hackathon)

### Inferences
- [INFERENCE] Track 1: fastest to demo (ledger/voice/insight screens over synthetic merchants) but the most visually and conceptually similar to existing repos, so it needs a niche (Chennai trade, working-capital forecasting, QR-fraud) to differentiate.
- [INFERENCE] Track 3: fastest to show a genuine tool-calling loop with escalation and KPIs (tickets, resolutions, cost per case) and it matches the sponsor's emphasis. It is also where competition from strong agent builders is densest. A defensible angle is an under-served function (e.g., lending or insurance collections/servicing, dispute handling, field-sales scheduling for non-Hindi regions) plus real evals.
- [INFERENCE] Track 2: a document-in, decision-out journey (like ClaimSaathi) can be built in a day with LLM vision plus a rules engine. It has the least visible competition from public repos and a self-reported Mumbai winner of that flavor. Risks are (a) regulatory scrutiny of claims, (b) pressure to prove accuracy that synthetic data cannot show, (c) generic "loan eligibility / literacy chatbot" decks diluting the category.
- [INFERENCE] Estimated "strong competitors per unit of opportunity" (judgment, not measured): Track 2 appears best, Track 3 is the most crowded among strong teams, Track 1 has many but mostly similar mid-tier builds. Opportunity measured by Paytm strategy emphasis is highest for Track 1 and Track 3 (Soundbox/SMB OS, agentic funnels), so Track 2's low crowding comes with lower sponsor signal in the sources found.

### Gaps
- No confirmation of what APIs/credentials Paytm provides to finalists on site. No evidence of an official Paytm Stage 2 dataset. The Paytm lending/insurance AI strategy was not covered in the sources I read.
