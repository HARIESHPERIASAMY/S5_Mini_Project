import { queryMeshAssistant } from '../frontend/src/api/adapters.js';

const mockRun = {
  id: '2841-demo',
  suite_health_score: 73.5,
  code_coverage: 54.1,
  mutation_score: 100,
  total_files: 1,
  lines_of_code: 280,
  fixes_verified_count: 2,
  bugs_count: 3,
  test_results: Array(14).fill({ name: 'test', status: 'PASSED' }),
  bugs: [
    { 
      id: 'b1', 
      title: 'Strict inequality boundary', 
      file_path: 'main.py', 
      line_number: 41, 
      fix_verified: true, 
      severity: 'HIGH', 
      description: 'Threshold at 100 fails strict comparison.', 
      beginner_explanation: 'Condition total > 100 excludes exact boundary 100.' 
    },
    { 
      id: 'b2', 
      title: 'Zero division hazard', 
      file_path: 'main.py', 
      line_number: 18, 
      fix_verified: false, 
      severity: 'CRITICAL', 
      description: 'Division without checking denominator.' 
    },
    { 
      id: 'b3', 
      title: 'Empty payload error', 
      file_path: 'main.py', 
      line_number: 89, 
      fix_verified: true, 
      severity: 'MEDIUM', 
      description: 'Missing None guard on dictionary.' 
    }
  ]
};

const tests = [
  { q: 'Why was the boundary fix proposed?', answerable: true },
  { q: 'Is the fix safe to merge?', answerable: true },
  { q: 'Summarize this run overview', answerable: true },
  { q: 'Explain this defect for a new teammate', answerable: true },
  { q: 'Draft PR description for verified patches', answerable: true },
  { q: 'What is the memory consumption of the checkout service?', answerable: false },
  { q: 'Who authored the last commit on main.py?', answerable: false },
  { q: 'What is the 99th percentile latency SLA of the endpoint?', answerable: false },
  { q: 'What is the production Kubernetes container image tag?', answerable: false },
  { q: 'How many user signups happened today in the demo shop?', answerable: false }
];

let passed = 0;
console.log("=== SentinelMesh Chatbot Grounding Test (D5) ===");
for (let i = 0; i < tests.length; i++) {
  const t = tests[i];
  const res = queryMeshAssistant(t.q, mockRun);
  const isUnrecorded = res.text.includes("I don't have that in this run");
  const citationsCount = res.citations ? res.citations.length : 0;
  const ok = t.answerable ? (!isUnrecorded && citationsCount > 0) : (isUnrecorded && citationsCount === 0);

  if (ok) passed++;
  const status = ok ? "PASS" : "FAIL";
  console.log(`Q${i + 1}: [${status}] "${t.q}" -> "${res.text.slice(0, 50)}..." (citations: ${citationsCount})`);
}

console.log(`\nResult: ${passed}/${tests.length} passed.`);
if (passed === tests.length) {
  process.exit(0);
} else {
  process.exit(1);
}
