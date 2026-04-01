/* Admin dashboard JS */
(function () {
    "use strict";

    /* Delete question */
    window.deleteQuestion = async function (questionId) {
        if (!confirm("Opravdu chcete smazat tuto otázku?")) return;

        try {
            const resp = await fetch("/api/admin/questions/" + questionId, {
                method: "DELETE",
            });
            if (resp.ok) {
                window.location.reload();
            } else {
                const err = await resp.json();
                alert(err.detail || "Chyba při mazání");
            }
        } catch (error) {
            alert("Chyba připojení");
        }
    };

    /* Delete participant */
    window.deleteParticipant = async function (participantId) {
        if (!confirm("Opravdu chcete smazat všechna data účastníka \"" + participantId + "\"?")) return;

        try {
            const resp = await fetch("/api/admin/participants/" + encodeURIComponent(participantId), {
                method: "DELETE",
            });
            if (resp.ok) {
                window.location.reload();
            } else {
                const err = await resp.json();
                alert(err.detail || "Chyba při mazání");
            }
        } catch (error) {
            alert("Chyba připojení");
        }
    };

    /* Load responses into the dashboard */
    async function loadResponses() {
        const area = document.getElementById("responsesArea");
        if (!area) return;

        try {
            const [respResp, qResp, sessResp] = await Promise.all([
                fetch("/api/admin/responses"),
                fetch("/api/admin/questions"),
                fetch("/api/admin/sessions"),
            ]);

            if (!respResp.ok || !qResp.ok || !sessResp.ok) throw new Error();

            const responses = await respResp.json();
            const questions = await qResp.json();
            const sessions = await sessResp.json();

            if (responses.length === 0) {
                area.innerHTML = '<p class="empty-state">Zatím žádné odpovědi.</p>';
                return;
            }

            // Build session lookup by participant_id
            const sessionLookup = {};
            sessions.forEach(function (s) {
                sessionLookup[s.participant_id] = s;
            });

            // Build lookup: (participant_id, question_id) -> answer
            const lookup = {};
            const participantSet = new Set();
            responses.forEach(function (r) {
                lookup[r.participant_id + "_" + r.question] = r.answer;
                participantSet.add(r.participant_id);
            });
            const participants = Array.from(participantSet).sort();

            // Filter to non-practice questions
            const surveyQuestions = questions.filter(function (q) { return !q.is_practice; });

            // Build table
            let html = '<div style="overflow-x:auto;"><table class="response-table"><thead><tr>';
            html += "<th>Účastník</th><th>Kód školy</th><th>Třída</th>";
            surveyQuestions.forEach(function (q) {
                html += "<th>" + escapeHtml(q.text) + "</th>";
            });
            html += "<th>Akce</th>";
            html += "</tr></thead><tbody>";

            participants.forEach(function (pid) {
                var sess = sessionLookup[pid] || {};
                var schoolCode = sess.school_code != null ? sess.school_code : "";
                var classNum = sess.class_number != null ? sess.class_number : "";
                html += "<tr><td>" + escapeHtml(pid) + "</td>";
                html += "<td>" + escapeHtml(String(schoolCode)) + "</td>";
                html += "<td>" + escapeHtml(String(classNum)) + "</td>";
                surveyQuestions.forEach(function (q) {
                    const ans = lookup[pid + "_" + q.id] || "";
                    const cls = ans ? "answer-" + ans : "";
                    const labels = { yes: "Ano", no: "Ne", skip: "Přeskočeno", "N/A": "N/A" };
                    html += '<td class="' + cls + '">' + (labels[ans] || "") + "</td>";
                });
                html += '<td><button class="btn btn-danger btn-sm" onclick="deleteParticipant(\'' + escapeHtml(pid).replace(/'/g, "\\'") + '\')">Smazat</button></td>';
                html += "</tr>";
            });

            html += "</tbody></table></div>";
            html += '<p style="margin-top:0.5rem;color:#6b7280;font-size:0.85rem;">' +
                "Celkem " + participants.length + " účastníků</p>";
            area.innerHTML = html;
        } catch (error) {
            area.innerHTML = '<p class="empty-state">Chyba při načítání odpovědí.</p>';
        }
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    loadResponses();
})();
