// API 설정
const API_CONFIG = {
    baseURL: '',
    headers: {
        'Accept': 'application/json'
    }
};

// 인증 헤더 가져오기
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        console.log('토큰이 없음');
        return {};
    }
    console.log('토큰 확인:', {
        tokenLength: token.length,
        tokenPreview: `${token.substring(0, 20)}...`
    });
    return { 'Authorization': `Bearer ${token}` };
}

// API 요청 함수
async function apiRequest(endpoint, options = {}) {
    try {
        const token = localStorage.getItem('access_token');
        if (!token && endpoint !== '/api/auth/login') {
            console.log('토큰이 없어 로그인 페이지로 이동');
            window.location.href = '/login';
            return null;
        }

        const headers = {
            ...API_CONFIG.headers,
            ...options.headers
        };

        // 로그인 요청이 아닌 경우에만 인증 헤더 추가
        if (endpoint !== '/api/auth/login') {
            Object.assign(headers, getAuthHeaders());
        }

        const requestOptions = {
            ...options,
            headers,
            credentials: 'include'
        };

        console.log('API 요청:', {
            endpoint,
            method: options.method || 'GET',
            headers: {
                ...headers,
                'Authorization': headers.Authorization ? 
                    `${headers.Authorization.substring(0, 20)}...` : 'none'
            }
        });

        const response = await fetch(endpoint, requestOptions);

        console.log('API 응답:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers)
        });

        if (response.status === 401) {
            console.log('인증 오류 발생');
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return null;
        }

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API 오류:', errorData);
            throw new Error(errorData.detail || '요청 처리 중 오류가 발생했습니다.');
        }

        const data = await response.json();
        console.log('API 응답 데이터:', data);
        return data;
    } catch (error) {
        console.error('API 요청 실패:', error);
        throw error;
    }
}

// API 엔드포인트 함수들
async function getCurrentUser() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.log('토큰이 없음');
            window.location.href = '/login';
            return null;
        }
        console.log('사용자 정보 요청 시작');
        return await apiRequest('/api/auth/me');
    } catch (error) {
        console.error('사용자 정보 조회 실패:', error);
        throw error;
    }
}

async function logout() {
    try {
        await apiRequest('/api/auth/logout', { method: 'POST' });
    } finally {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }
}

// 다른 API 함수들... 