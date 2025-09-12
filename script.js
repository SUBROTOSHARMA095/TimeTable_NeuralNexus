// function renderBranches() {
//     const container = document.getElementById('branchesContainer');
//     container.innerHTML = '';
//     const n = parseInt(document.getElementById('numBranches').value) || 0;
//     for (let i = 1; i <= n; i++) {
//         container.innerHTML += `
//             <div>
//                 <h3>Branch ${i}</h3>
//                 <label>Name: <input type="text" name="branchName${i}" required></label><br/>
//                 <label>Total No. of Students: <input type="number" name="students${i}" min="1" required></label><br/>
//                 <label>Subjects (comma separated): <input type="text" name="subjects${i}" required></label><br/>
//                 <label>No. of Practical Subjects: <input type="number" name="numPracticals${i}" min="0" required onchange="renderPracticals(${i})"></label><br/>
//                 <div id="practicalsContainer${i}"></div>
//                 <label>Total Class Hours per Day: <input type="number" name="classHours${i}" min="1" required></label>
//             </div><hr/>
//         `;
//     }
// }

// function renderPracticals(branchIndex) {
//     const container = document.getElementById(`practicalsContainer${branchIndex}`);
//     container.innerHTML = '';
//     const numPracticals = parseInt(document.querySelector(`[name="numPracticals${branchIndex}"]`).value) || 0;
//     for (let j = 1; j <= numPracticals; j++) {
//         container.innerHTML += `
//             <div>
//                 <h4>Practical Subject ${j}</h4>
//                 <label>Name: <input type="text" name="practicalName${branchIndex}_${j}" required></label><br/>
//                 <label>No. of Practical Classes per Week: <input type="number" name="practicalClasses${branchIndex}_${j}" min="1" required></label><br/>
//             </div>
//         `;
//     }
// }

// function renderLabTypes() {
//     const container = document.getElementById('labsContainer');
//     container.innerHTML = '';
//     const n = parseInt(document.getElementById('numLabTypes').value) || 0;
//     for (let i = 1; i <= n; i++) {
//         container.innerHTML += `
//             <div>
//                 <h3>Lab Type ${i}</h3>
//                 <label>Type Name: <input type="text" name="labType${i}" required></label><br/>
//                 <label>No. of Labs: <input type="number" name="numLabs${i}" min="1" required></label><br/>
//                 <label>Max Capacity per Lab: <input type="number" name="labCapacity${i}" min="1" required></label>
//             </div><hr/>
//         `;
//     }
// }

// function renderDepartments() {
//     const container = document.getElementById('departmentsContainer');
//     container.innerHTML = '';
//     const n = parseInt(document.getElementById('numDepartments').value) || 0;
//     for (let i = 1; i <= n; i++) {
//         container.innerHTML += `
//             <div>
//                 <h3>Department ${i}</h3>
//                 <label>Name: <input type="text" name="departmentName${i}" required></label><br/>
//                 <label>Faculty Members (comma separated): <input type="text" name="facultyNames${i}" required></label>
//             </div><hr/>
//         `;
//     }
// }

// document.getElementById('timetable-form').addEventListener('submit', function(e) {
//     e.preventDefault();

//     // Collect branches
//     const branches = [];
//     const numBranches = parseInt(document.getElementById('numBranches').value) || 0;
//     for (let i = 1; i <= numBranches; i++) {
//         const name = document.querySelector(`[name="branchName${i}"]`).value.trim();
//         const totalStudents = parseInt(document.querySelector(`[name="students${i}"]`).value) || 0;
//         const subjects = document.querySelector(`[name="subjects${i}"]`).value
//             .split(',')
//             .map(s => s.trim())
//             .filter(s => s.length > 0);

