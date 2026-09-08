/**
 * Zod validation schema for the bill creation form.
 * All error messages in Vietnamese.
 */
import { z } from 'zod';

import { CARGO_TYPES } from './contentTypes';

const phoneRegex = /^\+?[0-9 -]{8,20}$/;

const partySchema = z.object({
  customer_id: z.number().nullable().optional(),
  name: z.string().min(1, 'Trường này là bắt buộc.'),
  phone: z
    .string()
    .min(1, 'Trường này là bắt buộc.')
    .regex(phoneRegex, 'Số điện thoại không hợp lệ.'),
  address_detail: z.string().min(1, 'Trường này là bắt buộc.'),
  province_code: z.string().min(1, 'Trường này là bắt buộc.'),
  province_name: z.string().min(1, 'Trường này là bắt buộc.'),
  ward_code: z.string().min(1, 'Trường này là bắt buộc.'),
  ward_name: z.string().min(1, 'Trường này là bắt buộc.'),
});

const contentLineSchema = z.object({
  cargo_type: z.enum(CARGO_TYPES, {
    required_error: 'Vui lòng chọn loại hàng.',
    invalid_type_error: 'Vui lòng chọn loại hàng.',
  }),
  description: z.string().min(1, 'Trường này là bắt buộc.'),
  quantity: z.number().min(1, 'Giá trị phải lớn hơn 0.'),
  weight_kg: z.number().min(0, 'Giá trị không được âm.'),
  length_cm: z.number().min(0, 'Giá trị không được âm.').nullable().optional(),
  width_cm: z.number().min(0, 'Giá trị không được âm.').nullable().optional(),
  height_cm: z.number().min(0, 'Giá trị không được âm.').nullable().optional(),
  images: z.array(z.string()).max(3, 'Tối đa 3 ảnh cho mỗi dòng.').default([]),
  metadata: z.record(z.string(), z.any()).default({}),
});

const feeSchema = z
  .object({
    fee_main: z.number().min(0, 'Giá trị không được âm.'),
    fee_insurance: z.number().min(0, 'Giá trị không được âm.'),
    fee_other: z.number().min(0, 'Giá trị không được âm.'),
    fee_vat: z.number().min(0, 'Giá trị không được âm.'),
    fee_total: z.number().min(0, 'Giá trị không được âm.'),
  })
  .refine(
    (data) =>
      Math.abs(
        data.fee_total -
          (data.fee_main + data.fee_insurance + data.fee_other + data.fee_vat),
      ) < 1,
    { message: 'Tổng cước không khớp với tổng các khoản.', path: ['fee_total'] },
  );

export const billCreateSchema = z.object({
  sender: partySchema,
  receiver: partySchema,
  contents: z.array(contentLineSchema).min(1, 'Phiếu gửi phải có ít nhất một dòng nội dung.'),
  note: z.string().optional(),
  fee: feeSchema,
  payer: z.enum(['sender', 'receiver'], {
    required_error: 'Trường này là bắt buộc.',
  }),
});

export { partySchema, contentLineSchema, feeSchema };
