const el = (id) => document.getElementById(id);
const setStatus = (s) => (el("status").textContent = s);

async function getActiveTab() {
	const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
	return tab;
}

function normalizeHost(host) {
	return host.replace(/^www\./, "");
}

async function load() {
	const tab = await getActiveTab();
	const host = normalizeHost(new URL(tab.url).hostname);

	const stored = await chrome.storage.local.get([
		"backendUrl",
		"novelId",
		"chapterNo",
		"customExtractors",
	]);

	el("backendUrl").value = stored.backendUrl || "http://localhost:8787";
	el("novelId").value = stored.novelId || "1";
	el("chapterNo").value = stored.chapterNo || "1";

	const map = stored.customExtractors || {};
	el("customExtractor").value = map[host] ? JSON.stringify(map[host], null, 2) : "";

	setStatus(`Editing extractor config for: ${host}`);
}

async function saveAll() {
	const tab = await getActiveTab();
	const host = normalizeHost(new URL(tab.url).hostname);

	const backendUrl = el("backendUrl").value.trim() || "http://localhost:8787";
	const novelId = el("novelId").value.trim() || "1";
	const chapterNo = el("chapterNo").value.trim() || "1";

	const rawConfig = el("customExtractor").value.trim();
	let config = null;

	if (rawConfig) {
		try {
			config = JSON.parse(rawConfig);
		} catch (e) {
			setStatus("Extractor config must be valid JSON.\n" + String(e));
			return;
		}
	}

	const stored = await chrome.storage.local.get(["customExtractors"]);
	const map = stored.customExtractors || {};
	map[host] = config;

	await chrome.storage.local.set({
		backendUrl,
		novelId,
		chapterNo,
		customExtractors: map,
		autoIncrementChapterNo: true,
	});

	setStatus(`Saved.\nHost: ${host}\nHotkey will use this config.`);
}

el("saveAll").addEventListener("click", saveAll);
load().catch((e) => setStatus(String(e)));
