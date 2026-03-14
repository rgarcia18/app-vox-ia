'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, CheckSquare, Lightbulb, GitBranch,
  Clock, Globe, Copy, Check, ChevronDown, ChevronUp,
  ArrowLeft
} from 'lucide-react'

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
  onBack: () => void
}

function formatDuration(s: number): string {
  if (s < 60) return `${Math.round(s)}s`
  const m = Math.floor(s / 60)
  const sec = Math.round(s % 60)
  return sec > 0 ? `${m}m ${sec}s` : `${m}m`
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={copy}
      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs text-white/40 hover:text-white/70 hover:bg-white/8 transition-all"
    >
      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
      {copied ? 'Copiado' : 'Copiar'}
    </button>
  )
}

function Section({
  icon, title, color, children, defaultOpen = true
}: {
  icon: React.ReactNode
  title: string
  color: string
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="bg-white/[0.03] border border-white/8 rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/4 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
            {icon}
          </div>
          <span className="text-white/90 font-semibold text-sm">{title}</span>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-white/30" /> : <ChevronDown className="w-4 h-4 text-white/30" />}
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1 border-t border-white/6">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <p className="text-white/25 text-sm italic">{message}</p>
  )
}

function ListItems({ items, color }: { items: string[], color: string }) {
  if (items.length === 0) return null
  return (
    <ul className="space-y-2.5">
      {items.map((item, i) => (
        <motion.li
          key={i}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          className="flex items-start gap-3"
        >
          <span className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold flex-shrink-0 ${color}`}>
            {i + 1}
          </span>
          <span className="text-white/70 text-sm leading-relaxed">{item}</span>
        </motion.li>
      ))}
    </ul>
  )
}

export function ResultsPanel({ result, onBack }: ResultsPanelProps) {
  const fullText = [
    `TRANSCRIPCIÓN\n${'─'.repeat(40)}\n${result.transcript}`,
    `\nRESUMEN EJECUTIVO\n${'─'.repeat(40)}\n${result.summary}`,
    result.key_points.length > 0 ? `\nPUNTOS CLAVE\n${'─'.repeat(40)}\n${result.key_points.map((p, i) => `${i + 1}. ${p}`).join('\n')}` : '',
    result.tasks.length > 0 ? `\nTAREAS Y COMPROMISOS\n${'─'.repeat(40)}\n${result.tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}` : '',
    result.decisions.length > 0 ? `\nDECISIONES TOMADAS\n${'─'.repeat(40)}\n${result.decisions.map((d, i) => `${i + 1}. ${d}`).join('\n')}` : '',
  ].filter(Boolean).join('\n')

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-white/40 hover:text-white/70 text-sm transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          Nuevo análisis
        </button>
        <CopyButton text={fullText} />
      </div>

      {/* Meta chips */}
      <div className="flex flex-wrap gap-2 mb-6">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/6 border border-white/10 text-xs text-white/50">
          <FileText className="w-3.5 h-3.5" />
          {result.file_name}
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/6 border border-white/10 text-xs text-white/50">
          <Clock className="w-3.5 h-3.5" />
          {formatDuration(result.duration_seconds)} de audio
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/6 border border-white/10 text-xs text-white/50">
          <Globe className="w-3.5 h-3.5" />
          {result.language === 'es' ? 'Español' : 'English'}
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
          ✓ Procesado en {formatDuration(result.processing_time_seconds)}
        </div>
      </div>

      <div className="space-y-3">
        {/* Resumen ejecutivo */}
        <Section
          icon={<Lightbulb className="w-4 h-4 text-amber-400" />}
          title="Resumen Ejecutivo"
          color="bg-amber-500/15"
        >
          <p className="text-white/75 text-sm leading-relaxed">{result.summary}</p>
        </Section>

        {/* Puntos clave */}
        <Section
          icon={<GitBranch className="w-4 h-4 text-violet-400" />}
          title={`Puntos Clave ${result.key_points.length > 0 ? `(${result.key_points.length})` : ''}`}
          color="bg-violet-500/15"
        >
          {result.key_points.length > 0
            ? <ListItems items={result.key_points} color="bg-violet-500/20 text-violet-300" />
            : <EmptyState message="No se identificaron puntos clave destacados." />
          }
        </Section>

        {/* Tareas */}
        <Section
          icon={<CheckSquare className="w-4 h-4 text-emerald-400" />}
          title={`Tareas y Compromisos ${result.tasks.length > 0 ? `(${result.tasks.length})` : ''}`}
          color="bg-emerald-500/15"
        >
          {result.tasks.length > 0
            ? <ListItems items={result.tasks} color="bg-emerald-500/20 text-emerald-300" />
            : <EmptyState message="No se identificaron tareas ni compromisos." />
          }
        </Section>

        {/* Decisiones */}
        <Section
          icon={<GitBranch className="w-4 h-4 text-blue-400" />}
          title={`Decisiones Tomadas ${result.decisions.length > 0 ? `(${result.decisions.length})` : ''}`}
          color="bg-blue-500/15"
        >
          {result.decisions.length > 0
            ? <ListItems items={result.decisions} color="bg-blue-500/20 text-blue-300" />
            : <EmptyState message="No se identificaron decisiones explícitas." />
          }
        </Section>

        {/* Transcripción completa */}
        <Section
          icon={<FileText className="w-4 h-4 text-white/50" />}
          title="Transcripción Completa"
          color="bg-white/8"
          defaultOpen={false}
        >
          <div className="relative">
            <div className="absolute top-2 right-2">
              <CopyButton text={result.transcript} />
            </div>
            <div className="bg-black/20 rounded-xl p-4 max-h-72 overflow-y-auto scrollbar-thin">
              <p className="text-white/60 text-sm leading-relaxed whitespace-pre-wrap pr-16">
                {result.transcript}
              </p>
            </div>
          </div>
        </Section>
      </div>
    </motion.div>
  )
}
