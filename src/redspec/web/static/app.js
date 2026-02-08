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
        .catch(() => {});

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

    // Generate button
    document.getElementById("btn-generate").addEventListener("click", generateDiagram);

    // Validate button
    document.getElementById("btn-validate").addEventListener("click", validateYAML);

    // Download button
    document.getElementById("btn-download").addEventListener("click", downloadDiagram);

    // Load gallery on startup
    loadGallery();
});

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
    const statusBar = document.getElementById("status-bar");
    const downloadBtn = document.getElementById("btn-download");
    const generateBtn = document.getElementById("btn-generate");

    previewArea.innerHTML = '<div class="spinner"></div>';
    statusBar.textContent = "Generating...";
    statusBar.className = "status-bar";
    downloadBtn.disabled = true;
    generateBtn.classList.add("btn-loading");

    currentFormat = document.getElementById("format-picker").value;

    const payload = {
        yaml_content: editor.getValue(),
        theme: document.getElementById("theme-picker").value,
        direction: document.getElementById("direction-picker").value,
        dpi: parseInt(document.getElementById("dpi-slider").value),
        format: currentFormat,
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
        statusBar.textContent = "Diagram generated successfully";
        statusBar.className = "status-bar success";

        // Refresh gallery
        loadGallery();
    } catch (err) {
        previewArea.innerHTML = `<p class="placeholder-text" style="color: var(--danger);">${err.message}</p>`;
        statusBar.textContent = `Error: ${err.message}`;
        statusBar.className = "status-bar error";
    } finally {
        generateBtn.classList.remove("btn-loading");
    }
}

async function validateYAML() {
    const statusBar = document.getElementById("status-bar");

    try {
        const resp = await fetch("/api/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ yaml_content: editor.getValue() }),
        });

        const data = await resp.json();

        if (data.valid) {
            statusBar.textContent = `Valid: ${data.name} (${data.resources} resources, ${data.connections} connections)`;
            statusBar.className = "status-bar success";
        } else {
            statusBar.textContent = `Invalid: ${data.error}`;
            statusBar.className = "status-bar error";
        }
    } catch (err) {
        statusBar.textContent = `Validation error: ${err.message}`;
        statusBar.className = "status-bar error";
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
