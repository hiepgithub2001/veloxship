/**
 * Zod validation schema for the bill creation form.
 * All error messages in Vietnamese.
 */
import { z } from 'zod';

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
  description: z.string().min(1, 'Trường này là bắt buộc.'),
  quantity: z.number().min(1, 'Giá trị phải lớn hơn 0.'),
  weight_kg: z.number().min(0, 'Giá trị không được âm.'),
  length_cm: z.number().min(0, 'Giá trị không được âm.').nullable().optional(),
  width_cm: z.number().min(0, 'Giá trị không được âm.').nullable().optional(),
  height_cm: z.number().min(0, 'Giá trị không được âm.').nullable().optional(),
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
  cargo_type: z.enum(['document', 'goods'], {
    required_error: 'Trường này là bắt buộc.',
  }),
  service_tier_code: z.string().min(1, 'Trường này là bắt buộc.'),
  actual_weight_kg: z.number().min(0, 'Giá trị không được âm.'),
  contents: z.array(contentLineSchema).min(1, 'Phiếu gửi phải có ít nhất một dòng nội dung.'),
  is_insurance_required: z.boolean(),
  cod_amount: z.number().min(0, 'Giá trị không được âm.'),
  fee: feeSchema,
  payer: z.enum(['sender', 'receiver'], {
    required_error: 'Trường này là bắt buộc.',
  }),
});

export { partySchema, contentLineSchema, feeSchema };
