/**
 * Zod validation schema for the depot form.
 * All error messages in Vietnamese.
 */
import { z } from 'zod';

const codeRegex = /^[A-Z0-9]{3,20}$/;
const phoneRegex = /^0\d{9}$/;

export const depotFormSchema = z.object({
  code: z
    .string()
    .min(1, 'Mã bưu cục là bắt buộc.')
    .regex(codeRegex, 'Mã bưu cục phải gồm 3-20 ký tự in hoa hoặc số'),
  name: z
    .string()
    .min(1, 'Tên bưu cục là bắt buộc.')
    .max(255, 'Tên bưu cục phải từ 1 đến 255 ký tự'),
  phone: z
    .string()
    .min(1, 'Số điện thoại là bắt buộc.')
    .regex(phoneRegex, 'Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0'),
  address_detail: z
    .string()
    .min(1, 'Địa chỉ chi tiết là bắt buộc.')
    .max(500, 'Địa chỉ chi tiết phải từ 1 đến 500 ký tự'),
  ward_code: z.string().optional(),
});
