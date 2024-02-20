// 사용되지 않는(작동X) 코드입니다.

async function loginUser() {
    const form = document.getElementById('signinForm');
    const formData = new FormData(form);

    try {
        const response = await fetch('http://127.0.0.1:8000/user/signin/', {
            method: 'POST',
            content_type: 'application/x-www-form-urlencoded',
            body: formData,
        });

        const data = await response.json();
        if (data.access_token) {
            localStorage.setItem('access-token', data.access_token);
            await setAuthorizationHeader();
        }
    } catch (error) {
        alert(error)
        console.error('Error during login:', error);
    }
}

function setAuthorizationHeader() {
    let token = localStorage.getItem('access-token') || '';
    // alert('Bearer ' + token)
    let response = fetch('http://localhost:8000/user/info/', {
        method: 'GET',
        withCredentials: true,
        credentials: 'include',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    })
    window.location.href = 'http://127.0.0.1:8000/user/info/';
}
