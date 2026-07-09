-- ProverbGap Human Annotation Schema
-- Run this in Supabase SQL Editor

-- Items table: holds the 60 MCQs for human annotation
CREATE TABLE IF NOT EXISTS public.pg_annotation_items (
  id TEXT PRIMARY KEY,
  validation_id TEXT NOT NULL,
  language TEXT NOT NULL,
  proverb TEXT NOT NULL,
  option_a TEXT NOT NULL,
  option_b TEXT NOT NULL,
  option_c TEXT NOT NULL,
  option_d TEXT NOT NULL,
  correct_label TEXT NOT NULL,
  gold_meaning TEXT NOT NULL,
  is_attention_check BOOLEAN DEFAULT false,
  item_metadata JSONB DEFAULT '{}'::jsonb,
  lock_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Annotator profiles: demographics
CREATE TABLE IF NOT EXISTS public.pg_annotator_profiles (
  annotator_id TEXT PRIMARY KEY,
  nickname TEXT,
  language_expertise TEXT NOT NULL,
  is_native_speaker TEXT NOT NULL,
  age_group TEXT,
  education_level TEXT,
  country TEXT,
  device_info TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Annotations: one row per item per annotator
CREATE TABLE IF NOT EXISTS public.pg_annotations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id TEXT NOT NULL REFERENCES public.pg_annotation_items(id) ON DELETE CASCADE,
  annotator_id TEXT NOT NULL,
  selected_answer TEXT NOT NULL,
  correctness TEXT NOT NULL,
  confidence TEXT NOT NULL,
  time_taken_ms INTEGER NOT NULL,
  is_attention_check BOOLEAN DEFAULT false,
  attention_passed BOOLEAN,
  annotator_notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(item_id, annotator_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pg_annotations_annotator ON public.pg_annotations(annotator_id);
CREATE INDEX IF NOT EXISTS idx_pg_annotations_item ON public.pg_annotations(item_id);
CREATE INDEX IF NOT EXISTS idx_pg_items_language ON public.pg_annotation_items(language);

-- RLS Policies
ALTER TABLE public.pg_annotation_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pg_annotator_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pg_annotations ENABLE ROW LEVEL SECURITY;

-- Items: anon can only fetch via RPC (hidden gold_answer, model_provenance)
DROP POLICY IF EXISTS "anon_no_direct_select_items" ON public.pg_annotation_items;
CREATE POLICY "anon_no_direct_select_items" ON public.pg_annotation_items
  FOR SELECT TO anon USING (false);

DROP POLICY IF EXISTS "anon_no_insert_items" ON public.pg_annotation_items;
CREATE POLICY "anon_no_insert_items" ON public.pg_annotation_items
  FOR INSERT TO anon WITH CHECK (false);

DROP POLICY IF EXISTS "anon_no_update_items" ON public.pg_annotation_items;
CREATE POLICY "anon_no_update_items" ON public.pg_annotation_items
  FOR UPDATE TO anon USING (false);

-- Profiles: anon can insert their own profile
DROP POLICY IF EXISTS "anon_insert_own_profile" ON public.pg_annotator_profiles;
CREATE POLICY "anon_insert_own_profile" ON public.pg_annotator_profiles
  FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "anon_no_select_profiles" ON public.pg_annotator_profiles;
CREATE POLICY "anon_no_select_profiles" ON public.pg_annotator_profiles
  FOR SELECT TO anon USING (false);

-- Annotations: anon can insert their own annotations
DROP POLICY IF EXISTS "anon_insert_own_annotations" ON public.pg_annotations;
CREATE POLICY "anon_insert_own_annotations" ON public.pg_annotations
  FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "anon_no_select_annotations" ON public.pg_annotations;
CREATE POLICY "anon_no_select_annotations" ON public.pg_annotations
  FOR SELECT TO anon USING (false);

-- Service role bypasses RLS
DROP POLICY IF EXISTS "service_role_all_items" ON public.pg_annotation_items;
CREATE POLICY "service_role_all_items" ON public.pg_annotation_items
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_profiles" ON public.pg_annotator_profiles;
CREATE POLICY "service_role_all_profiles" ON public.pg_annotator_profiles
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_annotations" ON public.pg_annotations;
CREATE POLICY "service_role_all_annotations" ON public.pg_annotations
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- RPC: Get next batch of items for annotation
CREATE OR REPLACE FUNCTION public.pg_get_items(
  p_annotator_id TEXT,
  p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
  id TEXT,
  validation_id TEXT,
  language TEXT,
  proverb TEXT,
  option_a TEXT,
  option_b TEXT,
  option_c TEXT,
  option_d TEXT,
  is_attention_check BOOLEAN,
  item_metadata JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  WITH selected AS (
    SELECT i.id
    FROM public.pg_annotation_items i
    WHERE (i.lock_expires_at IS NULL OR i.lock_expires_at < now())
      AND NOT EXISTS (
        SELECT 1 FROM public.pg_annotations a
        WHERE a.item_id = i.id AND a.annotator_id = p_annotator_id
      )
    ORDER BY random()
    LIMIT p_limit
    FOR UPDATE SKIP LOCKED
  )
  UPDATE public.pg_annotation_items i
  SET lock_expires_at = now() + interval '30 minutes'
  WHERE i.id IN (SELECT id FROM selected)
  RETURNING
    i.id,
    i.validation_id,
    i.language,
    i.proverb,
    i.option_a,
    i.option_b,
    i.option_c,
    i.option_d,
    i.is_attention_check,
    i.item_metadata;
END;
$$;

-- RPC: Mark items as complete
CREATE OR REPLACE FUNCTION public.pg_mark_complete(
  p_item_ids TEXT[]
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  UPDATE public.pg_annotation_items
  SET lock_expires_at = NULL
  WHERE id = ANY(p_item_ids);
END;
$$;

-- RPC: Get annotator progress
CREATE OR REPLACE FUNCTION public.pg_get_progress(
  p_annotator_id TEXT
)
RETURNS TABLE (
  total_items INTEGER,
  completed_items INTEGER,
  remaining_items INTEGER,
  attention_passed BOOLEAN
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN QUERY
  SELECT
    (SELECT count(*) FROM public.pg_annotation_items WHERE is_attention_check = false),
    (SELECT count(*) FROM public.pg_annotations WHERE annotator_id = p_annotator_id AND is_attention_check = false),
    (SELECT count(*) FROM public.pg_annotation_items WHERE is_attention_check = false) - (SELECT count(*) FROM public.pg_annotations WHERE annotator_id = p_annotator_id AND is_attention_check = false),
    EXISTS (
      SELECT 1 FROM public.pg_annotations
      WHERE annotator_id = p_annotator_id AND is_attention_check = true AND attention_passed = true
    );
END;
$$;
