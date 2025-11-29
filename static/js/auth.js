/**
 * Frontend Authentication Module
 * Handles JWT token storage, refresh, and API request authorization
 */

class AuthService {
    constructor() {
        this.ACCESS_TOKEN_KEY = 'access_token';
        this.TOKEN_REFRESH_ENDPOINT = '/auth/refresh';
    }

    /**
     * Store access token in localStorage
     */
    setAccessToken(token) {
        if (token) {
            localStorage.setItem(this.ACCESS_TOKEN_KEY, token);
        }
    }

    /**
     * Get access token from localStorage
     */
    getAccessToken() {
        return localStorage.getItem(this.ACCESS_TOKEN_KEY);
    }

    /**
     * Remove access token from localStorage
     */
    removeAccessToken() {
        localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Refresh the access token using httpOnly refresh cookie
     */
    async refreshAccessToken() {
        try {
            const response = await fetch(this.TOKEN_REFRESH_ENDPOINT, {
                method: 'POST',
                credentials: 'include', // Include cookies (refresh token)
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();

            if (data.access_token) {
                this.setAccessToken(data.access_token);
                return data.access_token;
            }

            throw new Error('No access token in response');
        } catch (error) {
            console.error('Token refresh error:', error);
            this.logout();
            throw error;
        }
    }

    /**
     * Logout user - clear tokens and redirect to login
     */
    async logout() {
        try {
            // Call logout endpoint to clear refresh token cookie
            await fetch('/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.removeAccessToken();
            window.location.href = '/';
        }
    }

    /**
     * Make an authenticated API request
     * Automatically adds Authorization header and handles token refresh
     */
    async authenticatedFetch(url, options = {}) {
        const token = this.getAccessToken();

        if (!token) {
            throw new Error('No access token available');
        }

        // Add Authorization header
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'include'
            });

            // If 401, try to refresh token and retry
            if (response.status === 401) {
                console.log('Token expired, attempting refresh...');

                try {
                    const newToken = await this.refreshAccessToken();

                    // Retry request with new token
                    headers['Authorization'] = `Bearer ${newToken}`;
                    return await fetch(url, {
                        ...options,
                        headers,
                        credentials: 'include'
                    });
                } catch (refreshError) {
                    // Refresh failed, redirect to login
                    this.logout();
                    throw new Error('Session expired, please login again');
                }
            }

            return response;
        } catch (error) {
            console.error('Authenticated fetch error:', error);
            throw error;
        }
    }

    /**
     * Handle login response
     * Store access token from response
     */
    handleLoginResponse(data) {
        if (data.access_token) {
            this.setAccessToken(data.access_token);
            return true;
        }
        return false;
    }

    /**
     * Parse JWT token to get payload (without verification)
     * WARNING: This does NOT verify the token, only decodes it
     */
    parseToken(token = null) {
        token = token || this.getAccessToken();

        if (!token) {
            return null;
        }

        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));

            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Token parse error:', error);
            return null;
        }
    }

    /**
     * Get user info from token
     */
    getUserInfo() {
        const payload = this.parseToken();

        if (!payload) {
            return null;
        }

        return {
            user_id: payload.user_id,
            is_admin: payload.is_admin || false,
            exp: payload.exp,
            iat: payload.iat
        };
    }

    /**
     * Check if token is expired (without server validation)
     */
    isTokenExpired() {
        const payload = this.parseToken();

        if (!payload || !payload.exp) {
            return true;
        }

        // exp is in seconds, Date.now() is in milliseconds
        return payload.exp * 1000 < Date.now();
    }
}

// Initialize auth service
const authService = new AuthService();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthService;
}
