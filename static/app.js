"use strict";

let state = { chapters: [], progress: {}, current: null };

const $ = (id) => document.getElementById(id);

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function esc(s) {
  return s.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

/* ---------- 渲染 ---------- */

function renderTree() {
  const tree = $("tree");
  tree.innerHTML = "";
  let doneCount = 0, total = 0, scoreSum = 0, scoreN = 0;

  for (const chapter of state.chapters) {
    const chDone = chapter.lessons.filter((l) => state.progress[l.id]?.done).length;
    doneCount += chDone;
    total += chapter.lessons.length;

    const box = document.createElement("div");
    box.className = "chapter";
    box.innerHTML = `
      <div class="chapter-title">
        <span>${esc(chapter.title)}</span>
        <span>${chDone}/${chapter.lessons.length}</span>
      </div>
      <div class="chapter-bar"><i style="width:${chDone / chapter.lessons.length * 100}%"></i></div>`;

    for (const lesson of chapter.lessons) {
      const p = state.progress[lesson.id];
      const div = document.createElement("div");
      div.className = "lesson" + (p?.done ? " done" : "") + (state.current === lesson.id ? " active" : "");
      const score = p ? p.best_score : -1;
      if (score >= 0) { scoreSum += score; scoreN++; }
      div.innerHTML = `
        <span class="check">${p?.done ? "✓" : ""}</span>
        <span>${esc(lesson.title)}</span>
        ${score >= 0 ? `<span class="score${score === 100 ? " hot" : ""}">${score}</span>` : ""}`;
      div.onclick = () => selectLesson(lesson.id);
      box.appendChild(div);
    }
    tree.appendChild(box);
  }

  $("stat-done").textContent = `已学完 ${doneCount}/${total}`;
  $("stat-score").textContent = scoreN ? `平均分 ${Math.round(scoreSum / scoreN)}` : "平均分 --";
}

async function selectLesson(id) {
  state.current = id;
  const data = await api(`/api/lesson/${id}`);
  const { lesson, code, progress } = data;

  $("lesson-title").textContent = `${lesson.title}`;
  $("lesson-desc").textContent = `课时 ID: ${lesson.id}${data.tests.length ? ` · 测试用例 ${data.tests.length} 个（判题满分 100）` : " · 无测试用例，可手动运行验证"}`;
  $("code").value = code || `/* ${lesson.title} */\n#include <stdio.h>\n\nint main(void)\n{\n    return 0;\n}\n`;
  $("chk-done").checked = !!progress?.done;
  $("result").classList.add("hidden");
  $("save-hint").textContent = "";
  renderTree();
}

/* ---------- 操作 ---------- */

async function save() {
  await api(`/api/lesson/${state.current}/code`, {
    method: "PUT",
    body: JSON.stringify({ code: $("code").value }),
  });
  $("save-hint").textContent = "已保存 ✓";
  setTimeout(() => ($("save-hint").textContent = ""), 2000);
}

$("btn-save").onclick = save;

$("btn-run").onclick = async () => {
  if (!state.current) return;
  setBusy("运行中…");
  try {
    const r = await api(`/api/lesson/${state.current}/run`, {
      method: "POST",
      body: JSON.stringify({ code: $("code").value, input: $("stdin").value }),
    });
    showResult(`
      <div class="block">
        <h4 class="${r.compile_ok ? "ok" : "fail"}">${r.compile_ok ? "编译成功 · 程序输出" : "编译失败"}</h4>
        <pre>${esc(r.output || "（无输出）")}</pre>
      </div>`);
  } catch (e) {
    showResult(`<div class="block"><h4 class="fail">请求失败</h4><pre>${esc(e.message)}</pre></div>`);
  } finally { setBusy(null); }
};

$("btn-judge").onclick = async () => {
  if (!state.current) return;
  setBusy("编译判题中…");
  try {
    const r = await api(`/api/lesson/${state.current}/judge`, {
      method: "POST",
      body: JSON.stringify({ code: $("code").value }),
    });
    renderJudge(r);
    renderTree();
  } catch (e) {
    showResult(`<div class="block"><h4 class="fail">请求失败</h4><pre>${esc(e.message)}</pre></div>`);
  } finally { setBusy(null); }
};

$("chk-done").onchange = async () => {
  if (!state.current) return;
  await api(`/api/lesson/${state.current}/done`, {
    method: "POST",
    body: JSON.stringify({ done: $("chk-done").checked }),
  });
  renderTree();
};

function renderJudge(r) {
  let html = "";
  if (!r.compile.ok) {
    html = `
      <div class="block">
        <h4 class="fail">编译失败 · 得分 0</h4>
        <pre>${esc(r.compile.output)}</pre>
      </div>`;
  } else {
    const rows = r.tests.map((t) => `
      <div class="test-row">
        <span class="test-name">${esc(t.name)}</span>
        <span class="${t.passed ? "pass-badge" : "fail-badge"}">${t.passed ? "✓ 通过" : "✗ 失败"}</span>
        ${t.reason ? `<span class="muted">${esc(t.reason)}</span>` : ""}
        ${!t.passed ? `<span class="muted">期望: <pre style="display:inline">${esc(t.expected)}</pre> · 实际: <pre style="display:inline">${esc(t.actual)}</pre></span>` : ""}
      </div>`).join("");
    html = `
      <div class="block">
        <h4>判题结果：<span class="${r.score === 100 ? "pass-badge" : r.passed > 0 ? "ok" : "fail-badge"}">${r.score} 分</span>
        <span class="muted">（通过 ${r.passed}/${r.total} 个用例）</span></h4>
        ${r.total ? rows : '<p class="muted">该课时没有测试用例，试试"运行"手动验证。</p>'}
      </div>`;
  }
  showResult(html);
}

function showResult(html) {
  const box = $("result");
  box.innerHTML = html;
  box.classList.remove("hidden");
}

function setBusy(text) {
  $("btn-save").disabled = $("btn-run").disabled = $("btn-judge").disabled = !!text;
  $("save-hint").textContent = text || "";
}

/* ---------- 启动 ---------- */

(async () => {
  const data = await api("/api/lessons");
  state.chapters = data.chapters;
  state.progress = data.progress;
  renderTree();
  const first = data.chapters[0]?.lessons[0]?.id;
  if (first) selectLesson(first);
})().catch((e) => {
  $("lesson-title").textContent = "无法连接后端";
  $("lesson-desc").textContent = e.message + " —— 请先启动服务：cd c-learning-platform && uvicorn app.main:app --reload";
});
