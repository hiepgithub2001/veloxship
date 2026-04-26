/**
 * Vietnamese string catalogue — single source of truth for all UI text.
 * Usage: import { t } from '@/i18n/vi';  t('auth.login')
 */

const vi = {
  app: {
    name: 'VeloxShip',
    tagline: 'Quản Lý Phiếu Gửi Vận Chuyển',
  },
  auth: {
    login: 'Đăng nhập',
    logout: 'Đăng xuất',
    username: 'Tên đăng nhập',
    password: 'Mật khẩu',
    loginButton: 'Đăng nhập',
    loginFailed: 'Tên đăng nhập hoặc mật khẩu không đúng.',
    sessionExpired: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
  },
  layout: {
    bills: 'Phiếu Gửi',
    customers: 'Khách hàng',
    createBill: 'Tạo phiếu gửi',
    search: 'Tra cứu',
  },
  common: {
    save: 'Lưu',
    cancel: 'Huỷ',
    delete: 'Xoá',
    edit: 'Sửa',
    create: 'Tạo mới',
    search: 'Tìm kiếm',
    loading: 'Đang tải...',
    noData: 'Không có dữ liệu.',
    confirm: 'Xác nhận',
    back: 'Quay lại',
    actions: 'Thao tác',
    yes: 'Có',
    no: 'Không',
    close: 'Đóng',
    status: 'Trạng thái',
    createdAt: 'Ngày tạo',
    updatedAt: 'Ngày cập nhật',
    total: 'Tổng cộng',
    page: 'Trang',
    rowsPerPage: 'Dòng mỗi trang',
  },
  bills: {
    title: 'Danh sách phiếu gửi',
    create: 'Tạo phiếu gửi',
    detail: 'Chi tiết phiếu gửi',
    trackingNumber: 'Mã vận đơn',
    sender: 'Người gửi',
    receiver: 'Người nhận',
    senderName: 'Tên người gửi',
    senderAddress: 'Địa chỉ người gửi',
    senderDistrict: 'Quận/Huyện (gửi)',
    senderProvince: 'Tỉnh/TP (gửi)',
    senderPhone: 'SĐT người gửi',
    receiverName: 'Tên người nhận',
    receiverAddress: 'Địa chỉ người nhận',
    receiverDistrict: 'Quận/Huyện (nhận)',
    receiverProvince: 'Tỉnh/TP (nhận)',
    receiverPhone: 'SĐT người nhận',
    contents: 'Nội dung gói hàng',
    description: 'Mô tả',
    quantity: 'Số lượng',
    weight: 'Trọng lượng (kg)',
    length: 'Dài (cm)',
    width: 'Rộng (cm)',
    height: 'Cao (cm)',
    addLine: 'Thêm dòng',
    removeLine: 'Xoá dòng',
    cargoType: 'Loại hàng',
    document: 'Tài liệu',
    goods: 'Hàng hóa',
    serviceTier: 'Dịch vụ',
    domestic: 'Trong nước',
    international: 'Quốc tế',
    fees: 'Cước phí',
    feeMain: 'Cước chính',
    feeFuel: 'Phụ phí xăng dầu',
    feeOther: 'Phụ phí khác',
    feeVat: 'VAT',
    feeTotal: 'Tổng cộng',
    payer: 'Người thanh toán',
    payerSender: 'Người gửi thanh toán',
    payerReceiver: 'Người nhận thanh toán',
    customerCode: 'Mã KH',
    selectCustomer: 'Chọn khách hàng',
    saveAndPrint: 'Lưu & In phiếu',
    print: 'In phiếu',
    reprint: 'In lại',
    downloadPdf: 'Tải PDF',
    updateStatus: 'Cập nhật trạng thái',
    statusHistory: 'Lịch sử trạng thái',
    auditLog: 'Nhật ký kiểm toán',
    searchPlaceholder: 'Tìm theo mã VD, tên, SĐT...',
    notFound: 'Không tìm thấy phiếu gửi nào.',
    createSuccess: 'Tạo phiếu gửi thành công!',
    statusUpdateSuccess: 'Cập nhật trạng thái thành công!',
    feeTotalMismatch: 'Tổng cước không khớp với tổng các khoản.',
    deliveredToName: 'Tên người nhận hàng',
    cancellationReason: 'Lý do huỷ',
    note: 'Ghi chú',
  },
  status: {
    da_tao: 'Đã tạo',
    da_lay_hang: 'Đã lấy hàng',
    dang_van_chuyen: 'Đang vận chuyển',
    da_giao: 'Đã giao',
    hoan_tra: 'Hoàn trả',
    huy: 'Huỷ',
  },
  customers: {
    title: 'Danh sách khách hàng',
    create: 'Thêm mới',
    detail: 'Chi tiết khách hàng',
    customerCode: 'Mã KH',
    displayName: 'Tên hiển thị',
    address: 'Địa chỉ',
    district: 'Quận/Huyện',
    province: 'Tỉnh/TP',
    phone: 'Số điện thoại',
    isActive: 'Trạng thái',
    active: 'Đang hoạt động',
    inactive: 'Ngừng hoạt động',
    deactivate: 'Vô hiệu hoá',
    createSuccess: 'Tạo khách hàng thành công!',
    updateSuccess: 'Cập nhật khách hàng thành công!',
    notFound: 'Không tìm thấy khách hàng.',
    codeImmutable: 'Không thể thay đổi mã khách hàng.',
    searchPlaceholder: 'Tìm theo tên, mã KH, SĐT...',
  },
  validation: {
    required: 'Trường này là bắt buộc.',
    invalidPhone: 'Số điện thoại không hợp lệ.',
    positiveNumber: 'Giá trị phải lớn hơn 0.',
    nonNegativeNumber: 'Giá trị không được âm.',
    minContentLines: 'Phiếu gửi phải có ít nhất một dòng nội dung.',
  },
  print: {
    title: 'PHIẾU GỬI',
    signatureDate: 'ngày {dd} tháng {mm} năm {yyyy}',
    senderSignature: 'Người gửi ký tên',
    receiverSignature: 'Người nhận ký tên',
    carrierSignature: 'Nhân viên vận chuyển',
    disclaimer: 'Quý khách vui lòng kiểm tra hàng hóa trước khi ký nhận.',
  },
};

/**
 * Look up a nested key path like 'auth.login' → 'Đăng nhập'.
 * Returns the key itself if not found (makes missing keys visible in the UI).
 */
export function t(path) {
  const keys = path.split('.');
  let current = vi;
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return path;
    }
  }
  return current;
}

export default vi;
