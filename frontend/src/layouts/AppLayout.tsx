import { Outlet, useNavigate } from 'react-router-dom';
import { useMapStore } from '../stores/mapStore';
import { SideDrawer } from './SideDrawer';
import { Toast } from '../components/common/Toast';

export const AppLayout = () => {
  const { openSidebar } = useMapStore();
  const navigate = useNavigate();

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1 className="app-logo" onClick={() => navigate('/')}>🚚 푸릉푸릉</h1>
        <button className="menu-btn" onClick={openSidebar} aria-label="메뉴">☰</button>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <SideDrawer />
      <Toast />
    </div>
  );
};
