/* Redspec Web UI */

let editor;
let currentBlob = null;
let currentFormat = "png";

document.addEventListener("DOMContentLoaded", () => {
    // Init CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById("yaml-editor"), {
        mode: "yaml",
        theme: "dracula",
        lineNumbers: true,
        tabSize: 2,
        indentWithTabs: false,
        lineWrapping: true,
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

    // Format picker — dim glow toggle when PNG (glow only applies to SVG)
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

    // Initial glow hint state
    updateGlowHint();

    // Load gallery on startup
    loadGallery();
});

function updateStatus(message, type) {
    const statusBar = document.getElementById("status-bar");
    const statusText = statusBar.querySelector(".status-text");
    const indicator = statusBar.querySelector(".status-indicator");

    // If elements are missing (legacy fallback), just set textContent
    if (!statusText) {
        statusBar.textContent = message;
        statusBar.className = `status-bar ${type || ''}`;
        return;
    }

    statusText.textContent = message;
    statusBar.className = `status-bar ${type || ''}`;
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

        const img = new Image();
        img.alt = "Generated diagram";
        img.onload = () => img.classList.add("fade-in");
        img.src = url;
        previewArea.innerHTML = "";
        previewArea.appendChild(img);

        downloadBtn.disabled = false;
        updateStatus("GENERATION COMPLETE", "success");

        // Refresh gallery
        loadGallery();
    } catch (err) {
        previewArea.innerHTML = `<div class="empty-state"><p style="color: var(--danger);">ERROR</p></div>`;
        updateStatus(`ERROR: ${err.message}`, "error");
    } finally {
        generateBtn.classList.remove("btn-loading");
    }
}

async function validateYAML() {
    updateStatus("VALIDATING...", "");

    try {
        const resp = await fetch("/api/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ yaml_content: editor.getValue() }),
        });

        const data = await resp.json();

        if (data.valid) {
            updateStatus(`VALID: ${data.name} (${data.resources} RES, ${data.connections} CONN)`, "success");
        } else {
            updateStatus(`INVALID: ${data.error}`, "error");
        }
    } catch (err) {
        updateStatus(`VALIDATION ERROR: ${err.message}`, "error");
    }
}

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
                <div class="gallery-card" style="animation-delay: ${delay}s">
                    <div class="gallery-card-thumb">
                        <img src="${thumbSrc}" alt="${entry.name}" loading="lazy">
                    </div>
                    <div class="gallery-card-body">
                        <div class="gallery-card-title">${entry.name}</div>
                        <div class="gallery-card-meta">${meta}<br>${ts}</div>
                        <div class="gallery-card-actions">
                            <a href="/api/gallery/${entry.slug}/diagram.${fmt}" download>Diagram</a>
                            <a href="/api/gallery/${entry.slug}/spec.yaml" download>YAML</a>
                            <a href="/api/gallery/${entry.slug}/metadata.json" download>Metadata</a>
                        </div>
                    </div>
                </div>
            `;
        }).join("");
    } catch (err) {
        grid.innerHTML = '<p class="placeholder-text">Failed to load gallery</p>';
    }
}
