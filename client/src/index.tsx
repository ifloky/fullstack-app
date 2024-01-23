import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { store } from './app/store';
import reportWebVitals from './reportWebVitals';
import { Paths } from './paths';
import { Login } from './pages/login';
import { Register } from './pages/register';
import './index.css';

const router = createBrowserRouter([
  {
    path: Paths.login,
    element: <Login />
  },
  {
    path: Paths.register,
    element: <Register />
  },
  {
    path: Paths.home,
    element: <h1>Employees</h1>
  },
  {
    path: Paths.login,
    element: <h1>Log in</h1>
  },
  {
    path: Paths.login,
    element: <h1>Log in</h1>
  },
])

const container = document.getElementById('root')!;
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <RouterProvider router={router}></RouterProvider>
    </Provider>
  </React.StrictMode>
);

reportWebVitals();
