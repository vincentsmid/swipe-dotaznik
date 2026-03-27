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

    /* Load responses into the dashboard */
    async function loadResponses() {
        const area = document.getElementById("responsesArea");
        if (!area) return;

        try {
            const [respResp, qResp] = await Promise.all([
                fetch("/api/admin/responses"),
                fetch("/api/admin/questions"),
            ]);

            if (!respResp.ok || !qResp.ok) throw new Error();

            const responses = await respResp.json();
            const questions = await qResp.json();

            if (responses.length === 0) {
                area.innerHTML = '<p class="empty-state">Zatím žádné odpovědi.</p>';
                return;
            }

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
            html += "<th>Účastník</th>";
            surveyQuestions.forEach(function (q) {
                html += "<th>" + escapeHtml(q.text) + "</th>";
            });
            html += "</tr></thead><tbody>";

            participants.forEach(function (pid) {
                html += "<tr><td>" + escapeHtml(pid) + "</td>";
                surveyQuestions.forEach(function (q) {
                    const ans = lookup[pid + "_" + q.id] || "";
                    const cls = ans ? "answer-" + ans : "";
                    const labels = { yes: "Ano", no: "Ne", skip: "Přeskočeno", "N/A": "N/A" };
                    html += '<td class="' + cls + '">' + (labels[ans] || "") + "</td>";
                });
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
