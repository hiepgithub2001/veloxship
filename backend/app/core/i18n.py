"""Vietnamese error-message catalogue keyed by error_code."""

_MESSAGES: dict[str, str] = {
    # Auth
    "INVALID_CREDENTIALS": "Tên đăng nhập hoặc mật khẩu không đúng.",
    "TOKEN_EXPIRED": "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
    "TOKEN_INVALID": "Token không hợp lệ.",
    "UNAUTHORIZED": "Bạn chưa đăng nhập.",
    "FORBIDDEN": "Bạn không có quyền thực hiện thao tác này.",
    "USER_INACTIVE": "Tài khoản đã bị vô hiệu hoá.",

    # Bills
    "BILL_NOT_FOUND": "Không tìm thấy phiếu gửi.",
    "FEE_TOTAL_MISMATCH": "Tổng cước không khớp với tổng các khoản.",
    "INVALID_STATUS_TRANSITION": "Chuyển trạng thái không hợp lệ.",
    "CANCELLATION_REASON_REQUIRED": "Cần nhập lý do huỷ.",
    "DELIVERED_TO_NAME_REQUIRED": "Cần nhập tên người nhận khi giao hàng.",
    "CANNOT_CANCEL_IN_TRANSIT": "Không thể huỷ phiếu đang vận chuyển hoặc đã giao.",
    "TIER_SCOPE_MISMATCH": "Dịch vụ không phù hợp với loại hàng.",
    "TIER_NOT_FOUND": "Không tìm thấy loại dịch vụ.",

    # Customers
    "CUSTOMER_NOT_FOUND": "Không tìm thấy khách hàng.",
    "CUSTOMER_CODE_EXISTS": "Mã khách hàng đã tồn tại.",
    "CUSTOMER_CODE_IMMUTABLE": "Không thể thay đổi mã khách hàng.",

    # Validation
    "VALIDATION_ERROR": "Dữ liệu không hợp lệ.",
    "CONTENT_LINES_REQUIRED": "Phiếu gửi phải có ít nhất một dòng nội dung.",

    # Generic
    "INTERNAL_ERROR": "Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
}


def get_message(error_code: str) -> str:
    """Return the Vietnamese message for the given error code, or a fallback."""
    return _MESSAGES.get(error_code, _MESSAGES["INTERNAL_ERROR"])
