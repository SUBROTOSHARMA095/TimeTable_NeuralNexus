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
//     renderTimetable(data.timetable, true);
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

//   renderTimetable(timetable, false);
//   generationCount++;
// }

// function renderTimetable(timetable, isFinal) {
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

//   if (!isFinal) {
//     div.addEventListener('click', async () => {
//       await saveTimetable(timetable);
//       container.innerHTML = '';
//       renderTimetable(timetable, true);
//       generateBtn.disabled = true;
//     });
//   }

//   container.appendChild(div);
// }

// async function saveTimetable(timetable) {
//   await fetch('http://localhost:5000/save-timetable', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ timetable })
//   });
//   alert("Timetable saved!");
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
//     generateTimetable();
//   }
// })();

const container = document.getElementById('tablesContainer');
const generateBtn = document.getElementById('generateBtn');
const clearBtn = document.getElementById('clearBtn');
let generationCount = 0;
const maxGenerations = 5;

async function checkSavedTimetable() {
  const res = await fetch('http://localhost:5000/get-saved-timetable');
  const data = await res.json();
  if (data.timetable) {
    container.innerHTML = '';
    renderTimetable(data.timetable, data.facultyWorkload || {}, true);
    generateBtn.disabled = true;
    return true;
  }
  return false;
}

async function generateTimetable() {
  if (generationCount >= maxGenerations) {
    alert("Maximum of 5 timetables reached.");
    return;
  }
  const payload = JSON.parse(localStorage.getItem('timetablePayload'));
  if (!payload) {
    alert("No payload found. Please go back and fill the form.");
    return;
  }

  const res = await fetch('http://localhost:5000/generate-timetable', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  const timetable = data.timetable;
  const facultyWorkload = data.facultyWorkload;

  renderTimetable(timetable, facultyWorkload, false);
  generationCount++;
}

function renderTimetable(timetable, facultyWorkload = {}, isFinal) {
  const div = document.createElement('div');
  div.className = 'timetable' + (isFinal ? ' final' : '');

  for (const branch in timetable) {
    const branchDiv = document.createElement('div');
    branchDiv.innerHTML = `<h3>${branch}</h3>`;
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

    for (let d = 0; d < days.length; d++) {
      const dayDiv = document.createElement('div');
      dayDiv.innerHTML = `<h4>${days[d]}</h4>`;
      const shifts = timetable[branch][d];

      for (const shift in shifts) {
        const table = document.createElement('table');
        table.innerHTML = `<tr><th colspan="${shifts[shift].length}">${shift}</th></tr>`;
        const tr = document.createElement('tr');
        shifts[shift].forEach(slot => {
          const td = document.createElement('td');
          td.innerText = `${slot[0]} (${slot[2]})\n${slot[1]}`;
          tr.appendChild(td);
        });
        table.appendChild(tr);
        dayDiv.appendChild(table);
      }
      branchDiv.appendChild(dayDiv);
    }
    div.appendChild(branchDiv);
  }

  // Append Faculty Workload at the bottom
  if (facultyWorkload && Object.keys(facultyWorkload).length > 0) {
    const workloadDiv = document.createElement('div');
    workloadDiv.innerHTML = `<h3>Faculty Workload</h3>`;
    const ul = document.createElement('ul');
    for (const [faculty, load] of Object.entries(facultyWorkload)) {
      const li = document.createElement('li');
      li.innerText = `${faculty}: ${load} classes`;
      ul.appendChild(li);
    }
    workloadDiv.appendChild(ul);
    div.appendChild(workloadDiv);
  }

  if (!isFinal) {
    div.addEventListener('click', async () => {
      await saveTimetable(timetable);
      container.innerHTML = '';
      renderTimetable(timetable, facultyWorkload, true);
      generateBtn.disabled = true;
    });
  }

  container.appendChild(div);
}

async function saveTimetable(timetable) {
  await fetch('http://localhost:5000/save-timetable', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ timetable })
  });
  alert("Timetable saved!");
}

generateBtn.addEventListener('click', () => generateTimetable());
clearBtn.addEventListener('click', () => {
  container.innerHTML = '';
  generationCount = 0;
  generateBtn.disabled = false;
});

(async function init() {
  const hasSaved = await checkSavedTimetable();
  if (!hasSaved) {
    generateTimetable();
  }
})();
