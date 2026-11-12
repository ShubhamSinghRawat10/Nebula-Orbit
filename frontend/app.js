const API = "/api";
const app = document.querySelector("#app");
const state = { user: null, token: localStorage.getItem("nebula_token"), page: "overview", authMode: "login", authRole: "student", courses: [], quizzes: [], lessons: [], students: [], enrolledCourseIds: [], enrollmentsLoaded: false, courseView: "my", focusLessons: [], lessonTopicOptions: [], lessonViewing: null, progress: null, plan: null, recommendations: [], recommendationData: null, focusCourse: null, focusTopics: [], activeQuiz: null, selected: [], review: null, quizStartedAt: null, editingQuiz: null, quizDraftQuestions: [], toastTimer: null };

document.addEventListener("error", event => {
  const image = event.target;
  if (image instanceof HTMLImageElement && image.classList.contains("course-art-photo")) image.remove();
}, true);

const icons = {
  nebula: '<svg viewBox="0 0 24 24" fill="none"><path d="M7.5 17.7a5.5 5.5 0 0 1-1-10.9A7 7 0 0 1 20 9.5a4.2 4.2 0 0 1-1.2 8.2H7.5Z" stroke="currentColor" stroke-width="1.8"/><path d="m10 14 2-4 2 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  overview: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="5" rx="2"/><rect x="14" y="12" width="7" height="9" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/></svg>',
  courses: '<svg viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21V5.5Z"/><path d="M4 6v15m5-14h7m-7 4h7"/></svg>',
  plan: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M16 3v4M8 3v4M3 10h18m-13 5h3m-3 3h7"/></svg>',
  progress: '<svg viewBox="0 0 24 24"><path d="M3 3v18h18M7 14l4-4 4 3 6-7"/></svg>',
  profile: '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
  admin: '<svg viewBox="0 0 24 24"><path d="M4 19V5m0 14h16M8 15l3-4 3 2 5-7"/><circle cx="19" cy="6" r="1"/></svg>',
  quiz: '<svg viewBox="0 0 24 24"><path d="M8 4h10a2 2 0 0 1 2 2v14H6V6a2 2 0 0 1 2-2Z"/><path d="M9 9h7m-7 4h7m-7 4h4M4 7v14"/></svg>',
  spark: '<svg viewBox="0 0 24 24"><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2L12 3Z"/><path d="m19 14 .8 2.3L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.7L19 14Z"/></svg>',
  clock: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  search: '<svg viewBox="0 0 24 24"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></svg>',
  bell: '<svg viewBox="0 0 24 24"><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-8 12h4"/></svg>',
  eye: '<svg viewBox="0 0 24 24"><path d="M2.5 12s3.3-6 9.5-6 9.5 6 9.5 6-3.3 6-9.5 6-9.5-6-9.5-6Z"/><circle cx="12" cy="12" r="2.5"/></svg>',
  eyeOff: '<svg viewBox="0 0 24 24"><path d="m3 3 18 18M10.6 6.2A10.7 10.7 0 0 1 12 6c6.2 0 9.5 6 9.5 6a15 15 0 0 1-3.1 3.6M6.2 6.3C3.8 8 2.5 12 2.5 12s3.3 6 9.5 6c1.2 0 2.3-.2 3.2-.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>',
  logout: '<svg viewBox="0 0 24 24"><path d="M10 17l5-5-5-5m5 5H3m9-9h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/></svg>',
  arrow: '<svg viewBox="0 0 24 24"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>',
  book: '<svg viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21V5.5Z"/><path d="M8 7h8m-8 4h8"/></svg>',
  fire: '<svg viewBox="0 0 24 24"><path d="M12 22c4 0 7-3 7-7 0-3-2-5-4-7 0 2-1 3-2 3 0-4-2-7-5-9 1 5-4 8-4 13 0 4 3 7 8 7Z"/><path d="M12 22c2 0 3-2 3-4 0-1-1-3-2-4 0 2-2 2-2 4 0 1-1 2-1 2"/></svg>',
  close: '<svg viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></svg>'
};

const esc = (s = "") => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const initials = name => (name || "N").trim().split(/\s+/).slice(0, 2).map(x => x[0]).join("").toUpperCase();
function toast(message, bad = false) {
  const node = document.querySelector("#toast"); node.textContent = message; node.classList.toggle("bad", bad); node.classList.add("show");
  clearTimeout(state.toastTimer); state.toastTimer = setTimeout(() => node.classList.remove("show"), 3000);
}
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", "X-Timezone": Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC", ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}), ...(options.headers || {}) };
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) { if (response.status === 401) logout(false); throw new Error(data.error || "Something went wrong. Please try again."); }
  return data;
}
function brand() { return `<div class="brand"><div class="brand-mark">${icons.nebula}</div><div><span class="brand-name">nebula</span><span class="brand-caption">learn in your orbit</span></div></div>`; }

