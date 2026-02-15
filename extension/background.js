console.log("SW booted", new Date().toISOString());
console.log("background loaded");

async function apiFetch(baseUrl, path, method, body) {
	const url = baseUrl.replace(/\/+$/, "") + path;
	const res = await fetch(url, {
		method,
		headers: { "Content-Type": "application/json" },
		body: body ? JSON.stringify(body) : undefined,
	});

	const text = await res.text();
	let data;
	try { data = JSON.parse(text); } catch { data = text; }

	if (!res.ok) {
		throw new Error(`HTTP ${res.status}: ${typeof data === "string" ? data : JSON.stringify(data)}`);
	}
	return data;
}

function notify(tabId, message) {
	chrome.tabs.sendMessage(tabId, { type: "NOTIFY", message }).catch(() => { });
}

async function getActiveHttpTab() {
	const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
	if (!tab?.id) throw new Error("No active tab");

	const fullTab = await chrome.tabs.get(tab.id);
	const url = fullTab.url || tab.url;

	if (!url || !/^https?:\/\//.test(url)) throw new Error(`Invalid or missing URL: ${url}`);
	return { tabId: tab.id, url };
}

async function getSettingsForHost(host) {
	const stored = await chrome.storage.local.get([
		"backendUrl",
		"novelId",
		"chapterNo",
		"autoIncrementChapterNo",
		"customExtractors",
	]);

	const backendUrl = stored.backendUrl || "http://localhost:8787";
	const novelId = Number(stored.novelId || 1);
	const chapterNo = Number(stored.chapterNo || 1);
	const autoIncrement = stored.autoIncrementChapterNo !== false; // default true

	const map = stored.customExtractors || {};
	const normalized = host.replace(/^www\./, "");
	const config = map[normalized] || map[host] || null;

	return { backendUrl, novelId, chapterNo, autoIncrement, config, keyUsed: normalized };
}

async function runHotkeyFlow() {
	try {
		const { tabId, url } = await getActiveHttpTab();
		const host = new URL(url).hostname;

		const settings = await getSettingsForHost(host);
		console.log("Using settings:", settings);

		if (!settings.config) {
			notify(tabId, `No extractor config saved for ${host}. Open popup and save one.`);
			return;
		}

		// Confirm content script exists
		try {
			await chrome.tabs.sendMessage(tabId, { type: "PING" });
		} catch (e) {
			console.error("PING failed:", e);
			notify(tabId, "No content script on this page. Refresh the page and try again.");
			return;
		}

		notify(tabId, "ExtractingÉ");

		let extractRes;
		try {
			extractRes = await chrome.tabs.sendMessage(tabId, {
				type: "EXTRACT_WITH_CONFIG",
				config: settings.config,
			});
		} catch (err) {
			console.error("Content script not responding:", err);
			notify(tabId, "Content script not responding. Reload page.");
			return;
		}

		if (!extractRes?.ok) {
			notify(tabId, `Extract failed: ${extractRes?.error || "unknown error"}`);
			return;
		}

		const raw = extractRes.text?.trim();
		if (!raw) {
			notify(tabId, "Extractor returned empty text.");
			return;
		}

		notify(tabId, `Posting chapter ${settings.chapterNo}É`);

		const created = await apiFetch(
			settings.backendUrl,
			`/novels/${settings.novelId}/chapters`,
			"POST",
			{
				chapter_no: settings.chapterNo,
				raw,
				source_url: url,
			}
		);

		notify(tabId, `Translating id=${created.id}É`);

		await apiFetch(settings.backendUrl, `/chapters/${created.id}/translate`, "POST");

		notify(tabId, `Done. Saved chapter ${settings.chapterNo}.`);

		if (settings.autoIncrement) {
			const next = settings.chapterNo + 1;
			await chrome.storage.local.set({ chapterNo: String(next) });
			notify(tabId, `Next chapter = ${next}`);
		}
	} catch (err) {
		console.error("Hotkey flow error:", err);
	}
}

chrome.commands.onCommand.addListener((command) => {
	console.log("HOTKEY FIRED:", command);
	if (command === "extract_send_translate") runHotkeyFlow();
});
