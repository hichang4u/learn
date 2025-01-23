// 관리자 모달 표시 함수
function showAdminModal(action) {
    const modal = new bootstrap.Modal(document.getElementById('adminModal'));
    const modalTitle = document.querySelector('#adminModal .modal-title');
    const modalBody = document.querySelector('#adminModal .modal-body');
    
    switch(action) {
        case 'add':
            modalTitle.textContent = '일정 추가';
            modalBody.innerHTML = `
                <form id="addScheduleForm">
                    <div class="mb-3">
                        <label class="form-label">일정 제목</label>
                        <input type="text" class="form-control" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">시작 일시</label>
                        <input type="datetime-local" class="form-control" name="start" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">종료 일시</label>
                        <input type="datetime-local" class="form-control" name="end" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">수강 정원</label>
                        <input type="number" class="form-control" name="capacity" required>
                    </div>
                    <button type="submit" class="btn btn-primary">추가</button>
                </form>
            `;
            break;
        case 'edit':
            modalTitle.textContent = '일정 수정';
            modalBody.innerHTML = '선택된 일정을 수정합니다.';
            break;
        case 'delete':
            modalTitle.textContent = '일정 삭제';
            modalBody.innerHTML = '선택된 일정을 삭제하시겠습니까?';
            break;
    }
    modal.show();
}

// 사용자 모달 표시 함수
function showUserModal(action) {
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    const modalTitle = document.querySelector('#userModal .modal-title');
    const modalBody = document.querySelector('#userModal .modal-body');
    
    switch(action) {
        case 'register':
            modalTitle.textContent = '수강 신청';
            modalBody.innerHTML = '선택된 강의에 수강 신청하시겠습니까?';
            break;
        case 'view':
            modalTitle.textContent = '수강 내역';
            modalBody.innerHTML = '수강 신청 내역을 표시합니다.';
            break;
    }
    modal.show();
}

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listMonth'
        },
        height: 'auto',
        firstDay: 1,
        locale: 'ko',
        buttonText: {
            today: '오늘',
            month: '월',
            week: '주',
            list: '목록'
        },
        allDayText: '종일',
        dayCellClassNames: function(arg) {
            if (arg.date.getDay() === 0) { // 일요일
                return ['sunday'];
            } else if (arg.date.getDay() === 6) { // 토요일
                return ['saturday'];
            }
            return [];
        },
        dayHeaderFormat: { weekday: 'short' },
        views: {
            dayGridMonth: {
                dayCellContent: function(arg) {
                    return { html: String(arg.date.getDate()) };
                }
            },
            timeGridWeek: {
                titleFormat: { year: 'numeric', month: 'short', day: 'numeric' },
                dayHeaderFormat: { weekday: 'short', month: 'numeric', day: 'numeric' },
                slotLabelFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    omitZeroMinute: true,
                    meridiem: false
                }
            }
        },
        slotMinTime: '00:00:00',
        slotMaxTime: '24:00:00'
    });
    calendar.render();
});
