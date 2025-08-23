Roadmap Implementasi (3 Fase)
Fase 1 — “Core + Voice + Office”

Tujuan: asisten suara yang bisa mengendalikan Windows & Office (Excel/Word/PPT) dengan aman.

1) Voice Input (STT) + TTS

Tambah tool voice_input (Whisper.cpp/Vosk) dengan push-to-talk & VAD.

Tambah TTS ringan (Piper) untuk umpan balik lisan.

Acceptance: latensi STT→aksi ≤ 2 detik pada i7-7700HQ (model Whisper “base”/Vosk).

Tambah file/folder:

windows_use/tools/voice_input.py

windows_use/tools/tts_piper.py

examples/voice_loop.py

Ubah:

README.md → seksi “Voice Mode (Offline)” + kebutuhan model. 
zdoc.app

2) Intent Parser (ID) + Router

Grammar perintah ID (mis. “tambah sheet”, “hapus slide”, “ganti semua ‘X’ jadi ‘Y’ di Word”) → fast-path ke aksi COM tanpa planning GUI.

Fallback ke LLM (lokal/awan) jika perintah bebas.

Tambah:

windows_use/nlu/grammar_id.py

windows_use/nlu/router.py

Ubah:

windows_use/agent.py → cek router sebelum invoke langkah GUI.

3) Office Automation via COM (pywin32)

Excel: add_sheet, delete_sheet (dengan konfirmasi), write_cell, format_column, insert_chart, save_as.

Word: replace_all, insert_heading, save_as_pdf.

PowerPoint: add_slide, edit_title, export_pdf.

Tambah:

windows_use/actions/office/excel_actions.py

windows_use/actions/office/word_actions.py

windows_use/actions/office/ppt_actions.py

Ubah:

requirements.txt → tambah pywin32.

README.md → “Office Fast-Path (COM) vs GUI Fallback” + contoh prompt. 
zdoc.app

4) Guardrails & HITL (Human-in-the-Loop)

Allowlist intent + konfirmasi untuk aksi destruktif (hapus sheet/slide, install paket).

Dry-run mode + “undo plan” sederhana (mis. simpan salinan dokumen sebelum aksi risiko).

Tambah:

windows_use/safety/policy.py (allow/deny)

windows_use/safety/approver.py (konfirmasi interaktif)

5) Observability

Log JSON berstruktur setiap langkah: intent → plan/fast-path → action → result.

Screenshot before/after (redaksi judul jendela sensitif).

Rekam session opsional (gif/mp4).

Tambah:

windows_use/obs/logger.py

windows_use/obs/snapshots.py

Fase 2 — “Windows Tooling, UX, Local LLM, Evaluasi”

Tujuan: tambah kapabilitas sistemik & robustness sesuai roadmap repo.

6) Windows System Tools (aman)

winget (install/update app), PowerShell cmdlets (file/process/network; registry read-only dulu), Tasklist/Taskkill (dengan prompt).

Acceptance: bisa install 7-Zip via voice (“install tujuh zip”), zip & pindahkan file via PS.

Tambah:

windows_use/tools/ps_shell.py

windows_use/tools/winget.py

windows_use/tools/process.py

windows_use/tools/net.py

7) Fallback GUI Backend (UIA)

Integrasi pywinauto/UIA untuk elemen yang tidak punya API; selector by AutomationId/Name/ControlType.

Sinkron dengan Roadmap → Improve UI element detection & Ally Tree. 
zdoc.app

Tambah:

windows_use/backends/uia_backend.py

8) Memory (Short/Long)

Short-term: cache hierarchy UI per-aplikasi (dengan staleness check).

Long-term: simpan “rute UI sukses” (vector store kecil) per versi app.

Menjawab Roadmap: Integrate memory. 
zdoc.app

Tambah:

windows_use/memory/session_cache.py

windows_use/memory/routes_store.py

9) Dukungan LLM Lokal (Ollama/llama.cpp)

Template config untuk llama3.2:3b, phi3:mini, qwen2.5:3b (quant Q4).

Routing: task ringan → lokal; reasoning berat → opsional cloud.

Menjawab Roadmap: Support for local LLMs. 
zdoc.app

Tambah:

windows_use/llm/local_client.py

examples/local_llm_config.yaml

Ubah:

README.md → seksinya “Local Models (Offline)”. 
zdoc.app

10) UX & Error Recovery

