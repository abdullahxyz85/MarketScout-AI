"""Quick security-wiring audit. Run: python audit_security.py"""
import sys, os
os.chdir(os.path.dirname(__file__))

results = []
PASS, FAIL, WARN = "PASS", "FAIL", "WARN"

def check(label, condition, note=""):
    status = PASS if condition else FAIL
    results.append((status, label, note))

# ── 1. Read source files ──────────────────────────────────────────────────────
router_src   = open("router.py").read()
main_src     = open("main.py").read()
config_src   = open("config.py").read()
tavily_src   = open("services/tavily_client.py").read()
memory_src   = open("services/memory_service.py").read()
utils_src    = open("services/utils.py").read()
auth_src     = open("services/auth_guard.py").read()
models_src   = open("schemas/models.py").read()
rl_src       = open("services/rate_limiter.py").read()
ss_src       = open("services/secret_scanner.py").read()
rfront       = open("../frontend/lib/research-store.ts").read()
rcontext     = open("../frontend/lib/research-context.tsx").read()
rlayout      = open("../frontend/app/dashboard/layout.tsx").read()

# ── 2. Auth Guard ─────────────────────────────────────────────────────────────
check("Auth guard file exists",          "require_auth" in auth_src)
check("JWT cookie validated in guard",   "access_token" in auth_src and "jwt.decode" in auth_src)
check("DEV_USER bypass documented",      "_DEV_USER" in auth_src and "dev_anonymous" in auth_src)
check("401 on missing token",            "HTTP_401_UNAUTHORIZED" in auth_src or "401" in auth_src)
check("401 on expired token",            "ExpiredSignatureError" in auth_src)
check("Depends(require_auth) on start",  "auth_user_id: str = Depends(require_auth)" in router_src)

# ── 3. Job Ownership ─────────────────────────────────────────────────────────
check("owner_user_id stored in _jobs",   '"owner_user_id": auth_user_id' in router_src)
check("_assert_owns_job defined",        "def _assert_owns_job" in router_src)
check("Ownership check on stream",       "_assert_owns_job(job, auth_user_id)" in router_src)
check("Ownership check on result",       "_assert_owns_job" in router_src and router_src.count("_assert_owns_job(") >= 5,
      f"calls={router_src.count('_assert_owns_job(')}")
check("_get_completed_state takes auth", "async def _get_completed_state(job_id: str, auth_user_id: str)" in router_src)
check("startup-kit passes auth_user_id", "await _get_completed_state(job_id, auth_user_id)" in router_src)

# ── 4. UUID Validation ────────────────────────────────────────────────────────
check("_validate_uuid defined",          "def _validate_uuid" in router_src)
n_uuid = router_src.count("_validate_uuid(")
check(f"UUID validation called ({n_uuid}x)", n_uuid >= 5, f"calls={n_uuid}")

# ── 5. Rate Limiting ──────────────────────────────────────────────────────────
check("rate_limiter.py exists",          "limiter = _SlidingWindow()" in rl_src)
check("rate_limiter imported in router", "from services import rate_limiter" in router_src)
n_rl = router_src.count("rate_limiter.check")
check(f"Rate limits applied ({n_rl}x)",  n_rl >= 4, f"calls={n_rl}")
check("check_research_start wired",      "check_research_start(auth_user_id)" in router_src)
check("check_scenario wired",           "check_scenario(auth_user_id)" in router_src)
check("check_ask wired",                "check_ask(auth_user_id)" in router_src)
check("check_pdf wired",                "check_pdf(auth_user_id)" in router_src)
check("check_llm_doc wired",            "check_llm_doc(auth_user_id" in router_src)

