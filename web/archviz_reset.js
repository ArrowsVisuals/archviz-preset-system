// ArchViz Preset System — "reset to defaults" button on all (AV) nodes.
// Sits at the TOP of the widget list with a subtle bronze tint.
// Restores every widget to its default: combos to their first/default option
// ("(none)" for Matrix categories), numbers and strings to declared defaults.

import { app } from "../../scripts/app.js";

const AV_NODES = new Set([
    "ArchVizPresetLoader",
    "ArchVizPresetMatrix",
    "ArchVizPromptAssembler",
    "ArchVizScene",
]);

// Muted bronze — visible, not loud.
const TINT_FILL   = "rgba(176, 141, 87, 0.16)";
const TINT_BORDER = "rgba(176, 141, 87, 0.55)";
const TINT_TEXT   = "#d8c5a0";

function collectDefaults(nodeData) {
    const defaults = {};
    for (const group of [nodeData.input?.required, nodeData.input?.optional]) {
        if (!group) continue;
        for (const [name, spec] of Object.entries(group)) {
            const [type, cfg] = Array.isArray(spec) ? spec : [spec, undefined];
            if (Array.isArray(type)) {
                defaults[name] = cfg?.default !== undefined ? cfg.default : type[0];
            } else if (cfg && cfg.default !== undefined) {
                defaults[name] = cfg.default;
            } else if (type === "INT" || type === "FLOAT") {
                defaults[name] = 0;
            } else if (type === "STRING") {
                defaults[name] = "";
            }
        }
    }
    return defaults;
}

app.registerExtension({
    name: "archviz.reset_defaults",
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (!AV_NODES.has(nodeData.name)) return;

        const defaults = collectDefaults(nodeData);
        const onNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            const btn = this.addWidget("button", "↺ Reset to defaults", null, () => {
                for (const w of this.widgets ?? []) {
                    if (w.type === "button") continue;
                    if (w.name === "control_after_generate" ||
                        w.name?.startsWith("control_after")) {
                        if (w.options?.values?.includes("fixed")) w.value = "fixed";
                        continue;
                    }
                    if (w.name in defaults) {
                        w.value = defaults[w.name];
                        if (typeof w.callback === "function") {
                            try { w.callback(w.value, app.canvas, this, null, null); }
                            catch (e) { /* widget callbacks vary across versions */ }
                        }
                    }
                }
                this.setDirtyCanvas(true, true);
            }, { serialize: false });

            // Never contribute to saved widgets_values (cross-version safety).
            btn.serialize = false;
            btn.serializeValue = () => undefined;

            // Move to the top of the widget stack.
            const i = this.widgets.indexOf(btn);
            if (i > 0) {
                this.widgets.splice(i, 1);
                this.widgets.unshift(btn);
            }

            // Subtle bronze rendering. If a future frontend ignores custom
            // draw functions, the button falls back to its standard look.
            btn.draw = function (ctx, node, widgetWidth, y, H) {
                const m = 14;                       // side margin
                const w = widgetWidth - m * 2;
                ctx.save();
                ctx.beginPath();
                if (ctx.roundRect) ctx.roundRect(m, y, w, H, H * 0.5);
                else ctx.rect(m, y, w, H);
                ctx.fillStyle = TINT_FILL;
                ctx.fill();
                ctx.lineWidth = 1;
                ctx.strokeStyle = TINT_BORDER;
                ctx.stroke();
                ctx.fillStyle = TINT_TEXT;
                ctx.font = "11px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText("↺ Reset to defaults", widgetWidth / 2, y + H / 2);
                ctx.restore();
            };

            return r;
        };
    },
});
