-- ProverbGap Annotation RPCs
-- Run these AFTER schema.sql in Supabase SQL Editor

-- Get next batch of items for annotation
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
    SELECT i.id AS item_id
    FROM public.pg_annotation_items i
    WHERE i.is_attention_check = false
      AND (i.lock_expires_at IS NULL OR i.lock_expires_at < now())
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
  WHERE i.id IN (SELECT item_id FROM selected)
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

-- Mark items as complete (release lock)
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

-- Get annotator progress
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
    (SELECT count(*)::integer FROM public.pg_annotation_items WHERE is_attention_check = false),
    (SELECT count(*)::integer FROM public.pg_annotations WHERE annotator_id = p_annotator_id AND is_attention_check = false),
    (SELECT count(*)::integer FROM public.pg_annotation_items WHERE is_attention_check = false) - (SELECT count(*)::integer FROM public.pg_annotations WHERE annotator_id = p_annotator_id AND is_attention_check = false),
    EXISTS (
      SELECT 1 FROM public.pg_annotations
      WHERE annotator_id = p_annotator_id AND is_attention_check = true AND pg_annotations.attention_passed = true
    );
  END;
$$;

-- Check if an attention check answer is correct without exposing the gold answer
CREATE OR REPLACE FUNCTION public.pg_check_attention(
  p_item_id TEXT,
  p_selected_answer TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.pg_annotation_items
    WHERE id = p_item_id
      AND is_attention_check = true
      AND correct_label = p_selected_answer
  );
END;
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.pg_get_items(TEXT, INTEGER) TO anon;
GRANT EXECUTE ON FUNCTION public.pg_mark_complete(TEXT[]) TO anon;
GRANT EXECUTE ON FUNCTION public.pg_get_progress(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION public.pg_check_attention(TEXT, TEXT) TO anon;
