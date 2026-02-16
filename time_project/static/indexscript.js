// indexscript.js
const userIds = JSON.parse(document.getElementById('user-ids').textContent);
const userStatus = JSON.parse(document.getElementById('user-status').textContent);

let state = userStatus || {};


function updateTime() {
    const now = new Date();
    const dateString = now.toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' });
    const timeString = now.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    document.getElementById('current-date').textContent = dateString;
    document.getElementById('current-time').textContent = timeString;
}




function updateButtonStates(user_id) {
    const workstatus = state[user_id] || "none";
    const checkIn = document.getElementById(`check_InBtn${user_id}`);
    const checkOut = document.getElementById(`checkOutBtn${user_id}`);
    const restIn = document.getElementById(`rest_inBtn${user_id}`);
    const restOut = document.getElementById(`rest_outBtn${user_id}`);
    const icon = document.getElementById(`statusIcon${user_id}`);

    checkIn.disabled = (workstatus !== "none");
    checkOut.disabled = !(workstatus=== "working");
    restIn.disabled = !(workstatus === "working");
    restOut.disabled = !(workstatus === "on_break");

    if (workstatus === "none") {
        icon.textContent = "😴";
    } else if (workstatus === "working") {
        icon.textContent = "🟢 出勤中";
    } else if (workstatus === "on_break") {
        icon.textContent = "🟡 休憩中";
    }
}


function handleCheckIn(user_id) {
    recordEvent("出勤", user_id).then(success => {
        if (success) {
            state[user_id] = "working";
        } else {
            state[user_id] = "none";
        }
        updateButtonStates(user_id);
    });
}

function handleCheckOut(user_id) {
    recordEvent("退勤", user_id).then(success => {
        if (success) {
            state[user_id] = "none";
            updateButtonStates(user_id);
        }
    });
}

function handleBreak(user_id) {
    recordEvent("休憩", user_id).then(success => {
        if (success) {
            state[user_id] = "on_break";
            updateButtonStates(user_id);
        }
    });
}

function handleResume(user_id) {
    recordEvent("復帰", user_id).then(success => {
        if (success) {
            state[user_id] = "working";
            updateButtonStates(user_id);
        }
    });
}

function recordEvent(eventType, user_id) {
    const now = new Date();
    const time = now.toLocaleTimeString('ja-JP');

    const data = {
        eventType: eventType,
        time: time,
        user_id: user_id,
        note: ""
    };

    return fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(async response => {
        if (response.ok) {
            alert("✅ 送信成功");
            return true;
        } else {
            const result = await response.json();
            alert("❌ " + (result.error || "送信失敗"));
            return false;
        }
    })
    .catch(error => {
        alert("❌ " + error);
        console.error("送信失敗しました", error);
        return false;
    });
}  
let status;
// メイン初期化処理
window.addEventListener('DOMContentLoaded', () => {
    updateTime();
    setInterval(updateTime, 1000);

    userIds.forEach(user_id => {
        updateButtonStates(user_id);

        const modal = document.getElementById(`modalUser${user_id}`);
        if (modal) {
            modal.addEventListener('show.bs.modal', () => {
                updateButtonStates(user_id);
            });

            const checkIn = document.getElementById(`check_InBtn${user_id}`);
            const checkOut = document.getElementById(`checkOutBtn${user_id}`);
            const restIn = document.getElementById(`rest_inBtn${user_id}`);
            const restOut = document.getElementById(`rest_outBtn${user_id}`);

            if (checkIn) checkIn.addEventListener("click", () => handleCheckIn(user_id));
            if (checkOut) checkOut.addEventListener("click", () => handleCheckOut(user_id));
            if (restIn) restIn.addEventListener("click", () => handleBreak(user_id));
            if (restOut) restOut.addEventListener("click", () => handleResume(user_id));
        }
    });
});


