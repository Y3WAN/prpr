import { RouterProvider } from 'react-router-dom';
import { useEffect } from 'react';
import { router } from './router';
import { useAuthStore } from './stores/authStore';
import './index.css';

function App() {
  const { restoreSession } = useAuthStore();

  useEffect(() => {
    restoreSession();
  }, []);

  return <RouterProvider router={router} />;
}

export default App;
