# PRD: Keel

Team JustUs, Paytm Build for India AI Hackathon (Chennai), Track 2: AI-Powered Financial Journeys.

Status as of 14 Nov 2026: pitch deck written (`JustUs_Keel_Pitch.pdf`); the text-mode prototype is built and tested (detector, policy engine, audit log, screen, scenario run, Sarvam-driven agent). Keel's lines have cached Tamil audio and a recorded backup video exists; live speech-to-text is not built. Everything below describes the demo build, not shipped software. The event is on 15 Nov.

## What we were building

Keel is an AI agent that keeps a small merchant's loan on track, in Tamil, inside the lender's rules.

**The problem (our understanding; to be sourced before it is stated as fact in the pitch).** A merchant loan is repaid in small fixed daily amounts that are taken from the merchant's daily settlement (the UPI and QR sales money paid into their account). Income moves day to day, but the repayment does not. In a bad week the same repayment takes a bigger share of the day's income. We believe the lender usually hears about trouble only after a payment is missed, and that reminders often arrive in English.

**The product.** Keel watches the settlement data and acts before a payment is missed. The pitch describes one loan journey in three stages. The demo builds only stage 3.

| Stage | What it does | Demo status |
|---|---|---|
| 1. Explain the offer | Works out a loan pre-offer in code from a lender-set rule and explains it by voice in Tamil, with the Key Fact Statement and cooling-off period | Pitched, not built. One scripted voice line at most |
| 2. Onboard | Collects consent, completes the e-mandate, links the disbursal | Pitched, not built |
| 3. Spot stress early | Flags a fall in settlements, phones the merchant in Tamil, and offers relief inside limits the lender set: a lower daily repayment for a fixed period, with the loan ending a little later | **Built for the demo** |

**The worked example (illustrative, the same one as the deck).** Murugan runs a tea stall in T. Nagar. His Rs 2,00,000 loan is repaid at Rs 500 a day. For the demo his normal settlement is a fixed, seeded **Rs 4,000 a day**.

| Day | Settlement | Share of the Rs 4,000 normal | Repayment without Keel | Left for the merchant |
|---|---|---|---|---|
| 1 | Rs 4,000 | 100% | Rs 500 | Rs 3,500 |
| 2 | Rs 3,800 | 95% | Rs 500 | Rs 3,300 |
| 3 | Rs 3,300 | 82.5% | Rs 500 | Rs 2,800 |
| 4 | Rs 2,900 | 72.5% | Rs 500 | Rs 2,400 |
| 5 | Rs 2,500 | 62.5% | Rs 500 | Rs 2,000 |
| 6 | Rs 2,400 | 60% | Rs 500 | Rs 1,900 |
| 7 | Rs 2,400 | 60% | Rs 500 | Rs 1,900 |

- **The trigger.** The lender-set stress rule is "settlement below 75% of normal on two days in a row". Day 4 (72.5%) and day 5 (62.5%) both qualify, so the rule fires after day 5's settlement arrives. Keel calls that evening.
- **The offer.** Rs 300 a day for 14 days, starting on day 6. With Keel, days 6 and 7 cost Rs 300 and he keeps Rs 2,100, not Rs 1,900.
- **The arithmetic.** Rs 200 less a day for 14 days defers Rs 2,800. At Rs 500 a day that is five full repayments plus a final Rs 300, so the loan ends 6 days later and the merchant never overpays.
- **The caveats.** Interest is ignored. The loan size, the Rs 500 repayment, the Rs 4,000 normal level and the 75% rule are assumptions, not Paytm's real terms.

**Hard rules the product must follow.**
- The agent never makes a final adverse credit decision. Offers come from a lender-set rule that code applies and the agent explains.
- The model cannot take an action outside the lender's limits. Every action goes through a rules engine (the policy engine) that the model does not control.
- What the agent says aloud also goes through the policy engine: rupee figures are filled in from tool output, not written by the model, and are checked against it before speech. This does not make free-form Tamil wording fully verifiable. That limit is stated in the pitch.
- The merchant's agreement is captured by a fixed read-back of the offer and an explicit yes, not by the model's reading of what was said.
- Every call, consent and action is written to a tamper-evident audit log.
- Distress, disputes, requests outside the lender's limits, low confidence and repeated policy blocks go to a human, with a call summary and the audit trail attached. A deterministic backstop (keywords, and escalation after repeated blocks) covers cases the model misses.

