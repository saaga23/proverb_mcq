'use client'

import { useState } from 'react'
import { supabase } from '@/lib/supabase'
import { CheckCircle, Loader2, AlertCircle } from 'lucide-react'

type FormData = {
  nickname: string
  language_expertise: string
  is_native_speaker: string
  age_group: string
  education_level: string
  country: string
}

export default function Home() {
  const [annotatorId] = useState<string | null>(() => {
    if (typeof window === 'undefined') return null
    let id = localStorage.getItem('pg_annotator_id')
    if (!id) {
      id = 'rater_' + Math.random().toString(36).substring(2, 15) + '_' + Date.now().toString(36)
      localStorage.setItem('pg_annotator_id', id)
    }
    return id
  })
  const [form, setForm] = useState<FormData>({
    nickname: '',
    language_expertise: '',
    is_native_speaker: '',
    age_group: '',
    education_level: '',
    country: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [consentGiven, setConsentGiven] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!annotatorId) return

    setLoading(true)
    setError(null)

    try {
      const deviceInfo = navigator.userAgent

      const { error: insertError } = await supabase
        .from('pg_annotator_profiles')
        .insert({
          annotator_id: annotatorId,
          nickname: form.nickname || `Annotator ${annotatorId.slice(-6)}`,
          language_expertise: form.language_expertise,
          is_native_speaker: form.is_native_speaker,
          age_group: form.age_group || 'prefer_not_to_say',
          education_level: form.education_level || 'prefer_not_to_say',
          country: form.country || 'prefer_not_to_say',
          device_info: deviceInfo,
        })

      if (insertError) {
        // If duplicate, that's okay - they already have a profile
        if (insertError.code !== '23505') {
          throw insertError
        }
      }

      setSuccess(true)
      setTimeout(() => {
        window.location.href = '/annotate'
      }, 1500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof FormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }))
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Welcome!</h2>
          <p className="text-slate-600">Redirecting to annotation...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">ProverbGap Annotation</h1>
          <p className="text-lg text-slate-600">Help us evaluate proverb understanding across languages</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Language expertise */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Which language(s) are you expert in? *
              </label>
              <select
                value={form.language_expertise}
                onChange={handleChange('language_expertise')}
                required
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select language...</option>
                <option value="Arabic">Arabic</option>
                <option value="English">English</option>
                <option value="Yoruba">Yoruba</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Native speaker */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Are you a native speaker of this language? *
              </label>
              <div className="flex gap-4">
                {['yes', 'no'].map((option) => (
                  <label key={option} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      value={option}
                      checked={form.is_native_speaker === option}
                      onChange={handleChange('is_native_speaker')}
                      required
                      className="w-4 h-4 text-indigo-600"
                    />
                    <span className="text-slate-700 capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Nickname */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Nickname (optional)
              </label>
              <input
                type="text"
                value={form.nickname}
                onChange={handleChange('nickname')}
                placeholder="How should we call you?"
                maxLength={50}
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Age group */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Age group (optional)
              </label>
              <select
                value={form.age_group}
                onChange={handleChange('age_group')}
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select age group...</option>
                <option value="18-24">18-24</option>
                <option value="25-34">25-34</option>
                <option value="35-44">35-44</option>
                <option value="45-54">45-54</option>
                <option value="55+">55+</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>

            {/* Education level */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Education level (optional)
              </label>
              <select
                value={form.education_level}
                onChange={handleChange('education_level')}
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select education level...</option>
                <option value="high_school">High School</option>
                <option value="bachelors">Bachelor&apos;s Degree</option>
                <option value="masters">Master&apos;s Degree</option>
                <option value="phd">PhD</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Country (optional)
              </label>
              <input
                type="text"
                value={form.country}
                onChange={handleChange('country')}
                placeholder="Your country"
                className="w-full p-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Error message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Consent */}
            <div className="bg-slate-50 rounded-lg p-4 mb-6">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={consentGiven}
                  onChange={(e) => setConsentGiven(e.target.checked)}
                  className="mt-1 w-4 h-4 text-indigo-600 rounded border-slate-300"
                />
                <span className="text-sm text-slate-700">
                  I have read the{' '}
                  <a
                    href="https://github.com/saaga23/proverb_mcq/blob/main/annotation/protocol.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 underline hover:text-indigo-800"
                  >
                    annotation protocol
                  </a>{' '}
                  and consent to participate in this research study. *
                </span>
              </label>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading || !form.language_expertise || !form.is_native_speaker || !consentGiven}
              className={`w-full py-3 px-6 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
                loading || !form.language_expertise || !form.is_native_speaker
                  ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                'Start Annotating'
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-slate-500 mt-6">
          Your responses are anonymous and used for research purposes only.
        </p>
      </div>
    </div>
  )
}
