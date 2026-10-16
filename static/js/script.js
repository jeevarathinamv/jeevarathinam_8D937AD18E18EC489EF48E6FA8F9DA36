/**
 * Smart Classroom Management System - Client Side JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

    // 1. Live Attendance Statistics Calculation
    const attendanceForm = document.getElementById('attendance-form');
    if (attendanceForm) {
        const totalEl = document.getElementById('stat-total');
        const presentEl = document.getElementById('stat-present');
        const absentEl = document.getElementById('stat-absent');
        const percentageEl = document.getElementById('stat-percentage');
        const progressEl = document.getElementById('stat-progress');

        function calculateAttendanceStats() {
            const radioChoices = document.querySelectorAll('.att-radioChoice:checked');
            let presentCount = 0;
            let absentCount = 0;

            radioChoices.forEach(radio => {
                if (radio.value === 'Present') {
                    presentCount++;
                } else if (radio.value === 'Absent') {
                    absentCount++;
                }
            });

            const totalStudents = parseInt(totalEl.innerText) || (presentCount + absentCount);
            const percentage = totalStudents > 0 ? ((presentCount / totalStudents) * 100).toFixed(1) : 0.0;

            presentEl.innerText = presentCount;
            absentEl.innerText = absentCount;
            percentageEl.innerText = `${percentage}%`;

            if (progressEl) {
                progressEl.style.width = `${percentage}%`;
                if (percentage >= 75) {
                    progressEl.className = 'progress-bar bg-mint';
                } else if (percentage >= 50) {
                    progressEl.className = 'progress-bar bg-warning';
                } else {
                    progressEl.className = 'progress-bar bg-danger';
                }
            }
        }

        // Calculate initially
        calculateAttendanceStats();

        // Recalculate on any change
        document.querySelectorAll('.att-radioChoice').forEach(radio => {
            radio.addEventListener('change', calculateAttendanceStats);
        });

        // 2. Mark All Present / Mark All Absent Shortcuts
        const markAllPresentBtn = document.getElementById('btn-mark-all-present');
        const markAllAbsentBtn = document.getElementById('btn-mark-all-absent');

        if (markAllPresentBtn) {
            markAllPresentBtn.addEventListener('click', function () {
                document.querySelectorAll('input[type="radio"][value="Present"]').forEach(radio => {
                    radio.checked = true;
                });
                calculateAttendanceStats();
            });
        }

        if (markAllAbsentBtn) {
            markAllAbsentBtn.addEventListener('click', function () {
                document.querySelectorAll('input[type="radio"][value="Absent"]').forEach(radio => {
                    radio.checked = true;
                });
                calculateAttendanceStats();
            });
        }
    }

    // 3. Mark Notification Read Handler
    document.querySelectorAll('.btn-mark-read').forEach(button => {
        button.addEventListener('click', function () {
            const notifId = this.getAttribute('data-id');
            const parentItem = document.getElementById(`notif-item-${notifId}`);

            fetch(`/notifications/mark_read/${notifId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    if (parentItem) {
                        parentItem.classList.remove('bg-light', 'border-primary');
                        const badge = parentItem.querySelector('.badge');
                        if (badge) {
                            badge.className = 'badge bg-secondary me-2';
                            badge.innerText = 'Read';
                        }
                    }
                    button.remove();
                    decrementNotifBadges();
                }
            })
            .catch(err => console.error('Error marking notification read:', err));
        });
    });

    function decrementNotifBadges() {
        const topBadge = document.getElementById('top-notif-badge');
        const navBadge = document.getElementById('nav-notif-badge');

        [topBadge, navBadge].forEach(badge => {
            if (badge) {
                let count = parseInt(badge.innerText) || 0;
                count = Math.max(0, count - 1);
                if (count > 0) {
                    badge.innerText = count;
                } else {
                    badge.style.display = 'none';
                }
            }
        });
    }

    // 4. Live Notification Polling for Tutors
    const navNotifBadge = document.getElementById('nav-notif-badge');
    const topNotifBadge = document.getElementById('top-notif-badge');

    if (navNotifBadge || topNotifBadge) {
        setInterval(function () {
            fetch('/api/notifications')
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        const count = data.length;
                        [topNotifBadge, navNotifBadge].forEach(badge => {
                            if (badge) {
                                if (count > 0) {
                                    badge.innerText = count;
                                    badge.style.display = 'inline-block';
                                } else {
                                    badge.style.display = 'none';
                                }
                            }
                        });
                    }
                })
                .catch(err => console.log('Notification polling:', err));
        }, 10000); // Poll every 10s
    }

});