**What the demo has to show (about three minutes).**
1. One opening number: a merchant whose settlements fell 40% in a week.
2. The stress rule firing, then a live Tamil call that ends in a visible change: a new repayment schedule on screen. This is the golden path and is built first.
3. One deliberate escalation, showing the handover summary and the audit trail, plus the audit log's verify button.
4. A results screen from about 60 scripted text-mode scenarios, adversarial ones included (prompt injection, an out-of-hours call, an angry borrower, a hallucinated clause). Three figures, all labelled synthetic: policy violations blocked per rule, escalations by reason, and the number-audit pass rate.
5. A backup: a recording of one real successful run, shown as a recording if the live call fails.

**Metric definitions.**
- **Autonomous resolution:** a call that ends with the relief applied, or the merchant's question answered, with no human handover.
- **Violations blocked:** attempted rule-breaking actions the policy engine rejected in the scripted scenarios, counted per rule. We report "blocked N of N scripted attacks". The scenarios are ours, so this shows the gate works as designed, not that every attack is covered.
- **Number-audit pass rate:** the share of rupee figures spoken that match the tool output.
- **Roll-rate:** dropped from the build. We make no claim about reducing missed payments or credit losses.

**Out of scope for the hackathon build.**
- Stages 1 and 2 above.
- Real Paytm or bank integrations. Services are mocked. We connect the Paytm sandbox only if it is offered on the day.
- Real credit underwriting, real money movement, real borrower data.
- Insurance journeys. We chose lending because it ties to Paytm's distribution revenue (revenue it earns from distributing loans, reported as Rs 2,593 crore in FY26, up 52%, per the Paytm Q4 FY26 earnings summary; to be re-checked).
- Languages other than Tamil. The design allows more later.
- WhatsApp and SMS messaging (log lines only).

**Success looks like.**
- The golden path runs end to end in front of the judges, with the backup recording ready.
- The escalation and the audit trail are shown working.
- A judge can ask "what is real and what is mocked" and get a straight answer.

## Who it's for

**Primary user: the small merchant.** A Tamil-speaking shopkeeper or stall owner in Chennai (the demo persona is a tea stall in T. Nagar) who repays a loan from daily UPI settlements. They need to hear any change to their repayment in plain spoken Tamil, and they need room to breathe in a bad week before a miss, not a penalty after one.

**The customer: Paytm and its lending partners.** We believe they carry the credit-loss and guarantee cost when merchant loans go bad (to be sourced). Keel gives them earlier warning and fewer collection calls, and lets staff focus on the cases that need a person.

**The human teammates: collections and support staff.** They receive the escalated cases, each with a call summary and the audit trail, so they don't start from scratch.

**Reviewers: compliance and audit.** They need to replay any case and see that consent, calling hours and limits were respected.

**The immediate audience: the hackathon judges.** They are looking for a working prototype, quantified impact, a clear benefit to Paytm, and guardrails. The deck follows the seven required sections (Title, Problem, Solution, Tech stack, USP, Impact and benefits, Business model).

### Terms used in this document

- **Settlement:** the daily sales money paid into the merchant's account.
- **Policy engine:** the in-process code that every action and every spoken sentence passes through. It enforces the lender's limits.
- **Lender envelope:** the lender-set limits the engine enforces (stress rule, lowest daily amount, longest relief, calling window, consent required).
- **Key Fact Statement:** the plain-language summary of a loan's cost and terms that a lender must give a borrower.
- **Cooling-off period:** a short window in which a borrower can cancel a new loan.
- **E-mandate:** the borrower's electronic authorisation for automatic repayment deductions.
- **Calling window:** the hours calls are allowed. The demo default is 08:00 to 19:00, which matches the reported RBI recovery-call limit; the effective date is disputed across sources, so verify against the RBI text.
- **Paytm sandbox and Payment MCP server:** Paytm's developer test environment and its tool server for payments. Their availability on the day is unconfirmed.
