'use client'

import { Upload, Mic2, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { AppMode } from '@/app/dashboard/page'

interface ModeSelectorProps {
  onSelect: (mode: AppMode) => void
}

export function ModeSelector({ onSelect }: ModeSelectorProps) {
  return (
    <div className="flex flex-col items-center">
      {/* Heading */}
      <motion.div
        className="text-center mb-12"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-5">
          <Sparkles className="w-3 h-3" />
          IA de voz lista
        </div>
        <h1 className="text-4xl font-bold text-white tracking-tight mb-3">
          ¿Cómo deseas procesar<br />tu reunión?
        </h1>
        <p className="text-white/40 text-base">
          Selecciona un modo para comenzar
        </p>
      </motion.div>

      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
        <ModeCard
          delay={0.2}
          icon={Upload}
          iconBg="from-blue-500/20 to-indigo-600/20"
          iconColor="text-blue-400"
          glowColor="blue"
          title="Cargar Archivo"
          description="Sube un archivo de audio pregrabado (MP3, WAV, M4A) para procesar"
          badge="Procesamiento diferido"
          onClick={() => onSelect('upload')}
        />
        <ModeCard
          delay={0.3}
          icon={Mic2}
          iconBg="from-emerald-500/20 to-teal-600/20"
          iconColor="text-emerald-400"
          glowColor="emerald"
          title="Grabar en Vivo"
          description="Graba una reunión en tiempo real con transcripción progresiva"
          badge="Tiempo real"
          onClick={() => onSelect('live')}
        />
      </div>
    </div>
  )
}

interface ModeCardProps {
  delay: number
  icon: React.ElementType
  iconBg: string
  iconColor: string
  glowColor: 'blue' | 'emerald'
  title: string
  description: string
  badge: string
  onClick: () => void
}

const glowMap = {
  blue: 'hover:shadow-blue-500/15 hover:border-blue-500/30',
  emerald: 'hover:shadow-emerald-500/15 hover:border-emerald-500/30',
}

const badgeColorMap = {
  blue: 'bg-blue-500/10 text-blue-300 border-blue-500/20',
  emerald: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
}

function ModeCard({ delay, icon: Icon, iconBg, iconColor, glowColor, title, description, badge, onClick }: ModeCardProps) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -4, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        group relative text-left p-7 rounded-2xl
        bg-white/[0.04] backdrop-blur-sm
        border border-white/8
        shadow-xl
        hover:shadow-2xl hover:bg-white/[0.07]
        ${glowMap[glowColor]}
        transition-all duration-300
        cursor-pointer
        overflow-hidden
      `}
    >
      {/* Subtle corner accent */}
      <div className="absolute top-0 right-0 w-24 h-24 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: glowColor === 'blue'
            ? 'radial-gradient(circle at top right, rgba(59,130,246,0.08), transparent 70%)'
            : 'radial-gradient(circle at top right, rgba(52,211,153,0.08), transparent 70%)'
        }}
      />

      <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${iconBg} flex items-center justify-center mb-5 border border-white/10`}>
        <Icon className={`w-6 h-6 ${iconColor}`} strokeWidth={1.8} />
      </div>

      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-medium mb-3 ${badgeColorMap[glowColor]}`}>
        {badge}
      </div>

      <h2 className="text-xl font-bold text-white mb-2 tracking-tight">{title}</h2>
      <p className="text-white/45 text-sm leading-relaxed">{description}</p>

      <div className="mt-6 flex items-center gap-2 text-xs font-medium text-white/30 group-hover:text-white/60 transition-colors">
        Seleccionar
        <svg className="w-3.5 h-3.5 translate-x-0 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </motion.button>
  )
}
