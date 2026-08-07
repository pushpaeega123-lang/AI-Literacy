
    // Tab switching based on URL hashes
    document.addEventListener("DOMContentLoaded", function () {
        var hash = window.location.hash;
        if (hash) {
            var triggerEl = document.querySelector('button[data-bs-target="' + hash + '"]');
            if (triggerEl) {
                var tab = new bootstrap.Tab(triggerEl);
                tab.show();
            }
        }

        // Keep hash updated
        var tabButtons = document.querySelectorAll('button[data-bs-toggle="tab"]');
        tabButtons.forEach(function (button) {
            button.addEventListener("shown.bs.tab", function (e) {
                window.location.hash = e.target.getAttribute("data-bs-target");
            });
        });

        // Initialize Charts
        initCharts();
    });

    // Tab programmatic navigation helper
    function showTab(targetHash) {
        var triggerEl = document.querySelector('button[data-bs-target="' + targetHash + '"]');
        if (triggerEl) {
            var tab = new bootstrap.Tab(triggerEl);
            tab.show();
            window.location.hash = targetHash;
        }
    }

    // Set filter values programmatically
    function setLearnerFilter(role) {
        document.getElementById("roleFilter").value = role;
        filterLearners();
    }

    function openAddUserModal() {
        var modal = new bootstrap.Modal(document.getElementById("addUserModal"));
        modal.show();
    }

    // Modal populate helpers
    function editLearnerModal(btn) {
        document.getElementById("edit_learner_id").value = btn.getAttribute("data-id");
        document.getElementById("edit_learner_name").value = btn.getAttribute("data-fullname");
        document.getElementById("edit_learner_age").value = btn.getAttribute("data-age");
        document.getElementById("edit_learner_role").value = btn.getAttribute("data-role");
        document.getElementById("edit_learner_lang").value = btn.getAttribute("data-language");
        document.getElementById("edit_learner_level").value = btn.getAttribute("data-level");
        document.getElementById("edit_learner_status").value = btn.getAttribute("data-status");
        
        var modal = new bootstrap.Modal(document.getElementById("editLearnerModal"));
        modal.show();
    }

    // Edit lesson trigger
    function editLessonModal(btn) {
        document.getElementById("edit_lesson_id").value = btn.getAttribute("data-id");
        document.getElementById("edit_lesson_title").value = btn.getAttribute("data-title");
        document.getElementById("edit_lesson_category").value = btn.getAttribute("data-category");
        document.getElementById("edit_lesson_lang").value = btn.getAttribute("data-language");
        document.getElementById("edit_lesson_diff").value = btn.getAttribute("data-difficulty");
        document.getElementById("edit_lesson_content").value = btn.getAttribute("data-content");

        var modal = new bootstrap.Modal(document.getElementById("editLessonModal"));
        modal.show();
    }

    // Edit assessment trigger
    function editAssessmentModal(btn) {
        document.getElementById("edit_question_id").value = btn.getAttribute("data-id");
        document.getElementById("edit_question_category").value = btn.getAttribute("data-category");
        document.getElementById("edit_question_lang").value = btn.getAttribute("data-language");
        document.getElementById("edit_question_diff").value = btn.getAttribute("data-difficulty");
        document.getElementById("edit_question_prompt").value = btn.getAttribute("data-prompt");
        document.getElementById("edit_question_options").value = btn.getAttribute("data-options");
        document.getElementById("edit_question_correct").value = btn.getAttribute("data-correct");
        document.getElementById("edit_question_expl").value = btn.getAttribute("data-explanation");

        var modal = new bootstrap.Modal(document.getElementById("editAssessmentModal"));
        modal.show();
    }

    function openReplyFeedbackModal(id, message) {
        document.getElementById("reply_feedback_id").value = id;
        document.getElementById("reply_feedback_msg").innerText = message;
        var modal = new bootstrap.Modal(document.getElementById("replyFeedbackModal"));
        modal.show();
    }

    function openAddLessonModal() {
        var modal = new bootstrap.Modal(document.getElementById("addLessonModal"));
        modal.show();
    }

    function openAddQuestionModal() {
        var modal = new bootstrap.Modal(document.getElementById("addAssessmentModal"));
        modal.show();
    }

    function focusSearch(searchId) {
        setTimeout(function() {
            var input = document.getElementById(searchId);
            if (input) {
                input.focus();
            }
        }, 100);
    }

    // Global dashboard search filter
    function globalSearchFilter() {
        var input = document.getElementById("globalSearch");
        var filter = input.value.toUpperCase();
        
        // Search table lines in Active Learners if visible
        var learnersTable = document.getElementById("learnersTable");
        if (learnersTable) {
            var tr = learnersTable.getElementsByTagName("tr");
            for (var i = 1; i < tr.length; i++) {
                var txt = tr[i].innerText || tr[i].textContent;
                if (txt.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }

    // Learner list filtering
    function filterLearners() {
        var searchInput = document.getElementById("learnerSearch");
        var searchFilter = searchInput.value.toUpperCase();
        var roleFilter = document.getElementById("roleFilter").value.toUpperCase();
        var statusFilter = document.getElementById("statusFilter").value.toUpperCase();
        var table = document.getElementById("learnersTable");
        var tr = table.getElementsByTagName("tr");

        for (var i = 1; i < tr.length; i++) {
            var tdName = tr[i].getElementsByTagName("td")[0];
            var tdEmail = tr[i].getElementsByTagName("td")[1];
            var tdRole = tr[i].getElementsByTagName("td")[3];
            var tdStatus = tr[i].getElementsByTagName("td")[6];

            if (tdName && tdEmail && tdRole && tdStatus) {
                var nameVal = tdName.textContent || tdName.innerText;
                var emailVal = tdEmail.textContent || tdEmail.innerText;
                var roleVal = tdRole.textContent || tdRole.innerText;
                var statusVal = tdStatus.textContent || tdStatus.innerText;

                var matchesSearch = nameVal.toUpperCase().indexOf(searchFilter) > -1 || emailVal.toUpperCase().indexOf(searchFilter) > -1;
                var matchesRole = roleFilter === "ALL" || roleVal.toUpperCase().indexOf(roleFilter) > -1;
                var matchesStatus = statusFilter === "ALL" || statusVal.toUpperCase().indexOf(statusFilter) > -1;

                if (matchesSearch && matchesRole && matchesStatus) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }

    // View detailed learner progress trigger
    function viewLearnerProgress(userId) {
        fetch('/admin/learner/' + userId + '/progress')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("prog_name").innerText = data.user.fullname;
                    document.getElementById("prog_email").innerText = data.user.email;
                    document.getElementById("prog_lang").innerText = data.user.language;
                    document.getElementById("prog_level").innerText = data.user.learning_level;

                    document.getElementById("prog_xp").innerText = data.user.xp || 0;
                    document.getElementById("prog_coins").innerText = data.user.coins || 0;
                    document.getElementById("prog_streak").innerText = data.user.streak || 0;
                    document.getElementById("prog_percent").innerText = data.user.progress_percentage || 0;

                    // Populate lessons
                    let lessonsBody = document.getElementById("prog_lessons_body");
                    lessonsBody.innerHTML = "";
                    data.lessons.forEach(l => {
                        let tr = document.createElement("tr");
                        tr.innerHTML = `<td>${l.title}</td><td>${l.category}</td><td>${l.difficulty}</td><td>${l.timestamp}</td>`;
                        lessonsBody.appendChild(tr);
                    });

                    // Populate assessments
                    let assessmentsBody = document.getElementById("prog_assessments_body");
                    assessmentsBody.innerHTML = "";
                    data.assessments.forEach(a => {
                        let tr = document.createElement("tr");
                        tr.innerHTML = `<td>${a.score}%</td><td>${a.correct}/${a.total}</td><td>${a.language}</td><td>${a.timestamp}</td>`;
                        assessmentsBody.appendChild(tr);
                    });

                    // Populate voice
                    let voiceBody = document.getElementById("prog_voice_body");
                    voiceBody.innerHTML = "";
                    data.voice_practice.forEach(v => {
                        let tr = document.createElement("tr");
                        tr.innerHTML = `<td>"${v.expected_text}"</td><td>"${v.spoken_text}"</td><td>${v.pronunciation_score}%</td><td>${v.timestamp}</td>`;
                        voiceBody.appendChild(tr);
                    });

                    var modal = new bootstrap.Modal(document.getElementById("viewProgressModal"));
                    modal.show();
                } else {
                    alert("Failed to load progress records: " + data.error);
                }
            })
            .catch(error => {
                console.error("Error loading progress: ", error);
                alert("An error occurred while fetching progress data.");
            });
    }

    // Toggle game configuration status
    function toggleGameConfig(gameId, chk) {
        fetch('/api/admin/games/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: gameId, enabled: chk.checked })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert("Failed to update game configuration status.");
                chk.checked = !chk.checked;
            }
        });
    }

    // Chart.js initialization
    function initCharts() {
        // 1. Monthly User Registrations Chart
        var regsEl = document.getElementById('monthlyRegsChart');
        var ctxRegs = regsEl.getContext('2d');
        var regsData = JSON.parse(regsEl.getAttribute('data-regs') || '[]');
        
        new Chart(ctxRegs, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Registrations',
                    data: regsData,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.05)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        // 2. Age Distribution Chart (Doughnut)
        var ageEl = document.getElementById('ageDistributionChart');
        var ctxAge = ageEl.getContext('2d');
        
        new Chart(ctxAge, {
            type: 'doughnut',
            data: {
                labels: ['Toddler', 'Young', 'Middle', 'Older', 'Senior'],
                datasets: [{
                    data: [
                        Number(ageEl.dataset.toddler || 0),
                        Number(ageEl.dataset.young || 0),
                        Number(ageEl.dataset.middle || 0),
                        Number(ageEl.dataset.older || 0),
                        Number(ageEl.dataset.senior || 0)
                    ],
                    backgroundColor: ['#4f46e5', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });

        // 3. Lesson Completion Statistics by Language
        var complEl = document.getElementById('completionsChart');
        var ctxCompl = complEl.getContext('2d');
        var complStats = JSON.parse(complEl.getAttribute('data-stats') || '{}');
        
        new Chart(ctxCompl, {
            type: 'bar',
            data: {
                labels: Object.keys(complStats),
                datasets: [{
                    label: 'Completions',
                    data: Object.values(complStats),
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        // 4. Assessment Performance Chart
        var perfEl = document.getElementById('assessmentPerfChart');
        var ctxPerf = perfEl.getContext('2d');
        var perfStats = JSON.parse(perfEl.getAttribute('data-perf') || '{}');
        
        new Chart(ctxPerf, {
            type: 'bar',
            data: {
                labels: Object.keys(perfStats),
                datasets: [{
                    label: 'Average Score (%)',
                    data: Object.values(perfStats),
                    backgroundColor: '#3b82f6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        // 5. Language-wise User Distribution
        var distEl = document.getElementById('languageDistributionChart');
        var ctxDist = distEl.getContext('2d');
        var distStats = JSON.parse(distEl.getAttribute('data-dist') || '{}');
        
        new Chart(ctxDist, {
            type: 'doughnut',
            data: {
                labels: Object.keys(distStats),
                datasets: [{
                    data: Object.values(distStats),
                    backgroundColor: ['#a855f7', '#3b82f6', '#06b6d4', '#f97316', '#ec4899', '#10b981'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
            }
        });

        // 6. Analytics Levels Bar Chart
        var levelsBarEl = document.getElementById('analyticsLevelsChart');
        var ctxAnalyticLevels = levelsBarEl.getContext('2d');
        
        new Chart(ctxAnalyticLevels, {
            type: 'bar',
            data: {
                labels: ['Beginner', 'Basic', 'Intermediate', 'Advanced'],
                datasets: [{
                    label: 'Students',
                    data: [
                        Number(levelsBarEl.dataset.beginner || 0),
                        Number(levelsBarEl.dataset.basic || 0),
                        Number(levelsBarEl.dataset.intermediate || 0),
                        Number(levelsBarEl.dataset.advanced || 0)
                    ],
                    backgroundColor: ['#4f46e5', '#3b82f6', '#10b981', '#f59e0b'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
