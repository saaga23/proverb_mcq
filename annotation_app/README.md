# ProverbGap Human Annotation App

A Next.js annotation interface for evaluating proverb understanding across Arabic, English, and Yoruba.

## Stack

- **Framework**: Next.js 16 (App Router) + React 19
- **Styling**: Tailwind CSS v4
- **Backend**: Supabase (Postgres + RLS + RPC)
- **Icons**: Lucide React

## Features

- Anonymous annotator identity via `localStorage`
- Batch-based annotation (10 items per batch)
- Two-part judgment: correctness + confidence
- **Per-option plausibility ratings** (1–5 scale)
- **Shortcut flag detection** (same structure, length outlier, semantic echo, generic idiom, cultural mismatch)
- Option randomization per item (blind presentation)
- Attention checks embedded in batches
- Minimum time guard (10 seconds) to prevent rushing
- Training/practice item with feedback before real annotation
- Consent flow on landing page
- Atomic fetch-and-lock via Supabase RPC (`FOR UPDATE SKIP LOCKED`)
- Hidden gold answers (never exposed to browser)
- Time tracking per item
- Optional annotator notes
- Progress tracking
- Admin dashboard (password-protected)
- RTL support for Arabic proverbs

## Setup

### 1. Prerequisites

- Node.js 22.x (matches Next.js 16 engine requirement)
- Supabase project

### 2. Install dependencies

```bash
npm install
```

### 3. Set up Supabase database

Create a Supabase project, then run the SQL in `supabase/schema.sql` in the Supabase SQL Editor.

Then run the SQL in `supabase/rpc.sql` to create the stored procedures.

### 4. Upload items

```bash
npm run upload-items
```

This reads `human_validation_sample_60.csv` and uploads it to Supabase.

### 5. Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the app.

## Database Schema

### `pg_annotation_items`
- `id` (PK), `validation_id`, `language`, `proverb`
- `option_a/b/c/d` - the 4 multiple choice options
- `correct_label` - the gold answer (hidden from browser)
- `gold_meaning` - the curated meaning (hidden from browser)
- `is_attention_check` - flag for attention check items
- `item_metadata` - JSONB with additional metadata
- `lock_expires_at` - concurrency lock timestamp

### `pg_annotator_profiles`
- `annotator_id` (PK) - anonymous ID from localStorage
- `nickname`, `language_expertise`, `is_native_speaker`
- `age_group`, `education_level`, `country`
- `device_info` - browser user agent
- `created_at`

### `pg_annotations`
- `id` (PK, UUID)
- `item_id` (FK to pg_annotation_items)
- `annotator_id` - anonymous annotator ID
- `selected_answer` - A/B/C/D
- `confidence` - high/medium/low
- `time_taken_ms` - time spent on item
- `is_attention_check` - whether this was an attention check
- `attention_passed` - whether attention check was passed
- `annotator_notes` - optional text notes
- `plausibility_ratings` - JSONB map of option letter to 1–5 plausibility score
- `shortcut_flags` - array of detected shortcut artifacts
- `created_at`
- **Unique constraint**: `(item_id, annotator_id)`

## Key Design Decisions

1. **No authentication**: Annotators get a random ID stored in localStorage. Zero friction, but no cross-device tracking.

2. **Supabase RPC for concurrency**: `pg_get_items` uses `FOR UPDATE SKIP LOCKED` to prevent two annotators from getting the same item. 30-minute lock auto-releases abandoned batches.

3. **Hidden gold answers**: The `correct_label` and `gold_meaning` columns are never returned to the browser. The RPC only returns the public columns needed for annotation.

4. **Batch-based flow**: Items are fetched in batches of 10. After completing a batch, annotators can continue with the next batch.

5. **Attention checks**: Every 10th item is an attention check with a clear instruction. Results are tracked separately.

6. **Client-side only DB writes**: No API routes, no server actions. RLS policies are the only security boundary.

## Scripts

- `npm run upload-items` - Upload items from CSV to Supabase
- `npm run export-annotations` - Export all annotations to CSV
- `npm run setup-db` - Initialize database schema

## Deployment

Deploy to Vercel:

```bash
vercel
```

Make sure to set the following environment variables in Vercel:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `DATABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## License

MIT
