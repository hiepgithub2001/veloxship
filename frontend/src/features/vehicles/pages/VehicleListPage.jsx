/**
 * VehicleListPage — Main page for vehicle fleet management (CRUD).
 * Composes VehicleSearchBar, VehicleFilters, VehicleTable, and VehicleFormModal.
 */
import { useState, useCallback } from 'react';
import { Button, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { getVehicles, updateVehicle } from '../../../api/vehicles';
import VehicleSearchBar from '../components/VehicleSearchBar';
import VehicleFilters from '../components/VehicleFilters';
import VehicleTable from '../components/VehicleTable';
import VehicleFormModal from '../components/VehicleFormModal';

export function VehicleListPage() {
  const queryClient = useQueryClient();

  // Search & filter state
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState(null);
  const [vehicleType, setVehicleType] = useState(null);

  // Pagination state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);

  // Fetch vehicles
  const { data, isLoading } = useQuery({
    queryKey: ['vehicles', { page, pageSize, search, status, vehicleType }],
    queryFn: () =>
      getVehicles({
        page,
        pageSize,
        search: search || undefined,
        status: status || undefined,
        vehicleType: vehicleType || undefined,
      }),
  });

  // Soft-delete mutation (set status to 'inactive')
  const deleteMutation = useMutation({
    mutationFn: (id) => updateVehicle(id, { status: 'inactive' }),
    onSuccess: () => {
      message.success('Đã vô hiệu hóa xe thành công');
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
    },
    onError: (err) => {
      message.error(err.response?.data?.message || 'Lỗi khi vô hiệu hóa xe');
    },
  });

  // Handlers
  const handleSearch = useCallback((value) => {
    setSearch(value);
    setPage(1);
  }, []);

  const handleStatusChange = useCallback((value) => {
    setStatus(value);
    setPage(1);
  }, []);

  const handleVehicleTypeChange = useCallback((value) => {
    setVehicleType(value);
    setPage(1);
  }, []);

  const handlePageChange = useCallback((newPage, newPageSize) => {
    setPage(newPage);
    setPageSize(newPageSize);
  }, []);

  const handleEdit = useCallback((vehicle) => {
    setEditingVehicle(vehicle);
    setModalOpen(true);
  }, []);

  const handleDelete = useCallback(
    (vehicle) => {
      deleteMutation.mutate(vehicle.id);
    },
    [deleteMutation],
  );

  const handleCreate = useCallback(() => {
    setEditingVehicle(null);
    setModalOpen(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setModalOpen(false);
    setEditingVehicle(null);
  }, []);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Quản lý Đội xe</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Đăng ký xe mới
        </Button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <VehicleSearchBar onSearch={handleSearch} defaultValue={search} />
        <VehicleFilters
          status={status}
          vehicleType={vehicleType}
          onStatusChange={handleStatusChange}
          onVehicleTypeChange={handleVehicleTypeChange}
        />
      </div>

      <VehicleTable
        data={data?.items}
        loading={isLoading}
        page={page}
        pageSize={pageSize}
        total={data?.total}
        onPageChange={handlePageChange}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <VehicleFormModal
        open={modalOpen}
        onClose={handleModalClose}
        vehicle={editingVehicle}
      />
    </div>
  );
}

export default VehicleListPage;
