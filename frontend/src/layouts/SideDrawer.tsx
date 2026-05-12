import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useMapStore } from '../stores/mapStore';

export const SideDrawer = () => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const { isSidebarOpen, closeSidebar } = useMapStore();
  const navigate = useNavigate();

  const go = (path: string) => {
    navigate(path);
    closeSidebar();
  };

  if (!isSidebarOpen) return null;

  return (
    <div className="drawer-overlay" onClick={closeSidebar}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <button className="drawer__close" onClick={closeSidebar}>✕</button>

        {isAuthenticated ? (
          <>
            <div className="drawer__user">
              <p className="drawer__nickname">{user?.nickname}</p>
              <p className="drawer__role">{user?.role === 'owner' ? '사장님' : '손님'}</p>
            </div>
            <nav className="drawer__nav">
              <button onClick={() => go('/my')}>내 정보</button>
              {user?.role === 'owner' && (
                <button onClick={() => go('/owner/truck')}>내 가게 관리</button>
              )}
              <button onClick={() => { logout(); closeSidebar(); go('/'); }}>로그아웃</button>
            </nav>
          </>
        ) : (
          <nav className="drawer__nav">
            <button onClick={() => go('/login')}>로그인</button>
            <button onClick={() => go('/signup')}>회원가입</button>
          </nav>
        )}
      </div>
    </div>
  );
};
