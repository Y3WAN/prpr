import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../services/authApi';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { showToast } from '../components/common/Toast';

const SignupPage = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [form, setForm] = useState({ email: '', password: '', nickname: '', role: 'customer' });
  const [loading, setLoading] = useState(false);

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authApi.signup(form);
      const { data } = await authApi.login({ email: form.email, password: form.password });
      login(data.access_token, data.user);
      showToast('회원가입이 완료되었습니다!', 'success');
      navigate('/');
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? '회원가입에 실패했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2 className="auth-title">회원가입</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <Input
            label="이메일"
            type="email"
            value={form.email}
            onChange={update('email')}
            placeholder="이메일을 입력하세요"
            required
          />
          <Input
            label="비밀번호 (8자 이상)"
            type="password"
            value={form.password}
            onChange={update('password')}
            placeholder="비밀번호를 입력하세요"
            minLength={8}
            required
          />
          <Input
            label="닉네임"
            value={form.nickname}
            onChange={update('nickname')}
            placeholder="닉네임을 입력하세요"
            required
          />
          <div className="input-group">
            <label className="input-label">역할</label>
            <select className="input" value={form.role} onChange={update('role')}>
              <option value="customer">손님</option>
              <option value="owner">사장님</option>
            </select>
          </div>
          <Button type="submit" fullWidth disabled={loading}>
            {loading ? '가입 중...' : '회원가입'}
          </Button>
        </form>
        <p className="auth-link">
          이미 계정이 있으신가요? <Link to="/login">로그인</Link>
        </p>
      </div>
    </div>
  );
};

export default SignupPage;