function renderAuth() {
  const signup = state.authMode === "signup";
  app.innerHTML = `<main class="auth-page ${signup ? "auth-signup" : "auth-login"}"><section class="auth-left">${brand()}<div class="auth-card">
    <div class="eyebrow">Your next chapter starts here</div><h1>${signup ? "Create your account" : "Welcome back"}</h1><p>${signup ? "A learning path that moves at your pace." : "Pick up where your curiosity left off."}</p>
    <div class="auth-tabs"><button class="${!signup ? "active" : ""}" data-action="auth-mode" data-mode="login">Sign in</button><button class="${signup ? "active" : ""}" data-action="auth-mode" data-mode="signup">Create account</button></div>
    <form id="auth-form" class="${signup ? "auth-form-signup" : ""}">${signup ? `<div class="auth-signup-grid">
      <div class="field"><label for="auth-name">Your name</label><input id="auth-name" name="name" autocomplete="name" placeholder="e.g. Sam Rawat" required minlength="2" /></div>
      <div class="field"><label for="auth-email">Email address</label><input id="auth-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required /></div>
      <div class="field"><label for="auth-password">Password</label><div class="auth-password-control"><input id="auth-password" name="password" type="password" autocomplete="new-password" placeholder="At least 10 characters" required minlength="10" /><button class="auth-password-toggle" type="button" data-action="toggle-password" data-target="auth-password" aria-label="Show password" aria-pressed="false">${icons.eye}</button></div></div>
      <div class="field"><label for="auth-role">Account type</label><select id="auth-role" name="role"><option value="student" ${state.authRole === "student" ? "selected" : ""}>Student</option><option value="admin" ${state.authRole === "admin" ? "selected" : ""}>Administrator</option></select></div>
      <div id="student-profile-fields" class="auth-profile-fields ${state.authRole === "admin" ? "hidden" : ""}"><div class="field"><label for="auth-goal">What are you learning towards?</label><input id="auth-goal" name="goal" placeholder="e.g. Prepare for board exams" /></div><div class="form-grid"><div class="field"><label for="auth-level">Your level</label><input id="auth-level" name="level" placeholder="e.g. Class 12" /></div><div class="field"><label for="auth-minutes">Minutes per day</label><input id="auth-minutes" name="daily_minutes" type="number" min="10" max="480" value="60" /></div></div></div>
      <div id="admin-key-field" class="field auth-admin-key ${state.authRole === "student" ? "hidden" : ""}"><label for="admin-key">Admin setup key</label><div class="auth-password-control"><input id="admin-key" name="admin_signup_key" type="password" placeholder="Set in backend/.env by the project owner" /><button class="auth-password-toggle" type="button" data-action="toggle-password" data-target="admin-key" aria-label="Show setup key" aria-pressed="false">${icons.eye}</button></div><small class="auth-key-help">Your project owner sets this as <code>ADMIN_SIGNUP_KEY</code> in <code>backend/.env</code>. Ask them for it; it is private.</small></div>
    </div>` : `<div class="field"><label for="auth-email">Email address</label><input id="auth-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required /></div><div class="field"><label for="auth-password">Password</label><div class="auth-password-control"><input id="auth-password" name="password" type="password" autocomplete="current-password" placeholder="Your password" required minlength="1" /><button class="auth-password-toggle" type="button" data-action="toggle-password" data-target="auth-password" aria-label="Show password" aria-pressed="false">${icons.eye}</button></div></div>`}
      <button class="btn auth-submit" type="submit">${signup ? "Create my account" : "Sign in to Nebula"} ${icons.arrow}</button>
    </form><div class="auth-foot">${signup && state.authRole === "admin" ? "Admin key: backend/.env → ADMIN_SIGNUP_KEY. Ask the project owner; keep it private." : "Your progress is personal. Your learning is yours."}</div>
  </div><div class="auth-foot">© 2026 Nebula Learning</div></section><section class="auth-side"><div class="auth-orbit"></div><div class="auth-planet"></div><div class="auth-star"></div><div class="auth-copy"><div class="eyebrow">Built around the way you learn</div><h2>Small steps.<br/>Stronger understanding.</h2><p>Find your rhythm, focus on what matters, and watch your progress take shape.</p><div class="auth-quote"><strong>Learn with purpose.</strong> Your study path adapts as you grow.</div></div></section></main>`;
}

const navItems = {
  student: [["overview", "Overview"], ["courses", "My courses"], ["quiz", "Practice & quizzes"], ["plan", "Study plan"], ["progress", "Progress"], ["profile", "My profile"]],
  admin: [["overview", "Overview"], ["courses", "Courses"], ["lessons", "Lessons"], ["quizzes", "Quizzes"], ["students", "Students"], ["profile", "My profile"]]
};
function shell(content, title = "Overview") {
  const role = state.user.role === "admin" ? "admin" : "student";
  const items = navItems[role].map(([id, label]) => `<button class="${state.page === id ? "active" : ""}" data-action="go" data-page="${id}">${icons[id] || icons.overview}<span>${label}</span></button>`).join("");
  return `<div class="shell"><aside class="sidebar" id="sidebar">${brand()}<div class="nav-label">Workspace</div><nav class="nav">${items}</nav><div class="side-bottom">${role === "student" ? `<div class="streak-card"><div class="streak-top"><span>Study streak</span><span class="streak-icon">${icons.fire}</span></div><div class="streak-count">${state.progress?.summary?.streak_days || 0} <span>days</span></div><p>A little progress each day adds up.</p></div>` : `<div class="admin-note"><div class="eyebrow">Admin workspace</div><p>Shape the lessons and questions that help students grow.</p></div>`}<div class="profile-mini"><div class="avatar">${esc(initials(state.user.name))}</div><div class="profile-data"><div class="name">${esc(state.user.name)}</div><div class="email">${esc(state.user.email)}</div></div><button class="signout" aria-label="Sign out" title="Sign out" data-action="logout">${icons.logout}</button></div></div></aside><main class="main"><header class="topbar"><button class="icon-button mobile-menu" data-action="menu" aria-label="Open menu">☰</button><div class="mobile-brand"><span class="brand-mark">${icons.nebula}</span>nebula</div><div class="crumb">Workspace <span>/</span> <strong>${esc(title)}</strong></div><div class="top-actions"><label class="search">${icons.search}<input placeholder="Search your learning..." id="global-search" /></label><button class="icon-button" aria-label="Notifications" data-action="notifications">${icons.bell}</button><div class="avatar top-avatar">${esc(initials(state.user.name))}</div></div></header><section class="page">${content}</section></main></div>`;
}
function heading(kicker, title, subtitle, right = "") { return `<div class="page-heading"><div><div class="eyebrow">${kicker}</div><h1>${title}</h1><p>${subtitle}</p></div>${right}</div>`; }
function stat(label, value, hint, icon, extra = "") { return `<div class="stat-card"><div class="stat-top"><span>${label}</span><span class="stat-icon">${icons[icon] || icons.spark}</span></div><div class="stat-value">${value}</div><div class="stat-hint ${extra}">${hint}</div></div>`; }
function courseCover(index = 0) { return `<div class="course-cover cover-${index % 3}">${icons.book}<span class="cover-glow"></span></div>`; }
function courseArtTheme(title = "") {
  const t = title.toLowerCase();
  if (/database|dbms/.test(t)) return "database";
  if (/network/.test(t)) return "network";
  if (/security|cryptography/.test(t)) return "security";
  if (/cloud/.test(t)) return "cloud";
  if (/blockchain|distributed ledger/.test(t)) return "blockchain";
  if (/devops|ci\/cd/.test(t)) return "devops";
  if (/microprocessor|digital electronics|computer organization|architecture/.test(t)) return "hardware";
  if (/deep learning|neural network|artificial intelligence|\bai\b|natural language|\bnlp\b|big data/.test(t)) return "intelligence";
  if (/algorithm|data structure|\bdsa\b/.test(t)) return "algorithms";
  if (/operating system|compiler|theory of computation/.test(t)) return "systems";
  return "programming";
}
function courseArtwork(course, index = 0) {
  const title = course.title || course.subject || "Learning course";
  const theme = courseArtTheme(title);
  const photos = {
    database: "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?auto=format&fit=crop&w=1200&q=82",
    network: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=82",
    security: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=82",
    cloud: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=82",
    blockchain: "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=1200&q=82",
    devops: "https://images.unsplash.com/photo-1681408969415-34cb37122508?auto=format&fit=crop&w=1200&q=82",
    hardware: "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=82",
    intelligence: "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=82",
    algorithms: "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=1200&q=82",
    systems: "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=82",
    programming: "https://images.unsplash.com/photo-1681408969415-34cb37122508?auto=format&fit=crop&w=1200&q=82"
  };
  const labels = { database: "DATA SYSTEMS", network: "COMPUTER NETWORKS", security: "CYBER SECURITY", cloud: "CLOUD COMPUTING", blockchain: "BLOCKCHAIN", devops: "DEVOPS PIPELINES", hardware: "COMPUTER HARDWARE", intelligence: "ARTIFICIAL INTELLIGENCE", algorithms: "ALGORITHMS", systems: "SYSTEMS DESIGN", programming: "SOFTWARE DEVELOPMENT" };
  const glyphs = {
    database: '<ellipse cx="100" cy="39" rx="39" ry="13"/><path d="M61 39v47c0 8 17 15 39 15s39-7 39-15V39M61 62c0 8 17 15 39 15s39-7 39-15M61 84c0 8 17 15 39 15s39-7 39-15"/>',
    network: '<path d="m65 48 34 18 35-26M99 66l-27 31m27-31 39 28"/><circle cx="65" cy="48" r="10"/><circle cx="134" cy="40" r="10"/><circle cx="99" cy="66" r="12"/><circle cx="72" cy="97" r="9"/><circle cx="138" cy="94" r="9"/>',
    security: '<path d="M100 29 139 43v27c0 25-17 41-39 53-22-12-39-28-39-53V43l39-14Z"/><rect x="83" y="62" width="34" height="27" rx="7"/><path d="M91 62v-7a9 9 0 0 1 18 0v7m-9 11v6"/>',
    cloud: '<path d="M70 89h61a20 20 0 0 0 1-40 34 34 0 0 0-64-5 23 23 0 0 0 2 45Z"/><path d="M83 102v12m17-12v12m17-12v12M75 115h50"/>',
    blockchain: '<path d="m100 32 26 15v30l-26 15-26-15V47l26-15Zm0 30 26-15m-26 15-26-15m26 15v30m-26-45v30l26 15 26-15V47"/><circle cx="100" cy="32" r="5"/><circle cx="74" cy="47" r="5"/><circle cx="126" cy="47" r="5"/>',
    devops: '<rect x="55" y="48" width="29" height="29" rx="8"/><rect x="116" y="48" width="29" height="29" rx="8"/><rect x="86" y="83" width="29" height="29" rx="8"/><path d="M84 62h22l-8-8m8 8-8 8m-15 7v14h11m22-21v7h-9"/>',
    hardware: '<rect x="70" y="42" width="60" height="51" rx="10"/><path d="M84 56h32v23H84zM58 52h12m-12 15h12m-12 15h12m60-30h12m-12 15h12m-12 15h12M81 30v12m15-12v12m15-12v12m-30 51v12m15-12v12m15-12v12"/>',
    intelligence: '<path d="M100 37v58m0-43L72 67m28-15 27 21M72 67l-11 28m66-22 12 23m-39-3-24 13m24-13 25 14"/><circle cx="100" cy="37" r="8"/><circle cx="72" cy="67" r="8"/><circle cx="128" cy="72" r="8"/><circle cx="61" cy="95" r="7"/><circle cx="139" cy="95" r="7"/><circle cx="76" cy="110" r="7"/><circle cx="125" cy="110" r="7"/>',
    algorithms: '<rect x="83" y="33" width="34" height="22" rx="7"/><path d="M100 55v16M66 71h68M66 71v13m34-13v13m34-13v13M55 84h22v24H55zM89 84h22v24H89zM123 84h22v24h-22z"/><path d="m65 94 4 4 7-8m24 3v9m34-10v10"/>',
    systems: '<rect x="54" y="38" width="92" height="69" rx="10"/><path d="M54 56h92M69 48h1m11 0h1m11 0h1M69 70h24v22H69zm37 0h25m-25 11h25m-25 11h18"/>',
    programming: '<rect x="53" y="38" width="94" height="65" rx="11"/><path d="M53 57h94M68 48h1m11 0h1m11 0h1m-9 30-10 8 10 8m28-16 10 8-10 8m-6-20-8 25"/>'
  };
  return `<div class="course-art course-art-${theme} cover-${index % 3}" role="img" aria-label="${esc(title)} subject artwork"><img class="course-art-photo" src="${photos[theme]}" alt="" aria-hidden="true" loading="lazy"/><span class="course-art-grid"></span><span class="course-art-halo"></span><span class="course-art-orbit course-art-orbit-one"></span><span class="course-art-orbit course-art-orbit-two"></span><svg class="course-art-glyph" viewBox="0 0 200 140" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${glyphs[theme]}</svg><div class="course-art-caption"><span>SUBJECT AREA</span><strong>${labels[theme]}</strong></div><span class="course-art-index">${esc(course.course_id || String(index + 1).padStart(2, "0"))}</span></div>`;
}
function empty(title, detail) { return `<div class="empty"><strong>${title}</strong>${detail}</div>`; }
function youtubeSearchUrl(query) { return `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`; }
function courseVideoPanel(course, topics = course.topics || []) {
  const courseName = course.title || course.subject || "this course";
  const rawTopic = topics[0]?.topic_name || topics[0] || courseName;
  const prefix = `${courseName} - `;
  const firstTopic = rawTopic.startsWith(prefix) ? rawTopic.slice(prefix.length) : rawTopic;
  const level = course.level && course.level !== "All levels" ? course.level : "beginner";
  const overviewQuery = `${courseName} ${level} course tutorial`;
  const topicQuery = `${courseName} ${firstTopic} tutorial`;
  return `<section class="course-video-panel" aria-label="YouTube video lessons for ${esc(courseName)}"><div class="course-video-heading"><span class="course-video-play" aria-hidden="true">▶</span><div><span class="course-video-kicker">VIDEO LESSONS</span><strong>Learn with YouTube</strong><small>Topic-matched searches for ${esc(courseName)}</small></div></div><div class="course-video-links"><a href="${esc(youtubeSearchUrl(overviewQuery))}" target="_blank" rel="noopener noreferrer">Course overview <span aria-hidden="true">↗</span></a><a href="${esc(youtubeSearchUrl(topicQuery))}" target="_blank" rel="noopener noreferrer">${esc(firstTopic)} <span aria-hidden="true">↗</span></a></div></section>`;
}
function courseCard(course, index) { const enrolled = state.enrolledCourseIds.includes(course.course_id); return `<article class="course-card"><div class="course-cover cover-${index % 3}">${icons.book}<span class="cover-glow"></span></div><div class="course-info"><div class="course-meta">${esc(course.subject || "Learning")} · ${esc(course.level || "All levels")}</div><h4>${esc(course.title)}</h4><p>${esc(course.description || `${(course.topics || []).length} topics to explore`)}</p>${courseVideoPanel(course)}<div class="course-actions"><button class="subtle-link course-explore-link" data-action="open-course" data-id="${esc(course.course_id)}">Explore course ${icons.arrow}</button>${!enrolled ? `<button class="btn small" data-action="enroll-course" data-id="${esc(course.course_id)}">+ Add</button>` : `<span class="tag">Enrolled ✓</span>`}</div></div></article>`; }
function topicBars(topics = []) {
  if (!topics.length) return empty("Your topic map starts here", "Take a quiz and Nebula will reveal where to focus next.");
  return `<div class="topic-list">${topics.slice(0, 4).map(t => `<div class="topic-row"><span class="topic-title" title="${esc(t.course_id || "")}">${esc(t.topic)}${t.course_id ? ` · ${esc(t.course_id)}` : ""}</span><span class="topic-pct">${t.mastery}% mastery</span><div class="progress-track"><div class="progress-fill ${t.mastery < 45 ? "low" : t.mastery < 70 ? "mid" : ""}" style="width:${Math.max(2, t.mastery)}%"></div></div></div>`).join("")}</div>`;
}
function activityBars(attempts = []) {
  const now = new Date();
  const days = Array.from({ length: 7 }, (_, i) => { const d = new Date(now); d.setDate(d.getDate() - 6 + i); return d; });
  const counts = days.map(d => attempts.filter(a => new Date(a.created_at).toDateString() === d.toDateString()).length);
  const max = Math.max(1, ...counts);
  return `<div class="activity">${days.map((d, i) => `<div class="bar-wrap"><div class="bar ${i === 6 ? "current" : ""}" style="height:${Math.max(9, counts[i] / max * 118)}px" title="${counts[i]} quiz attempts"></div><span class="bar-label">${d.toLocaleDateString(undefined, { weekday: "short" })}</span></div>`).join("")}</div>`;
}
function scoreTrendBars(attempts = []) {
  const now = new Date();
  const days = Array.from({ length: 7 }, (_, i) => { const d = new Date(now); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - 6 + i); return d; });
  const scores = days.map(day => {
    const next = new Date(day); next.setDate(next.getDate() + 1);
    const rows = attempts.filter(a => { const date = new Date(a.created_at); return date >= day && date < next; });
    return rows.length ? Math.round(rows.reduce((sum, a) => sum + Number(a.percentage || 0), 0) / rows.length) : null;
  });
  return `<div class="score-trend">${days.map((day, i) => `<div class="score-point"><span class="score-value">${scores[i] == null ? "—" : `${scores[i]}%`}</span><div class="score-track"><div class="score-fill" style="height:${scores[i] == null ? 4 : Math.max(5, scores[i])}%"></div></div><span class="bar-label">${day.toLocaleDateString(undefined, { weekday: "short" })}</span></div>`).join("")}</div>`;
}

function studentOverview() {
  const summary = state.progress?.summary || {};
  const topics = state.progress?.topics || [];
  const goal = state.user.profile?.goal || "Keep building a learning habit";
  const enrolled = state.courses.filter(c => state.enrolledCourseIds.includes(c.course_id));
  const courses = enrolled.length ? enrolled.slice(0, 2) : state.courses.slice(0, 2);
  const weak = (state.recommendationData?.topic_guidance || []).filter(t => t.proficiency_status !== "Mastered").slice(0, 2);
  const modelAvailable = Boolean(state.recommendationData?.model?.available);
  const nextSteps = weak.length
    ? `<div class="lesson-stack">${weak.map((t, i) => `<div class="lesson-row"><span class="lesson-icon">${icons.spark}</span><div class="lesson-detail"><strong>${esc(t.proficiency_status)} · ${esc(t.topic)}</strong><span>${t.mastery}% quiz mastery · ${esc(t.next_step)}${modelAvailable && t.predicted_next_score != null ? ` · experimental next-score estimate ${t.predicted_next_score}%` : ""}</span></div><span class="lesson-time">${i ? 15 : 20} min</span></div>`).join("")}</div>`
    : `<div class="plan-teaser"><span class="lime-orb">${icons.spark}</span><div><strong>${summary.attempts ? "Your personal learning path" : "Start with a short diagnostic"}</strong><p>${summary.attempts ? "Your plan uses your quiz scores and available study time." : "Take a diagnostic quiz to establish your baseline."}</p></div><button class="subtle-link" data-action="go" data-page="${summary.attempts ? "plan" : "quiz"}">${summary.attempts ? "View plan" : "Start quiz"} ${icons.arrow}</button></div>`;
  return `${heading("Your learning space", `Hey ${esc(state.user.name.split(" ")[0])}, ready for a good study session?`, `Your goal: ${esc(goal)}`, `<button class="btn" data-action="go" data-page="${summary.attempts ? "plan" : "quiz"}">${summary.attempts ? "View study plan" : "Take your first diagnostic"} ${icons.arrow}</button>`)}
    <div class="hero-card"><div class="hero-copy"><div class="eyebrow">A little progress goes a long way</div><h2>Your next big result starts with today.</h2><p>${state.user.profile?.daily_minutes || 60} minutes today. One focused session. You’ve got this.</p><button class="btn" data-action="go" data-page="${summary.attempts ? "courses" : "quiz"}">${summary.attempts ? "Find your next lesson" : "Take a quick diagnostic"} ${icons.arrow}</button></div><div class="hero-art"><div class="hero-orbit"></div><div class="hero-planet"></div><div class="hero-dot"></div><div class="hero-star"></div></div></div>
    <div class="grid stats">${stat("Quiz average", `${summary.average || 0}%`, summary.attempts ? `${summary.attempts} attempts recorded` : "Take your first quiz to begin", "progress", summary.average >= 70 ? "positive" : "")}${stat("Study streak", `${summary.streak_days || 0} days`, "Consistency builds confidence", "fire")}${stat("Lessons completed", summary.completed_lessons || 0, "Keep your momentum going", "courses")}${stat("Daily study goal", `${state.user.profile?.daily_minutes || 60} min`, "Your chosen daily focus", "clock")}</div>
    <div class="grid two-col"><article class="card"><div class="card-head"><h3>Your activity</h3><span class="tag">Last 7 days</span></div>${activityBars(state.progress?.score_trend_attempts || state.progress?.recent_attempts || [])}</article><article class="card"><div class="card-head"><h3>Topic mastery</h3><button class="subtle-link" data-action="go" data-page="progress">See all ${icons.arrow}</button></div>${topicBars(topics)}</article></div>
    <div class="grid below-grid"><article class="card"><div class="card-head"><h3>${enrolled.length ? "Pick up where you left off" : "Courses to explore"}</h3><button class="subtle-link" data-action="go" data-page="courses">${enrolled.length ? "My courses" : "Explore catalog"} ${icons.arrow}</button></div>${courses.length ? `<div class="course-stack">${courses.map(courseCard).join("")}</div>` : empty("Your learning library is ready", "Courses and lessons will appear here once they're added.")}</article><article class="card"><div class="card-head"><h3>Suggested next steps</h3><span class="tag">${weak.length ? "Quiz-based" : "Start here"}</span></div>${nextSteps}</article></div>`;
}

function coursesPage() {
  const isAdmin = state.user.role === "admin";
  if (isAdmin) return adminCourses();
  const showExplore = state.courseView === "explore";
  const courses = showExplore ? state.courses : state.courses.filter(c => state.enrolledCourseIds.includes(c.course_id));
  if (state.focusCourse) {
    const c = state.focusCourse;
    const quizzes = state.quizzes.filter(q => q.course_id === c.course_id || !q.course_id);
    const topics = state.focusTopics.length ? state.focusTopics : (c.topics || []).map((topic_name, i) => ({ topic_id: c.topic_ids?.[i], topic_name, prerequisites: [] }));
    const lessonsByTopic = new Map();
    state.focusLessons.forEach(lesson => { const group = lessonsByTopic.get(lesson.topic_id) || []; group.push(lesson); lessonsByTopic.set(lesson.topic_id, group); });
    const lessonSection = state.focusLessons.length ? `<div class="card section-gap"><div class="card-head"><div><h3>Lessons</h3><p class="profile-help">Short guided content from your course instructor.</p></div><span class="tag">${state.focusLessons.filter(l => l.completed).length}/${state.focusLessons.length} complete</span></div>${topics.map(topic => { const lessons = lessonsByTopic.get(topic.topic_id) || []; return lessons.length ? `<section class="topic-lesson-group"><h4>${esc(topic.topic_name)}</h4><div class="lesson-stack">${lessons.map(lesson => `<div class="lesson-row"><span class="lesson-icon ${lesson.completed ? "lime" : ""}">${lesson.completed ? "✓" : icons.book}</span><div class="lesson-detail"><strong>${esc(lesson.title)}</strong><span>${esc(lesson.summary || "Open this lesson to start learning.")}</span></div><button class="subtle-link" data-action="open-lesson" data-id="${esc(lesson._id)}">${lesson.completed ? "Review" : "Start learning"} ${icons.arrow}</button></div>`).join("")}</div></section>` : ""}).join("")}</div>` : `<div class="card section-gap"><div class="card-head"><h3>Lessons</h3></div>${empty("Lessons are being prepared", "Your instructor has not published lesson content for this course yet.")}</div>`;
    return `${heading("Your library", esc(c.title), `${esc(c.subject)} · ${esc(c.level)}`, `<button class="btn secondary" data-action="back-courses">← All courses</button>`)}<div class="grid two-col"><article class="card course-detail-card">${courseArtwork(c, 0)}<div class="course-detail-copy"><div class="eyebrow">${esc(c.subject)}</div><h2>${esc(c.title)}</h2><p>${esc(c.description || "A clear path through the topics that matter.")}</p><div class="course-facts"><span>${icons.clock} ${c.estimated_hours || 1} hours</span><span>${icons.book} ${topics.length} topics</span></div></div></article><article class="card"><div class="card-head"><h3>Topics in this course</h3></div>${topics.length ? `<div class="lesson-stack">${topics.map((topic, i) => { const prefix = `${c.title} - `; const videoTopic = topic.topic_name.startsWith(prefix) ? topic.topic_name.slice(prefix.length) : topic.topic_name; return `<div class="lesson-row"><span class="lesson-icon">${icons.book}</span><div class="lesson-detail"><strong>${esc(topic.topic_name)}</strong><span>${esc(topic.difficulty_level || `Topic ${String(i + 1).padStart(2, "0")}`)}${topic.prerequisites?.length ? ` · Prerequisite: ${esc(topic.prerequisites.map(p => p.topic_name).join(", "))}` : ""}</span></div><a class="topic-video-link" href="${esc(youtubeSearchUrl(`${c.title} ${videoTopic} tutorial`))}" target="_blank" rel="noopener noreferrer" aria-label="Search YouTube for ${esc(topic.topic_name)}">Watch <span aria-hidden="true">↗</span></a></div>`; }).join("")}</div>` : empty("Topics coming soon", "Your admin can add topics to this course.")}</article></div>${lessonSection}<div class="card section-gap"><div class="card-head"><h3>Practice quizzes</h3></div>${quizzes.length ? `<div class="quiz-cards">${quizzes.map(q => `<button class="quiz-card" data-action="start-quiz" data-id="${esc(q._id)}"><span class="quiz-card-icon">${icons.quiz}</span><span><strong>${esc(q.title)}</strong><small>${esc(q.topic || "General")} · ${q.questions?.length || 0} questions</small></span>${icons.arrow}</button>`).join("")}</div>` : empty("No quiz published yet", "Check back soon for a practice quiz.")}</div>`;
  }
  const recommendIds = new Set((state.recommendations || []).filter(r => r.matched_topics?.length).map(r => r.course?.course_id));
  return `${heading(showExplore ? "Learning library" : "Your learning", showExplore ? "Explore courses" : "My courses", showExplore ? "Choose a subject to add to your personal learning space." : "Your enrolled courses, lessons, and practice in one place.")}
    <div class="course-view-tabs"><button class="${showExplore ? "active" : ""}" data-action="set-course-view" data-view="explore">Explore all <span>${state.courses.length}</span></button><button class="${!showExplore ? "active" : ""}" data-action="set-course-view" data-view="my">My courses <span>${state.enrolledCourseIds.length}</span></button></div>
    ${courses.length ? `<div class="course-grid">${courses.map((c, i) => { const isEnrolled = state.enrolledCourseIds.includes(c.course_id); return `<article class="card course-tile">${courseArtwork(c, i)}${recommendIds.has(c.course_id) ? `<span class="recommend-tag">For you</span>` : ""}<div class="course-body"><div class="course-meta">${esc(c.subject)} · ${esc(c.level)}</div><h3>${esc(c.title)}</h3><p>${esc(c.description || "Explore lessons and practice questions designed to build your skills.")}</p>${courseVideoPanel(c)}<div class="course-foot"><span>${(c.topics || []).length} topics · ${c.estimated_hours || 1} hr</span><div class="course-actions"><button class="subtle-link" data-action="open-course" data-id="${esc(c.course_id)}">Explore ${icons.arrow}</button><button class="btn ${isEnrolled ? "secondary" : "small"}" data-action="${isEnrolled ? "unenroll-course" : "enroll-course"}" data-id="${esc(c.course_id)}">${isEnrolled ? "Enrolled ✓" : "+ Add course"}</button></div></div></div></article>`; }).join("")}</div>` : empty("No courses enrolled yet", "Explore the catalog and add a course to build your learning space.")}
    ${state.recommendationData?.based_on_attempts ? `<div class="card section-gap"><div class="card-head"><h3>Chosen for your learning path</h3><span class="tag">Based on your quiz results</span></div><div class="recommend-list">${(state.recommendations || []).filter(r => r.matched_topics?.length).map(r => `<div class="lesson-row"><span class="lesson-icon">${icons.spark}</span><div class="lesson-detail"><strong>${esc(r.course?.title || "Course")}</strong><span>${esc(r.reason)}</span></div><button class="subtle-link" data-action="open-course" data-id="${esc(r.course?.course_id)}">View ${icons.arrow}</button></div>`).join("") || empty("No topic-specific course match yet", "Keep practicing and Nebula will suggest a course when a topic lines up.")}</div></div>` : ""}`;
}

function planPage() {
  const plan = state.plan;
  const tasks = plan?.tasks || [];
  const totalMinutes = tasks.reduce((total, task) => total + (Number(task.minutes) || 0), 0);
  const focusCourses = new Set(tasks.map(task => task.course_id).filter(Boolean)).size;
  const attempted = (state.progress?.summary?.attempts || 0) > 0;
  const flowSteps = [
    { title: "Check your results", detail: attempted ? "Quiz scores find the topics to revisit." : "Take a diagnostic to find your starting point.", icon: icons.quiz },
    { title: "Build the foundation", detail: "Review prerequisite topics first when needed.", icon: icons.book },
    { title: "Study with focus", detail: "Use each short session for one clear topic.", icon: icons.spark },
    { title: "Practice & improve", detail: "Try a quiz, then your next plan adapts.", icon: icons.progress }
  ];
  return `${heading("A plan that adapts", "Your study plan", "A manageable path built around your goal and your daily time.", `<button class="btn" data-action="generate-plan">${icons.spark} ${state.progress?.summary?.attempts ? "Refresh my plan" : "Build starter plan"}</button>`)}
    <div class="plan-summary"><div><div class="eyebrow">Your learning goal</div><h2>${esc(plan?.goal || state.user.profile?.goal || "Build a steady study habit")}</h2><p>${plan?.daily_minutes || state.user.profile?.daily_minutes || 60} min/day · Your plan responds to your quiz results.</p></div><div class="plan-summary-mark">${icons.plan}</div></div>
    <div class="plan-metrics"><div class="plan-metric"><span>ROADMAP</span><strong>${tasks.length || 0}<small> sessions</small></strong></div><div class="plan-metric"><span>FOCUSED TIME</span><strong>${totalMinutes >= 60 ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60 ? `${totalMinutes % 60}m` : ""}` : `${totalMinutes}m`}</strong></div><div class="plan-metric"><span>COURSES</span><strong>${focusCourses}</strong></div></div>
    <section class="card plan-flow-card"><div class="plan-section-head"><div><div class="eyebrow">Your adaptive learning loop</div><h3>From quiz result to stronger mastery</h3><p>Each step connects your current understanding to what you should practice next.</p></div><span class="plan-live-tag"><i></i> PERSONALIZED</span></div><div class="learning-flow">${flowSteps.map((step, i) => `<article class="flow-step"><span class="flow-step-icon">${step.icon}</span><div class="flow-step-copy"><span class="flow-index">0${i + 1}</span><strong>${step.title}</strong><p>${step.detail}</p></div>${i < flowSteps.length - 1 ? `<span class="flow-arrow" aria-hidden="true">→</span>` : ""}</article>`).join("")}</div></section>
    <section class="card plan-roadmap-card"><div class="plan-section-head"><div><div class="eyebrow">Your next sessions</div><h3>${tasks.length ? "A clear path, one day at a time" : "Your path starts with a quick diagnostic"}</h3><p>${tasks.length ? `${tasks.length} planned sessions · ${totalMinutes} total minutes · Ordered around your focus topics.` : "Take a quiz to get a personalized roadmap, or build a starter plan from your learning goal."}</p></div>${tasks.length ? `<span class="tag">${tasks.length}-day focus</span>` : ""}</div>${tasks.length ? `<div class="roadmap-scroll" aria-label="Study plan roadmap"><div class="roadmap-track">${tasks.map((task, i) => `<article class="roadmap-node ${i === 0 ? "is-today" : ""}"><div class="roadmap-marker"><span>${String(i + 1).padStart(2, "0")}</span></div><div class="roadmap-card"><div class="roadmap-card-top"><span class="roadmap-day">${esc(task.day_label || (i === 0 ? "TODAY" : `DAY ${i + 1}`))}</span><span class="roadmap-time">${Number(task.minutes) || 0} min</span></div><h4>${esc(task.topic)}</h4><p>${esc(task.activity)}${task.course_id ? ` · ${esc(task.course_id)}` : ""}</p>${task.course_id ? `<button class="subtle-link roadmap-open-course" data-action="open-course" data-id="${esc(task.course_id)}">Open course ${icons.arrow}</button>` : ""}<div class="roadmap-kind">${i === 0 ? "START HERE" : "UP NEXT"}</div></div></article>`).join("")}</div></div><div class="roadmap-hint"><span>← Scroll to follow your full plan →</span><span>Plan order may change as your quiz results improve.</span></div>` : `<div class="plan-empty-state">${empty("Let’s make your first plan", "Nebula uses your goal, daily availability and quiz results to create your next steps.")}</div>`}</section>
    <div class="plan-note">${icons.spark}<span>After each quiz, Nebula can refresh this path around the topics that need the most practice.</span></div>`;
}

