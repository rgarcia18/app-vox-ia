'use client'

import { useState, useRef, useCallback } from 'react'
import { ArrowLeft, Upload, File, X, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import api from '@/services/api'
import { ResultsPanel, type AnalysisResult } from './ResultsPanel'

interface FileUploadProps {
  onBack: () => void
}

type UploadState = 'idle' | 'uploading' | 'done'

const MAX_SIZE_MB = 100

export function FileUpload({ onBack }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [language, setLanguage] = useState<'es' | 'en'>('es')
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [progress, setProgress] = useState(0)
  const [statusMsg, setStatusMsg] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateFile = (f: File): boolean => {
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      toast.error(`El archivo supera los ${MAX_SIZE_MB}MB`)
      return false
    }
    const validExt = /\.(mp3|wav|m4a|ogg|flac|mp4)$/i.test(f.name)
    if (!validExt) {
      toast.error('Formato no soportado. Usa MP3, WAV o M4A')
      return false
    }
    return true
  }

  const handleFile = (f: File) => {
    if (validateFile(f)) {
      setFile(f)
      setUploadState('idle')
      setProgress(0)
      setResult(null)
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFile(dropped)
  }, [])

  const handleProcess = async () => {
    if (!file) return
    setUploadState('uploading')
    setProgress(5)
    setStatusMsg('Enviando audio al servidor...')

    // Progreso simulado mientras espera el backend
    const steps = [
      { pct: 15, msg: 'Cargando modelos de IA...', delay: 1200 },
      { pct: 30, msg: 'Transcribiendo con Whisper...', delay: 3000 },
      { pct: 60, msg: 'Generando resumen ejecutivo...', delay: 5000 },
      { pct: 75, msg: 'Extrayendo puntos clave...', delay: 7000 },
      { pct: 88, msg: 'Identificando tareas y decisiones...', delay: 9000 },
    ]

    const timers: ReturnType<typeof setTimeout>[] = []
    steps.forEach(({ pct, msg, delay }) => {
      timers.push(setTimeout(() => {
        setProgress(pct)
        setStatusMsg(msg)
      }, delay))
    })

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('language', language)

      const { data } = await api.post('/api/audio/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      timers.forEach(clearTimeout)
      setProgress(100)
      setStatusMsg('¡Análisis completado!')
      setUploadState('done')
      setResult(data)
      toast.success('Audio analizado correctamente')
    } catch (err: unknown) {
      timers.forEach(clearTimeout)
      setUploadState('idle')
      setProgress(0)
      setStatusMsg('')
      const e = err as { response?: { data?: { message?: string } } }
      toast.error(e?.response?.data?.message || 'Error al procesar el audio')
    }
  }

  const formatSize = (bytes: number) =>
    bytes < 1024 * 1024
      ? `${(bytes / 1024).toFixed(0)} KB`
      : `${(bytes / (1024 * 1024)).toFixed(1)} MB`

  // Si ya hay resultado, mostrar el panel de resultados
  if (result) {
    return (
      <div>
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-white/40 hover:text-white/70 text-sm mb-6 transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          Volver al inicio
        </button>
        <ResultsPanel result={result} onReset={() => { setResult(null); setFile(null); setUploadState('idle') }} />
      </div>
    )
  }

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-white/40 hover:text-white/70 text-sm mb-6 transition-colors group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
        Volver
      </button>

      <div className="bg-white/[0.04] backdrop-blur-sm border border-white/8 rounded-2xl p-7">
        <h2 className="text-xl font-bold text-white mb-1 tracking-tight">Cargar Archivo de Audio - zDSxBiAy)bj%6h-3PUnzTa1x9Bj4e</h2>
        <p className="text-white/35 text-sm mb-6">Sube un archivo pregrabado para transcribir y generar resumen</p>

        {/* Dropzone */}
        <div
          onDrop={onDrop}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onClick={() => !file && uploadState === 'idle' && inputRef.current?.click()}
          className={`
            relative rounded-xl border-2 border-dashed transition-all duration-300
            ${uploadState === 'uploading' ? 'cursor-default' : 'cursor-pointer'}
            ${isDragging
              ? 'border-violet-500/60 bg-violet-500/8'
              : file
                ? 'border-white/15 bg-white/4 cursor-default'
                : 'border-white/12 bg-white/[0.02] hover:border-white/25 hover:bg-white/5'
            }
          `}
        >
          <AnimatePresence mode="wait">
            {!file ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center py-12 px-6 text-center"
              >
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-colors ${isDragging ? 'bg-violet-500/20' : 'bg-white/5'}`}>
                  <Upload className={`w-7 h-7 ${isDragging ? 'text-violet-400' : 'text-white/30'}`} strokeWidth={1.5} />
                </div>
                <p className="text-white/60 text-sm font-medium mb-1">
                  {isDragging ? 'Suelta el archivo aquí' : 'Arrastra tu archivo aquí'}
                </p>
                <p className="text-white/25 text-xs mb-4">o haz clic para seleccionar</p>
                <button
                  type="button"
                  onClick={e => { e.stopPropagation(); inputRef.current?.click() }}
                  className="px-4 py-2 rounded-lg bg-violet-500/20 border border-violet-500/30 text-violet-300 text-sm font-medium hover:bg-violet-500/30 transition-colors"
                >
                  Seleccionar archivo
                </button>
                <p className="text-white/20 text-xs mt-4">Formatos: MP3, WAV, M4A (máx. {MAX_SIZE_MB}MB)</p>
              </motion.div>
            ) : (
              <motion.div
                key="file"
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="p-5"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/15 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <File className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white/80 text-sm font-medium truncate">{file.name}</p>
                    <p className="text-white/30 text-xs">{formatSize(file.size)}</p>
                  </div>
                  {uploadState === 'idle' && (
                    <button
                      onClick={(e) => { e.stopPropagation(); setFile(null) }}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-white/30 hover:text-white/60 hover:bg-white/8 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Barra de progreso */}
                {uploadState === 'uploading' && (
                  <div className="mt-4">
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="text-white/40 text-xs">{statusMsg}</span>
                      <span className="text-white/30 text-xs">{Math.round(progress)}%</span>
                    </div>
                    <div className="h-1.5 bg-white/8 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-violet-500 to-indigo-400 rounded-full"
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".mp3,.wav,.m4a,.ogg,.flac"
          className="hidden"
          onChange={e => {
            const f = e.target.files?.[0]
            if (f) handleFile(f)
            e.target.value = ''
          }}
        />

        {/* Idioma */}
        <div className="mt-5">
          <label className="block text-xs text-white/40 font-medium mb-2">Idioma del audio</label>
          <div className="flex gap-2">
            {(['es', 'en'] as const).map(lang => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                disabled={uploadState === 'uploading'}
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all border disabled:opacity-50 ${
                  language === lang
                    ? 'bg-violet-500/20 border-violet-500/40 text-violet-300'
                    : 'bg-white/4 border-white/8 text-white/40 hover:text-white/60 hover:bg-white/8'
                }`}
              >
                {lang === 'es' ? 'Español' : 'English'}
              </button>
            ))}
          </div>
        </div>

        {/* Botón procesar */}
        <motion.button
          whileHover={file && uploadState === 'idle' ? { scale: 1.01 } : {}}
          whileTap={file && uploadState === 'idle' ? { scale: 0.98 } : {}}
          onClick={handleProcess}
          disabled={!file || uploadState !== 'idle'}
          className={`
            w-full mt-4 py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200
            ${file && uploadState === 'idle'
              ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/20 hover:shadow-violet-500/35'
              : 'bg-white/5 text-white/20 cursor-not-allowed'
            }
          `}
        >
          {uploadState === 'uploading' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analizando audio...
            </>
          ) : (
            'Procesar y Analizar Audio'
          )}
        </motion.button>
      </div>
    </div>
  )
}
