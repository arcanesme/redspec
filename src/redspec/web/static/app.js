/* Redspec Web UI */

let editor;
let currentBlob = null;
let currentFormat = "png";
let zoomLevel = 1;
let resourceTypes = [];

document.addEventListener("DOMContentLoaded", () => {
    // Init CodeMirror with hint addon
    editor = CodeMirror.fromTextArea(document.getElementById("yaml-editor"), {
        mode: "yaml",
        theme: "dracula",
        lineNumbers: true,
        tabSize: 2,
        indentWithTabs: false,
        lineWrapping: true,
        extraKeys: { "Ctrl-Space": "autocomplete" },
        hintOptions: { hint: yamlHint },
    });

    // Load default template
    fetch("/api/templates/azure")
        .then(r => r.json())
        .then(data => editor.setValue(data.content))
        .catch(() => { });

    // Populate template picker
    fetch("/api/templates")
        .then(r => r.json())
        .then(names => {
            const picker = document.getElementById("template-picker");
            names.forEach(name => {
                const opt = document.createElement("option");
                opt.value = name;
                opt.textContent = name;
                picker.appendChild(opt);
            });
        });

    // Load resource types for autocomplete
    fetch("/api/resources")
        .then(r => r.json())
        .then(types => { resourceTypes = types; })
        .catch(() => { });

    // Template picker change
    document.getElementById("template-picker").addEventListener("change", (e) => {
        const name = e.target.value;
        if (!name) return;
        fetch(`/api/templates/${name}`)
            .then(r => r.json())
            .then(data => editor.setValue(data.content));
    });

    // DPI slider
    document.getElementById("dpi-slider").addEventListener("input", (e) => {
        document.getElementById("dpi-label").textContent = e.target.value;
    });

    // Theme picker — auto-toggle glow on dark/presentation themes
    document.getElementById("theme-picker").addEventListener("change", (e) => {
        const theme = e.target.value;
        const glowToggle = document.getElementById("glow-toggle");
        glowToggle.checked = (theme === "dark" || theme === "presentation");
    });

    // Format picker — dim glow toggle when PNG
    document.getElementById("format-picker").addEventListener("change", updateGlowHint);

    // Dark mode toggle
    document.getElementById("dark-mode-toggle").addEventListener("change", (e) => {
        document.body.classList.toggle("light-mode", !e.target.checked);
    });

    // Generate button
    document.getElementById("btn-generate").addEventListener("click", generateDiagram);

    // Validate button
    document.getElementById("btn-validate").addEventListener("click", validateYAML);

    // Download button
    document.getElementById("btn-download").addEventListener("click", downloadDiagram);

    // Zoom controls
    document.getElementById("btn-zoom-in").addEventListener("click", () => setZoom(zoomLevel + 0.25));
    document.getElementById("btn-zoom-out").addEventListener("click", () => setZoom(zoomLevel - 0.25));
    document.getElementById("btn-zoom-reset").addEventListener("click", () => setZoom(1));

    // Export dropdown
    document.getElementById("btn-export").addEventListener("click", (e) => {
        e.stopPropagation();
        document.getElementById("export-menu").classList.toggle("show");
    });
    document.addEventListener("click", () => {
        document.getElementById("export-menu").classList.remove("show");
    });
    document.querySelectorAll("#export-menu button").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            exportDiagram(btn.dataset.format);
            document.getElementById("export-menu").classList.remove("show");
        });
    });

    // Diff modal
    document.getElementById("btn-diff").addEventListener("click", openDiffModal);
    document.getElementById("diff-close").addEventListener("click", closeDiffModal);
    document.getElementById("btn-diff-run").addEventListener("click", runDiff);
    document.getElementById("diff-modal").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeDiffModal();
    });

    // Theme builder modal — open from theme picker context menu or a hidden trigger
    // We add a "Custom..." option to the theme picker
    const themePicker = document.getElementById("theme-picker");
    const customOpt = document.createElement("option");
    customOpt.value = "__custom__";
    customOpt.textContent = "CUSTOM...";
    themePicker.appendChild(customOpt);
    themePicker.addEventListener("change", (e) => {
        if (e.target.value === "__custom__") {
            openThemeModal();
            e.target.value = "default";
        }
    });

    document.getElementById("theme-close").addEventListener("click", closeThemeModal);
    document.getElementById("btn-theme-register").addEventListener("click", registerCustomTheme);
    document.getElementById("theme-modal").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeThemeModal();
    });

    // Initial glow hint state
    updateGlowHint();

    // Load gallery on startup
    loadGallery();

    // WebSocket live preview
    initWebSocket();
});

/* ===== Status ===== */

