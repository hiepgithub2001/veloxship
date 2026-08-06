/**
 * DepotListPage — Main page for depot management (CRUD).
 * Composes DepotSearchBar, DepotTable, and DepotFormModal.
 */
import { useState, useCallback } from 'react';
import { Button, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { getDepots, updateDepot } from '../../../api/depots';
import DepotSearchBar from '../components/DepotSearchBar';
import DepotTable from '../components/DepotTable';
import DepotFormModal from '../components/DepotFormModal';

export function DepotListPage() {
  const queryClient = useQueryClient();

  // Search & filter state
  const [search, setSearch] = useState('');
  const [isActive, setIsActive] = useState(null);

  // Pagination state
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDepot, setEditingDepot] = useState(null);

  // Fetch depots
  const { data, isLoading } = useQuery({
    queryKey: ['depots', { page: pagination.current, pageSize: pagination.pageSize, search, isActive }],
    queryFn: () =>
      getDepots({
        page: pagination.current,
        pageSize: pagination.pageSize,
        search: search || undefined,
        isActive,
      }),
  });

  // Toggle active mutation
  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }) => updateDepot(id, { is_active }),
    onSuccess: () => {
      message.success('Cập nhật trạng thái thành công');
      queryClient.invalidateQueries({ queryKey: ['depots'] });
    },
    onError: (err) => {
      message.error(err.response?.data?.message || 'Lỗi khi cập nhật trạng thái');
    },
  });

  // Handlers
  const handleSearchChange = useCallback((value) => {
    setSearch(value);
    setPagination((prev) => ({ ...prev, current: 1 }));
  }, []);

  const handleFilterChange = useCallback((value) => {
    setIsActive(value);
    setPagination((prev) => ({ ...prev, current: 1 }));
  }, []);

  const handlePaginationChange = useCallback(({ current, pageSize }) => {
    setPagination({ current, pageSize });
  }, []);

  const handleEdit = useCallback((depot) => {
    setEditingDepot(depot);
    setModalOpen(true);
  }, []);

  const handleToggleActive = useCallback(
    (depot) => {
      toggleActiveMutation.mutate({ id: depot.id, is_active: !depot.is_active });
    },
    [toggleActiveMutation],
  );

  const handleCreate = useCallback(() => {
    setEditingDepot(null);
    setModalOpen(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setModalOpen(false);
    setEditingDepot(null);
  }, []);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Quản lý bưu cục</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Thêm mới
        </Button>
      </div>

      <DepotSearchBar onSearchChange={handleSearchChange} onFilterChange={handleFilterChange} />

      <DepotTable
        data={data}
        loading={isLoading}
        onEdit={handleEdit}
        onToggleActive={handleToggleActive}
        pagination={pagination}
        onPaginationChange={handlePaginationChange}
      />

      <DepotFormModal
        open={modalOpen}
        onClose={handleModalClose}
        depot={editingDepot}
      />
    </div>
  );
}

export default DepotListPage;
