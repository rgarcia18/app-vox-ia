'use client'

/**
 * Componente AnimatedBackground
 * 
 * Fondo oscuro con glows ambientales para la pantalla de login.
 */
export function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 bg-[#080b10]">
      {/* Ambient glows */}
      <div className="absolute top-1/4 left-1/3 w-[600px] h-[600px] bg-violet-600/10 rounded-full blur-[140px] animate-pulse" style={{ animationDuration: '8s' }} />
      <div className="absolute bottom-1/4 right-1/3 w-[400px] h-[400px] bg-indigo-500/8 rounded-full blur-[120px] animate-pulse" style={{ animationDuration: '12s', animationDelay: '3s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[300px] bg-cyan-500/5 rounded-full blur-[160px]" />
      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.025]"
        style={{
          backgroundImage: 'linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px)',
          backgroundSize: '60px 60px'
        }}
      />
    </div>
  )
}