function progressPage() {
  const summary = state.progress?.summary || {};
  const topics = state.progress?.topics || [];
  const recent = state.progress?.recent_attempts || [];
  const model = state.recommendationData?.model;
  const metrics = model?.metrics;
  const modelCard = model?.available && metrics ? `<article class="card section-gap"><div class="card-head"><h3>Nebula score estimate</h3><span class="tag">Experimental ML</span></div><p class="content-help">Chronological holdout check: ${metrics.test_rows} assessments · score MAE ${metrics.mae_points} points · proficiency-band accuracy ${Math.round(metrics.proficiency_band_accuracy * 100)}% versus ${Math.round(metrics.majority_band_accuracy_baseline * 100)}% for the majority-band baseline. This estimate is experimental; your study plan prioritizes your actual quiz results.</p></article>` : "";
  return `${heading("Your progress", "Look how far you’ve come", "A clear picture of the work you’ve put in and what to focus on next.")}
    <div class="grid stats">${stat("Quiz average", `${summary.average || 0}%`, "Across your latest 100 attempts", "progress")}${stat("Quizzes taken", summary.attempts || 0, "Latest 100 attempts shown", "quiz")}${stat("Lessons completed", summary.completed_lessons || 0, "Your learning adds up", "courses")}${stat("Current streak", `${summary.streak_days || 0} days`, "Come back tomorrow to keep it going", "fire")}</div>
    <div class="grid two-col section-gap"><article class="card"><div class="card-head"><h3>Topic mastery</h3><span class="tag">Based on quiz results</span></div>${topicBars(topics)}</article><article class="card"><div class="card-head"><h3>Score trend</h3><span class="tag">Daily quiz average · 7 days</span></div>${scoreTrendBars(state.progress?.score_trend_attempts || recent)}</article></div>
    ${modelCard}
    <div class="card section-gap"><div class="card-head"><h3>Recent quiz attempts</h3><span class="tag">Latest ${recent.length}</span></div>${recent.length ? `<div class="table-wrap"><table class="admin-table"><thead><tr><th>Quiz</th><th>Topic focus</th><th>Score</th><th>Result</th><th>Time</th><th>Date</th></tr></thead><tbody>${recent.map(a => `<tr><td><strong>${esc(a.quiz_title || "Practice quiz")}</strong></td><td>${esc(a.topic)}</td><td>${a.score}/${a.max_score}</td><td><span class="tag">${a.percentage}%</span></td><td>${a.elapsed_seconds ? `${Math.ceil(a.elapsed_seconds / 60)} min` : "—"}</td><td>${new Date(a.created_at).toLocaleDateString()}</td></tr>`).join("")}</tbody></table></div>` : empty("Your first result is waiting", "Take a practice quiz to start building your progress story.")}</div>`;
}