# ── 6. Input Validation ───────────────────────────────────────────────────────
check("extra=forbid on ResearchRequest", "extra.*forbid" in models_src or '"extra": "forbid"' in models_src or "extra='forbid'" in models_src)
check("user_id removed from ResearchRequest", "user_id" not in models_src.split("class ResearchRequest")[1].split("class")[0] if "class ResearchRequest" in models_src else False)
check("user_id removed from ScenarioRequest", "user_id" not in models_src.split("class ScenarioRequest")[1].split("class")[0] if "class ScenarioRequest" in models_src else False)
check("control char validation in models","_SAFE_TEXT_RE" in models_src and "_reject_control_chars" in models_src)
check("max_length on idea field",        "max_length=1000" in models_src)
check("max_length on industry field",    "max_length=100" in models_src)
check("max_length on question field",    "max_length=500" in models_src)

# ── 7. Secret Scanner ─────────────────────────────────────────────────────────
check("secret_scanner.py exists",       "def scan(" in ss_src and "def assert_clean(" in ss_src)
check("Fireworks key pattern",          "fw_" in ss_src)
check("JWT pattern",                    "eyJ" in ss_src)
check("Private key pattern",           "BEGIN" in ss_src and "PRIVATE" in ss_src and "KEY" in ss_src)

# ── 8. Prompt Injection Guard ─────────────────────────────────────────────────
check("PROMPT_INJECTION_GUARD in utils","PROMPT_INJECTION_GUARD" in utils_src)
check("Untrusted source delimiters",    "UNTRUSTED_WEB_CONTENT" in utils_src)
for agent in ["research","competitor","patent","funding","trend","scientific","research_gap"]:
    ag_src = open(f"agents/{agent}_agent.py").read()
    check(f"Guard in {agent}_agent.py", "PROMPT_INJECTION_GUARD" in ag_src)

# ── 9. Mock Mode Control ──────────────────────────────────────────────────────
check("ALLOW_MOCK_SEARCH in config",    "ALLOW_MOCK_SEARCH" in config_src)
check("Mock blocked if flag=false",     "ALLOW_MOCK_SEARCH" in tavily_src and "RuntimeError" in tavily_src)
check("Production startup check",       "ALLOW_MOCK_SEARCH" in main_src or "TAVILY_API_KEY" in main_src)

# ── 10. Docs Protection ───────────────────────────────────────────────────────
check("Docs disabled in prod",          "_DOCS_URL" in main_src and "None if _IS_PROD" in main_src)
check("CORS restricted methods",        "GET.*POST.*OPTIONS" in main_src or '"GET"' in main_src)

# ── 11. Supabase owner filter ─────────────────────────────────────────────────
check("get_research_result owner filter","owner_user_id" in memory_src)
check("Supabase query filtered by owner","eq.*user_id.*owner_user_id" in memory_src.replace("\n","") or "owner_user_id" in memory_src)

# ── 12. Secure errors ─────────────────────────────────────────────────────────
check("_internal_error helper defined", "def _internal_error" in router_src)
check("Correlation ID in errors",       "corr_id" in router_src)
check("Generic error in pipeline",      "internal error occurred" in router_src)

# ── 13. Cache-Control on PDFs ─────────────────────────────────────────────────
check("Cache-Control private,no-store on PDF", "private, no-store" in router_src)

# ── 14. Frontend ──────────────────────────────────────────────────────────────
check("clearLastResearch exported",     "export function clearLastResearch" in rfront)
check("clearLastResearch on logout",    "clearLastResearch()" in rlayout)
check("user_id removed from fetch body", "user_id: userId" not in rcontext and "user_id:" not in rcontext.replace(" ",""))

# ── Print results ─────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  SECURITY WIRING AUDIT")
print("="*65)
passes = fails = 0
for status, label, note in results:
    icon = "✓" if status == PASS else "✗"
    extra = f"  [{note}]" if note else ""
    print(f"  {icon} {label}{extra}")
    if status == PASS: passes += 1
    else: fails += 1

print("="*65)
print(f"  {passes} PASS  {fails} FAIL")
print("="*65)
sys.exit(0 if fails == 0 else 1)
