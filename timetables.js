// const container = document.getElementById('tablesContainer');
// const generateBtn = document.getElementById('generateBtn');
// const clearBtn = document.getElementById('clearBtn');
// let generationCount = 0;
// const maxGenerations = 5;

// async function checkSavedTimetable() {
//   const res = await fetch('http://localhost:5000/get-saved-timetable');
//   const data = await res.json();
//   if (data.timetable) {
//     container.innerHTML = '';
//     renderTimetable(data.timetable, data.facultyWorkload || {}, true);
//     generateBtn.disabled = true;
//     return true;
//   }
//   return false;
// }

// async function generateTimetable() {
//   if (generationCount >= maxGenerations) {
//     alert("Maximum of 5 timetables reached.");
//     return;
//   }
//   const payload = JSON.parse(localStorage.getItem('timetablePayload'));
//   if (!payload) {
//     alert("No payload found. Please go back and fill the form.");
//     return;
//   }

//   const res = await fetch('http://localhost:5000/generate-timetable', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify(payload)
//   });
//   const data = await res.json();
//   const timetable = data.timetable;
//   const facultyWorkload = data.facultyWorkload;

//   container.innerHTML = ''; // ✅ Clear previous timetable
//   renderTimetable(timetable, facultyWorkload, false);
//   generationCount++;
// }

// function renderTimetable(timetable, facultyWorkload = {}, isFinal) {
//   const div = document.createElement('div');
//   div.className = 'timetable' + (isFinal ? ' final' : '');

//   for (const branch in timetable) {
//     const branchDiv = document.createElement('div');
//     branchDiv.innerHTML = `<h3>${branch}</h3>`;
//     const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

//     for (let d = 0; d < days.length; d++) {
//       const dayDiv = document.createElement('div');
//       dayDiv.innerHTML = `<h4>${days[d]}</h4>`;
//       const shifts = timetable[branch][d];

//       for (const shift in shifts) {
//         const table = document.createElement('table');
//         table.innerHTML = `<tr><th colspan="${shifts[shift].length}">${shift}</th></tr>`;
//         const tr = document.createElement('tr');
//         shifts[shift].forEach(slot => {
//           const td = document.createElement('td');
//           td.innerText = `${slot[0]} (${slot[2]})\n${slot[1]}`;
//           tr.appendChild(td);
//         });
//         table.appendChild(tr);
//         dayDiv.appendChild(table);
//       }
//       branchDiv.appendChild(dayDiv);
//     }
//     div.appendChild(branchDiv);
//   }

//   // Faculty Workload section
//   if (facultyWorkload && Object.keys(facultyWorkload).length > 0) {
//     const workloadDiv = document.createElement('div');
//     workloadDiv.innerHTML = `<h3>Faculty Workload</h3>`;
//     const ul = document.createElement('ul');
//     for (const [faculty, load] of Object.entries(facultyWorkload)) {
//       const li = document.createElement('li');
//       li.innerText = `${faculty}: ${load} classes`;
//       ul.appendChild(li);
//     }
//     workloadDiv.appendChild(ul);
//     div.appendChild(workloadDiv);
//   }

//   // ✅ Add Save button only if not final
//   if (!isFinal) {
//     const saveBtn = document.createElement('button');
//     saveBtn.innerText = "Save This Timetable";
//     saveBtn.addEventListener('click', async () => {
//       await saveTimetable(timetable);
//       container.innerHTML = '';
//       renderTimetable(timetable, facultyWorkload, true);
//       generateBtn.disabled = true;
//     });
//     div.appendChild(saveBtn);
//   }

//   container.appendChild(div);
// }

// async function saveTimetable(timetable) {
//   const res = await fetch('http://localhost:5000/save-timetable', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ timetable })
//   });
//   const data = await res.json();
//   alert(data.message || "Timetable saved!");
// }

// generateBtn.addEventListener('click', () => generateTimetable());
// clearBtn.addEventListener('click', () => {
//   container.innerHTML = '';
//   generationCount = 0;
//   generateBtn.disabled = false;
// });

// (async function init() {
//   const hasSaved = await checkSavedTimetable();
//   if (!hasSaved) {
//     generateTimetable(); // generate first one
//   }
// })();

const generateBtn = document.getElementById('generateBtn');
const saveBtn = document.getElementById('saveBtn');
const clearBtn = document.getElementById('clearBtn');
const browseBtn = document.getElementById('browseBtn');
const loader = document.getElementById('loader');
const tablesContainer = document.getElementById('tablesContainer');
const workloadDiv = document.getElementById('workloadDiv');
const savedTimetablesList = document.getElementById('savedTimetablesList');

let currentTimetable = null;

function getTimetablePayload() {
    const payload = localStorage.getItem('timetablePayload');
    return payload ? JSON.parse(payload) : null;
}