function updateStatus(message, type) {
    const statusBar = document.getElementById("status-bar");
    const statusText = statusBar.querySelector(".status-text");
    const indicator = statusBar.querySelector(".status-indicator");

    if (!statusText) {
        statusBar.textContent = message;
        statusBar.className = `status-bar ${type || ""}`;
        return;
    }

    statusText.textContent = message;
    statusBar.className = `status-bar ${type || ""}`;
}

function updateGlowHint() {
    const format = document.getElementById("format-picker").value;
    const glowLabel = document.getElementById("glow-toggle").closest(".toggle-label");
    if (format !== "svg") {
        glowLabel.classList.add("disabled-hint");
        glowLabel.title = "Glow effects only apply to SVG format";
    } else {
        glowLabel.classList.remove("disabled-hint");
        glowLabel.title = "";
    }
}

function updatePreviewBackground() {
    const previewArea = document.getElementById("preview-area");
    const theme = document.getElementById("theme-picker").value;
    if (theme === "dark" || theme === "presentation") {
        previewArea.classList.add("dark-preview");
    } else {
        previewArea.classList.remove("dark-preview");
    }
}

/* ===== WebSocket Live Preview ===== */

let ws = null;
let wsDebounceTimer = null;
const WS_DEBOUNCE_MS = 800;

