/* Survey swipe mechanics */
(function () {
    "use strict";

    const SWIPE_THRESHOLD_X = 80;
    const SWIPE_THRESHOLD_Y = 80;
    const ROTATION_FACTOR = 0.1;

    const participantId = sessionStorage.getItem("participant_id");
    if (!participantId) {
        window.location.href = "/survey";
        return;
    }
    const schoolCode = sessionStorage.getItem("school_code");
    const classNumber = sessionStorage.getItem("class_number");

    const cardArea = document.getElementById("cardArea");
    const progressFill = document.getElementById("progressFill");
    const progressText = document.getElementById("progressText");
    const btnYes = document.getElementById("btnYes");
    const btnNo = document.getElementById("btnNo");

    let questions = [];
    let currentIndex = 0;
    let practiceCount = 0;
    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isAnimating = false;
    let cardShownAt = 0;

    /* --- Init --- */
    async function init() {
        try {
            const resp = await fetch("/api/survey/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ participant_id: participantId }),
            });
            if (!resp.ok) throw new Error("Chyba načítání otázek");
            questions = await resp.json();
            practiceCount = questions.filter(function (q) { return q.is_practice; }).length;

            if (questions.length === 0) {
                cardArea.innerHTML = '<p style="text-align:center;color:#6b7280;">Žádné otázky k zobrazení.</p>';
                return;
            }

            // Check progress for resume
            const progResp = await fetch(`/api/survey/progress/${encodeURIComponent(participantId)}`);
            if (progResp.ok) {
                const progress = await progResp.json();
                const answeredSet = new Set(progress.answered_question_ids);
                // Skip already answered questions
                while (currentIndex < questions.length && answeredSet.has(questions[currentIndex].id)) {
                    currentIndex++;
                }
            }

            if (currentIndex >= questions.length) {
                completeSurvey();
                return;
            }

            // If resuming at the practice/real boundary and session not yet started, show confirm
            if (practiceCount > 0 && currentIndex === practiceCount && !sessionStorage.getItem("survey_started_at")) {
                updateProgress();
                showPracticeConfirm();
                return;
            }

            // If no practice questions, start session immediately
            if (practiceCount === 0 && !sessionStorage.getItem("survey_started_at")) {
                var startedAt = new Date().toISOString();
                sessionStorage.setItem("survey_started_at", startedAt);
                fetch("/api/survey/session/start", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        participant_id: participantId,
                        started_at: startedAt,
                        school_code: schoolCode || null,
                        class_number: classNumber ? parseInt(classNumber) : null,
                    }),
                }).catch(function () {});
            }

            renderCard();
            updateProgress();
        } catch (err) {
            cardArea.innerHTML = `<p style="text-align:center;color:#dc2626;">${err.message}</p>`;
        }
    }

    /* --- Render --- */
    function renderCard() {
        document.getElementById("buttonRow").style.display = "";
        cardArea.innerHTML = "";
        if (currentIndex >= questions.length) {
            completeSurvey();
            return;
        }

        const q = questions[currentIndex];
        const card = document.createElement("div");
        card.className = "card";
        card.id = "currentCard";

        // Media
        const ext = q.media_url.split(".").pop().toLowerCase();
        let mediaEl;
        if (["mp4", "webm"].includes(ext)) {
            mediaEl = document.createElement("video");
            mediaEl.src = q.media_url;
            mediaEl.className = "card-media";
            mediaEl.autoplay = true;
            mediaEl.loop = true;
            mediaEl.muted = true;
            mediaEl.playsInline = true;
        } else {
            mediaEl = document.createElement("img");
            mediaEl.src = q.media_url;
            mediaEl.className = "card-media";
            mediaEl.alt = q.text;
            mediaEl.draggable = false;
        }
        card.appendChild(mediaEl);

        // Text
        const textEl = document.createElement("div");
        textEl.className = "card-text";
        textEl.textContent = q.text;
        card.appendChild(textEl);

        // Practice badge
        if (q.is_practice) {
            const badge = document.createElement("div");
            badge.className = "practice-badge";
            badge.textContent = "Cvičná otázka";
            card.appendChild(badge);
        }

        // Overlays
        ["yes", "no", "skip"].forEach(function (type) {
            const overlay = document.createElement("div");
            overlay.className = "card-overlay overlay-" + type;
            overlay.id = "overlay-" + type;
            const labels = { yes: "ANO", no: "NE", skip: "PŘESKOČIT" };
            overlay.textContent = labels[type];
            card.appendChild(overlay);
        });

        cardArea.appendChild(card);
        attachCardEvents(card);
        cardShownAt = Date.now();
    }

    function updateProgress() {
        const total = questions.length;
        const pct = total > 0 ? Math.round((currentIndex / total) * 100) : 0;
        progressFill.style.width = pct + "%";

        // Count practice vs real
        const practiceCount = questions.filter(function (q) { return q.is_practice; }).length;
        const realTotal = total - practiceCount;
        const realAnswered = Math.max(0, currentIndex - practiceCount);

        if (currentIndex < practiceCount) {
            progressText.textContent = "Cvičná otázka";
        } else {
            progressText.textContent = realAnswered + " / " + realTotal;
        }
    }

    /* --- Touch / Pointer events --- */
    function attachCardEvents(card) {
        card.addEventListener("pointerdown", onPointerDown);
    }

    function onPointerDown(e) {
        if (isAnimating) return;
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        currentX = 0;
        currentY = 0;

        const card = document.getElementById("currentCard");
        if (card) {
            card.classList.add("dragging");
            card.setPointerCapture(e.pointerId);
        }

        document.addEventListener("pointermove", onPointerMove);
        document.addEventListener("pointerup", onPointerUp);
    }

    function onPointerMove(e) {
        if (!isDragging) return;
        currentX = e.clientX - startX;
        currentY = e.clientY - startY;

        const card = document.getElementById("currentCard");
        if (!card) return;

        const rotation = currentX * ROTATION_FACTOR;
        card.style.transform = "translateX(" + currentX + "px) translateY(" + currentY + "px) rotate(" + rotation + "deg)";

        // Show overlays based on direction
        const overlayYes = document.getElementById("overlay-yes");
        const overlayNo = document.getElementById("overlay-no");
        const overlaySkip = document.getElementById("overlay-skip");

        const absX = Math.abs(currentX);
        const absY = Math.abs(currentY);

        // Determine dominant direction
        if (absX > absY) {
            // Horizontal swipe
            if (currentX > 0) {
                overlayYes.style.opacity = Math.min(absX / SWIPE_THRESHOLD_X, 1);
                overlayNo.style.opacity = 0;
            } else {
                overlayNo.style.opacity = Math.min(absX / SWIPE_THRESHOLD_X, 1);
                overlayYes.style.opacity = 0;
            }
            overlaySkip.style.opacity = 0;
        } else if (currentY < 0) {
            // Up swipe
            overlaySkip.style.opacity = Math.min(absY / SWIPE_THRESHOLD_Y, 1);
            overlayYes.style.opacity = 0;
            overlayNo.style.opacity = 0;
        } else {
            overlayYes.style.opacity = 0;
            overlayNo.style.opacity = 0;
            overlaySkip.style.opacity = 0;
        }
    }

    function onPointerUp() {
        if (!isDragging) return;
        isDragging = false;

        document.removeEventListener("pointermove", onPointerMove);
        document.removeEventListener("pointerup", onPointerUp);

        const card = document.getElementById("currentCard");
        if (!card) return;
        card.classList.remove("dragging");

        const absX = Math.abs(currentX);
        const absY = Math.abs(currentY);

        // Decide action
        if (absX > absY && currentX > SWIPE_THRESHOLD_X) {
            commitSwipe("yes", "swipe-right");
        } else if (absX > absY && currentX < -SWIPE_THRESHOLD_X) {
            commitSwipe("no", "swipe-left");
        } else if (currentY < -SWIPE_THRESHOLD_Y && absY > absX) {
            commitSwipe("skip", "swipe-up");
        } else {
            // Snap back
            card.style.transform = "";
            resetOverlays();
        }
    }

    function resetOverlays() {
        ["yes", "no", "skip"].forEach(function (type) {
            const el = document.getElementById("overlay-" + type);
            if (el) el.style.opacity = 0;
        });
    }

    /* --- Commit swipe --- */
    function commitSwipe(answer, animationClass) {
        if (isAnimating) return;
        isAnimating = true;

        const card = document.getElementById("currentCard");
        if (!card) return;

        card.classList.add(animationClass);

        const q = questions[currentIndex];

        // Submit answer (skip for practice questions)
        if (!q.is_practice) {
            var questionDuration = cardShownAt ? Date.now() - cardShownAt : null;
            fetch("/api/survey/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    participant_id: participantId,
                    question_id: q.id,
                    answer: answer,
                    duration_ms: questionDuration,
                }),
            }).catch(function () {
                // Silently fail - answer may be lost but survey continues
            });
        }

        // Advance after animation
        setTimeout(function () {
            currentIndex++;
            isAnimating = false;
            updateProgress();

            // Check if we just finished practice questions
            if (practiceCount > 0 && currentIndex === practiceCount) {
                showPracticeConfirm();
            } else {
                renderCard();
            }
        }, 400);
    }

    /* --- Practice confirm screen --- */
    function showPracticeConfirm() {
        cardArea.innerHTML = "";
        document.getElementById("buttonRow").style.display = "none";

        var wrapper = document.createElement("div");
        wrapper.style.cssText = "text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1.5rem;height:100%;";

        var heading = document.createElement("h2");
        heading.textContent = "Cvičné otázky hotovy!";
        heading.style.cssText = "font-size:1.5rem;color:#16a34a;";

        var description = document.createElement("p");
        description.textContent = "Teď přijdou skutečné otázky. Tvoje odpovědi budou zaznamenány.";
        description.style.cssText = "color:#6b7280;font-size:1.05rem;line-height:1.5;";

        var btn = document.createElement("button");
        btn.textContent = "Můžeme jít na to!";
        btn.className = "btn btn-primary";
        btn.style.cssText = "padding:1rem 2rem;font-size:1.1rem;";
        btn.addEventListener("click", function () {
            var startedAt = new Date().toISOString();
            sessionStorage.setItem("survey_started_at", startedAt);

            fetch("/api/survey/session/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    participant_id: participantId,
                    started_at: startedAt,
                    school_code: schoolCode || null,
                    class_number: classNumber ? parseInt(classNumber) : null,
                }),
            }).catch(function () {});

            renderCard();
        });

        wrapper.appendChild(heading);
        wrapper.appendChild(description);
        wrapper.appendChild(btn);
        cardArea.appendChild(wrapper);
    }

    /* --- Complete survey --- */
    function completeSurvey() {
        var startedAt = sessionStorage.getItem("survey_started_at");
        var completedAt = new Date().toISOString();
        var durationMs = 0;
        if (startedAt) {
            durationMs = new Date(completedAt).getTime() - new Date(startedAt).getTime();
        }

        fetch("/api/survey/session/complete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                participant_id: participantId,
                completed_at: completedAt,
                duration_ms: durationMs,
            }),
        }).finally(function () {
            window.location.href = "/survey/done";
        });
    }

    /* --- Button handlers --- */
    btnYes.addEventListener("click", function () {
        if (!isAnimating) commitSwipe("yes", "swipe-right");
    });
    btnNo.addEventListener("click", function () {
        if (!isAnimating) commitSwipe("no", "swipe-left");
    });

    /* --- Start --- */
    init();
})();
