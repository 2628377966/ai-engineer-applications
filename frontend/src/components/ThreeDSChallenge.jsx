import React, { useState, useEffect } from 'react';
import './ThreeDSChallenge.css';

function ThreeDSChallenge({ transactionData, onVerificationComplete, onCancel }) {
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes countdown
  const [attempts, setAttempts] = useState(0);
  const maxAttempts = 3;

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setError('验证码已过期，请重新发起支付');
    }
  }, [timeLeft]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (attempts >= maxAttempts) {
      setError('验证次数已用完，请重新发起支付');
      return;
    }

    if (!verificationCode || verificationCode.length !== 6) {
      setError('请输入6位验证码');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/3ds-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transaction_id: transactionData.transaction_id,
          verification_code: verificationCode,
          card_number: transactionData.card_number
        })
      });

      const result = await response.json();

      if (result.success) {
        onVerificationComplete(result);
      } else {
        setAttempts(prev => prev + 1);
        setError(result.message || '验证失败，请重试');
        setVerificationCode('');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    onCancel();
  };

  return (
    <div className="three-ds-container">
      <div className="three-ds-card">
        <div className="three-ds-header">
          <div className="bank-logo">
            <div className="logo-placeholder">Mock Bank</div>
          </div>
          <div className="three-ds-title">3D Secure 验证</div>
        </div>

        <div className="three-ds-content">
          <div className="security-badge">
            <span className="shield-icon">🔒</span>
            <span>安全验证</span>
          </div>

          <div className="transaction-info">
            <h3>交易验证</h3>
            <p>为了您的账户安全，请完成银行验证</p>
          </div>

          <div className="amount-display">
            <span className="amount-label">交易金额</span>
            <span className="amount-value">¥{transactionData.amount}</span>
          </div>

          <div className="merchant-info">
            <span className="merchant-label">商户</span>
            <span className="merchant-value">Smart Checkout</span>
          </div>

          <form onSubmit={handleSubmit} className="verification-form">
            <div className="form-group">
              <label htmlFor="verification-code">银行验证码</label>
              <input
                type="text"
                id="verification-code"
                className="verification-input"
                placeholder="请输入6位验证码"
                value={verificationCode}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setVerificationCode(value);
                }}
                maxLength={6}
                disabled={isLoading || timeLeft <= 0}
                autoFocus
              />
              <div className="input-hint">
                请输入您手机收到的6位验证码
              </div>
            </div>

            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}

            <div className="timer-display">
              <span className="timer-icon">⏱️</span>
              <span className="timer-text">剩余时间: {formatTime(timeLeft)}</span>
            </div>

            <div className="attempts-info">
              尝试次数: {attempts}/{maxAttempts}
            </div>

            <div className="button-group">
              <button
                type="submit"
                className="verify-button"
                disabled={isLoading || timeLeft <= 0 || attempts >= maxAttempts}
              >
                {isLoading ? '验证中...' : '确认验证'}
              </button>
              <button
                type="button"
                className="cancel-button"
                onClick={handleCancel}
                disabled={isLoading}
              >
                取消
              </button>
            </div>
          </form>

          <div className="security-tips">
            <h4>安全提示</h4>
            <ul>
              <li>验证码仅用于本次交易验证</li>
              <li>请勿向任何人透露验证码</li>
              <li>验证码有效期为5分钟</li>
            </ul>
          </div>
        </div>

        <div className="three-ds-footer">
          <div className="footer-text">
            3D Secure 2.0 | Mock Bank | 安全支付保障
          </div>
        </div>
      </div>
    </div>
  );
}

export default ThreeDSChallenge;