'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Logo } from '@/components/shared/Logo'
import { loginSchema, type LoginFormData } from '@/lib/validations'
import { useAuthStore } from '@/stores/authStore'
import { login } from '@/services/authService'

/**
 * Componente LoginForm
 * 
 * Formulario de autenticación con:
 * - Validación en tiempo real (blur)
 * - Manejo de errores del servidor
 * - Alternancia de visibilidad de contraseña
 * - Rate limiting con countdown
 * - Redirección automática post-login
 */
export function LoginForm() {
  const router = useRouter()
  const { setAccessToken, setUser } = useAuthStore()
  
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRateLimited, setIsRateLimited] = useState(false)
  const [rateLimitCountdown, setRateLimitCountdown] = useState(0)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const [isExiting, setIsExiting] = useState(false)

  // Detectar preferencia de movimiento reducido
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setValue,
    setFocus
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur' // Validación solo en blur, no durante escritura
  })

  /**
   * Maneja el submit del formulario
   * Envía credenciales al backend y procesa la respuesta
   */
  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true)

    try {
      const response = await login(data.username, data.password)

      // Almacenar access token y datos de usuario
      setAccessToken(response.access_token)
      setUser({
        ...response.user,
        createdAt: new Date(response.user.createdAt),
        lastLoginAt: response.user.lastLoginAt ? new Date(response.user.lastLoginAt) : undefined,
      })
      // Animación de salida antes de redireccionar
      setIsExiting(true)
      setTimeout(() => {
        router.push('/dashboard')
      }, prefersReducedMotion ? 0 : 300)
    } catch (error: unknown) {
      // Type guard para verificar si es un error de Axios
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status: number; data?: { retry_after?: number } } }
        const status = axiosError.response?.status
        const errorData = axiosError.response?.data

        switch (status) {
          case 401:
            // Credenciales inválidas
            toast.error('Usuario o contraseña incorrectos')
            setValue('password', '') // Limpiar password
            setFocus('password') // Devolver foco a password
            break

          case 429:
            // Rate limiting
            const retryAfter = errorData?.retry_after || 300
            toast.warning('Demasiados intentos. Espera unos minutos')
            setIsRateLimited(true)
            setRateLimitCountdown(retryAfter)
            
            // Countdown timer
            const interval = setInterval(() => {
              setRateLimitCountdown((prev) => {
                if (prev <= 1) {
                  clearInterval(interval)
                  setIsRateLimited(false)
                  return 0
                }
                return prev - 1
              })
            }, 1000)
            break

          case 422:
            // Error de validación del servidor
            toast.error('Datos de entrada inválidos')
            break

          case 500:
          case 503:
            // Error del servidor
            toast.error('No pudimos conectar con el servidor')
            break

          default:
            toast.error('Ocurrió un error inesperado')
        }
      } else {
        // Error de red (sin respuesta del servidor)
        toast.error('No pudimos conectar con el servidor')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * Determina si el botón de submit debe estar deshabilitado
   */
  const isButtonDisabled = !isValid || isSubmitting || isRateLimited

  return (
    <motion.div
      className="w-full max-w-md rounded-2xl bg-white/[0.05] backdrop-blur-xl border border-white/10 p-8 shadow-2xl"
      initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
      animate={prefersReducedMotion ? {} : isExiting ? { opacity: 0, scale: 0.95 } : { opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <Logo />
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Campo Username */}
        <div className="space-y-1.5">
          <Label htmlFor="username" className="text-sm text-white/50 font-medium">Nombre de usuario</Label>
          <Input
            id="username"
            type="text"
            autoComplete="username"
            placeholder="usuario@ejemplo.com"
            className={`bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:border-violet-500/50 focus:bg-white/8 transition-all duration-200 ${errors.username ? 'border-red-500/60' : ''}`}
            {...register('username')}
          />
          {errors.username && (
            <p className="text-sm text-red-400" role="alert">
              {errors.username.message}
            </p>
          )}
        </div>

        {/* Campo Password */}
        <div className="space-y-1.5">
          <Label htmlFor="password" className="text-sm text-white/50 font-medium">Contraseña</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder="••••••••"
              className={`bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:border-violet-500/50 focus:bg-white/8 pr-10 transition-all duration-200 ${errors.password ? 'border-red-500/60' : ''}`}
              {...register('password')}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {errors.password && (
            <p className="text-sm text-red-400" role="alert">
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Botón Submit */}
        <motion.div
          whileHover={!isButtonDisabled && !prefersReducedMotion ? { scale: 1.01 } : {}}
          whileTap={!isButtonDisabled && !prefersReducedMotion ? { scale: 0.98 } : {}}
        >
          <Button
            type="submit"
            className={`w-full py-2.5 font-semibold transition-all duration-200 ${
              isButtonDisabled
                ? 'bg-white/8 text-white/25 cursor-not-allowed border-white/5'
                : 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:shadow-lg hover:shadow-violet-500/25 text-white border-0'
            }`}
            disabled={isButtonDisabled}
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Iniciando sesión...
              </span>
            ) : isRateLimited ? (
              `Espera ${rateLimitCountdown}s`
            ) : (
              'Iniciar sesión'
            )}
          </Button>
        </motion.div>
      </form>

      {/* Nota de acceso restringido */}
      <p className="mt-6 text-center text-xs text-white/20">
        El acceso está restringido. Contacta al administrador para obtener tus credenciales.
      </p>
    </motion.div>
  )
}
