import { z } from 'zod'

/**
 * Esquema de validación para el formulario de login
 * 
 * Reglas de validación:
 * - username: 3-50 caracteres, alfanumérico + ._@-
 * - password: 6-100 caracteres, sin restricciones de caracteres
 */
export const loginSchema = z.object({
  username: z
    .string()
    .min(3, 'Mínimo 3 caracteres')
    .max(50, 'Máximo 50 caracteres')
    .regex(/^[a-zA-Z0-9._@-]+$/, 'Usuario inválido'),
  password: z
    .string()
    .min(6, 'Mínimo 6 caracteres')
    .max(100, 'Máximo 100 caracteres')
})

/**
 * Tipo TypeScript inferido del esquema de validación
 */
export type LoginFormData = z.infer<typeof loginSchema>
