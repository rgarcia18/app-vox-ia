'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { ArrowLeft, Mic, Pause, Square, FileText, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import api from '@/services/api'
import { ResultsPanel, type AnalysisResult } from './ResultsPanel'

interface LiveRecordingProps {
  onBack: () => void
}

type RecordingState = 'idle' | 'recording' | 'paused' | 'processing'

export function LiveRecording({ onBack }: LiveRecordingProps) {
  const [recordingState, setRecordingState] = useState<RecordingState>('idle')
  const [elapsed, setElapsed] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [language, setLanguage] = useState<'es' | 'en'>('es')
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [selectedDevice, setSelectedDevice] = useState('default')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [processProgress, setProcessProgress] = useState(0)
  const [processMsg, setProcessMsg] = useState('')

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animFrameRef = useRef<number | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const cleanup = () => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    streamRef.current = null
    mediaRecorderRef.current = null
    analyserRef.current = null
  }

  useEffect(() => {
    navigator.mediaDevices?.enumerateDevices().then((devs) => {
      setDevices(devs.filter(d => d.kind === 'audioinput'))
    }).catch(() => {})
    return () => cleanup()
  }, [])

  // Timer del cronómetro
  useEffect(() => {
    if (recordingState === 'recording') {
      intervalRef.current = setInterval(() => setElapsed(e => e + 1), 1000)
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [recordingState])

  const startAudioLevel = (stream: MediaStream) => {
    try {
      const ctx = new AudioContext()
      const source = ctx.createMediaStreamSource(stream)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)
      analyserRef.current = analyser

      const tick = () => {
        const data = new Uint8Array(analyser.frequencyBinCount)
        analyser.getByteFrequencyData(data)
        const avg = data.reduce((a, b) => a + b, 0) / data.length
        setAudioLevel(avg / 128)
        animFrameRef.current = requestAnimationFrame(tick)
      }
      animFrameRef.current = requestAnimationFrame(tick)
    } catch {
      // Silenciar errores de AudioContext
    }
  }

  const handleStart = useCallback(async () => {
    try {
      const constraints: MediaStreamConstraints = {
        audio: selectedDevice !== 'default'
          ? { deviceId: { exact: selectedDevice } }
          : true
      }
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      streamRef.current = stream
      audioChunksRef.current = []

      // Determinar mime type soportado
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/ogg'

      const recorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      recorder.start(1000) // chunk cada 1s
      setRecordingState('recording')
      setElapsed(0)
      startAudioLevel(stream)
    } catch (err) {
      toast.error('No se pudo acceder al micrófono. Revisa los permisos.')
      console.error(err)
    }
  }, [selectedDevice])

  const handlePause = () => {
    if (!mediaRecorderRef.current) return
    if (recordingState === 'recording') {
      mediaRecorderRef.current.pause()
      setRecordingState('paused')
      setAudioLevel(0)
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    } else if (recordingState === 'paused') {
      mediaRecorderRef.current.resume()
      setRecordingState('recording')
      if (streamRef.current) startAudioLevel(streamRef.current)
    }
  }

  const handleStop = async () => {
    if (!mediaRecorderRef.current) return

    // Detener grabación y recolectar datos
    await new Promise<void>((resolve) => {
      if (!mediaRecorderRef.current) { resolve(); return }
      mediaRecorderRef.current.onstop = () => resolve()
      mediaRecorderRef.current.stop()
    })

    cleanup()
    setAudioLevel(0)
    setRecordingState('processing')
    setProcessProgress(5)
    setProcessMsg('Preparando audio...')

    const chunks = audioChunksRef.current
    if (chunks.length === 0) {
      toast.error('No se grabó audio. Intenta nuevamente.')
      setRecordingState('idle')
      return
    }

    const mimeType = chunks[0].type || 'audio/webm'
    const audioBlob = new Blob(chunks, { type: mimeType })
    const ext = mimeType.includes('ogg') ? '.ogg' : '.webm'

    // Progreso simulado
    const steps = [
      { pct: 15, msg: 'Cargando modelos de IA...', delay: 1200 },
      { pct: 35, msg: 'Transcribiendo con Whisper...', delay: 3000 },
      { pct: 60, msg: 'Generando resumen ejecutivo...', delay: 5500 },
      { pct: 78, msg: 'Extrayendo puntos clave...', delay: 8000 },
      { pct: 90, msg: 'Identificando tareas y decisiones...', delay: 10000 },
    ]
    const timers = steps.map(({ pct, msg, delay }) =>
      setTimeout(() => { setProcessProgress(pct); setProcessMsg(msg) }, delay)
    )

    try {
      const formData = new FormData()
      formData.append('file', audioBlob, `grabacion${ext}`)
      formData.append('language', language)

      const { data } = await api.post('/api/audio/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      timers.forEach(clearTimeout)
      setProcessProgress(100)
      setProcessMsg('¡Análisis completado!')

      setTimeout(() => {
        setResult({ ...data, file_name: `Grabación en vivo (${formatTime(elapsed)})` })
        setRecordingState('idle')
        toast.success('Grabación analizada correctamente')
      }, 600)
    } catch (err: unknown) {
      timers.forEach(clearTimeout)
      const e = err as { response?: { data?: { message?: string } } }
      toast.error(e?.response?.data?.message || 'Error al procesar la grabación')
      setRecordingState('idle')
      setProcessProgress(0)
      setProcessMsg('')
    }
  }

  const formatTime = (s: number) => {
    const h = Math.floor(s / 3600).toString().padStart(2, '0')
    const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0')
    const sec = (s % 60).toString().padStart(2, '0')
    return `${h}:${m}:${sec}`
  }

  const levelLabel = audioLevel < 0.3 ? 'Bajo' : audioLevel < 0.6 ? 'Normal' : 'Alto'
  const levelColor = audioLevel < 0.3 ? 'text-yellow-400' : audioLevel < 0.6 ? 'text-emerald-400' : 'text-red-400'

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
        <ResultsPanel
          result={result}
          onReset={() => { setResult(null); setElapsed(0) }}
        />
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Panel izquierdo: Controles */}
        <div className="bg-white/[0.04] backdrop-blur-sm border border-white/8 rounded-2xl p-6">
          <h2 className="text-lg font-bold text-white mb-5 flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center">
              <Mic className="w-4 h-4 text-emerald-400" />
            </div>
            Grabación en Vivo
          </h2>

          <AnimatePresence mode="wait">
            {/* Estado: idle — configuración */}
            {recordingState === 'idle' && (
              <motion.div key="setup" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <div>
                  <label className="block text-xs text-white/40 font-medium mb-2">Dispositivo de entrada</label>
                  <select
                    value={selectedDevice}
                    onChange={e => setSelectedDevice(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white/80 focus:outline-none focus:border-violet-500/50 transition-all appearance-none cursor-pointer"
                  >
                    {devices.length === 0 ? (
                      <option value="default">Micrófono predeterminado</option>
                    ) : (
                      devices.map(d => (
                        <option key={d.deviceId} value={d.deviceId}>
                          {d.label || 'Micrófono'}
                        </option>
                      ))
                    )}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-white/40 font-medium mb-2">Idioma</label>
                  <div className="flex gap-2">
                    <LangBtn active={language === 'es'} onClick={() => setLanguage('es')}>Español</LangBtn>
                    <LangBtn active={language === 'en'} onClick={() => setLanguage('en')}>English</LangBtn>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleStart}
                  className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
                >
                  <Mic className="w-4 h-4" />
                  Iniciar Grabación
                </motion.button>
              </motion.div>
            )}

            {/* Estado: grabando / pausado */}
            {(recordingState === 'recording' || recordingState === 'paused') && (
              <motion.div key="recording" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center">
                <div className="relative my-6">
                  <motion.div
                    animate={recordingState === 'recording' ? { scale: [1, 1.15, 1], opacity: [0.3, 0.6, 0.3] } : {}}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="absolute inset-0 w-20 h-20 rounded-full bg-emerald-500/30 -m-3"
                  />
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center ${recordingState === 'paused' ? 'bg-yellow-500/20' : 'bg-emerald-500/20'} border border-white/10`}>
                    <Mic className={`w-6 h-6 ${recordingState === 'paused' ? 'text-yellow-400' : 'text-emerald-400'}`} />
                  </div>
                </div>

                <div className="text-4xl font-mono font-bold text-white tracking-wider mb-1">{formatTime(elapsed)}</div>
                <div className="text-xs text-white/40 mb-6">{recordingState === 'paused' ? 'Pausado' : 'Grabando...'}</div>

                <div className="w-full mb-5">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs text-white/30">Nivel de audio</span>
                    <span className={`text-xs font-medium ${levelColor}`}>{levelLabel}</span>
                  </div>
                  <div className="h-1.5 bg-white/8 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                      animate={{ width: `${audioLevel * 100}%` }}
                      transition={{ duration: 0.1 }}
                    />
                  </div>
                </div>

                <div className="flex gap-3 w-full">
                  <button
                    onClick={handlePause}
                    className="flex-1 py-2.5 rounded-xl bg-yellow-500/15 border border-yellow-500/20 text-yellow-400 text-sm font-medium flex items-center justify-center gap-2 hover:bg-yellow-500/25 transition-colors"
                  >
                    <Pause className="w-4 h-4" />
                    {recordingState === 'paused' ? 'Reanudar' : 'Pausar'}
                  </button>
                  <button
                    onClick={handleStop}
                    className="flex-1 py-2.5 rounded-xl bg-red-500/15 border border-red-500/20 text-red-400 text-sm font-medium flex items-center justify-center gap-2 hover:bg-red-500/25 transition-colors"
                  >
                    <Square className="w-4 h-4" />
                    Detener y Analizar
                  </button>
                </div>
              </motion.div>
            )}

            {/* Estado: procesando */}
            {recordingState === 'processing' && (
              <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center py-6">
                <Loader2 className="w-12 h-12 text-violet-400 animate-spin mb-4" />
                <p className="text-white/70 text-sm font-medium mb-1">Analizando grabación...</p>
                <p className="text-white/35 text-xs mb-5">{processMsg}</p>
                <div className="w-full">
                  <div className="h-1.5 bg-white/8 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-violet-500 to-indigo-400 rounded-full"
                      animate={{ width: `${processProgress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                  <p className="text-white/25 text-xs mt-1.5 text-right">{Math.round(processProgress)}%</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Panel derecho: instrucciones / estado */}
        <div className="bg-white/[0.04] backdrop-blur-sm border border-white/8 rounded-2xl p-6 min-h-[300px] flex flex-col">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-500/15 flex items-center justify-center">
              <FileText className="w-4 h-4 text-violet-400" />
            </div>
            Información
          </h2>

          <div className="flex-1 flex flex-col justify-center">
            {recordingState === 'idle' && (
              <div className="space-y-4">
                {[
                  { num: '1', text: 'Selecciona el micrófono e idioma' },
                  { num: '2', text: 'Presiona "Iniciar Grabación"' },
                  { num: '3', text: 'Habla claramente hacia el micrófono' },
                  { num: '4', text: 'Detén la grabación cuando termines' },
                  { num: '5', text: 'El sistema analizará el audio automáticamente' },
                ].map(s => (
                  <div key={s.num} className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-full bg-violet-500/20 flex items-center justify-center text-xs font-bold text-violet-400 flex-shrink-0 mt-0.5">{s.num}</span>
                    <span className="text-white/50 text-sm">{s.text}</span>
                  </div>
                ))}
              </div>
            )}
            {recordingState === 'recording' && (
              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mx-auto mb-3 border border-emerald-500/20">
                  <Mic className="w-7 h-7 text-emerald-400" />
                </div>
                <p className="text-white/60 text-sm">Grabando en curso</p>
                <p className="text-white/30 text-xs mt-1">Habla claramente. El audio se guardará cuando detengas.</p>
              </div>
            )}
            {recordingState === 'paused' && (
              <div className="text-center">
                <p className="text-yellow-400/80 text-sm font-medium">Grabación pausada</p>
                <p className="text-white/30 text-xs mt-1">Reanuda cuando estés listo.</p>
              </div>
            )}
            {recordingState === 'processing' && (
              <div className="text-center">
                <p className="text-violet-400/80 text-sm font-medium">Procesando con IA</p>
                <p className="text-white/30 text-xs mt-2">Esto puede tardar entre 1 y 5 minutos según la duración del audio.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function LangBtn({ children, active, onClick }: { children: React.ReactNode; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 py-2 rounded-xl text-sm font-medium transition-all border ${
        active
          ? 'bg-violet-500/20 border-violet-500/40 text-violet-300'
          : 'bg-white/4 border-white/8 text-white/40 hover:text-white/60 hover:bg-white/8'
      }`}
    >
      {children}
    </button>
  )
}
