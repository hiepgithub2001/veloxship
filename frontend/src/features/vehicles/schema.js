/**
 * Zod validation schema for the vehicle form.
 * All error messages in Vietnamese.
 */
import { z } from 'zod';

export const vehicleFormSchema = z.object({
  license_plate: z
    .string()
    .min(1, 'Biển số xe là bắt buộc.'),
  vehicle_type: z
    .enum(['motorcycle', 'truck'], { errorMap: () => ({ message: "Loại xe phải là 'motorcycle' hoặc 'truck'." }) }),
  max_weight_kg: z
    .coerce.number({ invalid_type_error: 'Tải trọng phải là số.' })
    .positive('Tải trọng phải là số dương.'),
  max_volume_m3: z
    .coerce.number({ invalid_type_error: 'Thể tích phải là số.' })
    .positive('Thể tích phải là số dương.'),
  status: z
    .enum(['active', 'inactive', 'maintenance'], { errorMap: () => ({ message: "Trạng thái không hợp lệ." }) })
    .optional()
    .default('active'),
  driver_id: z.coerce.number().nullable().optional(),
  latest_depot_id: z.coerce.number().nullable().optional(),
  images: z.array(z.string()).default([]),
});
