/**
 * Zod validation schema for staff management.
 * All error messages in Vietnamese.
 */
import { z } from 'zod';

const usernameRegex = /^[a-z0-9._-]{3,50}$/;
const phoneRegex = /^0\d{9}$/;

export const employeeFormSchema = z.object({
  username: z
    .string()
    .min(1, 'Tên đăng nhập là bắt buộc.')
    .regex(usernameRegex, 'Tên đăng nhập phải gồm 3-50 ký tự thường, số hoặc . _ -'),
  full_name: z
    .string()
    .min(1, 'Họ tên là bắt buộc.')
    .max(255, 'Họ tên phải từ 1 đến 255 ký tự'),
  phone: z
    .union([z.string().regex(phoneRegex, 'SĐT phải gồm 10 chữ số, bắt đầu bằng 0'), z.literal('')])
    .optional()
    .transform((v) => (v ? v : undefined)),
  password: z
    .union([z.string().min(6, 'Mật khẩu phải có ít nhất 6 ký tự'), z.literal('')])
    .optional()
    .transform((v) => (v ? v : undefined)),
  role: z.string().min(1, 'Vai trò là bắt buộc.'),
  department: z.string().optional(),
  position: z.string().optional(),
  employee_code: z.string().optional(),
  depot_id: z.number().nullable().optional(),
});
