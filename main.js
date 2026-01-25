/* =========================
   HELPERS
========================= */
const $ = id => document.getElementById(id);

const hideLoader = () => {
  $("loader").classList.add("hidden");
};

/* =========================
   LOAD MAIN DATA
========================= */
async function loadMainData() {
  const res = await fetch("data.json");
  if (!res.ok) throw new Error("Failed to load data.json");
  const data = await res.json();

  // HEADER
  $("name").textContent = data.name;
  $("role").textContent = data.role;

  $("email").textContent = data.email;
  $("email").href = `mailto:${data.email}`;

  $("linkedin").textContent = `linkedin.com/in/${data.linkedin}`;
  $("linkedin").href = `https://linkedin.com/in/${data.linkedin}`;

  $("github").textContent = `github.com/${data.github}`;
  $("github").href = `https://github.com/${data.github}`;

  $("summary").textContent = data.summary;

  renderSkills(data.skills);
  renderExperience(data.experience);
  renderEducation(data.education);
  renderLanguages(data.languages);
}

/* =========================
   RENDER FUNCTIONS
========================= */
function renderSkills(skills) {
  const div = $("skills");
  div.innerHTML = "";

  for (const section in skills) {
    div.innerHTML += `
      <div class="skill-block">
        <h4>${section}</h4>
        <ul>${skills[section].map(s => `<li>${s}</li>`).join("")}</ul>
      </div>
    `;
  }
}

function renderExperience(exp) {
  const div = $("experience");
  div.innerHTML = "";

  exp.forEach(job => {
    div.innerHTML += `
      <div class="exp-item">
        <div class="exp-header">
          <h4>${job.title}</h4>
          <p class="date">${job.date}</p>
        </div>
        <p class="company">${job.company}</p>
        <ul>${job.tasks.map(t => `<li>${t}</li>`).join("")}</ul>
      </div>
    `;
  });
}

function renderEducation(edu) {
  $("education").innerHTML = `
    <p><strong>${edu.degree}</strong></p>
    <p>${edu.school} — ${edu.year}</p>
  `;
}

function renderLanguages(langs) {
  const ul = $("languages");
  ul.innerHTML = "";
  langs.forEach(l => ul.innerHTML += `<li>${l}</li>`);
}

/* =========================
   PROJECTS
========================= */
async function loadProjects() {
  const res = await fetch("projects.json");
  if (!res.ok) throw new Error("Failed to load projects.json");
  const projects = await res.json();

  const div = $("projects");
  div.innerHTML = "";

  projects.forEach(p => {
    div.innerHTML += `
      <a href="${p.link || "#"}" target="_blank" class="project-link" rel="noopener">
        <div class="project">
          ${p.image ? `<img src="${p.image}" class="project-img" alt="${p.title}">` : ""}
          <h4>${p.title}</h4>
          <p class="tech">${p.tech}</p>
          <ul>${p.points.map(pt => `<li>${pt}</li>`).join("")}</ul>
        </div>
      </a>
    `;
  });
}

/* =========================
   INIT APP
========================= 

async function initPortfolio() {
  try {
    await Promise.all([
      loadMainData(),
      loadProjects()
    ]);
  } catch (err) {
    console.error(err);
    alert("Something went wrong loading the portfolio 😢");
  } finally {
    hideLoader();
  }
}

document.addEventListener("DOMContentLoaded", initPortfolio); 

*/
