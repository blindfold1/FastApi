const SwaggerUIBundle = window.SwaggerUIBundle;

SwaggerUIBundle({
  url: "http://localhost:8000/openapi.json",
  dom_id: "#swagger-ui",
  presets: [
    SwaggerUIBundle.presets.apis,
    SwaggerUIBundle.SwaggerUIStandalonePreset
  ],
  onComplete: () => {
    console.log('swagger-custom.js loaded successfully');

    // Перехватываем авторизацию через AccessToken
    const originalAuthorize = window.ui.authActions.authorize;
    window.ui.authActions.authorize = async (auth) => {
      const result = await originalAuthorize(auth);
      if (auth["AccessToken"]) {
        const response = await fetch('http://localhost:8000/auth/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: auth["AccessToken"].username,
            password: auth["AccessToken"].password,
          }),
        });
        const data = await response.json();
        if (response.ok) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          window.ui.authActions.preauthorizeApiKey("AccessToken", data.access_token);
          window.ui.authActions.preauthorizeApiKey("RefreshToken", data.refresh_token);
        }
      }
      return result;
    };

    // Добавляем кнопку для обновления токена
    const refreshButton = document.createElement('button');
    refreshButton.innerText = 'Refresh Token';
    refreshButton.style.margin = '10px';
    refreshButton.style.padding = '5px 10px';
    refreshButton.style.backgroundColor = '#4CAF50';
    refreshButton.style.color = 'white';
    refreshButton.style.border = 'none';
    refreshButton.style.cursor = 'pointer';
    refreshButton.onclick = async () => {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        alert('No refresh token found. Please login again.');
        window.location.href = '/docs';
        return;
      }
      try {
        const response = await fetch('http://localhost:8000/auth/refresh', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${refreshToken}`,
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        if (response.ok) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          window.ui.authActions.preauthorizeApiKey("AccessToken", data.access_token);
          window.ui.authActions.preauthorizeApiKey("RefreshToken", data.refresh_token);
          alert('Token refreshed successfully!');
        } else {
          if (data.detail === 'Token has expired') {
            alert('Refresh token expired. Please login again.');
            window.location.href = '/docs';
          } else {
            alert('Failed to refresh token: ' + data.detail);
          }
        }
      } catch (err) {
        alert('Error refreshing token: ' + err.message);
      }
    };

    // Добавляем кнопку Logout
    const logoutButton = document.createElement('button');
    logoutButton.innerText = 'Logout';
    logoutButton.style.margin = '10px';
    logoutButton.style.padding = '5px 10px';
    logoutButton.style.backgroundColor = '#f44336';
    logoutButton.style.color = 'white';
    logoutButton.style.border = 'none';
    logoutButton.style.cursor = 'pointer';
    logoutButton.onclick = () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.ui.authActions.logout(["AccessToken", "RefreshToken"]);
      alert('Logged out successfully!');
      window.location.href = '/docs';
    };

    const topbar = document.querySelector('.topbar-wrapper');
    if (topbar) {
      topbar.appendChild(refreshButton);
      topbar.appendChild(logoutButton);
    }

    // Получаем refresh_token из localStorage и применяем его для схемы RefreshToken
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      window.ui.authActions.preauthorizeApiKey("RefreshToken", refreshToken);
    }

    // Получаем access_token из localStorage и применяем его для схемы AccessToken
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      window.ui.authActions.preauthorizeApiKey("AccessToken", accessToken);
    }

    // Перехватываем запросы и добавляем нужный токен (синхронно)
    window.ui.getSystem().getConfigs().requestInterceptor = (req) => {
      if (req.url.endsWith('/auth/refresh')) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          req.headers.Authorization = `Bearer ${refreshToken}`;
          console.log('Using refresh_token for /auth/refresh:', refreshToken);
          console.log('Request headers:', req.headers);
        }
      } else {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
          req.headers.Authorization = `Bearer ${accessToken}`;
          console.log('Using access_token for request:', accessToken);
          console.log('Request headers:', req.headers);
        }
      }
      console.log('Request URL:', req.url);
      return req;  // Синхронный возврат
    };
  }
});