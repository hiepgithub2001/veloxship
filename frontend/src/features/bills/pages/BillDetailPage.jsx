import { useParams } from 'react-router-dom';
import { BillDetailView } from '../components/BillDetailView';

export function BillDetailPage() {
  const { id } = useParams();
  return <BillDetailView id={id} />;
}

export default BillDetailPage;