//         const numPracticals = parseInt(document.querySelector(`[name="numPracticals${i}"]`).value) || 0;
//         const practicals = [];
//         for (let j = 1; j <= numPracticals; j++) {
//             const pname = document.querySelector(`[name="practicalName${i}_${j}"]`).value.trim();
//             const pclasses = parseInt(document.querySelector(`[name="practicalClasses${i}_${j}"]`).value) || 0;
//             if (pname && pclasses > 0) {
//                 practicals.push({
//                     name: pname,
//                     classesPerWeek: pclasses
//                 });
//             }
//         }

//         const classHours = parseInt(document.querySelector(`[name="classHours${i}"]`).value) || 0;

//         if (name && totalStudents > 0 && subjects.length > 0 && classHours > 0) {
//             branches.push({
//                 name,
//                 totalStudents,
//                 subjects,
//                 practicals,
//                 classHoursPerDay: classHours
//             });
//         }
//     }

//     // Collect lecture rooms
//     const lectureRooms = {
//         totalRooms: parseInt(document.getElementById('numLectureRooms').value) || 0,
//         maxCapacity: parseInt(document.getElementById('lectureRoomCapacity').value) || 0
//     };

//     // Collect labs
//     const labs = [];
//     const numLabs = parseInt(document.getElementById('numLabTypes').value) || 0;
//     for (let i = 1; i <= numLabs; i++) {
//         const type = document.querySelector(`[name="labType${i}"]`).value.trim();
//         const numLabsVal = parseInt(document.querySelector(`[name="numLabs${i}"]`).value) || 0;
//         const capacity = parseInt(document.querySelector(`[name="labCapacity${i}"]`).value) || 0;

//         if (type && numLabsVal > 0 && capacity > 0) {
//             labs.push({
//                 type,
//                 numLabs: numLabsVal,
//                 maxCapacity: capacity
//             });
//         }
//     }

//     // Collect departments
//     const departments = [];
//     const numDepartments = parseInt(document.getElementById('numDepartments').value) || 0;
//     for (let i = 1; i <= numDepartments; i++) {
//         const name = document.querySelector(`[name="departmentName${i}"]`).value.trim();
//         const faculties = document.querySelector(`[name="facultyNames${i}"]`).value
//             .split(',')
//             .map(s => s.trim())
//             .filter(s => s.length > 0);

//         if (name && faculties.length > 0) {
//             departments.push({
//                 name,
//                 faculties
//             });
//         }
//     }

//     // Max lectures per faculty
//     const maxLecturesPerFaculty = parseInt(document.getElementById('maxLecturesPerFaculty').value) || 0;

//     const timetableData = {
//         branches,
//         lectureRooms,
//         labs,
//         departments,
//         maxLecturesPerFaculty
//     };

//     console.log("Data to send:", timetableData);
//     console.log("Payload size:", JSON.stringify(timetableData).length, "bytes");

//     fetch('http://localhost:5000/generate-timetable', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(timetableData)
//     })
//     .then(response => response.json())
//     .then(result => {
//         console.log("Timetable Result:", result);
//         alert("Timetable generated successfully!");
//     })
//     .catch(err => {
//         console.error("Error:", err);
//         alert("Failed to generate timetable. See console for details.");
//     });
// });

// =========================
// Render Dynamic Inputs
// =========================

// script.js (updated) - includes grouping/shift-aware validation
// ... all your functions remain unchanged above

// Define constants (adjust as needed)
const WORKING_DAYS_PER_WEEK = 5;
const LECTURES_PER_SUBJECT_PER_WEEK = 4; // adjust if needed

function renderBranches() {
  const container = document.getElementById('branchesContainer');
  container.innerHTML = '';
  const n = parseInt(document.getElementById('numBranches').value, 10) || 0;
  for (let i = 1; i <= n; i++) {
    container.innerHTML += `
      <div class="branch-block">
        <h3>Branch ${i}</h3>
        <label>Name: <input type="text" name="branchName${i}" required></label><br/>
        <label>Total No. of Students: <input type="number" name="students${i}" min="1" required></label><br/>
        <label>Subjects (comma separated): <input type="text" name="subjects${i}" required placeholder="e.g. Math, Physics"></label><br/>
        <label>No. of Practical Subjects: <input type="number" name="numPracticals${i}" min="0" value="0" onchange="renderPracticals(${i})"></label><br/>
        <div id="practicalsContainer${i}"></div>
        <label>Total Class Hours per Day (minutes): <input type="number" name="classHours${i}" min="1" required></label><br/>
        <label>Per Period Duration (minutes): <input type="number" name="periodDuration${i}" min="1" required></label>
      </div><hr/>
    `;
  }
}

