console.log("content.js loaded:", location.href);

function toast(msg) {
	const el = document.createElement("div");
	el.textContent = msg;
	el.style.position = "fixed";
	el.style.right = "12px";
	el.style.bottom = "12px";
	el.style.zIndex = "999999";
	el.style.padding = "10px 12px";
	el.style.background = "rgba(0,0,0,0.85)";
	el.style.color = "white";
	el.style.borderRadius = "8px";
	el.style.fontSize = "12px";
	el.style.maxWidth = "340px";
	el.style.whiteSpace = "pre-wrap";
	document.body.appendChild(el);
	setTimeout(() => el.remove(), 2500);
}

function firstShadowRootQuery(selector) {
	const roots = [...document.querySelectorAll("*")]
		.filter((el) => el.shadowRoot)
		.map((el) => el.shadowRoot);

	for (const r of roots) {
		const node = r.querySelector(selector);
		if (node) return node;
	}
	return null;
}

function extractWithConfig(config) {
	if (!config || typeof config !== "object") {
		return { ok: false, error: "Missing extractor config." };
	}

	const prop = config.prop === "innerText" ? "innerText" : "textContent";

	if (config.mode === "selector") {
		const el = document.querySelector(config.selector);
		const text = (el?.[prop] || "").trim();
		return text ? { ok: true, text } : { ok: false, error: "Selector returned empty." };
	}

	if (config.mode === "shadowSelector") {
		const node = firstShadowRootQuery(config.shadowSelector);
		const text = (node?.[prop] || "").trim();
		return text ? { ok: true, text } : { ok: false, error: "Shadow selector returned empty." };
	}

	return { ok: false, error: `Unknown mode: ${config.mode}` };
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
	if (msg.type === "PING") {
		sendResponse({ ok: true, url: location.href });
		return true;
	}

	if (msg.type === "EXTRACT_WITH_CONFIG") {
		sendResponse(extractWithConfig(msg.config));
		return true;
	}

	if (msg.type === "NOTIFY") {
		toast(msg.message);
		return true;
	}
});
