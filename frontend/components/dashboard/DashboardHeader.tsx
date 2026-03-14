'use client'

import { Mic, History, Settings, LogOut } from 'lucide-react'
import { motion } from 'framer-motion'

interface User {
  id: string
  username: string
  displayName: string
  createdAt: string
  lastLoginAt?: string
}

interface DashboardHeaderProps {
  user: User | null
  onLogout: () => void
}

export function DashboardHeader({ user, onLogout }: DashboardHeaderProps) {
  return (
    <header className="relative z-20 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#080b10]/60 backdrop-blur-xl">
      {/* Logo */}
      <motion.div
        className="flex items-center gap-3"
        initial={{ opacity: 0, x: -16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="relative">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Mic className="w-4.5 h-4.5 text-white" strokeWidth={2.5} />
          </div>
          {/* Live indicator dot */}
          <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-[#080b10]" />
        </div>
        <div>
          <span className="text-[15px] font-bold tracking-tight text-white">VoxIA</span>
          {user && (
            <p className="text-[11px] text-white/35 leading-none mt-0.5">
              Hola, {user.displayName}
            </p>
          )}
        </div>
      </motion.div>

      {/* Actions */}
      <motion.div
        className="flex items-center gap-1"
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <HeaderIcon icon={History} label="Historial" />
        <HeaderIcon icon={Settings} label="Configuración" />
        <div className="w-px h-5 bg-white/10 mx-1" />
        <button
          onClick={onLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-white/50 hover:text-white/80 hover:bg-white/5 transition-all duration-200 text-xs font-medium"
        >
          <LogOut className="w-3.5 h-3.5" />
          Salir
        </button>
      </motion.div>
    </header>
  )
}

function HeaderIcon({ icon: Icon, label }: { icon: React.ElementType; label: string }) {
  return (
    <button
      title={label}
      className="w-9 h-9 rounded-lg flex items-center justify-center text-white/40 hover:text-white/70 hover:bg-white/5 transition-all duration-200"
    >
      <Icon className="w-4 h-4" />
    </button>
  )
}
