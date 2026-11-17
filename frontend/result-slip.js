
const token = localStorage.getItem("studentToken");
const student = JSON.parse(localStorage.getItem("studentData"));

const resultsBody = document.getElementById("resultsBody");
const academicYear = document.getElementById("academicYear");
const semester = document.getElementById("semester");

if (!token || !student) {
    alert("Please log in first.");
    window.location.href = "login.html";
}

let allResults = [];

async function fetchResults() {
    try {
        const response = await fetch(
            "http://127.0.0.1:8000/student-results/",
            {
                headers: {
                    "Authorization": "Token " + token
                }
            }
        );

        if (!response.ok) {
            throw new Error("Unable to load results.");
        }

        allResults = await response.json();

        // Display student information
        document.getElementById("studentInfo").innerHTML = `
            <p><strong>Name:</strong> ${student.name}</p>
            <p><strong>Registration Number:</strong> ${student.reg_number}</p>
            <p><strong>Course:</strong> ${student.course}</p>
        `;

        // Get academic years automatically
        const years = [...new Set(
            allResults.map(result => result.academic_year)
        )];

        years.forEach(year => {
            const option = document.createElement("option");
            option.value = year;
            option.textContent = year;
            academicYear.appendChild(option);
        });

        if (years.length > 0) {
            academicYear.value = years[0];
            loadResults();
        } else {
            resultsBody.innerHTML = `
                <tr><td colspan="6">No results available.</td></tr>
            `;
        }

    } catch (error) {
        console.error(error);
        resultsBody.innerHTML = `
            <tr><td colspan="6">Could not load results.</td></tr>
        `;
    }
}

function loadResults() {
    const selectedYear = academicYear.value;
    const selectedSemester = semester.value;

    const filteredResults = allResults.filter(result => {
        const yearMatches = result.academic_year === selectedYear;

        const semesterMatches =
            selectedSemester === "all" ||
            result.semester === selectedSemester;

        return yearMatches && semesterMatches;
    });

    resultsBody.innerHTML = "";

    if (filteredResults.length === 0) {
        resultsBody.innerHTML = `
            <tr><td colspan="6">No results found.</td></tr>
        `;
        return;
    }

    filteredResults.forEach(result => {
        resultsBody.innerHTML += `
            <tr>
                <td>${result.unit_name}</td>
                <td>${result.marks ?? "Missing"}</td>
                <td>${result.grade}</td>
                <td>${result.description}</td>
                <td>${result.semester}</td>
                <td>${result.academic_year}</td>
            </tr>
        `;
    });
}

fetchResults();
