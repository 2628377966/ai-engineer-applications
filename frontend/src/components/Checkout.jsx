import { useState, useEffect } from 'react'
import './Checkout.css'
import ThreeDSChallenge from './ThreeDSChallenge'

function Checkout() {
  const [formData, setFormData] = useState({
    amount: '',
    payment_method: 'credit_card',
    card_number: '',
    card_expiry_month: '',
    card_expiry_year: '',
    card_cvv: '',
    ip_country: 'CN',
    user_history: 0
  })
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showQRCode, setShowQRCode] = useState(false)
  const [showThreeDS, setShowThreeDS] = useState(false)
  const [threeDSTransaction, setThreeDSTransaction] = useState(null)
  const [countdown, setCountdown] = useState(300)
  const [paymentStatus, setPaymentStatus] = useState('pending')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  useEffect(() => {
    let timer
    if (showQRCode && countdown > 0) {
      timer = setInterval(() => {
        setCountdown(prev => prev - 1)
      }, 1000)
    } else if (countdown === 0 && showQRCode) {
      setPaymentStatus('expired')
      setShowQRCode(false)
    }
    return () => clearInterval(timer)
  }, [showQRCode, countdown])

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const handleMobilePayment = () => {
    setShowQRCode(true)
    setCountdown(300)
    setPaymentStatus('pending')
    
    setTimeout(() => {
      setPaymentStatus('success')
      setResult({
        status: 'success',
        transaction_id: `${formData.payment_method.toUpperCase()}_${Math.floor(Math.random() * 900000) + 100000}`,
        risk_score: 15,
        message: '支付成功'
      })
      setShowQRCode(false)
    }, 5000)
  }

  const handleThreeDSComplete = (verificationResult) => {
    setShowThreeDS(false)
    setResult({
      status: 'success',
      transaction_id: verificationResult.transaction_id,
      risk_score: threeDSTransaction?.risk_score || 0,
      message: verificationResult.message || '3DS验证成功，支付完成'
    })
  }

  const handleThreeDSCancel = () => {
    setShowThreeDS(false)
    setResult({
      status: 'cancelled',
      message: '3DS验证已取消'
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (formData.payment_method === 'credit_card') {
      if (!formData.card_number || formData.card_number.length < 13) {
        alert('请输入有效的卡号')
        return
      }
      if (!formData.card_expiry_month) {
        alert('请选择过期月份')
        return
      }
      if (!formData.card_expiry_year) {
        alert('请选择过期年份')
        return
      }
      if (!formData.card_cvv || formData.card_cvv.length < 3) {
        alert('请输入有效的CVV')
        return
      }
    }
    
    if (formData.payment_method === 'alipay' || formData.payment_method === 'wechat_pay') {
      handleMobilePayment()
      return
    }
    
    setLoading(true)
    
    try {
      const response = await fetch('/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          amount: parseFloat(formData.amount)
        })
      })
      
      const data = await response.json()
      
      if (data.status === 'pending_3ds') {
        setThreeDSTransaction({
          transaction_id: `3DS_${Math.floor(Math.random() * 900000) + 100000}`,
          amount: formData.amount,
          card_number: formData.card_number,
          risk_score: data.risk?.risk_score || 0
        })
        setShowThreeDS(true)
        setResult(data)
      } else {
        setResult(data)
      }
    } catch (error) {
      console.error('Error:', error)
      setResult({
        status: 'error',
        message: '网络错误，请稍后重试'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="checkout-container">
      {showThreeDS && threeDSTransaction && (
        <ThreeDSChallenge
          transactionData={threeDSTransaction}
          onVerificationComplete={handleThreeDSComplete}
          onCancel={handleThreeDSCancel}
        />
      )}
      
      {!showThreeDS && (
        <>
          <h1>智能支付收银台</h1>
      
      <form onSubmit={handleSubmit} className="checkout-form">
        <div className="form-group">
          <label htmlFor="amount">金额 (CNY)</label>
          <input
            type="number"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            required
            step="0.01"
            min="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="payment_method">支付方式</label>
          <select
            id="payment_method"
            name="payment_method"
            value={formData.payment_method}
            onChange={handleChange}
          >
            <option value="credit_card">信用卡</option>
            <option value="alipay">支付宝</option>
            <option value="wechat_pay">微信支付</option>
          </select>
        </div>

        {formData.payment_method === 'credit_card' && (
          <>
            <div className="form-group">
              <label htmlFor="card_number">卡号</label>
              <input
                type="text"
                id="card_number"
                name="card_number"
                value={formData.card_number}
                onChange={handleChange}
                placeholder="4111111111111111"
                maxLength={16}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="card_expiry_month">过期月份</label>
                <select
                  id="card_expiry_month"
                  name="card_expiry_month"
                  value={formData.card_expiry_month}
                  onChange={handleChange}
                >
                  <option value="">选择月份</option>
                  {Array.from({ length: 12 }, (_, i) => (
                    <option key={i + 1} value={String(i + 1).padStart(2, '0')}>
                      {String(i + 1).padStart(2, '0')}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="card_expiry_year">过期年份</label>
                <select
                  id="card_expiry_year"
                  name="card_expiry_year"
                  value={formData.card_expiry_year}
                  onChange={handleChange}
                >
                  <option value="">选择年份</option>
                  {Array.from({ length: 10 }, (_, i) => {
                    const year = new Date().getFullYear() + i
                    return (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    )
                  })}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="card_cvv">CVV</label>
              <input
                type="text"
                id="card_cvv"
                name="card_cvv"
                value={formData.card_cvv}
                onChange={handleChange}
                placeholder="123"
                maxLength={4}
              />
            </div>
          </>
        )}

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? '处理中...' : '支付'}
        </button>
      </form>

      {showQRCode && (
        <div className="qr-modal">
          <div className="qr-modal-content">
            <button className="qr-close" onClick={() => setShowQRCode(false)}>×</button>
            <h2>扫码支付</h2>
            <p className="payment-amount">¥{formData.amount}</p>
            <div className="qr-code-container">
              <div className="qr-code">
                {formData.payment_method === 'alipay' ? (
                  <div className="qr-placeholder alipay">
                    <div className="qr-icon">支付宝</div>
                    <div className="qr-pattern"></div>
                  </div>
                ) : (
                  <div className="qr-placeholder wechat">
                    <div className="qr-icon">微信</div>
                    <div className="qr-pattern"></div>
                  </div>
                )}
              </div>
            </div>
            <p className="payment-reminder">
              请使用{formData.payment_method === 'alipay' ? '支付宝' : '微信支付'}扫描二维码完成支付
            </p>
            <div className="countdown-timer">
              <span className="timer-icon">⏱️</span>
              <span className="timer-text">支付剩余时间: {formatTime(countdown)}</span>
            </div>
            <p className="payment-status">
              {paymentStatus === 'pending' && '等待支付...'}
              {paymentStatus === 'success' && '支付成功！'}
              {paymentStatus === 'expired' && '支付已过期，请重新发起支付'}
            </p>
          </div>
        </div>
      )}

      {result && (
        <div className={`result ${result.status}`}>
          <h3>支付结果: {result.status}</h3>
          <p>交易ID: {result.transaction_id || 'N/A'}</p>
          <p>风险评分: {result.risk_score || 0}/100</p>
          
          {result.risk && result.risk.llm_insight && (
            <div className="risk-info">
              <strong>风控分析:</strong> {result.risk.llm_insight}
            </div>
          )}
          
          {result.status === 'pending_3ds' && (
            <p className="pending-message">需要3DS验证，请完成银行验证</p>
          )}
          
          {result.status === 'error' && (
            <p className="error-message">{result.message}</p>
          )}
        </div>
      )}
        </>
      )}
    </div>
  )
}

export default Checkout