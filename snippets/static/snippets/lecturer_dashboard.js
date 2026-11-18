
const token = sessionStorage.getItem("lecturerToken");

if (!token) {
    window.location.href = "/lecturer-login-page/";
}

const headers = {
    "Authorization": `Token ${token}`,
    "Content-Type": "application/json"
};

async function loadDashboard() {
    try {
        const response = await fetch("/lecturer-dashboard/", {
            headers: headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to load dashboard.");
        }

        document.getElementById("lecturerName").textContent =
            data.username;

        document.getElementById("staffNumber").textContent =
            data.staff_number;

        document.getElementById("totalUnits").textContent =
            data.total_units;

        const unitsList = document.getElementById("unitsList");
        const unitSelect = document.getElementById("unitSelect");

        unitsList.textContent = "";

        if (data.units.length === 0) {
            unitsList.textContent = "No units have been assigned.";
        }

        data.units.forEach(function(unit) {
            const item = document.createElement("div");
            item.className = "unit-item";
            item.textContent = `${unit.unit_code} - ${unit.unit_name}`;
            unitsList.appendChild(item);

            const option = document.createElement("option");
            option.value = unit.id;
            option.textContent = `${unit.unit_code} - ${unit.unit_name}`;
            unitSelect.appendChild(option);
        });

    } catch (error) {
        document.getElementById("unitsList").textContent =
            error.message;
    }
}

document.getElementById("marksForm").addEventListener(
    "submit",
    async function(event) {
        event.preventDefault();

        const message = document.getElementById("marksMessage");
        const button = document.getElementById("submitMarksButton");

        const marksData = {
            reg_number: document.getElementById("regNumber").value.trim(),
            unit_id: document.getElementById("unitSelect").value,
            marks: document.getElementById("marks").value,
            semester: document.getElementById("semester").value.trim(),
            academic_year: document.getElementById("academicYear").value.trim()
        };

        button.disabled = true;
        button.textContent = "Submitting...";
        message.textContent = "";

        try {
            const response = await fetch("/lecturer-submit-result/", {
                method: "POST",
                headers: headers,
                body: JSON.stringify(marksData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to submit marks."
                );
            }

            message.textContent = data.message;
            message.style.color = "green";

            document.getElementById("marksForm").reset();

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";
        } finally {
            button.disabled = false;
            button.textContent = "Submit Marks";
        }
    }
);

document.getElementById("logoutButton").addEventListener(
    "click",
    function() {
        sessionStorage.removeItem("lecturerToken");
        sessionStorage.removeItem("lecturerUsername");

        window.location.href = "/lecturer-login-page/";
    }
);

loadDashboard();