function profilePage() {
  const p = state.user.profile || {};
  const isStudent = state.user.role === "student";
  const roleLabel = isStudent ? "STUDENT ACCOUNT" : "ADMIN ACCOUNT";
  const editor = isStudent
    ? `<section class="card profile-editor"><div class="card-head"><div><div class="eyebrow">Learning preferences</div><h3>Shape your study plan</h3></div><span class="tag">Personalized</span></div><p class="profile-help">These details help Nebula tailor your recommendations and daily study plan.</p><form id="profile-form"><div class="field"><label for="profile-goal">Learning goal</label><input id="profile-goal" name="goal" maxlength="160" value="${esc(p.goal || "")}" placeholder="e.g. Prepare for board exams" /><small>What would you like to achieve?</small></div><div class="form-grid"><div class="field"><label for="profile-level">Class or learning level</label><input id="profile-level" name="level" maxlength="80" value="${esc(p.level || "")}" placeholder="e.g. Class 12" /><small>We use this to keep suggestions relevant.</small></div><div class="field"><label for="profile-minutes">Study time per day</label><div class="input-suffix"><input id="profile-minutes" name="daily_minutes" type="number" min="10" max="480" step="5" value="${p.daily_minutes || 60}" required /><span>minutes</span></div><small>Choose between 10 and 480 minutes.</small></div></div><div class="profile-actions"><button class="btn secondary" type="reset">Reset changes</button><button class="btn" type="submit">Save profile ${icons.arrow}</button></div></form></section>`
    : `<section class="card profile-editor"><div class="eyebrow">Account access</div><h3>Administrator workspace</h3><p class="profile-help">Your account is used to manage Nebula’s courses and quizzes. Contact the project owner to change account details.</p></section>`;
  return `${heading("My profile", "Your Nebula account", isStudent ? "Keep your learning goals and daily study rhythm up to date." : "View your account details and workspace access.")}
    <div class="profile-layout"><aside class="card profile-identity"><div class="profile-large-avatar">${esc(initials(state.user.name))}</div><span class="profile-role">${roleLabel}</span><h2>${esc(state.user.name)}</h2><p>${esc(state.user.email)}</p><div class="profile-divider"></div><div class="profile-fact"><span>Account type</span><strong>${isStudent ? "Student" : "Administrator"}</strong></div>${isStudent ? `<div class="profile-fact"><span>Daily study goal</span><strong>${p.daily_minutes || 60} minutes</strong></div>` : ""}</aside>${editor}</div>`;
}

