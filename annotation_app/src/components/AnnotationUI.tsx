'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { supabase } from '@/lib/supabase'
import { CheckCircle, Loader2, AlertCircle, RotateCcw, Target, Gauge, Eye, EyeOff } from 'lucide-react'

type Item = {
  id: string
  validation_id: string
  language: string
  proverb: string
  option_a: string
  option_b: string
  option_c: string
  option_d: string
  is_attention_check: boolean
  item_metadata: Record<string, any>
}

type AnnotationResult = {
  success: boolean
  message: string
  batchComplete?: boolean
  progress?: {
    total: number
    completed: number
    remaining: number
  }
}

const BATCH_SIZE = 10
const MIN_TIME_MS = 3000

export function AnnotationUI() {
  const [annotatorId, setAnnotatorId] = useState<string | null>(null)
  const [items, setItems] = useState<Item[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [correctness, setCorrectness] = useState<string | null>(null)
  const [confidence, setConfidence] = useState<string | null>(null)
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnnotationResult | null>(null)
  const [startTime, setStartTime] = useState<number>(Date.now())
  const [showAttentionBanner, setShowAttentionBanner] = useState(false)
  const [attentionWarning, setAttentionWarning] = useState(false)

  const currentItem = items[currentIndex]
  const isLastItem = currentIndex === items.length - 1
  const timeTaken = Date.now() - startTime

  // Initialize annotator ID
  useEffect(() => {
    let id = localStorage.getItem('pg_annotator_id')
    if (!id) {
      id = 'rater_' + Math.random().toString(36).substring(2, 15) + '_' + Date.now().toString(36)
      localStorage.setItem('pg_annotator_id', id)
    }
    setAnnotatorId(id)
  }, [])

  // Load first batch
  useEffect(() => {
    if (!annotatorId) return
    loadBatch(annotatorId)
  }, [annotatorId])

  const loadBatch = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const { data, error: rpcError } = await supabase.rpc('pg_get_items', {
        p_annotator_id: id,
        p_limit: BATCH_SIZE,
      })

      if (rpcError) throw rpcError

      if (!data || data.length === 0) {
        setResult({
          success: true,
          message: 'All items completed! Thank you for your contribution.',
          batchComplete: true,
          progress: { total: 0, completed: 0, remaining: 0 },
        })
        setLoading(false)
        return
      }

      setItems(data as Item[])
      setCurrentIndex(0)
      setSelectedAnswer(null)
      setCorrectness(null)
      setConfidence(null)
      setNotes('')
      setStartTime(Date.now())
      setShowAttentionBanner(data[0]?.is_attention_check || false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load items')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleSubmit = async () => {
    if (!annotatorId || !currentItem || !selectedAnswer || !correctness || !confidence) return
    if (submitting) return

    // Minimum time guard
    if (timeTaken < MIN_TIME_MS) {
      setAttentionWarning(true)
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      const isAttention = currentItem.is_attention_check
      const attentionPassed = isAttention ? correctness === 'correct' : null

      const { error: insertError } = await supabase.from('pg_annotations').insert({
        item_id: currentItem.id,
        annotator_id: annotatorId,
        selected_answer: selectedAnswer,
        correctness,
        confidence,
        time_taken_ms: timeTaken,
        is_attention_check: isAttention,
        attention_passed: attentionPassed,
        annotator_notes: notes.trim() || null,
      })

      if (insertError) throw insertError

      // Mark item as complete
      await supabase.rpc('pg_mark_complete', { p_item_ids: [currentItem.id] })

      // Move to next item or complete batch
      if (isLastItem) {
        // Get progress
        const { data: progress } = await supabase.rpc('pg_get_progress', {
          p_annotator_id: annotatorId,
        })

        setResult({
          success: true,
          message: 'Batch completed! Ready for more?',
          batchComplete: true,
          progress: progress?.[0] || { total: 0, completed: 0, remaining: 0 },
        })
        setItems([])
      } else {
        const nextIndex = currentIndex + 1
        setCurrentIndex(nextIndex)
        setSelectedAnswer(null)
        setCorrectness(null)
        setConfidence(null)
        setNotes('')
        setStartTime(Date.now())
        setShowAttentionBanner(items[nextIndex]?.is_attention_check || false)
        setAttentionWarning(false)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit annotation')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNextBatch = () => {
    if (!annotatorId) return
    setResult(null)
    loadBatch(annotatorId)
  }

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <Loader2 className="w-12 h-12 animate-spin text-indigo-600" />
        <p className="text-slate-600 text-lg">Loading annotation items...</p>
      </div>
    )
  }

  // Completion state
  if (result?.batchComplete || (!loading && items.length === 0 && !error)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Batch Complete!</h2>
          <p className="text-slate-600 mb-6">{result?.message || 'Thank you for your annotations.'}</p>
          {result?.progress && (
            <div className="bg-slate-50 rounded-lg p-4 mb-6 text-left">
              <p className="text-sm text-slate-600">Progress: {result.progress.completed} / {result.progress.total} items</p>
              <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all"
                  style={{ width: `${(result.progress.completed / result.progress.total) * 100}%` }}
                />
              </div>
            </div>
          )}
          <button
            onClick={handleNextBatch}
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
          >
            Continue Annotating
          </button>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Error</h2>
          <p className="text-slate-600 mb-6">{error}</p>
          <button
            onClick={() => annotatorId && loadBatch(annotatorId)}
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!currentItem) return null

  const options = [
    { key: 'A', text: currentItem.option_a },
    { key: 'B', text: currentItem.option_b },
    { key: 'C', text: currentItem.option_c },
    { key: 'D', text: currentItem.option_d },
  ]

  const canSubmit = selectedAnswer && correctness && confidence && !submitting

  return (
    <div className="max-w-3xl mx-auto p-4 sm:p-6">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-slate-600 mb-2">
          <span>Item {currentIndex + 1} of {items.length}</span>
          <span>{Math.round(((currentIndex) / items.length) * 100)}%</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div
            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentIndex / items.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Attention check banner */}
      {showAttentionBanner && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
          <Target className="w-5 h-5 text-amber-600 mt-0.5" />
          <div>
            <p className="font-semibold text-amber-800">Attention Check</p>
            <p className="text-sm text-amber-700">Please read this item carefully and answer correctly.</p>
          </div>
        </div>
      )}

      {/* Time warning */}
      {attentionWarning && (
        <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <p className="font-semibold text-yellow-800">Please take your time</p>
            <p className="text-sm text-yellow-700">Please read the proverb and options carefully before submitting.</p>
            <button
              onClick={() => setAttentionWarning(false)}
              className="mt-2 text-sm text-yellow-600 underline"
            >
              I understand, submit anyway
            </button>
          </div>
        </div>
      )}

      {/* Main annotation card */}
      <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
        {/* Language badge */}
        <div className="flex items-center gap-2 mb-4">
          <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
            {currentItem.language}
          </span>
          {currentItem.is_attention_check && (
            <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium flex items-center gap-1">
              <Eye className="w-3 h-3" /> Attention Check
            </span>
          )}
        </div>

        {/* Proverb */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-slate-700 mb-3">Proverb:</h2>
          <div className="bg-slate-50 rounded-lg p-4 sm:p-6">
            <p className="text-xl sm:text-2xl font-medium text-slate-900 leading-relaxed">
              {currentItem.proverb}
            </p>
          </div>
        </div>

        {/* Options */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-slate-700 mb-3">Select the correct meaning:</h2>
          <div className="space-y-3">
            {options.map((option) => (
              <button
                key={option.key}
                onClick={() => setSelectedAnswer(option.key)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedAnswer === option.key
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-slate-200 hover:border-indigo-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    selectedAnswer === option.key
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-600'
                  }`}>
                    {option.key}
                  </span>
                  <p className="text-slate-800 leading-relaxed pt-1">{option.text}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Correctness judgment */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-slate-700 mb-3">Is this the correct meaning?</h2>
          <div className="flex flex-wrap gap-3">
            {[
              { value: 'correct', label: 'Correct', color: 'green' },
              { value: 'incorrect', label: 'Incorrect', color: 'red' },
              { value: 'unsure', label: 'Unsure', color: 'yellow' },
              { value: 'cannot_answer', label: 'Cannot Answer', color: 'gray' },
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setCorrectness(option.value)}
                className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                  correctness === option.value
                    ? `border-${option.color}-500 bg-${option.color}-50 text-${option.color}-700`
                    : 'border-slate-200 hover:border-slate-300 text-slate-600'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Confidence judgment */}
        {correctness && correctness !== 'cannot_answer' && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-slate-700 mb-3">How confident are you?</h2>
            <div className="flex flex-wrap gap-3">
              {[
                { value: 'high', label: 'High confidence', desc: 'Very sure' },
                { value: 'medium', label: 'Medium confidence', desc: 'Somewhat sure' },
                { value: 'low', label: 'Low confidence', desc: 'Not very sure' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setConfidence(option.value)}
                  className={`px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                    confidence === option.value
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                      : 'border-slate-200 hover:border-indigo-300 text-slate-600'
                  }`}
                >
                  <div>{option.label}</div>
                  <div className="text-xs text-slate-500">{option.desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-slate-700 mb-3">Notes (optional)</h2>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any observations about this proverb or translation..."
            className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
            rows={3}
          />
        </div>

        {/* Submit button */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
              canSubmit
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-slate-300 text-slate-500 cursor-not-allowed'
            }`}
          >
            {submitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                {isLastItem ? 'Finish Batch' : 'Submit & Next'}
              </>
            )}
          </button>
          {!isLastItem && (
            <button
              onClick={() => {
                setSelectedAnswer(null)
                setCorrectness(null)
                setConfidence(null)
                setNotes('')
                setStartTime(Date.now())
              }}
              className="py-3 px-6 rounded-lg font-semibold border-2 border-slate-300 text-slate-600 hover:bg-slate-50 transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-5 h-5" />
              Reset
            </button>
          )}
        </div>

        {/* Time indicator */}
        <div className="mt-4 flex items-center justify-center gap-2 text-sm text-slate-500">
          <Gauge className="w-4 h-4" />
          <span>Time: {Math.floor(timeTaken / 1000)}s</span>
        </div>
      </div>
    </div>
  )
}
