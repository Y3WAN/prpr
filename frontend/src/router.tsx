import { createBrowserRouter, Navigate } from 'react-router-dom';
import { type ReactNode } from 'react';
import { useAuthStore } from './stores/authStore';
import { AppLayout } from './layouts/AppLayout';
import MainMapPage from './pages/MainMapPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import MyPage from './pages/MyPage';
import TruckManagePage from './pages/TruckManagePage';

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const OwnerRoute = ({ children }: { children: ReactNode }) => {
  const { user, isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== 'owner') return <Navigate to="/" replace />;
  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <MainMapPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'signup', element: <SignupPage /> },
      {
        path: 'my',
        element: <ProtectedRoute><MyPage /></ProtectedRoute>,
      },
      {
        path: 'owner/truck',
        element: <OwnerRoute><TruckManagePage /></OwnerRoute>,
      },
    ],
  },
]);
