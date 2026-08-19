/**
 * Bill print view — renders the bill layout matching the reference template.
 */
import JsBarcode from 'jsbarcode';
import { QRCodeSVG } from 'qrcode.react';
import { useEffect, useRef } from 'react';
import { formatVND, formatWeight } from '../../../lib/format';
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

  const totalQty = bill.contents?.reduce((sum, l) => sum + l.quantity, 0) || 0;
  const totalWeight = bill.contents?.reduce((sum, l) => sum + l.weight_kg, 0) || 0;

  const renderParty = (party) => (
    <>
      <div className="bill-party-row"><span className="label">Họ tên:</span> {party.name}</div>
      <div className="bill-party-row"><span className="label">Địa chỉ:</span> {party.address_detail}</div>
      <div className="bill-party-row"><span className="label">Phường/Xã:</span> {party.ward_name}</div>
      <div className="bill-party-row"><span className="label">Tỉnh/TP:</span> {party.province_name}</div>
      <div className="bill-party-row"><span className="label">Điện thoại:</span> {party.phone}</div>
    </>
  );

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
          {bill.sender?.code && (
            <div className="bill-customer-code">Mã KH: {bill.sender.code}</div>
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
          {renderParty(bill.sender)}
        </div>
        <div className="bill-party">
          <div className="bill-party-title">{t('bills.receiver').toUpperCase()}</div>
          {renderParty(bill.receiver)}
        </div>
      </div>
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
      <div className="bill-weight-note">
        Cân nặng thực tế: {formatWeight(bill.actual_weight_kg)} | Cân nặng quy đổi: {formatWeight(bill.chargeable_weight_kg)}
      </div>

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
          <div className="bill-checkbox-row" style={{ marginTop: 8 }}>
            <span className={`bill-checkbox ${bill.is_insurance_required ? 'checked' : ''}`} />
            <span>Bảo hiểm bưu gửi</span>
          </div>
        </div>
        <div className="bill-fees">
          <div className="bill-section-title">CƯỚC PHÍ</div>
          <div className="bill-fee-row"><span>Cước chính</span><span>{formatVND(bill.fee.fee_main)}</span></div>
          <div className="bill-fee-row"><span>Phí bảo hiểm</span><span>{formatVND(bill.fee.fee_insurance)}</span></div>
          <div className="bill-fee-row"><span>Phụ phí khác</span><span>{formatVND(bill.fee.fee_other)}</span></div>
          <div className="bill-fee-row"><span>VAT</span><span>{formatVND(bill.fee.fee_vat)}</span></div>
          <div className="bill-fee-row bill-fee-total"><span>Tổng cộng</span><span>{formatVND(bill.fee.fee_total)}</span></div>
          <div className="bill-fee-row"><span>Thu hộ COD</span><span>{formatVND(bill.cod_amount)}</span></div>
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
