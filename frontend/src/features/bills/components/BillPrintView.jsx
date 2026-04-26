/**
 * Bill print view — renders the bill layout matching the reference template.
 */
import JsBarcode from 'jsbarcode';
import { QRCodeSVG } from 'qrcode.react';
import { useEffect, useRef } from 'react';
import { formatVND, formatWeight, formatViDate } from '../../../lib/format';
import { t } from '../../../i18n/vi';
import logo from '../../../assets/logo.png';
import './BillPrintView.css';

export function BillPrintView({ bill }) {
  const barcodeRef = useRef(null);

  useEffect(() => {
    if (barcodeRef.current && bill?.tracking_number) {
      JsBarcode(barcodeRef.current, bill.tracking_number, {
        format: 'CODE128',
        width: 1.5,
        height: 50,
        displayValue: false,
      });
    }
  }, [bill?.tracking_number]);

  if (!bill) return null;

  const trackingUrl = `https://newlinks.vn/tra-cuu/${bill.tracking_number}`;
  const now = new Date();
  const day = String(now.getDate()).padStart(2, '0');
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const year = now.getFullYear();

  // Calculate totals
  const totalQty = bill.contents?.reduce((sum, l) => sum + l.quantity, 0) || 0;
  const totalWeight = bill.contents?.reduce((sum, l) => sum + l.weight_kg, 0) || 0;

  const statusMap = {
    da_tao: t('status.da_tao'),
    da_lay_hang: t('status.da_lay_hang'),
    dang_van_chuyen: t('status.dang_van_chuyen'),
    da_giao: t('status.da_giao'),
    hoan_tra: t('status.hoan_tra'),
    huy: t('status.huy'),
  };

  return (
    <div className="bill-print">
      {/* Header */}
      <div className="bill-header">
        <div className="bill-header-left">
          <img src={logo} alt="Logo" className="bill-logo" />
        </div>
        <div className="bill-header-center">
          <h1>{t('print.title')}</h1>
          <div className="bill-tracking-number">{bill.tracking_number}</div>
          {bill.customer_code && (
            <div className="bill-customer-code">Mã KH: {bill.customer_code}</div>
          )}
        </div>
        <div className="bill-header-right">
          <svg ref={barcodeRef} className="bill-barcode" />
          <QRCodeSVG value={trackingUrl} size={72} className="bill-qr" />
        </div>
      </div>

      {/* Parties */}
      <div className="bill-parties">
        <div className="bill-party">
          <div className="bill-party-title">{t('bills.sender').toUpperCase()}</div>
          <div className="bill-party-row"><span className="label">Họ tên:</span> {bill.sender.name}</div>
          <div className="bill-party-row"><span className="label">Địa chỉ:</span> {bill.sender.address}</div>
          <div className="bill-party-row"><span className="label">Quận/Huyện:</span> {bill.sender.district}</div>
          <div className="bill-party-row"><span className="label">Tỉnh/TP:</span> {bill.sender.province}</div>
          <div className="bill-party-row"><span className="label">Điện thoại:</span> {bill.sender.phone}</div>
        </div>
        <div className="bill-party">
          <div className="bill-party-title">{t('bills.receiver').toUpperCase()}</div>
          <div className="bill-party-row"><span className="label">Họ tên:</span> {bill.receiver.name}</div>
          <div className="bill-party-row"><span className="label">Địa chỉ:</span> {bill.receiver.address}</div>
          <div className="bill-party-row"><span className="label">Quận/Huyện:</span> {bill.receiver.district}</div>
          <div className="bill-party-row"><span className="label">Tỉnh/TP:</span> {bill.receiver.province}</div>
          <div className="bill-party-row"><span className="label">Điện thoại:</span> {bill.receiver.phone}</div>
        </div>
      </div>

      {/* Content lines */}
      <div className="bill-section-title">NỘI DUNG GÓI HÀNG</div>
      <table className="bill-content-table">
        <thead>
          <tr>
            <th>STT</th>
            <th>Mô tả</th>
            <th>Số lượng</th>
            <th>Trọng lượng</th>
            <th>Kích thước</th>
          </tr>
        </thead>
        <tbody>
          {bill.contents?.map((line, i) => (
            <tr key={i}>
              <td>{line.line_no || i + 1}</td>
              <td>{line.description}</td>
              <td className="num">{line.quantity}</td>
              <td className="num">{formatWeight(line.weight_kg)}</td>
              <td>
                {[line.length_cm, line.width_cm, line.height_cm].filter(Boolean).join(' × ')}
                {(line.length_cm || line.width_cm || line.height_cm) ? ' cm' : ''}
              </td>
            </tr>
          ))}
          <tr className="total-row">
            <td colSpan={2}><strong>Tổng cộng</strong></td>
            <td className="num"><strong>{totalQty}</strong></td>
            <td className="num"><strong>{formatWeight(totalWeight)}</strong></td>
            <td></td>
          </tr>
        </tbody>
      </table>

      {/* Service + Fees */}
      <div className="bill-service-fees">
        <div className="bill-service">
          <div className="bill-section-title">LOẠI HÀNG & DỊCH VỤ</div>
          <div className="bill-checkbox-row">
            <span className={`bill-checkbox ${bill.cargo_type === 'document' ? 'checked' : ''}`} />
            <span>Tài liệu</span>
          </div>
          <div className="bill-checkbox-row">
            <span className={`bill-checkbox ${bill.cargo_type === 'goods' ? 'checked' : ''}`} />
            <span>Hàng hóa</span>
          </div>
          <div style={{ marginTop: 8, fontWeight: 600 }}>{bill.service_tier_code}</div>
        </div>
        <div className="bill-fees">
          <div className="bill-section-title">CƯỚC PHÍ</div>
          <div className="bill-fee-row"><span>Cước chính</span><span>{formatVND(bill.fee.fee_main)}</span></div>
          <div className="bill-fee-row"><span>Phụ phí xăng dầu</span><span>{formatVND(bill.fee.fee_fuel_surcharge)}</span></div>
          <div className="bill-fee-row"><span>Phụ phí khác</span><span>{formatVND(bill.fee.fee_other_surcharge)}</span></div>
          <div className="bill-fee-row"><span>VAT</span><span>{formatVND(bill.fee.fee_vat)}</span></div>
          <div className="bill-fee-row bill-fee-total"><span>Tổng cộng</span><span>{formatVND(bill.fee.fee_total)}</span></div>
        </div>
      </div>

      {/* Payer */}
      <div className="bill-payer">
        <div className="bill-checkbox-row">
          <span className={`bill-checkbox ${bill.payer === 'sender' ? 'checked' : ''}`} />
          <span>{t('bills.payerSender')}</span>
        </div>
        <div className="bill-checkbox-row">
          <span className={`bill-checkbox ${bill.payer === 'receiver' ? 'checked' : ''}`} />
          <span>{t('bills.payerReceiver')}</span>
        </div>
      </div>

      {/* Signatures */}
      <div className="bill-signatures">
        <div className="bill-sig">
          <div className="bill-sig-title">{t('print.senderSignature')}</div>
          <div className="bill-sig-date">…ngày {day} tháng {month} năm {year}</div>
          <div className="bill-sig-line" />
        </div>
        <div className="bill-sig">
          <div className="bill-sig-title">{t('print.carrierSignature')}</div>
          <div className="bill-sig-date">…ngày {day} tháng {month} năm {year}</div>
          <div className="bill-sig-line" />
        </div>
        <div className="bill-sig">
          <div className="bill-sig-title">{t('print.receiverSignature')}</div>
          <div className="bill-sig-date">…ngày {day} tháng {month} năm {year}</div>
          <div className="bill-sig-line" />
        </div>
      </div>

      {/* Footer */}
      <div className="bill-footer">
        <strong>Vận Chuyển HN</strong> | Hotline: 0972 160 610 | Website: newlinks.vn | Email: info@newlinks.vn
        <br />
        {t('print.disclaimer')}
      </div>
    </div>
  );
}

export default BillPrintView;