function renderPracticals(branchIndex) {
  const container = document.getElementById(`practicalsContainer${branchIndex}`);
  container.innerHTML = '';
  const numPracticals = parseInt(document.querySelector(`[name="numPracticals${branchIndex}"]`)?.value, 10) || 0;
  for (let j = 1; j <= numPracticals; j++) {
    container.innerHTML += `
      <div class="practical-block">
        <h4>Practical Subject ${j}</h4>
        <label>Name: <input type="text" name="practicalName${branchIndex}_${j}" placeholder="(optional)"></label><br/>
        <label>No. of Practical Classes per Week: <input type="number" name="practicalClasses${branchIndex}_${j}" min="0" value="0"></label><br/>
      </div>
    `;
  }
}

function renderLabTypes() {
  const container = document.getElementById('labsContainer');
  container.innerHTML = '';
  const n = parseInt(document.getElementById('numLabTypes').value, 10) || 0;
  for (let i = 1; i <= n; i++) {
    container.innerHTML += `
      <div class="labtype-block">
        <h3>Lab Type ${i}</h3>
        <label>Lab Name: <input type="text" name="labType${i}" required></label><br/>
        <label>No. of Labs: <input type="number" name="numLabs${i}" min="1" required></label><br/>
        <label>Max Capacity per Lab: <input type="number" name="labCapacity${i}" min="1" required></label>
      </div><hr/>
    `;
  }
}

function renderDepartments() {
  const container = document.getElementById('departmentsContainer');
  container.innerHTML = '';
  const n = parseInt(document.getElementById('numDepartments').value, 10) || 0;
  for (let i = 1; i <= n; i++) {
    container.innerHTML += `
      <div class="department-block">
        <h3>Department ${i}</h3>
        <label>Name: <input type="text" name="departmentName${i}" required></label><br/>
        <label>No. of Faculty Members: <input type="number" id="numFaculty${i}" name="numFaculty${i}" min="0" value="0" onchange="renderFaculty(${i})"></label><br/>
        <div id="facultiesContainer${i}"></div>
      </div><hr/>
    `;
  }
}

function renderFaculty(deptIndex) {
  const container = document.getElementById(`facultiesContainer${deptIndex}`);
  container.innerHTML = '';
  const numFaculty = parseInt(document.getElementById(`numFaculty${deptIndex}`)?.value, 10) || 0;
  for (let j = 1; j <= numFaculty; j++) {
    container.innerHTML += `
      <div class="faculty-block">
        <h4>Faculty ${j}</h4>
        <label>Name: <input type="text" name="facultyName${deptIndex}_${j}" required></label><br/>
        <label>Assigned Subjects (comma separated): <input type="text" name="facultySubjects${deptIndex}_${j}" placeholder="e.g. Math, Physics" required></label>
      </div>
    `;
  }
}

