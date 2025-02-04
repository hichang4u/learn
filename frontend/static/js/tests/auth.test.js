// 테스트를 위한 모의 localStorage
const localStorageMock = {
    store: {},
    getItem(key) {
        return this.store[key];
    },
    setItem(key, value) {
        this.store[key] = value;
    },
    removeItem(key) {
        delete this.store[key];
    },
    clear() {
        this.store = {};
    }
};

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// 테스트를 위한 모의 fetch
global.fetch = jest.fn();

describe('인증 테스트', () => {
    beforeEach(() => {
        localStorageMock.clear();
        fetch.mockClear();
    });

    test('로그인 성공 테스트', async () => {
        const mockToken = 'test-token';
        const mockUser = {
            email: 'admin@wrsoft.co.kr',
            full_name: '관리자',
            position: 'STAFF'
        };

        // 로그인 응답 모의
        fetch.mockImplementationOnce(() => Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({
                access_token: mockToken,
                user: mockUser
            })
        }));

        // 로그인 요청
        const formData = new FormData();
        formData.append('username', 'admin@wrsoft.co.kr');
        formData.append('password', 'admin1234');
        
        await handleLogin({ 
            preventDefault: () => {},
            target: { formData }
        });

        // localStorage에 토큰이 저장되었는지 확인
        expect(localStorage.getItem('access_token')).toBe(mockToken);
    });

    test('API 요청 시 토큰 포함 테스트', async () => {
        const mockToken = 'test-token';
        localStorage.setItem('access_token', mockToken);

        // API 응답 모의
        fetch.mockImplementationOnce(() => Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({})
        }));

        // API 요청
        await apiRequest('/api/auth/me');

        // Authorization 헤더에 토큰이 포함되었는지 확인
        expect(fetch).toHaveBeenCalledWith(
            '/api/auth/me',
            expect.objectContaining({
                headers: expect.objectContaining({
                    'Authorization': `Bearer ${mockToken}`
                })
            })
        );
    });

    test('401 응답 시 로그인 페이지 리다이렉트', async () => {
        const mockToken = 'test-token';
        localStorage.setItem('access_token', mockToken);

        // 원래의 window.location을 저장
        const originalLocation = window.location;
        delete window.location;
        window.location = { href: '' };

        // 401 응답 모의
        fetch.mockImplementationOnce(() => Promise.resolve({
            ok: false,
            status: 401,
            json: () => Promise.resolve({ detail: '인증 실패' })
        }));

        // API 요청
        await apiRequest('/api/auth/me');

        // localStorage에서 토큰이 제거되었는지 확인
        expect(localStorage.getItem('access_token')).toBeNull();
        
        // 로그인 페이지로 리다이렉트되었는지 확인
        expect(window.location.href).toBe('/login');

        // window.location 복구
        window.location = originalLocation;
    });

    test('토큰 형식 테스트', () => {
        const token = 'test-token';
        const authHeader = getAuthHeaders();
        
        // 토큰이 없을 때
        expect(authHeader).toEqual({});
        
        // 토큰이 있을 때
        localStorage.setItem('access_token', token);
        expect(getAuthHeaders()).toEqual({
            'Authorization': `Bearer ${token}`
        });
    });
}); 