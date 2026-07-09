'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { Download, Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function AdminPage() {
  const [annotations, setAnnotations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    fetchAnnotations()
  }, [])

  const fetchAnnotations = async () => {
    const { data, error } = await supabase
      .from('pg_annotations')
      .select(`
        *,
        item:pg_annotation_items (
          validation_id, language, proverb, option_a, option_b, option_c, option_d, correct_label
        )
      `)
      .order('created_at', { ascending: false })
      .limit(100)

    if (error) {
      console.error('Error:', error)
    } else {
      setAnnotations(data || [])
    }
    setLoading(false)
  }

  const exportCsv = async () => {
    setExporting(true)
    try {
      const { data, error } = await supabase
        .from('pg_annotations')
        .select(`
          *,
          item:pg_annotation_items (
            validation_id, language, proverb, option_a, option_b, option_c, option_d, correct_label
          )
        `)
        .order('created_at', { ascending: true })

      if (error || !data) {
        console.error('Export error:', error)
        return
      }

      const headers = [
        'annotation_id', 'item_id', 'validation_id', 'language', 'proverb',
        'option_a', 'option_b', 'option_c', 'option_d', 'correct_label',
        'selected_answer', 'correctness', 'confidence', 'time_taken_ms',
        'is_attention_check', 'attention_passed', 'annotator_notes',
        'annotator_id', 'created_at'
      ]

      const rows = data.map(a => [
        a.id,
        a.item_id,
        a.item?.validation_id || '',
        a.item?.language || '',
        `"${(a.item?.proverb || '').replace(/"/g, '""')}"`,
        `"${(a.item?.option_a || '').replace(/"/g, '""')}"`,
        `"${(a.item?.option_b || '').replace(/"/g, '""')}"`,
        `"${(a.item?.option_c || '').replace(/"/g, '""')}"`,
        `"${(a.item?.option_d || '').replace(/"/g, '""')}"`,
        a.item?.correct_label || '',
        a.selected_answer,
        a.correctness,
        a.confidence,
        a.time_taken_ms,
        a.is_attention_check,
        a.attention_passed,
        `"${(a.annotator_notes || '').replace(/"/g, '""')}"`,
        a.annotator_id,
        a.created_at,
      ])

      const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `annotations_export_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Export error:', err)
    } finally {
      setExporting(false)
    }
  }

  const getCorrectnessColor = (correctness: string) => {
    switch (correctness) {
      case 'correct': return 'text-green-600 bg-green-50'
      case 'incorrect': return 'text-red-600 bg-red-50'
      case 'unsure': return 'text-yellow-600 bg-yellow-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 sm:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Annotation Admin</h1>
            <p className="text-slate-600 mt-1">Monitor and export annotation data</p>
          </div>
          <button
            onClick={exportCsv}
            disabled={exporting || annotations.length === 0}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              exporting || annotations.length === 0
                ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            {exporting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Download className="w-5 h-5" />
            )}
            Export CSV
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          </div>
        ) : annotations.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <p className="text-slate-600 text-lg">No annotations yet.</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">ID</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Validation</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Language</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Answer</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Correctness</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Confidence</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Time</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700">Annotator</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {annotations.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 text-sm text-slate-600 font-mono">
                        {a.id.slice(0, 8)}...
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-900">
                        {a.item?.validation_id || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">
                        {a.item?.language || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className="font-semibold text-slate-900">{a.selected_answer}</span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCorrectnessColor(a.correctness)}`}>
                          {a.correctness}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">
                        {a.confidence}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">
                        {(a.time_taken_ms / 1000).toFixed(1)}s
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600 font-mono">
                        {a.annotator_id.slice(0, 12)}...
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
