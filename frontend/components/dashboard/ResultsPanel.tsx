'use client'

import { useState } from 'react'
import { FileText, ClipboardList, CheckSquare, Gavel, Download, ChevronDown, ChevronUp, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import api from '@/services/api'

export interface AnalysisResult {
  file_name: string
  language: string
  duration_seconds: number
  processing_time_seconds: number
  transcript: string
  summary: string
  key_points: string[]
  tasks: string[]
  decisions: string[]
}

interface ResultsPanelProps {
  result: AnalysisResult
  onReset: () => void
}

export function ResultsPanel({ result, onReset }: ResultsPanelProps) {
  const [expandedTranscript, setExpandedTranscript] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true)
    try {
      const response = await api.post(
        '/api/audio/export-pdf',
        result,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      const safeName = (result.file_name || 'voxia_reporte').replace(/\.[^/.]+$/, '')
      link.setAttribute('download', `${safeName}_reporte.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('PDF descargado correctamente')
    } catch {
      toast.error('Error al generar el PDF')
    } finally {
      setDownloadingPdf(false)
    }
  }

  const formatDuration = (secs: number) => {
    if (secs < 60) return `${Math.round(secs)}s`
    const m = Math.floor(secs / 60)
    const s = Math.round(secs % 60)
    return `${m}m ${s}s`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-4xl mx-auto space-y-4"
    >
      {/* Header de resultados */}
      <div className="bg-white/[0.04] border border-white/8 rounded-2xl p-5 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Análisis completado</h2>
          <div className="flex items-center gap-3 mt-1 text-xs text-white/40">
            <span>🎙 {result.file_name || 'Audio'}</span>
            <span>•</span>
            <span>⏱ {formatDuration(result.duration_seconds)} de audio</span>
            <span>•</span>
            <span>⚡ Procesado en {formatDuration(result.processing_time_seconds)}</span>
            <span>•</span>
            <span>🌐 {result.language === 'es' ? 'Español' : 'Inglés'}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-500/20 border border-violet-500/30 text-violet-300 text-sm font-medium hover:bg-violet-500/30 transition-colors disabled:opacity-50"
          >
            {downloadingPdf ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            Descargar PDF
          </motion.button>
          <button
            onClick={onReset}
            className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white/50 text-sm font-medium hover:bg-white/10 hover:text-white/70 transition-colors"
          >
            Nuevo análisis
          </button>
        </div>
      </div>

      {/* Resumen ejecutivo */}
      <Section
        icon={<FileText className="w-4 h-4 text-blue-400" />}
        iconBg="bg-blue-500/15"
        title="Resumen Ejecutivo"
        defaultOpen
      >
        <p className="text-white/70 text-sm leading-relaxed">{result.summary || 'Sin resumen disponible.'}</p>
      </Section>

      {/* Puntos clave */}
      {result.key_points?.length > 0 && (
        <Section
          icon={<ClipboardList className="w-4 h-4 text-indigo-400" />}
          iconBg="bg-indigo-500/15"
          title={`Puntos Clave (${result.key_points.length})`}
          defaultOpen
        >
          <ul className="space-y-2">
            {result.key_points.map((point, i) => (
              <li key={i} className="flex gap-3 text-sm text-white/70">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-500/20 flex items-center justify-center text-[10px] font-bold text-indigo-400 mt-0.5">
                  {i + 1}
                </span>
                <span className="leading-relaxed">{point}</span>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Tareas y compromisos */}
      <Section
        icon={<CheckSquare className="w-4 h-4 text-emerald-400" />}
        iconBg="bg-emerald-500/15"
        title={`Tareas y Compromisos (${result.tasks?.length || 0})`}
        defaultOpen
      >
        {result.tasks?.length > 0 ? (
          <ul className="space-y-2">
            {result.tasks.map((task, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="flex-shrink-0 w-4 h-4 rounded border border-emerald-500/40 bg-emerald-500/10 flex items-center justify-center mt-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                </span>
                <span className="text-white/70 leading-relaxed">{task}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-white/30 text-sm italic">No se identificaron tareas o compromisos explícitos.</p>
        )}
      </Section>

      {/* Decisiones */}
      <Section
        icon={<Gavel className="w-4 h-4 text-amber-400" />}
        iconBg="bg-amber-500/15"
        title={`Decisiones (${result.decisions?.length || 0})`}
        defaultOpen={false}
      >
        {result.decisions?.length > 0 ? (
          <ul className="space-y-2">
            {result.decisions.map((decision, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="flex-shrink-0 text-amber-400/60 font-mono text-xs mt-1">→</span>
                <span className="text-white/70 leading-relaxed">{decision}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-white/30 text-sm italic">No se identificaron decisiones explícitas.</p>
        )}
      </Section>

      {/* Transcripción completa (colapsable) */}
      <Section
        icon={<FileText className="w-4 h-4 text-white/40" />}
        iconBg="bg-white/5"
        title="Transcripción Completa"
        defaultOpen={false}
        collapsible
        expanded={expandedTranscript}
        onToggle={() => setExpandedTranscript(v => !v)}
      >
        <div className={`text-white/55 text-sm leading-relaxed whitespace-pre-wrap font-mono text-xs ${!expandedTranscript ? 'line-clamp-6' : ''}`}>
          {result.transcript || 'Sin transcripción disponible.'}
        </div>
        {!expandedTranscript && result.transcript?.length > 400 && (
          <button
            onClick={() => setExpandedTranscript(true)}
            className="mt-2 text-xs text-violet-400 hover:text-violet-300 transition-colors"
          >
            Ver transcripción completa ↓
          </button>
        )}
      </Section>
    </motion.div>
  )
}

// ─── Componente Section reutilizable ───────────────────────────────────────────
interface SectionProps {
  icon: React.ReactNode
  iconBg: string
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
  collapsible?: boolean
  expanded?: boolean
  onToggle?: () => void
}

function Section({ icon, iconBg, title, children, defaultOpen = true, collapsible, expanded, onToggle }: SectionProps) {
  const [open, setOpen] = useState(defaultOpen)
  const isOpen = collapsible ? expanded : open
  const toggle = collapsible ? onToggle : () => setOpen(v => !v)

  return (
    <div className="bg-white/[0.04] border border-white/8 rounded-2xl overflow-hidden">
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between p-5 text-left hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg ${iconBg} flex items-center justify-center`}>
            {icon}
          </div>
          <span className="text-sm font-semibold text-white/80">{title}</span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-white/30" />
        ) : (
          <ChevronDown className="w-4 h-4 text-white/30" />
        )}
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-white/5 pt-4">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