function initWebSocket() {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${location.host}/ws/preview`;

    try {
        ws = new WebSocket(wsUrl);
    } catch {
        setWsStatus("off");
        return;
    }

    ws.onopen = () => {
        setWsStatus("on");
        // Send current content on connect
        sendWsPreview();
    };

    ws.onclose = () => {
        setWsStatus("off");
        // Reconnect after delay
        setTimeout(initWebSocket, 3000);
    };

    ws.onerror = () => {
        setWsStatus("off");
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "preview" && data.svg) {
                showSvgPreview(data.svg);
            }
        } catch {
            // Ignore invalid messages
        }
    };

    // Watch editor changes for live preview
    editor.on("change", () => {
        clearTimeout(wsDebounceTimer);
        wsDebounceTimer = setTimeout(sendWsPreview, WS_DEBOUNCE_MS);
    });
}

function sendWsPreview() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({
        yaml_content: editor.getValue(),
        theme: document.getElementById("theme-picker").value,
        direction: document.getElementById("direction-picker").value,
    }));
}

function showSvgPreview(svgText) {
    const previewArea = document.getElementById("preview-area");
    updatePreviewBackground();
    previewArea.innerHTML = "";
    const container = document.createElement("div");
    container.className = "svg-preview";
    container.innerHTML = svgText;
    container.style.transform = `scale(${zoomLevel})`;
    previewArea.appendChild(container);
}

function setWsStatus(state) {
    const dot = document.getElementById("ws-status");
    if (!dot) return;
    dot.className = `ws-dot ws-${state}`;
    dot.title = state === "on" ? "Live preview connected" : "Live preview disconnected";
}

/* ===== Zoom ===== */

function setZoom(level) {
    zoomLevel = Math.max(0.25, Math.min(4, level));
    const previewArea = document.getElementById("preview-area");
    const target = previewArea.querySelector("img, .svg-preview");
    if (target) {
        target.style.transform = `scale(${zoomLevel})`;
        target.style.transformOrigin = "center center";
    }
}

/* ===== CodeMirror YAML Hints ===== */

function yamlHint(cm) {
    const cursor = cm.getCursor();
    const line = cm.getLine(cursor.line);
    const token = cm.getTokenAt(cursor);
    const start = token.start;
    const end = cursor.ch;
    const currentWord = line.slice(start, end).toLowerCase();

    // Detect if we're in a type: field
    const isTypeField = /^\s*-?\s*type:\s*/.test(line.slice(0, start)) || /type:\s*$/.test(line.slice(0, end));

    let completions = [];

    if (isTypeField && resourceTypes.length > 0) {
        completions = resourceTypes.filter(t => t.toLowerCase().includes(currentWord));
    } else {
        // General YAML keys
        const yamlKeys = [
            "diagram:", "name:", "theme:", "direction:", "dpi:", "legend:", "animation:",
            "resources:", "type:", "children:", "zone:", "metadata:",
            "connections:", "source:", "to:", "label:", "style:", "color:", "style_ref:",
            "connection_styles:", "variables:",
        ];
        completions = yamlKeys.filter(k => k.toLowerCase().startsWith(currentWord));
    }

    return {
        list: completions,
        from: CodeMirror.Pos(cursor.line, start),
        to: CodeMirror.Pos(cursor.line, end),
    };
}

/* ===== Generate ===== */

async function generateDiagram() {
    const previewArea = document.getElementById("preview-area");
    const downloadBtn = document.getElementById("btn-download");
    const generateBtn = document.getElementById("btn-generate");

    previewArea.innerHTML = '<div class="spinner"></div>';
    updateStatus("GENERATING...", "");

    downloadBtn.disabled = true;
    generateBtn.classList.add("btn-loading");

    currentFormat = document.getElementById("format-picker").value;
    const glowChecked = document.getElementById("glow-toggle").checked;

    const payload = {
        yaml_content: editor.getValue(),
        theme: document.getElementById("theme-picker").value,
        direction: document.getElementById("direction-picker").value,
        dpi: parseInt(document.getElementById("dpi-slider").value),
        format: currentFormat,
        glow: glowChecked,
    };

    try {
        const resp = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Generation failed");
        }

        currentBlob = await resp.blob();
        const url = URL.createObjectURL(currentBlob);

        updatePreviewBackground();
        zoomLevel = 1;

        const img = new Image();
        img.alt = "Generated diagram";
        img.onload = () => img.classList.add("fade-in");
        img.src = url;
        previewArea.innerHTML = "";
        previewArea.appendChild(img);

        downloadBtn.disabled = false;
        updateStatus("GENERATION COMPLETE", "success");

        loadGallery();
    } catch (err) {
        previewArea.innerHTML = `<div class="empty-state"><p style="color: var(--danger);">ERROR</p></div>`;
        updateStatus(`ERROR: ${err.message}`, "error");
    } finally {
        generateBtn.classList.remove("btn-loading");
    }
}

/* ===== Validate ===== */

async function validateYAML() {
    updateStatus("VALIDATING...", "");

    try {
        const resp = await fetch("/api/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ yaml_content: editor.getValue(), lint: true }),
        });

        const data = await resp.json();

        if (!resp.ok) {
            updateStatus(`INVALID: ${data.detail || "Parse error"}`, "error");
            return;
        }

        if (data.valid) {
            let msg = `VALID: ${data.name} (${data.resources} RES, ${data.connections} CONN)`;
            if (data.lint_warnings && data.lint_warnings.length > 0) {
                msg += ` | ${data.lint_warnings.length} LINT WARNING(S)`;
            }
            updateStatus(msg, "success");
        } else {
            updateStatus(`INVALID: ${data.error}`, "error");
        }
    } catch (err) {
        updateStatus(`VALIDATION ERROR: ${err.message}`, "error");
    }
}

/* ===== Download ===== */

function downloadDiagram() {
    if (!currentBlob) return;
    const url = URL.createObjectURL(currentBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `diagram.${currentFormat}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/* ===== Export ===== */

async function exportDiagram(format) {
    updateStatus(`EXPORTING ${format.toUpperCase()}...`, "");

    try {
        const resp = await fetch("/api/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ yaml_content: editor.getValue(), format }),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Export failed");
        }

        const data = await resp.json();

        // Download as text file
        const ext = { mermaid: "mmd", plantuml: "puml", drawio: "xml" }[format] || "txt";
        const blob = new Blob([data.content], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `diagram.${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        updateStatus(`EXPORTED ${format.toUpperCase()}`, "success");
    } catch (err) {
        updateStatus(`EXPORT ERROR: ${err.message}`, "error");
    }
}

/* ===== Diff ===== */

function openDiffModal() {
    const modal = document.getElementById("diff-modal");
    modal.hidden = false;
    // Pre-fill "new" with current editor content
    document.getElementById("diff-new").value = editor.getValue();
    document.getElementById("diff-result").innerHTML = "";
}

function closeDiffModal() {
    document.getElementById("diff-modal").hidden = true;
}

async function runDiff() {
    const oldYaml = document.getElementById("diff-old").value;
    const newYaml = document.getElementById("diff-new").value;
    const resultDiv = document.getElementById("diff-result");

    if (!oldYaml.trim() || !newYaml.trim()) {
        resultDiv.innerHTML = '<p class="diff-error">Both YAML specs are required.</p>';
        return;
    }

    resultDiv.innerHTML = '<div class="spinner"></div>';

    try {
        const resp = await fetch("/api/diff", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ old_yaml: oldYaml, new_yaml: newYaml, format: "svg" }),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Diff failed");
        }

        const data = await resp.json();

        if (data.is_empty) {
            resultDiv.innerHTML = '<p class="diff-empty">No differences found.</p>';
            return;
        }

        let html = '<div class="diff-summary">';
        if (data.added_resources.length) html += `<span class="diff-added">+${data.added_resources.length} resources</span>`;
        if (data.removed_resources.length) html += `<span class="diff-removed">-${data.removed_resources.length} resources</span>`;
        if (data.added_connections.length) html += `<span class="diff-added">+${data.added_connections.length} connections</span>`;
        if (data.removed_connections.length) html += `<span class="diff-removed">-${data.removed_connections.length} connections</span>`;
        if (data.changed_connections.length) html += `<span class="diff-changed">~${data.changed_connections.length} changed</span>`;
        html += "</div>";

        if (data.diff_diagram) {
            html += `<div class="diff-diagram">${data.diff_diagram}</div>`;
        }

        resultDiv.innerHTML = html;
    } catch (err) {
        resultDiv.innerHTML = `<p class="diff-error">ERROR: ${err.message}</p>`;
    }
}

/* ===== Theme Builder ===== */

function openThemeModal() {
    document.getElementById("theme-modal").hidden = false;
    document.getElementById("theme-result").innerHTML = "";
}

function closeThemeModal() {
    document.getElementById("theme-modal").hidden = true;
}

async function registerCustomTheme() {
    const resultDiv = document.getElementById("theme-result");

    function parseField(id) {
        const val = document.getElementById(id).value.trim();
        return val ? JSON.parse(val) : {};
    }

    const name = document.getElementById("theme-name").value.trim();
    if (!name) {
        resultDiv.innerHTML = '<p class="diff-error">Theme name is required.</p>';
        return;
    }

    let payload;
    try {
        payload = {
            name,
            graph_attr: parseField("theme-graph"),
            node_attr: parseField("theme-node"),
            edge_attr: parseField("theme-edge"),
            cluster_base: parseField("theme-cluster"),
        };
    } catch (e) {
        resultDiv.innerHTML = `<p class="diff-error">Invalid JSON: ${e.message}</p>`;
        return;
    }

    try {
        const resp = await fetch("/api/themes/custom", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Registration failed");
        }

        // Add to theme picker
        const picker = document.getElementById("theme-picker");
        if (![...picker.options].some(o => o.value === name)) {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name.toUpperCase();
            // Insert before the CUSTOM... option
            picker.insertBefore(opt, picker.querySelector('[value="__custom__"]'));
        }
        picker.value = name;

        resultDiv.innerHTML = `<p class="diff-empty">Theme "${name}" registered.</p>`;
    } catch (err) {
        resultDiv.innerHTML = `<p class="diff-error">ERROR: ${err.message}</p>`;
    }
}

/* ===== Gallery ===== */

async function loadGallery() {
    const grid = document.getElementById("gallery-grid");

    try {
        const resp = await fetch("/api/gallery");
        const entries = await resp.json();

        if (entries.length === 0) {
            grid.innerHTML = '<p class="placeholder-text">No diagrams generated yet</p>';
            return;
        }

        grid.innerHTML = entries.map((entry, index) => {
            const fmt = entry.format || "png";
            const thumbSrc = `/api/gallery/${entry.slug}/diagram.${fmt}`;
            const ts = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "";
            const meta = [entry.theme, entry.direction, entry.dpi ? `${entry.dpi}dpi` : ""].filter(Boolean).join(" | ");
            const delay = index * 0.08;

            return `
                <div class="gallery-card" style="animation-delay: ${delay}s" data-slug="${entry.slug}">
                    <div class="gallery-card-thumb">
                        <img src="${thumbSrc}" alt="${entry.name}" loading="lazy">
                    </div>
                    <div class="gallery-card-body">
                        <div class="gallery-card-title">${entry.name}</div>
                        <div class="gallery-card-meta">${meta}<br>${ts}</div>
                        <div class="gallery-card-actions">
                            <a href="/api/gallery/${entry.slug}/diagram.${fmt}" download>Diagram</a>
                            <a href="/api/gallery/${entry.slug}/spec.yaml" download>YAML</a>
                            <button class="gallery-btn gallery-btn-load" data-slug="${entry.slug}">Load</button>
                            <button class="gallery-btn gallery-btn-delete" data-slug="${entry.slug}">Delete</button>
                        </div>
                    </div>
                </div>
            `;
        }).join("");

        // Wire up gallery action buttons
        grid.querySelectorAll(".gallery-btn-delete").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                deleteGalleryEntry(btn.dataset.slug);
            });
        });
        grid.querySelectorAll(".gallery-btn-load").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                loadGallerySpec(btn.dataset.slug);
            });
        });
    } catch (err) {
        grid.innerHTML = '<p class="placeholder-text">Failed to load gallery</p>';
    }
}

async function deleteGalleryEntry(slug) {
    if (!confirm(`Delete "${slug}"?`)) return;

    try {
        const resp = await fetch(`/api/gallery/${slug}`, { method: "DELETE" });
        if (!resp.ok) throw new Error("Delete failed");
        updateStatus(`DELETED: ${slug}`, "success");
        loadGallery();
    } catch (err) {
        updateStatus(`DELETE ERROR: ${err.message}`, "error");
    }
}

async function loadGallerySpec(slug) {
    try {
        const resp = await fetch(`/api/gallery/${slug}/spec.yaml`);
        if (!resp.ok) throw new Error("Failed to load spec");
        const text = await resp.text();
        editor.setValue(text);
        updateStatus(`LOADED: ${slug}`, "success");
    } catch (err) {
        updateStatus(`LOAD ERROR: ${err.message}`, "error");
    }
}