Latency cut (pre-warm model, cache context).

Self-check: screenshot-diff setelah aksi penting.

Graceful retry: fallback COM→UIA→OCR.

Tambah:

windows_use/recovery/retry_policy.py

windows_use/vision/ocr_fallback.py (Tesseract)

11) Evaluator & Benchmark

Harness tugas Windows: “ubah tema”, “export event log”, “Excel→chart→ke PPT”.

Success criteria tegas (file ada, format benar, UI elemen terdeteksi).

Menjawab Roadmap: Evaluation benchmarks. 
zdoc.app

Tambah:

eval/tasks/*.py

eval/runner.py

eval/reports/README.md

Fase 3 — “Game Mode (SEAL BOD Legal) & Cookbook”

Tujuan: mode bot legal untuk SEAL BOD (sesuai pengumuman GM), dikendalikan suara & skrip aman.

12) Game Input & Macro Builder

Emulasi input manusia (key down/up, click), delay natural, anti-spam.

Macro pendek & loop waktu (mis. 30-60 menit).

Tambah:

windows_use/actions/game/input_emulator.py

windows_use/actions/game/macro_scheduler.py

13) Game State Awareness (Legal)

OCR/vision untuk baca HP/MP bar & cooldown ikon (tanpa bypass anti-cheat).

Rules sederhana: “potion jika HP < X%”, “buff tiap 10 menit”.

Tambah:

windows_use/actions/game/state_reader.py

windows_use/actions/game/rules_engine.py

14) Voice Commands untuk Game

Grammar ID: “mulai farming map Goblin 1 jam”, “stop bot”, “balik kota & jual”.

Safety: panic hotkey (deadman switch).

Tambah:

windows_use/nlu/grammar_game_id.py

examples/game_seal_bod_bot.py

15) Cookbook & Demo Lengkap

Excel→Chart→PPT, Outlook kirim lampiran, Event Viewer → ZIP, SEAL BOD farming loop.

Video/GIF demo + skrip siap jalan.

Tambah:

examples/cookbook/office_report_to_ppt.py

examples/cookbook/outlook_send_attachment.py

examples/cookbook/eventlog_export_zip.py

examples/cookbook/seal_bod_farming_loop.py

docs/cookbook.md

Ubah:

README.md → tambah “Cookbook & Demos” + link video. 
zdoc.app

Ringkasan “Apa yang Ditambahkan vs Diubah” (ringkas)
Ditambahkan (folder/file kunci)

windows_use/tools/: voice_input.py, tts_piper.py, ps_shell.py, winget.py, process.py, net.py

windows_use/actions/office/: excel_actions.py, word_actions.py, ppt_actions.py

windows_use/actions/game/: input_emulator.py, macro_scheduler.py, state_reader.py

windows_use/backends/: uia_backend.py

windows_use/nlu/: grammar_id.py, grammar_game_id.py, router.py

windows_use/memory/: session_cache.py, routes_store.py

windows_use/obs/: logger.py, snapshots.py

windows_use/recovery/: retry_policy.py

windows_use/vision/: ocr_fallback.py

windows_use/llm/: local_client.py

eval/: tasks/*.py, runner.py, reports/

examples/: voice_loop.py, local_llm_config.yaml, game_seal_bod_bot.py, cookbook/*.py

docs/: cookbook.md, SECURITY_SANDBOX.md

Diubah (file eksisting)

advanced_ai_agents/single_agent_apps/windows_use_autonomous_agent/README.md

Tambah: Voice Mode, Office Fast-Path (COM), Local LLMs, Security & Sandbox, Evaluation, Cookbook & Demos. (Selaras Roadmap resmi). 
zdoc.app

windows_use/agent.py

Integrasi intent router (fast-path Office/Game) sebelum langkah GUI.

requirements.txt

Tambah: pywin32, pywinauto, pydantic, pillow, pytesseract (opsional), sounddevice/webrtcvad (untuk STT), piper-phonemizer (opsional).

Acceptance Criteria (contoh cepat)

Voice Office: “Excel, tambah sheet ‘Laporan’, isi A1 ‘Pendapatan Q3’, format kolom B persen.” → sukses ≤ 3 detik, tanpa intervensi manual.

System Tools: “Install 7-Zip lalu zip file terbesar di Downloads ke Desktop.” → sukses, ada artefak .zip.

Local LLM: ollama profile bekerja (3B Q4), respons ≤ 2 s untuk intent standar.

Evaluator: eval/runner.py melaporkan >90% pass pada 10 tugas Windows standar.

Game Mode (legal): “Mulai farming map Goblin 30 menit, potion <40% HP, stop lalu balik kota jual item” → loop berjalan, bisa dihentikan suara/panic key.

Catatan penting

Semua penambahan di atas sejalan dengan niat & roadmap modul (memory, Ally Tree, UX, local LLM, evaluasi). 
zdoc.app

Struktur repo utama memang mengarahkan pengguna untuk masuk ke tiap sub-app dan mengikuti README.md masing-masing; update kita mempertahankan pola itu. 
GitHub
📌 To-Do List Tambahan – Integrasi Self-Evolving Agent
1. Modul Evolusi & Refleksi

 Buat folder evolve/ di project.

 Tambahkan evaluator.py → cek hasil eksekusi (contoh: file ada, jumlah slide benar, sel Excel berisi nilai yang diinginkan).

 Tambahkan reflector.py → ringkas sukses/gagal dari log (kenapa gagal, apa yang bisa diperbaiki).

 Tambahkan mutator.py → perbaiki prompt atau urutan tool (misalnya prefer COM > UIA, tambah delay, retry policy).

 Tambahkan selector.py → pilih konfigurasi/prompt terbaik berdasarkan skor evaluator.

 Tambahkan memory_store.py → simpan “playbook terbaik” per task signature (SQLite/JSON).

2. Integrasi LLM Lokal (Ollama) untuk Multi-Peran

 Buat config llm/local_ollama.yaml → profil:

task_llm (misalnya llama3.2:3b Q4) untuk planning/eksekusi.

judge_llm (misalnya sama model kecil, atau fallback cloud opsional) untuk evaluasi/refleksi.

 Update agent.py → tambahkan call ke judge_llm saat menjalankan modul reflector.py.

 Tambahkan flag/env variable untuk fallback ke cloud LLM kalau reasoning berat diperlukan (opsional).

3. Loop Self-Improvement

 Buat evolve/loop.py → alur:

Plan → (task_llm)

Execute → (windows_use executor)

Evaluate → (evaluator.py)

Reflect → (reflector.py + judge_llm)

Mutate → (mutator.py)

Select & Save Best Policy → (selector.py + memory_store.py)

 Simpan hasil evolusi (log JSON, artifact file, skor).

4. Evaluator Tugas Standar

 Tambahkan task evaluasi di eval/tasks/:

Excel: tambah sheet, isi sel, format kolom → cek isi sel & format.

Word: replace teks & export PDF → cek file PDF ada & >0 KB.

PowerPoint: tambah slide judul → cek jumlah slide.

Windows System: install app via winget → cek file executable ada.

Game legal (SEAL BOD): farming loop 10 menit → cek log event & panic key bekerja.

 Buat eval/runner.py → jalankan batch tugas, skor hasil, simpan laporan.

5. Memory & Playbook

 Buat memory/routes_cache.json → simpan rute UI sukses (per aplikasi/versi).

 Buat memory/policy_store.sqlite → simpan best policy per task signature.

 Update agent untuk cek memory sebelum planning → kalau ada playbook sukses, pakai ulang.

6. Observabilitas Evolusi

 Tambahkan logging JSON detail (plan, hasil, refleksi, mutasi, skor).

 Tambahkan opsi rekam GIF/mp4 pendek saat evolusi untuk debugging.

 Buat reports/evolution_history.md → timeline perbaikan (versi policy, skor, alasan refleksi).

7. Cookbook & Demo Evolusi

 Tambahkan examples/evolve_office_report.py → tugas: buat laporan Excel→chart→PPT→PDF, lalu jalankan evolusi 2–3 iterasi.

 Tambahkan examples/evolve_game_macro.py → farming loop di SEAL BOD, lalu bot memperbaiki urutan skill/cooldown setelah evaluasi.

 Update docs/cookbook.md → bagian “Self-Evolving Mode”.

8. Update Dokumentasi

 Update README.md:

Tambahkan seksi Self-Evolving Agent Mode.

Jelaskan flow Plan→Execute→Evaluate→Reflect→Mutate→Select.

Tambahkan instruksi untuk pakai Ollama (ollama run llama3.2:3b) sebagai task_llm & judge_llm.

 Tambahkan SECURITY_EVOLUTION.md: catat guardrails (misalnya aksi berbahaya tetap minta konfirmasi).

📌 Output akhir tambahan:

Agent tidak hanya mengeksekusi perintah (via suara atau teks), tapi juga belajar dari kesalahan dan makin lama makin stabil/efektif menjalankan tugas di Windows, Office, dan game legal.

Semua tetap berjalan dengan LLM lokal (Ollama), aman untuk laptop kamu.
📌 To-Do List Tambahan – Surfing Internet
1. Modul Dasar Web Search

 Buat folder web/.

 Tambahkan web/search.py: wrapper API ke serper.dev / Bing / Brave (atau duckduckgo-search kalau mau tanpa API key).

 Tambahkan web/results_parser.py: normalisasi hasil ke schema JSON {title, url, snippet}.

 Tambahkan config/web.yaml: simpan API key, max results, timeout.

2. Modul Web Open (Fetch & Parse)

 web/open_url.py: ambil konten HTML (pakai requests / httpx).

 web/html2text.py: convert HTML → Markdown/Text (pakai readability-lxml atau trafilatura).

 Tambahkan filter: drop script/ads, limit 5–10k karakter.

3. Tool Dispatcher (Router ke Web)

 Daftar tool baru di agent:

search_web(query: str) -> [Result]

open_url(url: str) -> str

 Tambahkan ke tool registry (llm/tools/schema.py) → agar bisa dipanggil oleh semua provider (Gemini/Claude/Ollama).

4. LLM Integration (Web Agent)

 Update agent.py: jika user tanya hal di luar konteks lokal (deteksi: query mengandung "cari", "apa itu", "terbaru"), → panggil search_web.

 Tambahkan policy:

default → ambil 3 hasil pertama, parse konten, ringkas.

long query → multi-hop: search → baca 2–3 sumber → gabung ringkasan.

 Streaming respons: bacakan temuan satu per satu (“Sumber A mengatakan…, Sumber B mengatakan…”).

5. Surf Mode dengan Voice

 Grammar suara:

“Cari di internet tentang harga kentang 2025” → panggil search_web.

“Buka link kedua” → open_url(results[1]).

“Ringkas halaman ini” → html2text + LLM summarizer.

 Tambahkan HITL (human-in-the-loop) prompt: konfirmasi sebelum klik random URL.

6. Observabilitas & Safety

 Logging setiap search_web & open_url ke file logs/web_history.json.

 Tambahkan filter konten (block site di blacklist).

 Tambahkan SECURITY_WEB.md → jelaskan batasan (tidak submit form otomatis, tidak login akun sensitif).

7. Evaluasi

 eval/tasks/web_tasks.py: tes standar

“Cari capital of Indonesia” → harus mengembalikan “Jakarta”.

“Cari berita terbaru AI” → return snippet dengan tanggal < 7 hari.

 eval/runner.py update → jalankan juga web tasks.

8. Cookbook & Demo

 examples/web_search_voice.py → tanya suara → cari → baca hasil.

 examples/web_multi_hop.py → pertanyaan kompleks, agent lakukan 2 search + ringkas.

 Update docs/cookbook.md → tambah “Surfing Internet Mode”.

Ringkas

Dengan tambahan ini, asistenmu akan:

🔎 Cari info terbaru dari internet (search API).

🌐 Buka & baca halaman → ringkas jadi teks/markdown.

🗣️ Kendalikan dengan suara: “Cari berita terbaru…”, “Buka link nomor 3”, “Ringkas halaman ini”.

🛡️ Tetap ada guardrails: logging, confirm sebelum klik, tidak login/submit form.
To-Do List Tambahan – Multi-Provider LLM
1) Abstraksi & Registry

 Buat llm/base.py:

Interface LLMProvider dengan:

chat(messages, tools=None, system=None, temperature=..., top_p=..., max_tokens=..., stream=False, **kwargs)

embed(texts, **kwargs) (opsional)

token_count(messages)

properties: name, max_context, supports_tools, supports_vision, supports_json_mode

 Buat llm/registry.py:

MODEL_CATALOG = { "gemini-1.5-flash": {...}, "claude-3.5-sonnet": {...}, "groq/llama3-70b": {...}, "deepseek-r1": {...}, "qwen2.5-7b-instruct": {...}, "ollama/llama3.2:3b": {...} }

Simpan info: context, harga (perkiraan), latensi, tool-call support, vision support.

 Buat config/models.yaml untuk override via file, bukan hard-code.

2) Adapter per Provider

 llm/adapters/gemini.py (Google Generative Language API) – tool calling & vision kuat.

 llm/adapters/anthropic_claude.py – Tool Use & JSON mode khas Claude.

 llm/adapters/groq.py – inferensi cepat (hosting Llama/Mixtral) → bagus untuk planner cepat.

 llm/adapters/deepseek.py – reasoning murah, cocok untuk reflector/judge.

 llm/adapters/qwen.py – kuat multibahasa, konteks besar; API OpenAI-compatible (varian).

 llm/adapters/ollama.py – lokal, HTTP http://localhost:11434 (streaming, json mode via format:"json").

 (Opsional) llm/adapters/openai_compatible.py – umumkan untuk server kompatibel (vllm, llama.cpp server, Text-Gen WebUI).

Semua adapter:

Standarkan payload internal ke satu format (messages [{"role":"system|user|assistant|tool","content":...}], tools schema, function-call).

Implementasikan konversi ke format khusus vendor.

Dukung streaming (SSE/chunk) → yield token demi token.

3) Router & Kebijakan Pemilihan Model

 llm/router.py:

Heuristik default:

Planning/Action singkat → Groq (Llama-3 8/70B) atau Ollama 3B (offline).

Judging/Reflector → Claude/DeepSeek/Qwen (pilih 1 default; bisa toggled).

Vision (screenshot UI) → Gemini/Qwen-VL.

Privasi ketat/offline → Ollama.

Budget Low → prefer lokal (Ollama) → fallback Groq/DeepSeek (murah).

Parameterisasi via config/router.yaml.

 Tambahkan failover: jika 429/5xx/timeouts → coba model lain di bucket sama (mis. “planner_fast” punya {Groq→DeepSeek→Ollama}).

4) Tokenizer & Guard

 llm/tok.py: pembungkus count token (pakai tiktoken/transformers/provider-count kalau ada).

 Middleware:

Truncation aman (prioritaskan system + instruksi + terakhir user).

JSON Schema Guard (untuk tool-calling) → re-ask ke model jika schema invalid.

5) Tool-Calling Normalisasi

 llm/tools/schema.py – schema fungsi konsisten (pydantic).

 llm/tools/dispatcher.py – parser tool_calls lintas vendor → panggil tool Python (COM, PS, UIA).

 Uji silang: Gemini/Claude (native tool use) vs Groq/Ollama (OpenAI-style function call).

6) Konfigurasi & Rahasia

 .env.example → GEMINI_API_KEY=, ANTHROPIC_API_KEY=, GROQ_API_KEY=, DEEPSEEK_API_KEY=, QWEN_API_KEY=.

 settings.py → load env, izinkan disable provider yang tidak diisi.

7) Logging & Telemetri per Provider

 obs/llm_metrics.py: catat latensi, tps, fail rate, biaya estimasi (jika pakai cloud).

 reports/provider_scorecard.md: ranking performa untuk task umum (plan/eval/reflect).

8) Uji Fungsional

 tests/llm/test_adapters.py: smoke test tiap adapter (mock respons).

 tests/llm/test_router.py: pemilihan model sesuai kebijakan.

 examples/multi_provider_demo.py: CLI untuk ganti provider on-the-fly:

python examples/multi_provider_demo.py --role planner --model groq/llama3-70b --stream

9) Integrasi ke Agent

 agent.py:

Tambahkan parameter --provider-profile planner_fast|judge_strict|vision → router pilih model.

Pasang fallback chain di tingkat agent (bukan hanya adapter).

 README.md: dokumentasi multi-provider, cara set env, contoh skenario:

“Offline only” (semua ke Ollama).

“Mixed” (planner Groq, judge Claude, vision Gemini).

“Budget saver” (planner DeepSeek, judge Qwen).

10) (Opsional) Ensemble & Cross-Check

 llm/ensemble.py: majority vote untuk langkah berisiko (hapus/format).

 evolve/judge_dual.py: dua judge (DeepSeek + Claude) → jika tidak sepakat, minta konfirmasi user.
 Buatkan sistem voice AI dengan karakteristik berikut:

1. Suara default "Jarvis" seperti dalam film Iron Man, dengan kemampuan untuk:
   - Mengubah nama voice AI kapan saja sesuai kebutuhan pengguna
   - Mendukung penggunaan dual bahasa (Indonesia dan Inggris) secara native
   - Memahami dan merespons percakapan campuran kedua bahasa

2. Antarmuka dashboard yang memenuhi kriteria:
   - Desain intuitif dan mudah dipahami oleh pengguna awam
   - Menyediakan kontrol dasar untuk berinteraksi dengan voice AI
   - Tampilan visual yang sederhana namun fungsional

3. Implementasi suara menggunakan salah satu opsi berikut:
   - Clone dari repository  (jika dianggap solusi terbaik)
   - Memanfaatkan instalasi Voice.ai yang sudah ada di D:\Voice.ai

Pilih metode implementasi suara yang paling optimal berdasarkan pertimbangan teknis dan kualitas output. Sistem harus berjalan stabil dengan latency minimal dan kualitas suara yang jelas.
To-Do List Tambahan – Web Form Automation (RPA)
1) Browser Automation Layer

 Tambah web/browser.py (Playwright)

Launch (Chromium/Edge), profil user terpisah, persistent session.

Opsi headful (tampak) & headless (terjadwal).

Hook untuk human-like delays & scrolling.

 Tambah web/selector_utils.py

Strategi selector: get_by_label, get_by_placeholder, role=*, CSS/XPath fallback.

Otomatis retry saat DOM dinamis.

2) Form Filler Engine

 web/form_filler.py

API: fill_form(url, schema: FormSchema, data: dict, steps: list[Action]).

Aksi umum: click, type, select, check, upload, wait_for_nav, assert_text, download.

Penanganan date-picker, mask angka, iframe.

 web/field_mapper.py

Pemetaan field berbasis label/aria-label/placeholder/name/id dengan fallback heuristik.

Cache selector (per situs versi) di memory/routes_store.py.

3) Template & Data Binding

 web/templates/ekinerja_daily.json (contoh)

Skema: daftar langkah + selector + validasi.

 web/templates/laporan_keu_qX.json

 data_bindings/

Transformasi dari Excel/CSV → dict field (mis. tanggal, jam, uraian, nilai).

 Integrasi Office COM: baca Excel sumber → kirim ke form_filler.

4) Voice & Intent untuk Web

 nlu/grammar_web_id.py

“Isi e-Kinerja hari ini 8 jam, uraian ‘Pelayanan loket’”

“Unggah laporan keuangan Q3”

“Simpan bukti PDF”

 Router: intent web_fill → form_filler.

5) Keamanan & Kredensial

 security/credentials.py

Integrasi Windows Credential Manager (baca saat login).

Mode login manual (HITL): agent pause saat halaman login.

 security/policy_web.py

Allowlist domain (mis. *.go.id, *.asn.*), block unknown.

Confirm before submit (opsi: preview ringkasan field).

6) Observabilitas & Audit

 obs/audit_trail.py

Log JSON: timestamp, URL, field yang diisi (nilai disamarkan untuk data sensitif), hasil validasi.

 obs/snapshots.py

Screenshot before/after submit, simpan tanda terima/nomor tiket.

 reports/web_runs/

Arsip bukti pengiriman per hari/bulan.

7) Penanganan Edge Case

 web/anti_automation_handling.md

CAPTCHA → stop & minta intervensi; tidak ada bypass.

Session timeout → auto-relogin (jika kredensial aman tersedia).

File upload via input tersembunyi → gunakan set_input_files.

 recovery/retry_policy.py

Retry idempoten, backoff, resume from step.

8) Evaluasi & Demo

 eval/tasks/web_form_demo.py

Site dummy (mis. example web form) untuk CI test: isi, validasi, submit, unduh bukti.

 examples/web_fill_ekinerja.py

Alur: buka → login (manual/credman) → isi → validasi → submit → simpan PDF.

 docs/cookbook.md

“Isi e-Kinerja harian dari voice atau Excel.”
0) Fondasi Mode & Switching

 modes/manager.py

Enum: ASSISTIVE, SEMI_AUTO, FULL_AUTO

API: get_mode(), set_mode(mode), event on_mode_change

 nlu/grammar_mode_id.py (voice intents)

“mode bantuan/assistive”, “mode semi otomatis”, “mode penuh otomatis”, “kembali ke assistive”

 Integrasi ke agent loop

Injector current_mode yang mempengaruhi perilaku submit/konfirmasi/scheduling

 Persistensi mode (per user/profil)

config/profile.json: { "default_mode": "ASSISTIVE" }

1) Mode ASSISTIVE (HITL sepenuhnya)

Tujuan: Agent mengisi & menyiapkan, kamu yang menekan “Kirim”.

Fungsional

 web/form_filler.py: jalankan semua langkah kecuali submit

 ui/preview_panel: tampilkan ringkasan field + diff & validasi

 Voice intents:

“tinjau isian”, “perbaiki field [nama] jadi [nilai]”, “kirim sekarang”

 Safety

Always-confirm sebelum submit; blok aksi destruktif

Audit

 obs/audit_trail.py: log JSON isian (mask data sensitif), SS sebelum/ sesudah

Acceptance

 Dari suara: “isi e-Kinerja 8 jam, uraian Pelayanan Loket” → preview muncul → “kirim” → submit + simpan bukti ekinerja-YYYY-MM-DD.pdf

2) Mode SEMI-AUTO (terjadwal & OTP manual)

Tujuan: Agent otomatis sampai login/OTP, lanjut otomatis setelah OTP diisi.

Fungsional

 scheduler/jobs.py: job harian/mingguan (RRULE)

 security/credentials.py: integrasi Windows Credential Manager (username), OTP tetap manual

 web/session_keeper.py: persist cookie; auto-relogin jika kadaluarsa

 Flow: buka → isi → pause di login/OTP → lanjut → preview singkat → kirim

Voice & Dashboard

 Perintah suara: “jadwalkan e-Kinerja tiap hari jam 16:30”, “jalan sekarang”

 Toggle dashboard: ON/OFF jadwal; tombol “Lanjutkan setelah OTP”

Acceptance

 Job otomatis mulai, berhenti di halaman OTP, setelah OTP diinput → agent lanjut isi, preview, submit, simpan bukti

3) Mode FULL-AUTO (bila ToS/aturan sistem memperbolehkan)

Tujuan: End-to-end tanpa intervensi (tanpa CAPTCHA/OTP atau via SSO/cred aman).

Fungsional

 security/credentials.py: opsi auto-login (CredMan/SSO)

 web/form_filler.py: auto-submit (skip preview, tetap validasi internal)

 policy/auto_guard.py: guardrails—allowlist domain, limiter jam jalan, deadman switch

Pemantauan

 obs/healthcheck.py: watchdog + retry/resume; minidump saat gagal

 reports/web_runs/: arsip tanda terima/bukti & nomor tiket

Acceptance

 Tugas batch (mis. unggah laporan keuangan Q3) selesai tanpa intervensi, bukti tersimpan, log bersih

4) Dashboard 1-Klik (untuk user awam)

Sederhana, ringan, dan bisa portable. Opsi: Electron + FastAPI, atau PySide6 (Qt) standalone.

Tampilan Utama

 Tombol Besar “Aktifkan AI (1-Klik)”

Start semua servis (STT/TTS, router LLM, scheduler, web module)

 Pemilih Mode (radio/segmented): Assistive / Semi-Auto / Full-Auto

 Perintah Cepat:

“Isi e-Kinerja Hari Ini”, “Unggah Laporan Keuangan”, “Mulai Bot SEAL 30 menit”

 Status & Log (ringkas): indikator online, task running, error terakhir

 Kredensial & Keamanan

Panel set Credential Manager (simpan/tes), allowlist domain

 Jadwal

Tabel job: nama, waktu, mode, tombol ON/OFF

 Bukti & Arsip

Daftar PDF/SS terakhir + tombol “Buka Folder”

Teknis

 ui/app.py (backend FastAPI) + ui/frontend/ (Electron/Qt)

 services/launcher.py: start/stop komponen (STT, TTS, LLM router, scheduler)

 tray_icon (opsional): quick toggle mic, mode, panic/stop all

Acceptance

 User awam bisa klik 1 tombol → agent siap dengar & jalan; pilih mode; jalankan task preset; lihat bukti/riwayat

5) Voice Switching & Shortcut

 Voice intents: “aktifkan AI”, “nonaktifkan AI”, “ganti ke semi-otomatis”, “mode penuh otomatis”, “panic stop”

 Hotkey global:

Push-to-talk, Panic (matikan semua input/aksi), Buka Dashboard

6) Preset Tugas (Library Task untuk Awam)

 tasks_library/ JSON template: ekinerja_daily.json, laporan_keu_qX.json, web_download_bukti.json

 Binding data dari Excel/CSV: data_bindings/*.py

 Di dashboard: dropdown “Pilih tugas” + isian minimal (tanggal/jam/uraian/file)

7) Keamanan & Etika

 SECURITY_MODES.md: jelaskan perilaku tiap mode, batasan, dan konsekuensi

 Full-Auto default OFF; aktifkan hanya per-tugas & domain terdaftar

 CAPTCHA/OTP: tidak dibypass; Semi-Auto berhenti dan minta intervensi

8) Observabilitas & Recovery

 Log terpadu (logs/app.jsonl), tag mode & task_id

 Rekap harian otomatis (reports/daily-summary.md)

 Resume-from-step: jika gagal di langkah N, lanjut dari N setelah perbaikan

9) Distribusi & 1-Klik Start

 Packager: PyInstaller/Briefcase untuk EXE; atau Electron builder

 Profile Wizard pertama kali: set mic, model LLM (Ollama lokal / campuran), kredensial, default mode

 Autostart Opsional: shortcut di Startup; tray app aktif saat boot

Ringkas Alur Suara yang Didukung

“Aktifkan AI” → layanan jalan, dashboard minim tampil

“Mode semi otomatis” → set_mode(SEMI_AUTO)

“Isi e-Kinerja 8 jam uraian Pelayanan Loket, kirim”

Assistive: isi → preview → “kirim”

Semi-Auto: kalau perlu OTP, pause & minta OTP → lanjut → preview singkat → kirim

Full-Auto: langsung submit (jika domain di allowlist & login tersedia)

“Panic stop” → hentikan semua input/aksi/job
Review dan bersihkan semua dependensi yang tidak digunakan dalam aplikasi. Pastikan aplikasi berfungsi dengan optimal saat pertama kali dijalankan. 

Saat pertama kali dijalankan, aplikasi harus meminta admin untuk merekam suaranya sebagai identifikasi. Setelah itu, jika ada pengguna lain yang memberikan perintah melalui suara, sistem akan memverifikasi terlebih dahulu apakah suara tersebut berasal dari admin atau bukan. 

Jika perintah diberikan oleh non-admin, sistem hanya akan menjalankan perintah yang sesuai dengan hak akses yang telah ditetapkan oleh admin sebelumnya. Pastikan pembatasan hak akses ini diterapkan secara konsisten.
Design a comprehensive and intuitive dashboard UI that effectively displays key metrics, data visualizations, and navigation elements. The dashboard should feature:

1. A clean, modern layout with fully responsive design that adapts to all screen sizes
2. Clearly organized, logically grouped sections for different data categories with proper labeling
3. Interactive, customizable charts/graphs (line, bar, pie) with tooltips and zoom functionality
4. Prominent, well-labeled action buttons/controls for quick access to core functions
5. A consistent, accessible color scheme and clear typography hierarchy following WCAG guidelines
6. Real-time data updates with visual indicators for fresh/changed data
7. Drag-and-drop customizable widgets and layout options to accommodate user preferences

Ensure the UI follows current UX best practices for usability, accessibility, and performance optimization.

Buat sebuah dashboard terpisah di luar folder Jarvis AI yang menampilkan dan mengelola semua fitur agent yang tersedia dalam sistem. Dashboard ini harus mencakup:

1. Tampilan terpusat yang menampilkan semua fungsi agent secara komprehensif dalam satu antarmuka
2. Kemampuan manajemen penuh termasuk pembuatan, konfigurasi, dan monitoring seluruh agent
3. Antarmuka yang intuitif dengan navigasi logis dan petunjuk yang jelas untuk semua level pengguna
4. Akses instan ke semua fitur agent melalui shortcut yang terorganisir.

Pastikan dashboard dirancang dengan:
- Tata letak yang terstruktur dengan pengelompokan fungsi yang logis
- Performa tinggi yang mampu menangani operasi multi-agent secara efisien
- Sistem navigasi hierarkis dengan breadcrumb dan pencarian untuk kemudahan pengelolaan fitur
Buatkan dokumen panduan pengguna dan petunjuk instalasi yang mudah dipahami oleh pengguna awam. Sertakan langkah-langkah detail beserta solusi alternatif jika fitur 1 klik tidak berfungsi, termasuk cara melakukan instalasi manual jika diperlukan. Pastikan dokumen menggunakan bahasa yang sederhana dan dilengkapi dengan ilustrasi/screenshot untuk memandu pengguna.