/**
 * Zod validation schema for the customer edit form.
 */
import { z } from 'zod';

const phoneRegex = /^0\d{9}$/;

export const customerFormSchema = z.object({
  name: z.string().min(1, 'Tên khách hàng là bắt buộc.').max(255, 'Tên quá dài.'),
  phone: z
    .string()
    .optional()
    .refine((v) => !v || phoneRegex.test(v), 'Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0'),
  customer_type: z.enum(['retail', 'shop', 'enterprise']),
  address_detail: z.string().optional(),
  province_code: z.string().optional().or(z.literal('')),
  ward_code: z.string().optional().or(z.literal('')),
  is_active: z.boolean(),
});
