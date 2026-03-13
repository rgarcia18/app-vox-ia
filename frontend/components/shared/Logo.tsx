import { Mic } from 'lucide-react'

/**
 * Componente Logo de VoxIA - Tema oscuro
 */
export function Logo() {
  return (
    <div className="flex flex-col items-center gap-3 mb-7">
      <div className="relative">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-xl shadow-violet-500/30">
          <Mic className="h-7 w-7 text-white" strokeWidth={2} />
        </div>
        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#080b10] shadow" />
      </div>
      <div className="text-center">
        <h1 className="text-2xl font-bold text-white tracking-tight">VoxIA</h1>
        <p className="text-sm text-white/35">Transcripción inteligente de reuniones</p>
      </div>
    </div>
  )
}