function quizPage() {
  const quiz = state.activeQuiz;
  if (!quiz) {
    const attempts = state.progress?.summary?.attempts || 0;
    const average = state.progress?.summary?.average || 0;
    const quizCount = state.quizzes.length;
    const courseById = new Map(state.courses.map(course => [course.course_id, course]));
    const cards = state.quizzes.map((item, index) => {
      const course = courseById.get(item.course_id);
      const count = item.questions?.length || 0;
      const difficulty = (item.difficulty || "mixed").toLowerCase();
      const label = attempts ? `PRACTICE SET ${String(index + 1).padStart(2, "0")}` : index === 0 ? "YOUR BASELINE" : `DIAGNOSTIC ${String(index + 1).padStart(2, "0")}`;
      return `<button class="practice-quiz-card practice-tone-${index % 4}" data-action="start-quiz" data-id="${esc(item._id)}" aria-label="Start ${esc(item.title)} quiz">
        <span class="practice-card-orbit" aria-hidden="true"></span><span class="practice-card-orbit practice-card-orbit-small" aria-hidden="true"></span>
        <span class="practice-card-top"><span class="practice-card-label">${label}</span><span class="practice-card-icon">${icons.quiz}</span></span>
        <span class="practice-card-course">${esc(course?.subject || item.course_id || "NEBULA PRACTICE")}</span>
        <strong class="practice-card-title">${esc(item.title)}</strong>
        <span class="practice-card-topic">${esc(item.topic || course?.subject || "Mixed practice")}</span>
        <span class="practice-card-bottom"><span class="practice-card-facts"><b>${count}</b> questions <i></i> ${Math.max(1, Math.ceil(count * 1.5))} min <i></i> <span class="practice-difficulty difficulty-${esc(difficulty)}">${esc(difficulty)}</span></span><span class="practice-card-start">Start quiz ${icons.arrow}</span></span>
      </button>`;
    }).join("");
    return `${heading("Practice studio", attempts ? "Make your next attempt count." : "Find your starting point.", attempts ? "Pick a focused quiz. Every result sharpens your study plan." : "A quick baseline shows what you already know and where to focus next.")}
      <section class="practice-hero"><div class="practice-hero-copy"><span class="practice-live"><i></i> YOUR LEARNING LOOP</span><h2>${attempts ? "Small sessions. Stronger results." : "Start curious. Grow with a plan."}</h2><p>${attempts ? "Choose one topic to practice today. Nebula will use your result to tune your next steps." : "Take a short diagnostic to unlock a study plan shaped around your strengths and gaps."}</p><div class="practice-hero-pills"><span>${quizCount} quizzes ready</span><span>${attempts ? `${attempts} attempts saved` : "8 questions each"}</span></div></div><div class="practice-hero-visual" aria-hidden="true"><div class="practice-ring practice-ring-one"></div><div class="practice-ring practice-ring-two"></div><div class="practice-orb"></div><span class="practice-star practice-star-one">✦</span><span class="practice-star practice-star-two">✧</span></div>${attempts ? `<div class="practice-average"><span>YOUR QUIZ AVERAGE</span><strong>${average}<small>%</small></strong><i><b style="width:${Math.max(0, Math.min(100, average))}%"></b></i></div>` : ""}</section>
      <div class="practice-section-head"><div><span class="eyebrow">PICK YOUR NEXT SESSION</span><h2>Ready when you are</h2></div><span class="practice-section-count">${quizCount} <small>QUIZZES</small></span></div>
      ${quizCount ? `<div class="practice-quiz-grid">${cards}</div>` : `<div class="card practice-empty">${empty("No quizzes ready just yet", "Your teacher or admin needs to publish a quiz before you can begin.")}</div>`}
      <div class="practice-footnote"><span>${icons.spark}</span><p><strong>Your score has a purpose.</strong> Nebula saves each attempt and uses topic results to update your progress and study plan.</p></div>`;
  }
  if (state.review) {
    const attempt = state.review.attempt;
    const course = state.courses.find(c => c.course_id === state.activeQuiz?.course_id);
    const weakTopics = (attempt.topic_scores || []).map(t => ({ ...t, mastery: t.max_score ? Math.round(100 * t.score / t.max_score) : 0 })).filter(t => t.mastery < 80).sort((a, b) => a.mastery - b.mastery);
    const plannedTasks = (state.plan?.tasks || []).slice(0, 3);
    const nextActions = `<section class="resource-section result-actions-section"><div class="resource-heading"><div><div class="eyebrow">Your personalized next steps</div><h3>Turn this score into progress</h3><p>${course ? `We matched your result to ${esc(course.title)} and built a focused path from your weaker topics.` : "Your result is saved. Explore the course catalog and open your generated study plan."}</p></div></div>${course ? `<article class="card result-course-card"><span class="lesson-icon">${icons.courses}</span><div class="lesson-detail"><strong>${esc(course.title)}</strong><span>${esc(course.subject || "Course")} · ${(course.topics || []).length} topics · Tailored to this quiz's weak topics</span></div><button class="btn small" data-action="open-course" data-id="${esc(course.course_id)}">Open course ${icons.arrow}</button></article>` : `<button class="btn small" data-action="go" data-page="courses">Explore courses ${icons.arrow}</button>`}<div class="result-plan-preview"><div class="card-head"><h4>Study plan · next sessions</h4><button class="subtle-link" data-action="go" data-page="plan">View full plan ${icons.arrow}</button></div>${plannedTasks.length ? `<div class="lesson-stack">${plannedTasks.map((task, i) => `<div class="lesson-row"><span class="lesson-icon ${i === 0 ? "lime" : ""}">${i + 1}</span><div class="lesson-detail"><strong>${esc(task.topic)}</strong><span>${esc(task.activity || "Review this topic, then practice again.")}</span></div><span class="lesson-time">${Number(task.minutes) || 0} min</span></div>`).join("")}</div>` : `<p class="profile-help">Your score is saved. Open the study plan to build or refresh your next sessions.</p>`}</div></section>`;
    const resources = weakTopics.length ? `<section class="resource-section"><div class="resource-heading"><div><div class="eyebrow">A helpful next step</div><h3>Strengthen your weak topics</h3><p>Pick a short lesson, then return to Nebula for another practice quiz.</p></div><span class="tag">${weakTopics.length} topic${weakTopics.length === 1 ? "" : "s"}</span></div><div class="resource-grid">${weakTopics.map((t, i) => {
      const search = new URLSearchParams({ search_query: `${course?.title || state.activeQuiz?.course_id || "study"} ${t.topic} tutorial explained` }).toString();
      const url = `https://www.youtube.com/results?${search}`;
      return `<article class="resource-card spotlight-card" data-spotlight style="--resource-hue:${i % 2 ? "145,255,63" : "67,117,255"}"><div class="resource-art resource-art-${i % 3}"><span class="resource-orbit"></span><span class="resource-play">▶</span><span class="resource-topic">${esc(t.topic)}</span><span class="resource-chip">${t.mastery}% mastery</span></div><div class="resource-copy"><span class="resource-kicker">YOUTUBE SEARCH · ${esc(course?.title || "NEBULA LEARNING")}</span><h4>${esc(t.topic)}</h4><p>Find a clear explanation and review the foundations at your pace.</p><a class="resource-link" href="${esc(url)}" target="_blank" rel="noopener noreferrer">Explore lessons <span aria-hidden="true">↗</span></a></div></article>`;
    }).join("")}</div><p class="resource-footnote">Opens YouTube search results. Video order and availability are set by YouTube.</p></section>` : `<section class="resource-section resource-all-good"><div class="resource-heading"><div><div class="eyebrow">Next level unlocked</div><h3>No weak topics in this attempt</h3><p>Your topic scores are at 80% or above. Keep your momentum with the next challenge.</p></div><span class="tag">Strong work</span></div></section>`;
    return `${heading("Quiz complete", "Nice work showing up.", `You got ${attempt.score} out of ${attempt.max_score} correct.`)}<div class="card review-card"><div class="review-score">${attempt.percentage}<span>%</span></div><p class="review-message">${attempt.percentage >= 80 ? "Strong understanding. Nebula has updated your plan with the next challenge." : attempt.percentage >= 50 ? "Good starting point. Your plan now includes focused practice for this topic." : "This gives us a useful baseline. Your plan will start with the foundations."}</p><p class="review-message">${attempt.elapsed_seconds ? `Completed in ${Math.ceil(attempt.elapsed_seconds / 60)} min · ` : ""}Result saved to your personal progress.</p>${nextActions}${resources}${state.review.review.map((r, i) => `<div class="review-item"><strong>${i + 1}. ${esc(r.prompt)}</strong><div class="${r.correct ? "review-correct" : "review-wrong"}">${r.correct ? "Correct" : `Your answer: ${esc(r.options[r.selected_index] || "Not answered")}. Correct: ${esc(r.options[r.answer_index])}.`} ${r.explanation ? esc(r.explanation) : ""}</div></div>`).join("")}<div class="modal-actions"><button class="btn secondary" data-action="go" data-page="progress">See my progress</button><button class="btn" data-action="go" data-page="plan">View updated study plan</button><button class="btn secondary" data-action="reset-quiz">Back to quizzes</button></div></div>`;
  }
  const q = quiz.questions[state.questionIndex || 0];
  const idx = state.questionIndex || 0;
  if (!q) return empty("This quiz has no questions", "Ask an admin to add practice questions.");
  return `${heading("Practice quiz", esc(quiz.title), `${esc(quiz.topic || "General")} · ${idx + 1} of ${quiz.questions.length}`, `<button class="btn secondary" data-action="reset-quiz">Exit quiz</button>`)}<div class="card quiz-panel"><div class="quiz-progress"><span>Question ${idx + 1} of ${quiz.questions.length}</span><span>${Math.round((idx + 1) / quiz.questions.length * 100)}% complete · answer required</span></div><div class="progress-track"><div class="progress-fill" style="width:${(idx + 1) / quiz.questions.length * 100}%"></div></div><div class="quiz-question">${esc(q.prompt)}</div><div class="quiz-options">${q.options.map((o, i) => `<button class="quiz-option ${state.selected[idx] === i ? "selected" : ""}" data-action="answer" data-index="${i}"><span class="option-key">${String.fromCharCode(65 + i)}</span>${esc(o)}</button>`).join("")}</div><div class="quiz-footer"><span>Your answers are saved with this attempt to track topic progress.</span><button class="btn" data-action="next-question">${idx === quiz.questions.length - 1 ? "Finish diagnostic" : "Next question"} ${icons.arrow}</button></div></div>`;
}

function adminOverview() {
  const summary = state.adminSummary || {};
  return `${heading("Admin workspace", `Good to have you here, ${esc(state.user.name.split(" ")[0])}.`, "Build a useful learning library for every student.", `<button class="btn" data-action="add-course">+ Add course</button>`)}
    <div class="hero-card admin-hero"><div class="hero-copy"><div class="eyebrow">Your impact starts with great content</div><h2>Make the next learning step feel clear.</h2><p>Add courses and practice quizzes to give students a thoughtful place to begin.</p><button class="btn" data-action="go" data-page="courses">Manage courses ${icons.arrow}</button></div><div class="hero-art"><div class="hero-orbit"></div><div class="hero-planet"></div><div class="hero-dot"></div><div class="hero-star"></div></div></div>
    <div class="grid stats">${stat("Students", summary.students || 0, "Learners on Nebula", "profile")}${stat("Courses", summary.courses || 0, "In your learning library", "courses")}${stat("Published quizzes", summary.quizzes || 0, "Ready for student practice", "quiz")}${stat("Quiz attempts", summary.attempts || 0, "Learning in progress", "progress")}</div>
    <div class="grid two-col"><div class="card"><div class="card-head"><h3>Quick actions</h3></div><div class="admin-actions"><button class="admin-action" data-action="add-course"><span class="lesson-icon">${icons.courses}</span><span><strong>Add a course</strong><small>Set up a new subject and its topics</small></span>${icons.arrow}</button><button class="admin-action" data-action="add-quiz"><span class="lesson-icon lime">${icons.quiz}</span><span><strong>Create a quiz</strong><small>Give learners a way to check progress</small></span>${icons.arrow}</button></div></div><div class="card"><div class="card-head"><h3>Content overview</h3><span class="tag">Nebula library</span></div><div class="content-meter"><div class="content-meter-item"><span>Courses</span><strong>${summary.courses || 0}</strong></div><div class="content-meter-item"><span>Quizzes</span><strong>${summary.quizzes || 0}</strong></div><div class="content-meter-item"><span>Student attempts</span><strong>${summary.attempts || 0}</strong></div></div><p class="content-help">Tip: Add clear topic names so Nebula can connect quiz results to helpful recommendations.</p></div></div>`;
}
function adminCourses() {
  const rows = state.courses;
  return `${heading("Content library", "Manage courses", "Keep lessons organized into subjects and topics.", `<button class="btn" data-action="add-course">+ Add course</button>`)}<div class="card"><div class="card-head"><h3>Your courses</h3><span class="tag">${rows.length} total</span></div>${rows.length ? `<div class="table-wrap"><table class="admin-table"><thead><tr><th>Course</th><th>Subject</th><th>Level</th><th>Topics</th><th>Actions</th></tr></thead><tbody>${rows.map(c => `<tr><td><strong>${esc(c.title)}</strong><small>${esc(c.course_id)}</small></td><td>${esc(c.subject)}</td><td>${esc(c.level)}</td><td>${(c.topics || []).length}</td><td><div class="table-actions"><button data-action="edit-course" data-id="${esc(c.course_id)}">Edit</button><button class="danger-text" data-action="delete-course" data-id="${esc(c.course_id)}">Delete</button></div></td></tr>`).join("")}</tbody></table></div>` : empty("Your first course starts here", "Add a subject, outline its topics, and give students a place to begin.")}</div>`;
}
function adminQuizzes() {
  const rows = state.quizzes;
  return `${heading("Content library", "Manage quizzes", "Create practice that makes understanding visible.", `<button class="btn" data-action="add-quiz">+ Create quiz</button>`)}<div class="card"><div class="card-head"><h3>Quiz library</h3><span class="tag">${rows.length} total</span></div>${rows.length ? `<div class="table-wrap"><table class="admin-table"><thead><tr><th>Quiz</th><th>Course</th><th>Topic</th><th>Questions</th><th>Status</th><th>Actions</th></tr></thead><tbody>${rows.map(q => `<tr><td><strong>${esc(q.title)}</strong></td><td>${esc(q.course_id || "—")}</td><td>${esc(q.topic)}</td><td>${q.questions?.length || 0}</td><td><span class="tag ${q.published ? "" : "tag-muted"}">${q.published ? "Published" : "Draft"}</span></td><td><div class="table-actions"><button data-action="edit-quiz" data-id="${esc(q._id)}">Edit</button><button class="danger-text" data-action="delete-quiz" data-id="${esc(q._id)}">Delete</button></div></td></tr>`).join("")}</tbody></table></div>` : empty("No quizzes yet", "Create a short quiz to help students see what they know.")}</div>`;
}
function adminLessons() {
  const query = (state.lessonSearch || "").toLowerCase();
  const rows = state.lessons.filter(l => !query || `${l.title} ${l.course_id} ${l.topic_name}`.toLowerCase().includes(query));
  return `${heading("Content library", "Manage lessons", "Write short, structured lessons and publish them course by course.", `<button class="btn" data-action="add-lesson">+ Add lesson</button>`)}<form id="lesson-search-form" class="student-search"><input name="q" value="${esc(state.lessonSearch || "")}" placeholder="Search lesson, course or topic"/><button class="btn secondary">Search</button><span class="tag">${state.lessons.length} total lessons</span></form><div class="card"><div class="card-head"><h3>Lesson library</h3><span class="tag">${rows.length} shown</span></div>${rows.length ? `<div class="table-wrap"><table class="admin-table"><thead><tr><th>Lesson</th><th>Course</th><th>Topic</th><th>Status</th><th>Actions</th></tr></thead><tbody>${rows.map(l => `<tr><td><strong>${esc(l.title)}</strong><small>${esc(l.summary || "No summary")}</small></td><td>${esc(l.course_id)}</td><td>${esc(l.topic_name || l.topic_id)}</td><td><span class="tag ${l.published ? "" : "tag-muted"}">${l.published ? "Published" : "Draft"}</span></td><td><div class="table-actions"><button data-action="edit-lesson" data-id="${esc(l._id)}">Edit</button><button class="danger-text" data-action="delete-lesson" data-id="${esc(l._id)}">Delete</button></div></td></tr>`).join("")}</tbody></table></div>` : empty("No lessons found", state.lessonSearch ? "Try another search." : "Create a lesson and attach it to a course topic.")}</div>`;
}
function adminStudents() {
  const rows = state.students;
  return `${heading("Learner accounts", "Manage students", "Review account status and high-level activity. Quiz answers and private response details are not shown.")}<form id="student-search-form" class="student-search"><input name="q" value="${esc(state.studentSearch || "")}" placeholder="Search name or email"/><button class="btn secondary">Search</button><span class="tag">Up to 200 accounts</span></form><div class="card"><div class="card-head"><h3>Student accounts</h3><span class="tag">${rows.length} shown</span></div>${rows.length ? `<div class="table-wrap"><table class="admin-table"><thead><tr><th>Student</th><th>Learning goal</th><th>Activity</th><th>Status</th><th>Actions</th></tr></thead><tbody>${rows.map(s => `<tr><td><strong>${esc(s.name)}</strong><small>${esc(s.email)}</small></td><td>${esc(s.profile?.goal || "—")}<small>${esc(s.profile?.level || "Level not set")} · ${s.profile?.daily_minutes || 60} min/day</small></td><td>${s.attempt_count} quiz attempts<small>Last activity: ${s.last_activity ? new Date(s.last_activity).toLocaleDateString() : "No quiz yet"}</small></td><td><span class="tag ${s.status === "active" ? "" : "tag-muted"}">${esc(s.status || "active")}</span></td><td><button class="${s.status === "active" ? "danger-text" : "subtle-link"}" data-action="student-status" data-id="${esc(s.id)}" data-status="${s.status === "active" ? "suspended" : "active"}">${s.status === "active" ? "Suspend" : "Reactivate"}</button></td></tr>`).join("")}</tbody></table></div>` : empty("No students found", state.studentSearch ? "Try a different search." : "Student accounts will appear here after signup.")}</div>`;
}

function paintPage() {
  if (!state.user) { renderAuth(); return; }
  let title = ({ overview: "Overview", courses: state.user.role === "admin" ? "Courses" : "My courses", lessons: "Lessons", students: "Students", plan: "Study plan", progress: "Progress", profile: "My profile", quizzes: "Quizzes", quiz: "Practice quiz" })[state.page] || "Overview";
  let content = state.user.role === "admin"
    ? ({ overview: adminOverview, courses: adminCourses, quizzes: adminQuizzes, lessons: adminLessons, students: adminStudents, profile: profilePage }[state.page] || adminOverview)()
    : ({ overview: studentOverview, courses: coursesPage, plan: planPage, progress: progressPage, profile: profilePage, quiz: quizPage }[state.page] || studentOverview)();
  app.innerHTML = shell(content, title);
  app.querySelectorAll("[data-spotlight]").forEach(card => card.addEventListener("pointermove", event => {
    const rect = card.getBoundingClientRect();
    card.style.setProperty("--spot-x", `${event.clientX - rect.left}px`);
    card.style.setProperty("--spot-y", `${event.clientY - rect.top}px`);
  }));
}

async function render({ fast = false } = {}) {
  if (!state.user) { renderAuth(); return; }
  if (fast) {
    // Paint the destination from in-memory state immediately. Refresh it after the
    // network work completes, without making navigation wait for the database.
    paintPage();
    void render();
    return;
  }
  const page = state.page;
  const role = state.user.role;
  try {
    if (role === "admin") {
      const jobs = [];
      if (page === "overview") jobs.push(api("/admin/overview").then(r => { state.adminSummary = r; }));
      if (page === "courses") jobs.push(api("/courses").then(r => { state.courses = r.courses; }));
      if (page === "quizzes") jobs.push(api("/quizzes").then(r => { state.quizzes = r.quizzes; }));
      if (page === "lessons") jobs.push(Promise.all([api("/admin/lessons"), api("/courses")]).then(([l, c]) => { state.lessons = l.lessons; state.courses = c.courses; }));
      if (page === "students") jobs.push(api(`/admin/students${state.studentSearch ? `?q=${encodeURIComponent(state.studentSearch)}` : ""}`).then(r => { state.students = r.students; }));
      const results = await Promise.allSettled(jobs);
      const failed = results.find(result => result.status === "rejected");
      if (failed) throw failed.reason;
    } else {
      const jobs = [];
      if (!state.enrollmentsLoaded) jobs.push(api("/enrollments").then(r => {
        state.enrolledCourseIds = r.course_ids;
        state.courseView = state.enrolledCourseIds.length ? "my" : "explore";
        state.enrollmentsLoaded = true;
      }).catch(() => {
        state.enrolledCourseIds = []; state.courseView = "explore"; state.enrollmentsLoaded = true;
        toast("Course enrollment is unavailable right now. You can still take a quiz.", true);
      }));
      if (["overview", "progress", "plan"].includes(page)) jobs.push(api("/progress").then(r => { state.progress = r; }));
      if (["overview", "courses"].includes(page) || (page === "plan" && !state.courses.length)) jobs.push(api("/courses").then(r => { state.courses = r.courses; }));
      if (["overview", "courses", "progress"].includes(page)) jobs.push(api("/recommendations").then(r => { state.recommendationData = r; state.recommendations = r.recommendations; }));
      if (["overview", "courses"].includes(page) || (page === "quiz" && !state.quizzes.length)) jobs.push(api("/quizzes").then(r => { state.quizzes = r.quizzes; }));
      if (page === "plan") jobs.push(api("/study-plan").then(r => { state.plan = r.plan; }));
      const results = await Promise.allSettled(jobs);
      const failed = results.find(result => result.status === "rejected");
      if (failed) throw failed.reason;
    }
  } catch (e) { toast(e.message, true); }
  // Ignore stale responses if the learner has navigated elsewhere meanwhile.
  if (state.page === page && state.user?.role === role) paintPage();
}

async function logout(show = true) {
  state.user = null; state.token = null; state.enrollmentsLoaded = false; state.enrolledCourseIds = []; localStorage.removeItem("nebula_token"); state.page = "overview"; state.activeQuiz = null; state.review = null;
  if (show) toast("You’re signed out. See you again soon."); renderAuth();
}
async function boot() {
  if (state.token) {
    try { state.user = (await api("/auth/me")).user; state.page = "overview"; await render(); return; }
    catch { state.user = null; state.token = null; localStorage.removeItem("nebula_token"); }
  }
  renderAuth();
}

document.addEventListener("submit", async event => {
  event.preventDefault();
  if (event.target.id === "auth-form") {
    const form = Object.fromEntries(new FormData(event.target));
    const signup = state.authMode === "signup";
    const payload = signup ? { name: form.name, email: form.email, password: form.password, role: form.role, admin_signup_key: form.admin_signup_key, profile: { goal: form.goal, level: form.level, daily_minutes: Number(form.daily_minutes || 60) } } : { email: form.email, password: form.password };
    const button = event.target.querySelector("button[type=submit]"); button.disabled = true; button.innerHTML = '<span class="spinner"></span> One moment…';
    try {
      const result = await api(`/auth/${signup ? "register" : "login"}`, { method: "POST", body: JSON.stringify(payload) });
      state.token = result.access_token; state.user = result.user; state.enrollmentsLoaded = false; state.page = "overview"; localStorage.setItem("nebula_token", state.token); toast(signup ? "Your Nebula account is ready." : `Welcome back, ${state.user.name.split(" ")[0]}.`); await render();
    } catch (e) { toast(e.message, true); button.disabled = false; button.innerHTML = `${signup ? "Create my account" : "Sign in to Nebula"} ${icons.arrow}`; }
  }
  if (event.target.id === "profile-form") {
    const form = Object.fromEntries(new FormData(event.target));
    try { const result = await api("/auth/profile", { method: "PATCH", body: JSON.stringify({ profile: { goal: form.goal, level: form.level, daily_minutes: Number(form.daily_minutes) } }) }); state.user = result.user; try { state.plan = (await api("/study-plan/generate", { method: "POST", body: "{}" })).plan; } catch { /* The profile save remains successful if plan refresh is temporarily unavailable. */ } toast("Your learning profile is updated."); await render(); }
    catch (e) { toast(e.message, true); }
  }
  if (event.target.id === "course-form") {
    const form = Object.fromEntries(new FormData(event.target)); const courseId = form.course_id.toUpperCase();
    const payload = { course_id: courseId, title: form.title, subject: form.subject, level: form.level, description: form.description, estimated_hours: Number(form.estimated_hours), topics: form.topics.split(",").map(x => x.trim()).filter(Boolean) };
    try { await api(form.editing ? `/courses/${encodeURIComponent(courseId)}` : "/courses", { method: form.editing ? "PUT" : "POST", body: JSON.stringify(payload) }); closeModal(); toast(form.editing ? "Course updated." : "Course created."); await render(); }
    catch (e) { toast(e.message, true); }
  }
  if (event.target.id === "quiz-form") {
    const form = Object.fromEntries(new FormData(event.target)); const quizId = form.quiz_id;
    const editors = [...event.target.querySelectorAll("[data-question-editor]")];
    const questions = editors.map(editor => {
      const rawOptions = [0, 1, 2, 3].map(i => editor.querySelector(`[name="option_${i}"]`).value.trim());
      const correctLetter = Number(editor.querySelector('[name="answer_index"]').value);
      const options = rawOptions.filter(Boolean);
      const answer_index = rawOptions[correctLetter] ? rawOptions.slice(0, correctLetter + 1).filter(Boolean).length - 1 : -1;
      return { prompt: editor.querySelector('[name="prompt"]').value.trim(), topic: editor.querySelector('[name="question_topic"]').value.trim(), options, answer_index, explanation: editor.querySelector('[name="explanation"]').value.trim() };
    });
    const payload = { title: form.title, course_id: form.course_id, topic: form.topic, difficulty: form.difficulty, published: form.published === "on", questions };
    try { await api(quizId ? `/quizzes/${quizId}` : "/quizzes", { method: quizId ? "PUT" : "POST", body: JSON.stringify(payload) }); closeModal(); toast(quizId ? "Quiz updated." : "Quiz created."); await render(); }
    catch (e) { toast(e.message, true); }
  }
  if (event.target.id === "lesson-form") {
    const form = Object.fromEntries(new FormData(event.target));
    const payload = { course_id: form.course_id, topic_id: form.topic_id, title: form.title, summary: form.summary, content: form.content, video_url: form.video_url, position: Number(form.position || 0), published: form.published === "on" };
    const lessonId = form.lesson_id;
    try { await api(lessonId ? `/admin/lessons/${lessonId}` : "/admin/lessons", { method: lessonId ? "PUT" : "POST", body: JSON.stringify(payload) }); closeModal(); toast(lessonId ? "Lesson updated." : "Lesson created."); await render(); }
    catch (e) { toast(e.message, true); }
  }
  if (event.target.id === "student-search-form") {
    state.studentSearch = new FormData(event.target).get("q")?.toString().trim() || "";
    await render();
  }
  if (event.target.id === "lesson-search-form") {
    state.lessonSearch = new FormData(event.target).get("q")?.toString().trim() || "";
    await render();
  }
});

function closeModal() { document.querySelector("#modal-root")?.remove(); state.editingQuiz = null; state.quizDraftQuestions = []; }
function showCourseModal(course = null) {
  const c = course || {};
  document.body.insertAdjacentHTML("beforeend", `<div id="modal-root" class="modal-backdrop"><div class="modal"><div class="modal-heading"><div><div class="eyebrow">Course builder</div><h2>${course ? "Edit course" : "Create a course"}</h2></div><button class="icon-button" data-action="close-modal">${icons.close}</button></div><form id="course-form"><input type="hidden" name="editing" value="${course ? "1" : ""}"/><div class="form-grid"><div class="field"><label>Course ID</label><input name="course_id" value="${esc(c.course_id || "")}" placeholder="SCI-101" ${course ? "readonly" : ""} required/></div><div class="field"><label>Subject</label><input name="subject" value="${esc(c.subject || "")}" placeholder="Biology" required/></div></div><div class="field"><label>Course title</label><input name="title" value="${esc(c.title || "")}" placeholder="Foundations of Biology" required/></div><div class="field"><label>Description</label><textarea name="description" placeholder="What will students learn?">${esc(c.description || "")}</textarea></div><div class="form-grid"><div class="field"><label>Level</label><input name="level" value="${esc(c.level || "Beginner")}" placeholder="Class 12"/></div><div class="field"><label>Estimated hours</label><input name="estimated_hours" type="number" min="1" value="${c.estimated_hours || 3}"/></div></div><div class="field"><label>Topics (comma separated)</label><input name="topics" value="${esc((c.topics || []).join(", "))}" placeholder="Cell structure, Genetics, Ecology"/></div><div class="modal-actions"><button type="button" class="btn secondary" data-action="close-modal">Cancel</button><button class="btn">${course ? "Save changes" : "Create course"}</button></div></form></div></div>`);
}
async function showLessonModal(lesson = null) {
  try {
    if (!state.courses.length) state.courses = (await api("/courses")).courses;
    const selectedCourse = lesson?.course_id || state.courses[0]?.course_id;
    state.lessonTopicOptions = selectedCourse ? (await api(`/courses/${encodeURIComponent(selectedCourse)}/topics`)).topics : [];
    const courseOptions = state.courses.map(c => `<option value="${esc(c.course_id)}" ${selectedCourse === c.course_id ? "selected" : ""}>${esc(c.title)}</option>`).join("");
    const topics = state.lessonTopicOptions.map(t => `<option value="${esc(t.topic_id)}" ${lesson?.topic_id === t.topic_id ? "selected" : ""}>${esc(t.topic_name)}</option>`).join("");
    document.body.insertAdjacentHTML("beforeend", `<div id="modal-root" class="modal-backdrop"><div class="modal lesson-modal"><div class="modal-heading"><div><div class="eyebrow">Lesson editor</div><h2>${lesson ? "Edit lesson" : "Create a lesson"}</h2></div><button class="icon-button" data-action="close-modal">${icons.close}</button></div><form id="lesson-form"><input type="hidden" name="lesson_id" value="${esc(lesson?._id || "")}"/><div class="form-grid"><div class="field"><label>Course</label><select name="course_id" required>${courseOptions}</select></div><div class="field"><label>Topic</label><select name="topic_id" required>${topics}</select></div></div><div class="field"><label>Lesson title</label><input name="title" maxlength="160" value="${esc(lesson?.title || "")}" placeholder="e.g. How binary search works" required/></div><div class="field"><label>Short summary</label><input name="summary" maxlength="500" value="${esc(lesson?.summary || "")}" placeholder="A one sentence preview for students"/></div><div class="field"><label>Lesson content</label><textarea name="content" maxlength="20000" rows="9" placeholder="Explain the concept in clear steps…">${esc(lesson?.content || "")}</textarea></div><div class="form-grid"><div class="field"><label>Optional video URL</label><input name="video_url" type="url" value="${esc(lesson?.video_url || "")}" placeholder="https://…"/></div><div class="field"><label>Order within course</label><input name="position" type="number" min="0" max="10000" value="${lesson?.position || 0}"/></div></div><div class="field"><label>Visibility</label><select name="published"><option value="on" ${lesson?.published ? "selected" : ""}>Published for students</option><option value="off" ${!lesson?.published ? "selected" : ""}>Save as draft</option></select></div><div class="modal-actions"><button type="button" class="btn secondary" data-action="close-modal">Cancel</button><button class="btn">${lesson ? "Save lesson" : "Create lesson"}</button></div></form></div></div>`);
  } catch (e) { toast(e.message, true); }
}
function openLesson(lesson) {
  state.lessonViewing = lesson;
  document.body.insertAdjacentHTML("beforeend", `<div id="modal-root" class="modal-backdrop"><article class="modal lesson-reader"><div class="modal-heading"><div><div class="eyebrow">${esc(lesson.topic_name || "Course lesson")}</div><h2>${esc(lesson.title)}</h2><p>${esc(lesson.summary || "")}</p></div><button class="icon-button" data-action="close-modal">${icons.close}</button></div><div class="lesson-reader-content">${esc(lesson.content || "Lesson content is coming soon.")}</div>${lesson.video_url ? `<a class="btn secondary lesson-video" href="${esc(lesson.video_url)}" target="_blank" rel="noopener noreferrer">Watch lesson video ↗</a>` : ""}<div class="modal-actions"><button class="btn secondary" data-action="close-modal">Close</button>${lesson.completed ? `<span class="tag">Completed ✓</span>` : `<button class="btn" data-action="complete-lesson" data-id="${esc(lesson._id)}">Mark complete</button>`}</div></article></div>`);
}
function quizQuestionEditor(question = {}, index = 0, total = 1) {
  const options = question.options || [];
  const correctLetter = options[question.answer_index] ? question.answer_index : 0;
  const choiceFields = ["A", "B", "C", "D"].map((letter, i) => `<div class="field"><label>Choice ${letter}${i > 1 ? " (optional)" : ""}</label><input name="option_${i}" value="${esc(options[i] || "")}" ${i < 2 ? "required" : ""}/></div>`).join("");
  const correctOptions = ["A", "B", "C", "D"].map((letter, i) => `<option value="${i}" ${correctLetter === i ? "selected" : ""}>${letter}</option>`).join("");
  return `<section class="quiz-question-editor" data-question-editor><div class="card-head"><h3>Question ${index + 1}</h3>${total > 1 ? `<button type="button" class="table-actions" data-action="remove-quiz-question" data-index="${index}">Remove</button>` : ""}</div><div class="form-grid"><div class="field"><label>Question topic (optional)</label><input name="question_topic" value="${esc(question.topic || "")}" placeholder="Match a topic from the course catalog"/></div><div class="field"><label>Question</label><textarea name="prompt" required placeholder="Write a clear question…">${esc(question.prompt || "")}</textarea></div></div><div class="form-grid">${choiceFields}</div><div class="form-grid"><div class="field"><label>Correct choice</label><select name="answer_index">${correctOptions}</select></div><div class="field"><label>Answer explanation (optional)</label><input name="explanation" value="${esc(question.explanation || "")}" placeholder="Explain why this answer is correct"/></div></div></section>`;
}
function renderQuizQuestionList() {
  const count = state.quizDraftQuestions.length;
  return `<div class="quiz-question-list-head"><div><strong>Quiz questions</strong><small>Edit each question and its answer below.</small></div><span>${count} ${count === 1 ? "question" : "questions"}</span></div>${state.quizDraftQuestions.map((question, i) => quizQuestionEditor(question, i, count)).join("")}`;
}
function showQuizModal(quiz = null) {
  state.editingQuiz = quiz;
  state.quizDraftQuestions = quiz?.questions?.length ? quiz.questions.map(q => structuredClone(q)) : [{}];
  const q = quiz || {};
  document.body.insertAdjacentHTML("beforeend", `<div id="modal-root" class="modal-backdrop"><div class="modal quiz-modal"><div class="modal-heading"><div><div class="eyebrow">Quiz builder</div><h2>${quiz ? "Edit quiz" : "Create a quiz"}</h2></div><button type="button" class="btn secondary quiz-builder-back" data-action="close-modal">← Back to quizzes</button></div><form id="quiz-form"><input type="hidden" name="quiz_id" value="${esc(q._id || "")}"/><div class="form-grid"><div class="field"><label>Quiz title</label><input name="title" value="${esc(q.title || "")}" placeholder="Fractions check-in" required/></div><div class="field"><label>Course ID (optional)</label><input name="course_id" value="${esc(q.course_id || "")}" placeholder="MATH-101"/></div></div><div class="form-grid"><div class="field"><label>Topic</label><input name="topic" value="${esc(q.topic || "")}" placeholder="Fractions" required/></div><div class="field"><label>Difficulty</label><select name="difficulty"><option ${q.difficulty === "easy" ? "selected" : ""}>easy</option><option ${q.difficulty === "medium" || !q.difficulty ? "selected" : ""}>medium</option><option ${q.difficulty === "hard" ? "selected" : ""}>hard</option></select></div></div><div id="quiz-question-list">${renderQuizQuestionList()}</div><button type="button" class="btn secondary" data-action="add-quiz-question">+ Add question</button><div class="form-grid"><div class="field"><label>Publish</label><select name="published"><option value="on" ${q.published !== false ? "selected" : ""}>Publish for students</option><option value="off" ${q.published === false ? "selected" : ""}>Save as draft</option></select></div></div><div class="modal-actions"><button type="button" class="btn secondary" data-action="close-modal">Cancel</button><button class="btn">${quiz ? "Save changes" : "Create quiz"}</button></div></form></div></div>`);
}
function captureQuizQuestionDrafts() {
  return [...document.querySelectorAll("#quiz-question-list [data-question-editor]")].map(editor => {
    const rawOptions = [0, 1, 2, 3].map(i => editor.querySelector(`[name="option_${i}"]`).value.trim());
    const correct = Number(editor.querySelector('[name="answer_index"]').value);
    const options = rawOptions.filter(Boolean);
    return { prompt: editor.querySelector('[name="prompt"]').value, topic: editor.querySelector('[name="question_topic"]').value, options, answer_index: rawOptions[correct] ? rawOptions.slice(0, correct + 1).filter(Boolean).length - 1 : -1, explanation: editor.querySelector('[name="explanation"]').value };
  });
}

document.addEventListener("change", async event => {
  if (event.target.name !== "course_id" || !event.target.closest("#lesson-form")) return;
  const select = document.querySelector('#lesson-form [name="topic_id"]');
  if (!select) return;
  select.innerHTML = '<option value="">Loading topics…</option>';
  try {
    state.lessonTopicOptions = (await api(`/courses/${encodeURIComponent(event.target.value)}/topics`)).topics;
    select.innerHTML = state.lessonTopicOptions.map(t => `<option value="${esc(t.topic_id)}">${esc(t.topic_name)}</option>`).join("") || '<option value="">No topics in this course</option>';
  } catch (e) { select.innerHTML = '<option value="">Could not load topics</option>'; toast(e.message, true); }
});

document.addEventListener("click", async event => {
  const button = event.target.closest("[data-action]"); if (!button) return;
  const action = button.dataset.action;
  if (action === "toggle-password") {
    const input = document.getElementById(button.dataset.target);
    if (!input) return;
    const visible = input.type === "password";
    input.type = visible ? "text" : "password";
    button.setAttribute("aria-label", `${visible ? "Hide" : "Show"} ${input.name === "admin_signup_key" ? "setup key" : "password"}`);
    button.setAttribute("aria-pressed", String(visible));
    button.innerHTML = visible ? icons.eyeOff : icons.eye;
    return;
  }
  if (action === "auth-mode") { state.authMode = button.dataset.mode; renderAuth(); }
  if (action === "logout") logout();
  if (action === "menu") document.querySelector("#sidebar")?.classList.toggle("open");
  if (action === "notifications") toast("You’re all caught up.");
  if (action === "go") { state.page = button.dataset.page; state.focusCourse = null; if (state.page === "quiz") { state.activeQuiz = null; state.review = null; } await render({ fast: true }); document.querySelector("#sidebar")?.classList.remove("open"); }
  if (action === "open-course") { state.focusCourse = state.courses.find(c => c.course_id === button.dataset.id); if (!state.focusCourse) { try { state.courses = (await api("/courses")).courses; state.focusCourse = state.courses.find(c => c.course_id === button.dataset.id); } catch (e) { toast(e.message, true); return; } } if (!state.focusCourse) { toast("This course is no longer available.", true); return; } state.page = "courses"; state.focusTopics = (await api(`/courses/${encodeURIComponent(button.dataset.id)}/topics`)).topics; state.focusLessons = (await api(`/courses/${encodeURIComponent(button.dataset.id)}/lessons`)).lessons; if (!state.quizzes.length) state.quizzes = (await api("/quizzes")).quizzes; await render(); }
  if (action === "set-course-view") { state.courseView = button.dataset.view; state.focusCourse = null; await render(); }
  if (action === "enroll-course") { try { await api(`/enrollments/${encodeURIComponent(button.dataset.id)}`, { method: "POST", body: "{}" }); if (!state.enrolledCourseIds.includes(button.dataset.id)) state.enrolledCourseIds.push(button.dataset.id); state.courseView = "my"; try { state.plan = (await api("/study-plan/generate", { method: "POST", body: "{}" })).plan; } catch { /* Enrollment remains successful if plan generation is temporarily unavailable. */ } toast("Course added to My courses."); await render(); } catch (e) { toast(e.message, true); } }
  if (action === "unenroll-course") { try { await api(`/enrollments/${encodeURIComponent(button.dataset.id)}`, { method: "DELETE" }); state.enrolledCourseIds = state.enrolledCourseIds.filter(id => id !== button.dataset.id); if (!state.enrolledCourseIds.length) state.courseView = "explore"; try { state.plan = (await api("/study-plan/generate", { method: "POST", body: "{}" })).plan; } catch { /* Enrollment remains successful if plan generation is temporarily unavailable. */ } toast("Course removed from My courses."); await render(); } catch (e) { toast(e.message, true); } }
  if (action === "back-courses") { state.focusCourse = null; state.focusTopics = []; await render(); }
  if (action === "generate-plan") { button.disabled = true; try { const result = await api("/study-plan/generate", { method: "POST", body: "{}" }); state.plan = result.plan; toast("Your updated study plan is ready."); await render(); } catch (e) { toast(e.message, true); button.disabled = false; } }
  if (action === "start-quiz") { try { const result = await api(`/quizzes/${button.dataset.id}`); state.activeQuiz = result.quiz; state.selected = []; state.review = null; state.questionIndex = 0; state.quizStartedAt = Date.now(); state.page = "quiz"; await render(); } catch (e) { toast(e.message, true); } }
  if (action === "answer") { state.selected[state.questionIndex || 0] = Number(button.dataset.index); await render(); }
  if (action === "next-question") {
    const index = state.questionIndex || 0;
    if (state.selected[index] == null) { toast("Choose an answer to continue.", true); return; }
    if (index < state.activeQuiz.questions.length - 1) { state.questionIndex = index + 1; await render(); }
    else {
      try {
        const result = await api(`/quizzes/${state.activeQuiz._id}/submit`, { method: "POST", body: JSON.stringify({ answers: state.selected, elapsed_seconds: Math.round((Date.now() - state.quizStartedAt) / 1000) }) });
        state.review = result;
        state.progress = await api("/progress");
        try { state.courses = (await api("/courses")).courses; } catch { /* The score remains visible if the catalog is briefly unavailable. */ }
        try { state.plan = (await api("/study-plan/generate", { method: "POST", body: "{}" })).plan; }
        catch { toast("Result saved. Open Study plan to try generating your plan.", true); }
        await render();
      } catch (e) { toast(e.message, true); }
    }
  }
  if (action === "reset-quiz") { state.activeQuiz = null; state.review = null; state.selected = []; state.quizStartedAt = null; state.page = "quiz"; await render(); }
  if (action === "add-course") showCourseModal();
  if (action === "edit-course") showCourseModal(state.courses.find(c => c.course_id === button.dataset.id));
  if (action === "add-lesson") showLessonModal();
  if (action === "edit-lesson") showLessonModal(state.lessons.find(l => l._id === button.dataset.id));
  if (action === "open-lesson") { const lesson = state.focusLessons.find(l => l._id === button.dataset.id); if (lesson) openLesson(lesson); }
  if (action === "complete-lesson") { try { await api(`/lessons/${button.dataset.id}/complete`, { method: "POST", body: "{}" }); closeModal(); if (state.focusCourse) { state.focusLessons = (await api(`/courses/${encodeURIComponent(state.focusCourse.course_id)}/lessons`)).lessons; } toast("Lesson marked complete."); await render(); } catch (e) { toast(e.message, true); } }
  if (action === "add-quiz") { if (!state.courses.length) state.courses = (await api("/courses")).courses; showQuizModal(); }
  if (action === "edit-quiz") { try { showQuizModal((await api(`/quizzes/${button.dataset.id}`)).quiz); } catch (e) { toast(e.message, true); } }
  if (action === "add-quiz-question") { state.quizDraftQuestions = captureQuizQuestionDrafts(); state.quizDraftQuestions.push({}); document.querySelector("#quiz-question-list").innerHTML = renderQuizQuestionList(); }
  if (action === "remove-quiz-question") { state.quizDraftQuestions = captureQuizQuestionDrafts(); if (state.quizDraftQuestions.length > 1) state.quizDraftQuestions.splice(Number(button.dataset.index), 1); document.querySelector("#quiz-question-list").innerHTML = renderQuizQuestionList(); }
  if (action === "close-modal") closeModal();
  if (action === "delete-course") { const course = state.courses.find(c => c.course_id === button.dataset.id); if (confirm(`Delete “${course?.title || button.dataset.id}”?`)) { try { await api(`/courses/${encodeURIComponent(button.dataset.id)}`, { method: "DELETE" }); toast("Course deleted."); await render(); } catch (e) { toast(e.message, true); } } }
  if (action === "delete-quiz") { const quiz = state.quizzes.find(q => q._id === button.dataset.id); if (confirm(`Delete “${quiz?.title || "this quiz"}”?`)) { try { await api(`/quizzes/${button.dataset.id}`, { method: "DELETE" }); toast("Quiz deleted."); await render(); } catch (e) { toast(e.message, true); } } }
  if (action === "delete-lesson") { const lesson = state.lessons.find(l => l._id === button.dataset.id); if (confirm(`Delete “${lesson?.title || "this lesson"}”? Student completion records for this lesson will also be removed.`)) { try { await api(`/admin/lessons/${button.dataset.id}`, { method: "DELETE" }); toast("Lesson deleted."); await render(); } catch (e) { toast(e.message, true); } } }
  if (action === "student-status") { const status = button.dataset.status; if (confirm(`${status === "suspended" ? "Suspend" : "Reactivate"} this student account?`)) { try { await api(`/admin/students/${button.dataset.id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }); toast(status === "suspended" ? "Student account suspended." : "Student account reactivated."); await render(); } catch (e) { toast(e.message, true); } } }
});

