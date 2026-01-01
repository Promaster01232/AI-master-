-- Placeholder DB initialization script
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  filename TEXT,
  filepath TEXT,
  filetype TEXT,
  size INTEGER,
  uploaded_at TEXT,
  processed INTEGER DEFAULT 0,
  chunks_count INTEGER DEFAULT 0,
  processed_at TEXT,
  processing_error TEXT
);

CREATE TABLE IF NOT EXISTS document_chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT,
  content TEXT,
  chunk_index INTEGER,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  conversation_id TEXT,
  role TEXT,
  message TEXT,
  model_used TEXT,
  tokens_used INTEGER DEFAULT 0,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS chat_context (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT,
  document_id TEXT,
  chunk_id TEXT,
  relevance_score REAL
);
