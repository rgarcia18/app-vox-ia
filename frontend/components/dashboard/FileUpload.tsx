'use client'

import { useState, useRef, useCallback } from 'react'
import { ArrowLeft, Upload, File, X, Loader2, CheckCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'

interface FileUploadProps {
  onBack: () => void
}

type UploadState = 'idle' | 'uploading' | 'done'

const ACCEPTED_FORMATS = ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/mp4', 'audio/mp3', 'audio/wave']
const MAX_SIZE_MB = 100

export function FileUpload({ onBack }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [language, setLanguage] = useState<'es' | 'en'>('es')
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [progress, setProgress] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateFile = (f: File): boolean => {
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      toast.error(`El archivo supera los ${MAX_SIZE_MB}MB`)
      return false
    }
    const validExt = /\.(mp3|wav|m4a)$/i.test(f.name)
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
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFile(dropped)
  }, [])

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const onDragLeave = () => setIsDragging(false)

  const handleProcess = async () => {
    if (!file) return
    setUploadState('uploading')
    setProgress(0)

    // Simular progreso
    const sim = setInterval(() => {
      setProgress(p => {
        if (p >= 90) {
          clearInterval(sim)
          return 90
        }
        return p + Math.random() * 15
      })
    }, 300)

    await new Promise(r => setTimeout(r, 2500))
    clearInterval(sim)
    setProgress(100)
    setUploadState('done')
    toast.success('Audio procesado correctamente')
  }

  const formatSize = (bytes: number) =>
    bytes < 1024 * 1024
      ? `${(bytes / 1024).toFixed(0)} KB`
      : `${(bytes / (1024 * 1024)).toFixed(1)} MB`

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
        <h2 className="text-xl font-bold text-white mb-1 tracking-tight">Cargar Archivo de Audio</h2>
        <p className="text-white/35 text-sm mb-6">Sube un archivo pregrabado para transcribir y generar resumen</p>

        {/* Dropzone */}
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onClick={() => !file && inputRef.current?.click()}
          className={`
            relative rounded-xl border-2 border-dashed transition-all duration-300 cursor-pointer
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
                <p className="text-white/20 text-xs mt-4">Formatos soportados: MP3, WAV, M4A (máx. {MAX_SIZE_MB}MB)</p>
              </motion.div>
            ) : (
              <motion.div
                key="file"
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-4 p-5"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-500/15 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                  <File className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white/80 text-sm font-medium truncate">{file.name}</p>
                  <p className="text-white/30 text-xs">{formatSize(file.size)}</p>
                  {uploadState === 'uploading' && (
                    <div className="mt-2">
                      <div className="h-1 bg-white/8 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-violet-500 to-indigo-400 rounded-full"
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                      <p className="text-white/30 text-[11px] mt-1">{Math.round(progress)}% procesado...</p>
                    </div>
                  )}
                  {uploadState === 'done' && (
                    <div className="flex items-center gap-1.5 mt-1">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400 text-xs">Procesado correctamente</span>
                    </div>
                  )}
                </div>
                {uploadState === 'idle' && (
                  <button
                    onClick={(e) => { e.stopPropagation(); setFile(null) }}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-white/30 hover:text-white/60 hover:bg-white/8 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".mp3,.wav,.m4a"
          className="hidden"
          onChange={e => {
            const f = e.target.files?.[0]
            if (f) handleFile(f)
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
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all border ${
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

        {/* Process button */}
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
              Procesando audio...
            </>
          ) : uploadState === 'done' ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Procesado
            </>
          ) : (
            'Procesar Audio'
          )}
        </motion.button>
      </div>
    </div>
  )
}
