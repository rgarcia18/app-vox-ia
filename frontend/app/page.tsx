import { LoginForm } from '@/components/shared/LoginForm'
import { AnimatedBackground } from '@/components/shared/AnimatedBackground'

/**
 * Página de Login (Home)
 *
 * Punto de entrada de la aplicación VoxIA.
 * Renderiza el formulario de autenticación con fondo oscuro animado.
 */
export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-[#080b10]">
      <AnimatedBackground />
      <LoginForm />
    </main>
  )
}