// -----------------------------
// Generate Timetable from Backend
// -----------------------------
async function generateTimetable() {
    tablesContainer.innerHTML = '';
    workloadDiv.innerHTML = '';
    savedTimetablesList.style.display = 'none';
    loader.style.display = 'block';
    saveBtn.style.display = 'none';
    
    const payload = getTimetablePayload();

    if (!payload) {
        loader.style.display = 'none';
        tablesContainer.innerHTML = `<h2 style="color:red;">No data found. Please go back to the input page to add data.</h2>`;
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/generate-timetable', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) { throw new Error('Network response was not ok'); }

        const data = await response.json();
        currentTimetable = data;
        renderTimetable(data.timetable);
        renderFacultyWorkload(data.facultyWorkload);

        loader.style.display = 'none';
        saveBtn.style.display = 'inline-block';

    } catch (error) {
        console.error('Error:', error);
        loader.style.display = 'none';
        tablesContainer.innerHTML = `<h2 style="color:red;">Error generating timetable. Please check the backend server.</h2>`;
    }
}

// -----------------------------
// Save Timetable
// -----------------------------
async function saveTimetable() {
    if (!currentTimetable) {
        alert('No timetable to save!');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/save-timetable', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timetable: currentTimetable.timetable }),
        });

        if (response.ok) {
            alert('Timetable saved successfully!');
            // After saving, automatically display the newly saved timetable
            await getFinalizedTimetable();
        } else {
            alert('Failed to save timetable.');
        }
    } catch (error) {
        console.error('Error saving timetable:', error);
        alert('An error occurred while saving.');
    }
}

// -----------------------------
// Get and display the finalized timetable
// -----------------------------
async function getFinalizedTimetable() {
    tablesContainer.innerHTML = '';
    workloadDiv.innerHTML = '';
    savedTimetablesList.style.display = 'none'; // Hide the saved list
    loader.style.display = 'block';

    try {
        const response = await fetch('http://localhost:5000/get-saved-timetable');
        const data = await response.json();
        loader.style.display = 'none';

        if (data.timetable) {
            tablesContainer.innerHTML = '<h2>Finalized Timetable</h2>';
            renderTimetable(data.timetable);
            // Assuming workload data isn't saved with the final timetable, you'd need to re-calculate it
            // or modify the backend to return it with this endpoint. For now, we'll skip the workload.
        } else {
            tablesContainer.innerHTML = '<h2>No finalized timetable found.</h2>';
        }
    } catch (error) {
        console.error('Error fetching finalized timetable:', error);
        loader.style.display = 'none';
        tablesContainer.innerHTML = `<h2>Error fetching finalized timetable.</h2>`;
    }
}


// -----------------------------
// Render Timetable (remains the same)
// -----------------------------
function renderTimetable(timetable) {
    if (!timetable || Object.keys(timetable).length === 0) {
        tablesContainer.innerHTML = '<h2>No timetable could be generated.</h2>';
        return;
    }

    let html = '';
    for (const branchName in timetable) {
        html += `<h2>${branchName}</h2>`;
        const sections = timetable[branchName];

        for (const sectionName in sections) {
            const sectionData = sections[sectionName];
            const schedule = sectionData.schedule;
            
            html += `<h3>${sectionName} - ${sectionData.shift} Shift</h3>`;
            html += '<table>';
            
            const days = Object.keys(schedule);
            const maxPeriods = Math.max(...days.map(day => schedule[day].length));

            html += '<thead><tr><th>Period</th>';
            days.forEach(day => { html += `<th>${day}</th>`; });
            html += '</tr></thead>';

            html += '<tbody>';
            for (let i = 0; i < maxPeriods; i++) {
                html += `<tr><td>${i + 1}</td>`;
                days.forEach(day => {
                    const slot = schedule[day][i];
                    if (slot) {
                        html += `<td>${slot.subject}<br>(${slot.faculty})<br>${slot.room}</td>`;
                    } else {
                        html += `<td>-</td>`;
                    }
                });
                html += '</tr>';
            }
            html += '</tbody></table>';
        }
    }
    tablesContainer.innerHTML = html;
}

// -----------------------------
// Render Faculty Workload (remains the same)
// -----------------------------
function renderFacultyWorkload(workloadData) {
    if (!workloadData || workloadData.length === 0) {
        workloadDiv.innerHTML = '';
        return;
    }

    workloadData.sort((a, b) => b.workload - a.workload);
    const maxWorkload = workloadData[0] ? workloadData[0].workload : 1;

    let html = '<h2>Faculty Workload</h2>';
    html += '<table><thead><tr><th>Faculty</th><th>Workload</th><th>Relative Load</th></tr></thead><tbody>';
    
    workloadData.forEach(faculty => {
        const relativeLoad = (faculty.workload / maxWorkload) * 100;
        html += `
            <tr>
                <td>${faculty.name}</td>
                <td>${faculty.workload} classes</td>
                <td>
                    <div class="relative-load-bar">
                        <div class="load-fill" style="width: ${relativeLoad}%;"></div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    workloadDiv.innerHTML = html;
}

// -----------------------------
// Event Listeners
// -----------------------------
generateBtn.addEventListener('click', generateTimetable);
saveBtn.addEventListener('click', saveTimetable);
clearBtn.addEventListener('click', () => {
    tablesContainer.innerHTML = '';
    workloadDiv.innerHTML = '';
    savedTimetablesList.style.display = 'none';
    saveBtn.style.display = 'none';
    currentTimetable = null;
});

// Modify the browseBtn listener to get the finalized timetable instead of saved ones
browseBtn.addEventListener('click', getFinalizedTimetable);

// Initial action: Load a new timetable on page load
window.onload = () => {
    if (getTimetablePayload()) {
        generateTimetable();
    }
};