app.addEventListener("input", event => {
  if (event.target.id !== "global-search") return;
  const query = event.target.value.trim().toLowerCase();
  const cards = [...app.querySelectorAll(".course-tile, .course-card, .quiz-card, .lesson-row")];
  let visibleCount = 0;
  for (const card of cards) {
    const visible = !query || card.textContent.toLowerCase().includes(query);
    card.hidden = !visible;
    if (visible) visibleCount++;
  }
  let emptyMessage = app.querySelector(".search-result-empty");
  if (query && cards.length && visibleCount === 0) {
    if (!emptyMessage) {
      emptyMessage = document.createElement("div");
      emptyMessage.className = "empty search-result-empty";
      emptyMessage.setAttribute("role", "status");
      (app.querySelector(".page-heading") || app.querySelector(".page")).after(emptyMessage);
    }
    emptyMessage.innerHTML = `<strong>No results for “${esc(event.target.value)}”</strong>Try another course, topic, or quiz title.`;
  } else emptyMessage?.remove();
});

app.addEventListener("change", event => {
  if (event.target.id === "auth-role") {
    state.authRole = event.target.value;
    document.querySelector("#student-profile-fields")?.classList.toggle("hidden", state.authRole === "admin");
    document.querySelector("#admin-key-field")?.classList.toggle("hidden", state.authRole !== "admin");
    const foot = document.querySelector(".auth-card .auth-foot"); if (foot) foot.textContent = state.authRole === "admin" ? "Admin key: backend/.env → ADMIN_SIGNUP_KEY. Ask the project owner; keep it private." : "Your progress is personal. Your learning is yours.";
  }
});

boot();