// Form submit handler
document.getElementById('timetable-form').addEventListener('submit', function (e) {
  e.preventDefault();

  // Collect Branches
  const branches = [];
  const numBranches = parseInt(document.getElementById('numBranches').value, 10) || 0;
  for (let i = 1; i <= numBranches; i++) {
    const name = (document.querySelector(`[name="branchName${i}"]`)?.value || '').trim();
    const totalStudents = parseInt(document.querySelector(`[name="students${i}"]`)?.value, 10) || 0;
    const subjects = (document.querySelector(`[name="subjects${i}"]`)?.value || '')
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0);

    const numPracticals = parseInt(document.querySelector(`[name="numPracticals${i}"]`)?.value, 10) || 0;
    const practicals = [];
    for (let j = 1; j <= numPracticals; j++) {
      const pname = (document.querySelector(`[name="practicalName${i}_${j}"]`)?.value || '').trim();
      const pclasses = parseInt(document.querySelector(`[name="practicalClasses${i}_${j}"]`)?.value, 10) || 0;
      practicals.push({ name: pname || `Practical ${j}`, classesPerWeek: pclasses });
    }

    const classHours = parseInt(document.querySelector(`[name="classHours${i}"]`)?.value, 10) || 0;
    const periodDuration = parseInt(document.querySelector(`[name="periodDuration${i}"]`)?.value, 10) || 0;

    if (name && totalStudents > 0 && subjects.length > 0 && classHours > 0 && periodDuration > 0) {
      branches.push({
        name,
        totalStudents,
        subjects,
        practicals,
        classHoursPerDay: classHours,
        periodDuration
      });
    }
  }

  // Lecture Rooms
  const lectureRooms = {
    totalRooms: parseInt(document.getElementById('numLectureRooms')?.value, 10) || 0,
    maxCapacity: parseInt(document.getElementById('lectureRoomCapacity')?.value, 10) || 0
  };

  // Labs
  const labs = [];
  const numLabs = parseInt(document.getElementById('numLabTypes').value, 10) || 0;
  for (let i = 1; i <= numLabs; i++) {
    const type = (document.querySelector(`[name="labType${i}"]`)?.value || '').trim();
    const numLabsVal = parseInt(document.querySelector(`[name="numLabs${i}"]`)?.value, 10) || 0;
    const capacity = parseInt(document.querySelector(`[name="labCapacity${i}"]`)?.value, 10) || 0;
    if (type && numLabsVal > 0 && capacity > 0) {
      labs.push({ type, numLabs: numLabsVal, maxCapacity: capacity });
    }
  }

  // Departments
  const departments = [];
  const numDepartments = parseInt(document.getElementById('numDepartments').value, 10) || 0;
  for (let i = 1; i <= numDepartments; i++) {
    const name = (document.querySelector(`[name="departmentName${i}"]`)?.value || '').trim();
    const numFaculty = parseInt(document.getElementById(`numFaculty${i}`)?.value, 10) || 0;
    const faculties = [];
    for (let j = 1; j <= numFaculty; j++) {
      const fname = (document.querySelector(`[name="facultyName${i}_${j}"]`)?.value || '').trim();
      const fsubjects = (document.querySelector(`[name="facultySubjects${i}_${j}"]`)?.value || '')
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      if (fname) {
        faculties.push({ name: fname, assignedSubjects: fsubjects });
      }
    }
    if (name && faculties.length > 0) {
      departments.push({ name, faculties });
    }
  }

  // Max lectures per faculty
  const maxLecturesPerFaculty = parseInt(document.getElementById('maxLecturesPerFaculty')?.value, 10) || 0;

  // Minimal validation
  const errors = [];
  if (branches.length === 0) errors.push("Please fill at least one branch with required details.");
  if (lectureRooms.totalRooms <= 0 || lectureRooms.maxCapacity <= 0) errors.push("Please fill lecture room details.");
  if (departments.length === 0) errors.push("Please fill at least one department with faculties.");
  if (maxLecturesPerFaculty <= 0) errors.push("Please fill max lectures per faculty.");

  if (errors.length) {
    alert(errors.join("\n"));
    return;
  }

  // Payload with assumptions included
  const payload = {
    branches,
    lectureRooms,
    labs,
    departments,
    maxLecturesPerFaculty,
    validationAssumptions: {
      workingDaysPerWeek: WORKING_DAYS_PER_WEEK,
      lecturesPerSubjectPerWeek: LECTURES_PER_SUBJECT_PER_WEEK
    }
  };

  console.log('Payload:', payload);

  // ✅ Save payload to localStorage and redirect
  localStorage.setItem("timetablePayload", JSON.stringify(payload));
  window.open("timetables.html", "_blank");
});

