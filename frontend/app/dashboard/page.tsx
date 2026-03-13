'use client'

import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'next/navigation'
import api from '@/services/api'
import { ModeSelector } from '@/components/dashboard/ModeSelector'
import { LiveRecording } from '@/components/dashboard/LiveRecording'
import { FileUpload } from '@/components/dashboard/FileUpload'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { motion, AnimatePresence } from 'framer-motion'

export type AppMode = 'selector' | 'live' | 'upload'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const router = useRouter()
  const [mode, setMode] = useState<AppMode>('selector')

  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch {
      // silenciar errores de logout
    } finally {
      logout()
      router.push('/')
    }
  }

  return (
    <div className="min-h-screen bg-[#080b10] text-white overflow-hidden">
      {/* Ambient background glows */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-100px] left-1/4 w-[700px] h-[700px] bg-violet-600/10 rounded-full blur-[140px]" />
        <div className="absolute bottom-[-100px] right-1/4 w-[500px] h-[500px] bg-cyan-400/8 rounded-full blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[400px] bg-indigo-800/6 rounded-full blur-[160px]" />
        {/* Subtle grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '60px 60px'
          }}
        />
      </div>

      <DashboardHeader user={user} onLogout={handleLogout} />

      <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-68px)] px-4 py-8">
        <AnimatePresence mode="wait">
          {mode === 'selector' && (
            <motion.div
              key="selector"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16, scale: 0.98 }}
              transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="w-full max-w-3xl"
            >
              <ModeSelector onSelect={setMode} />
            </motion.div>
          )}

          {mode === 'live' && (
            <motion.div
              key="live"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16, scale: 0.98 }}
              transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="w-full max-w-5xl"
            >
              <LiveRecording onBack={() => setMode('selector')} />
            </motion.div>
          )}

          {mode === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16, scale: 0.98 }}
              transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="w-full max-w-2xl"
            >
              <FileUpload onBack={() => setMode('selector')} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
