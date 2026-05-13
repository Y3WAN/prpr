import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../services/authApi';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { showToast } from '../components/common/Toast';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const validateEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateEmail(email)) {
      showToast('올바른 이메일 형식을 입력해주세요. (예: example@email.com)', 'error');
      return;
    }
    setLoading(true);
    try {
      const { data } = await authApi.login({ email, password });
      login(data.access_token, data.user);
      navigate('/');
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? '로그인에 실패했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2 className="auth-title">로그인</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <Input
            label="이메일"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="이메일을 입력하세요"
            required
          />
          <Input
            label="비밀번호"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="비밀번호를 입력하세요"
            required
          />
          <Button type="submit" fullWidth disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </Button>
        </form>
        <p className="auth-link">
          계정이 없으신가요? <Link to="/signup">회원가입</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
