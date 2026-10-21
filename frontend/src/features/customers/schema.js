/**
 * Zod validation schema for the customer create/edit form.
 *
 * Phone is optional but must be a Vietnamese mobile-shaped 10-digit number
 * starting with 0 when provided. The backend allows duplicate phones on
 * purpose, so "already exists" is a warning in the form, not a schema rule.
 */
import { z } from 'zod';

const phoneRegex = /^0\d{9}$/;

export const customerFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Tên khách hàng là bắt buộc.')
    .max(255, 'Tên khách hàng quá dài.'),
  phone: z
    .string()
    .trim()
    .optional()
    .refine(
      (value) => !value || phoneRegex.test(value),
      'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.',
    ),
  customer_type: z.enum(['retail', 'shop', 'enterprise']),
  address_detail: z.string().optional(),
  province_code: z.string().optional(),
  ward_code: z.string().optional(),
  is_active: z.boolean().optional(),
});

export default customerFormSchema;
