/* =========================
   HELPERS
========================= */
const $ = id => document.getElementById(id);

const hideLoader = () => {
    const loader = $("loader");
    if (loader) loader.classList.add("hidden");
};

/* =========================
   LOAD MAIN DATA (data.json)
========================= */
async function loadMainData() {
    try {
        const res = await fetch("data.json");
        if (!res.ok) throw new Error("Failed to load data.json");
        const data = await res.json();

        // HEADER & INFO
        if ($("name")) $("name").textContent = data.name;
        if ($("role")) $("role").textContent = data.role;

        if ($("email")) {
            $("email").textContent = data.email;
            $("email").href = `mailto:${data.email}`;
        }

        if ($("linkedin")) {
            $("linkedin").textContent = `linkedin.com/in/${data.linkedin}`;
            $("linkedin").href = `https://linkedin.com/in/${data.linkedin}`;
        }

        if ($("github")) {
            $("github").textContent = `github.com/${data.github}`;
            $("github").href = `https://github.com/${data.github}`;
        }

        if ($("summary")) $("summary").textContent = data.summary;

        if (data.skills) renderSkills(data.skills);
        if (data.experience) renderExperience(data.experience);
        if (data.education) renderEducation(data.education);
        if (data.languages) renderLanguages(data.languages);
        
    } catch (err) {
        console.error("Error loading main data:", err);
    }
}

/* =========================
   RENDER FUNCTIONS
========================= */
function renderSkills(skills) {
    const div = $("skills");
    if (!div) return;
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
    if (!div) return;
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
    const div = $("education");
    if (!div) return;
    div.innerHTML = `
        <p><strong>${edu.degree}</strong></p>
        <p>${edu.school} — ${edu.year}</p>
    `;
}

function renderLanguages(langs) {
    const ul = $("languages");
    if (!ul) return;
    ul.innerHTML = "";
    langs.forEach(l => {
        const li = document.createElement("li");
        li.textContent = l;
        ul.appendChild(li);
    });
}

/* =========================
   PROJECTS (projects.json)
========================= */
async function loadProjects() {
    try {
        const res = await fetch("projects.json");
        if (!res.ok) throw new Error("Failed to load projects.json");
        const data = await res.json();

        const div = $("projects");
        if (!div) return;
        div.innerHTML = "";

        // ملاحظة: نستخدم data.projects لأن السكريبت ينشئ كائن يحتوي على مصفوفة
        const projectsArray = data.projects || [];

        projectsArray.forEach(p => {
            div.innerHTML += `
                <a href="${p.link || "#"}" target="_blank" class="project-link" rel="noopener">
                    <div class="project">
                        ${p.image ? `<img src="${p.image}" class="project-img" alt="${p.title}" onerror="this.style.display='none'">` : ""}
                        <h4>${p.title}</h4>
                        <p class="tech"><strong>Tech:</strong> ${p.tech}</p>
                        <ul>${p.points.map(pt => `<li>${pt}</li>`).join("")}</ul>
                    </div>
                </a>
            `;
        });
    } catch (err) {
        console.error("Error loading projects:", err);
    }
}

/* =========================
   INIT APP
========================= */
async function initPortfolio() {
    // تشغيل العمليتين معاً لسرعة التحميل
    await Promise.allSettled([
        loadMainData(),
        loadProjects()
    ]);
    
    hideLoader();
}

document.addEventListener("DOMContentLoaded", initPortfolio);
