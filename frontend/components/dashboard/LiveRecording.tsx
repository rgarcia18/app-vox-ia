'use client'

import { useState, useEffect, useRef } from 'react'
import { ArrowLeft, Mic, Pause, Square, FileText } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface LiveRecordingProps {
  onBack: () => void
}

type RecordingState = 'idle' | 'recording' | 'paused'

export function LiveRecording({ onBack }: LiveRecordingProps) {
  const [recordingState, setRecordingState] = useState<RecordingState>('idle')
  const [elapsed, setElapsed] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [selectedDevice, setSelectedDevice] = useState('default')
  const [language, setLanguage] = useState<'es' | 'en'>('es')
  const [transcript, setTranscript] = useState('')
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const audioLevelRef = useRef<NodeJS.Timeout | null>(null)

  // Obtener dispositivos de audio
  useEffect(() => {
    navigator.mediaDevices?.enumerateDevices().then((devs) => {
      setDevices(devs.filter(d => d.kind === 'audioinput'))
    }).catch(() => {})
  }, [])

  // Timer
  useEffect(() => {
    if (recordingState === 'recording') {
      intervalRef.current = setInterval(() => setElapsed(e => e + 1), 1000)
      // Simular nivel de audio
      audioLevelRef.current = setInterval(() => {
        setAudioLevel(Math.random() * 0.7 + 0.1)
      }, 150)
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (audioLevelRef.current) clearInterval(audioLevelRef.current)
      if (recordingState !== 'paused') setAudioLevel(0)
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (audioLevelRef.current) clearInterval(audioLevelRef.current)
    }
  }, [recordingState])

  const formatTime = (s: number) => {
    const h = Math.floor(s / 3600).toString().padStart(2, '0')
    const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0')
    const sec = (s % 60).toString().padStart(2, '0')
    return `${h}:${m}:${sec}`
  }

  const handleStart = () => {
    setRecordingState('recording')
    setElapsed(0)
    setTranscript('')
  }

  const handlePause = () => {
    setRecordingState(prev => prev === 'paused' ? 'recording' : 'paused')
  }

  const handleStop = () => {
    setRecordingState('idle')
    setElapsed(0)
    setAudioLevel(0)
    // Simular transcripción resultante
    setTranscript('La grabación ha finalizado. Aquí aparecería el texto transcrito por el modelo Whisper una vez conectado al backend.')
  }

  const levelLabel = audioLevel < 0.3 ? 'Bajo' : audioLevel < 0.6 ? 'Normal' : 'Alto'
  const levelColor = audioLevel < 0.3 ? 'text-yellow-400' : audioLevel < 0.6 ? 'text-emerald-400' : 'text-red-400'

  return (
    <div>
      {/* Back button */}
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
            {recordingState === 'idle' ? (
              <motion.div
                key="setup"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                {/* Dispositivo */}
                <div>
                  <label className="block text-xs text-white/40 font-medium mb-2">Dispositivo de entrada</label>
                  <select
                    value={selectedDevice}
                    onChange={e => setSelectedDevice(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white/80 focus:outline-none focus:border-violet-500/50 focus:bg-white/8 transition-all appearance-none cursor-pointer"
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

                {/* Idioma */}
                <div>
                  <label className="block text-xs text-white/40 font-medium mb-2">Idioma</label>
                  <div className="flex gap-2">
                    <LanguageBtn active={language === 'es'} onClick={() => setLanguage('es')}>Español</LanguageBtn>
                    <LanguageBtn active={language === 'en'} onClick={() => setLanguage('en')}>English</LanguageBtn>
                  </div>
                </div>

                {/* Botón iniciar */}
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleStart}
                  className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/35 transition-shadow"
                >
                  <Mic className="w-4 h-4" />
                  Iniciar Grabación
                </motion.button>
              </motion.div>
            ) : (
              <motion.div
                key="recording"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center"
              >
                {/* Mic pulsing icon */}
                <div className="relative my-6">
                  <motion.div
                    animate={recordingState === 'recording' ? {
                      scale: [1, 1.15, 1],
                      opacity: [0.3, 0.6, 0.3]
                    } : {}}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="absolute inset-0 w-20 h-20 rounded-full bg-emerald-500/30 -m-3"
                  />
                  <motion.div
                    animate={recordingState === 'recording' ? {
                      scale: [1, 1.08, 1],
                      opacity: [0.5, 0.8, 0.5]
                    } : {}}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                    className="absolute inset-0 w-16 h-16 rounded-full bg-emerald-500/20 -m-1"
                  />
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center ${recordingState === 'paused' ? 'bg-yellow-500/20' : 'bg-emerald-500/20'} border border-white/10`}>
                    <Mic className={`w-6 h-6 ${recordingState === 'paused' ? 'text-yellow-400' : 'text-emerald-400'}`} />
                  </div>
                </div>

                {/* Timer */}
                <div className="text-4xl font-mono font-bold text-white tracking-wider mb-1">
                  {formatTime(elapsed)}
                </div>
                <div className="text-xs text-white/40 mb-6">
                  {recordingState === 'paused' ? 'Pausado' : 'Grabando...'}
                </div>

                {/* Audio level bar */}
                <div className="w-full mb-5">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs text-white/30">Nivel de audio</span>
                    <span className={`text-xs font-medium ${levelColor}`}>{levelLabel}</span>
                  </div>
                  <div className="h-1.5 bg-white/8 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                      animate={{ width: `${audioLevel * 100}%` }}
                      transition={{ duration: 0.15 }}
                    />
                  </div>
                </div>

                {/* Controls */}
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
                    Detener
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Panel derecho: Transcripción */}
        <div className="bg-white/[0.04] backdrop-blur-sm border border-white/8 rounded-2xl p-6 min-h-[340px] flex flex-col">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-500/15 flex items-center justify-center">
              <FileText className="w-4 h-4 text-violet-400" />
            </div>
            Transcripción
          </h2>

          <div className="flex-1 flex items-center justify-center">
            {transcript ? (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-white/70 text-sm leading-relaxed"
              >
                {transcript}
              </motion.p>
            ) : (
              <div className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-3">
                  <FileText className="w-6 h-6 text-white/20" />
                </div>
                <p className="text-white/25 text-sm">
                  {recordingState === 'idle'
                    ? 'Inicia una grabación para ver la transcripción'
                    : 'La transcripción aparecerá aquí progresivamente...'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function LanguageBtn({ children, active, onClick }: { children: React.ReactNode; active: boolean; onClick: () => void }) {
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
