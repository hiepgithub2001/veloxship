/**
 * useBillDraft — shared react-hook-form context for the mobile bill creation wizard.
 * Uses the same Zod schema as the desktop form.
 */
import { createContext, useContext } from 'react';
import { useForm, FormProvider, useFormContext } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { billCreateSchema } from '../schema';

const BillDraftContext = createContext(null);

const defaultValues = {
  customer_id: null,
  customer_code: null,
  sender: { name: '', address: '', district: '', province: '', phone: '' },
  receiver: { name: '', address: '', district: '', province: '', phone: '' },
  contents: [
    {
      description: '',
      quantity: 1,
      weight_kg: 0,
      length_cm: null,
      width_cm: null,
      height_cm: null,
    },
  ],
  cargo_type: 'goods',
  service_tier_code: '',
  fee: { fee_main: 0, fee_fuel_surcharge: 0, fee_other_surcharge: 0, fee_vat: 0, fee_total: 0 },
  payer: 'sender',
};

/**
 * Hook that returns the react-hook-form instance configured with the bill schema.
 */
export function useBillDraft() {
  return useForm({
    resolver: zodResolver(billCreateSchema),
    defaultValues,
    mode: 'onTouched',
  });
}

/**
 * Provider wrapping children in FormProvider so step components can call useFormContext().
 */
export function BillDraftProvider({ methods, children }) {
  return (
    <BillDraftContext.Provider value={methods}>
      <FormProvider {...methods}>{children}</FormProvider>
    </BillDraftContext.Provider>
  );
}

/**
 * Hook to access the form context from within step components.
 */
export function useBillFormContext() {
  return useFormContext();
}

export { defaultValues };
