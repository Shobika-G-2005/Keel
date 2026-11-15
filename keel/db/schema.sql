-- Keel schema. Amounts are integer rupees. Dates are ISO text.

CREATE TABLE IF NOT EXISTS merchant (
  merchant_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  trade TEXT NOT NULL,
  city TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'ta',
  phone TEXT NOT NULL,
  normal_daily_settlement_rupees INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS loan (
  loan_id TEXT PRIMARY KEY,
  merchant_id TEXT NOT NULL REFERENCES merchant(merchant_id),
  principal_rupees INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','relief','closed'))
);

CREATE TABLE IF NOT EXISTS settlement_day (
  loan_id TEXT NOT NULL REFERENCES loan(loan_id),
  merchant_id TEXT NOT NULL,
  date TEXT NOT NULL,
  settlement_rupees INTEGER NOT NULL,
  PRIMARY KEY (loan_id, date)
);

CREATE TABLE IF NOT EXISTS ledger_entry (
  entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
  loan_id TEXT NOT NULL REFERENCES loan(loan_id),
  date TEXT NOT NULL,
  amount_rupees INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('scheduled','upi_link','adjustment'))
);

CREATE TABLE IF NOT EXISTS stress_signal (
  signal_id TEXT PRIMARY KEY,
  loan_id TEXT NOT NULL REFERENCES loan(loan_id),
  detected_on TEXT NOT NULL,
  low_days TEXT NOT NULL,                      -- JSON: [{date, pct_tenths}]
  normal_daily_settlement_rupees INTEGER NOT NULL,
  envelope_id TEXT NOT NULL,
  UNIQUE (loan_id, detected_on)
);

CREATE TABLE IF NOT EXISTS call (
  call_id TEXT PRIMARY KEY,
  merchant_id TEXT NOT NULL,
  loan_id TEXT NOT NULL,
  signal_id TEXT,
  started_at TEXT NOT NULL,
  language TEXT NOT NULL,
  identity_verified INTEGER NOT NULL DEFAULT 0,
  outcome TEXT CHECK (outcome IN ('resolved','declined','escalated','no_answer','identity_failed')),
  autonomous INTEGER NOT NULL DEFAULT 0,
  escalation_reason TEXT CHECK (escalation_reason IN ('DISTRESS','DISPUTE','OUT_OF_ENVELOPE','LOW_CONFIDENCE','POLICY_BLOCK')),
  handover_summary TEXT
);

CREATE TABLE IF NOT EXISTS offer (
  offer_id TEXT PRIMARY KEY,
  signal_id TEXT NOT NULL REFERENCES stress_signal(signal_id),
  call_id TEXT NOT NULL REFERENCES call(call_id),
  envelope_id TEXT NOT NULL,
  current_daily_amount_rupees INTEGER NOT NULL,
  new_daily_amount_rupees INTEGER NOT NULL,
  relief_days INTEGER NOT NULL,
  deferred_rupees INTEGER NOT NULL,
  extension_days INTEGER NOT NULL,
  old_end_date TEXT NOT NULL,
  new_end_date TEXT NOT NULL,
  starts_on TEXT NOT NULL,
  within_envelope INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed','accepted','declined','escalated'))
);

CREATE TABLE IF NOT EXISTS consent (
  consent_id TEXT PRIMARY KEY,
  merchant_id TEXT NOT NULL,
  offer_id TEXT NOT NULL UNIQUE REFERENCES offer(offer_id),
  text_hash TEXT NOT NULL,
  granted_at TEXT NOT NULL,
  revoked_at TEXT,
  transcript_span TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule_version (
  loan_id TEXT NOT NULL REFERENCES loan(loan_id),
  version INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('original','relief','resume')),
  daily_amount_rupees INTEGER NOT NULL,
  starts_on TEXT NOT NULL,
  ends_on TEXT,
  offer_id TEXT UNIQUE REFERENCES offer(offer_id),   -- set on the relief row only; blocks a double apply
  created_by TEXT NOT NULL,
  PRIMARY KEY (loan_id, version)
);

CREATE TABLE IF NOT EXISTS handover_case (
  case_id TEXT PRIMARY KEY,
  call_id TEXT NOT NULL REFERENCES call(call_id),
  loan_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  summary TEXT NOT NULL,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS audit_event (
  seq INTEGER PRIMARY KEY,
  timestamp TEXT NOT NULL,
  call_id TEXT,
  loan_id TEXT NOT NULL,
  merchant_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  inputs TEXT NOT NULL,
  result TEXT NOT NULL,
  rule_id TEXT,
  prev_hash TEXT NOT NULL,
  hash TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_event
BEGIN SELECT RAISE(ABORT, 'audit_event is append-only'); END;

CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_event
BEGIN SELECT RAISE(ABORT, 'audit_event is append-only'); END;
