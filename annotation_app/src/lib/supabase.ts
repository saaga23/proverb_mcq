import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Database = {
  public: {
    Tables: {
      pg_annotation_items: {
        Row: {
          id: string
          validation_id: string
          language: string
          proverb: string
          option_a: string
          option_b: string
          option_c: string
          option_d: string
          correct_label: string
          gold_meaning: string
          is_attention_check: boolean
          item_metadata: Record<string, unknown>
          created_at: string
        }
        Insert: {
          id?: string
          validation_id: string
          language: string
          proverb: string
          option_a: string
          option_b: string
          option_c: string
          option_d: string
          correct_label: string
          gold_meaning?: string
          is_attention_check?: boolean
          item_metadata?: Record<string, unknown>
          created_at?: string
        }
        Update: {
          id?: string
          validation_id?: string
          language?: string
          proverb?: string
          option_a?: string
          option_b?: string
          option_c?: string
          option_d?: string
          correct_label?: string
          gold_meaning?: string
          is_attention_check?: boolean
          item_metadata?: Record<string, unknown>
          created_at?: string
        }
      }
      pg_annotator_profiles: {
        Row: {
          annotator_id: string
          nickname: string
          language_expertise: string
          is_native_speaker: string
          age_group: string
          education_level: string
          country: string
          device_info: string
          created_at: string
        }
        Insert: {
          annotator_id: string
          nickname: string
          language_expertise: string
          is_native_speaker: string
          age_group?: string
          education_level?: string
          country?: string
          device_info?: string
          created_at?: string
        }
        Update: {
          annotator_id?: string
          nickname?: string
          language_expertise?: string
          is_native_speaker?: string
          age_group?: string
          education_level?: string
          country?: string
          device_info?: string
          created_at?: string
        }
      }
      pg_annotations: {
        Row: {
          id: string
          item_id: string
          annotator_id: string
          selected_answer: string
          correctness: string
          confidence: string
          time_taken_ms: number
          is_attention_check: boolean
          attention_passed: boolean
          annotator_notes: string
          created_at: string
        }
        Insert: {
          id?: string
          item_id: string
          annotator_id: string
          selected_answer: string
          correctness: string
          confidence: string
          time_taken_ms: number
          is_attention_check?: boolean
          attention_passed?: boolean
          annotator_notes?: string
          created_at?: string
        }
        Update: {
          id?: string
          item_id?: string
          annotator_id?: string
          selected_answer?: string
          correctness?: string
          confidence?: string
          time_taken_ms?: number
          is_attention_check?: boolean
          attention_passed?: boolean
          annotator_notes?: string
          created_at?: string
        }
      }
    }
  }
}
