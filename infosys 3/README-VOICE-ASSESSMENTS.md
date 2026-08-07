Voice Assessments (React frontend + Node/Express backend)

Backend (C:\\...\\project540\\backend)
- Exposes POST /api/assessments to accept multipart/form-data with field 'audio' (file) and optional fields: userId, promptId, expected
- Saves uploaded audio to backend/uploads
- Sends audio to OpenAI Whisper API for transcription (model: whisper-1)
- Stores assessment records in a local SQLite DB at backend/migrations/assessments.db
- Scoring: if an `expected` string is provided, a simple Levenshtein similarity score (0..1) is returned. Optionally an LLM-based rubric can be added for pronunciation/fluency ratings.
- Multilingual: generation and transcription support a language parameter. Frontend includes a language selector; Whisper receives a language hint to improve transcription accuracy.

Setup
1. Copy backend/.env.example to backend/.env and set OPENAI_API_KEY
2. From the project root run:
   cd backend
   npm install
   npm start
3. Endpoint: POST http://localhost:4000/api/assessments
   Example using fetch multipart/form-data:
   
   Additional endpoint: POST http://localhost:4000/api/assessments/generate
   - Accepts JSON { age, level } and returns a generated spoken prompt and an expected answer (useful to pre-fill assessments).
   
   Example using fetch multipart/form-data:
     form.append('audio', fileBlob, 'answer.wav');
     form.append('userId', 'user-123');
     form.append('promptId', 'prompt-1');
     form.append('expected', 'The expected answer here');

Frontend
- A React component example (frontend/RecordAssessment.jsx) is included. Drop it into an existing React app and point requests to the backend (modify URL if needed).

Notes
- Ensure OPENAI_API_KEY is set. Transcription costs apply per OpenAI pricing.
- This is a minimal implementation intended for local testing. For production consider:
  - Uploads to S3 instead of local disk
  - Authentication and authorization
  - Rate limiting and file size limits
  - More advanced scoring (embeddings, pronunciation analysis, grammar checks)
