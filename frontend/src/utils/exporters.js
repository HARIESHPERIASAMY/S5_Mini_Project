/**
 * Technical Report Exporters for SentinelMesh
 * Generates SARIF 2.1.0 JSON, JUnit XML, and multi-patch zip bundles offline in the browser.
 */

// ---------------------------------------------------------------------------
// 1. SARIF 2.1.0 Exporter
// ---------------------------------------------------------------------------
export function generateSarifReport(runData) {
  if (!runData) return null;

  const bugs = runData.bugs || [];

  const rules = [];
  const ruleMap = new Map();

  bugs.forEach((b) => {
    const ruleId = `SM-${b.category || "LOGIC"}`;
    if (!ruleMap.has(ruleId)) {
      ruleMap.set(ruleId, true);
      rules.push({
        id: ruleId,
        shortDescription: {
          text: `${b.category || "Logic"} Defect Detected by Swarm`
        },
        fullDescription: {
          text: b.description || b.title
        },
        defaultConfiguration: {
          level: b.severity === "CRITICAL" || b.severity === "HIGH" ? "error" : "warning"
        }
      });
    }
  });

  const results = bugs.map((b) => {
    const ruleId = `SM-${b.category || "LOGIC"}`;
    return {
      ruleId,
      message: {
        text: `${b.title}: ${b.description}`
      },
      level: b.severity === "CRITICAL" || b.severity === "HIGH" ? "error" : "warning",
      locations: [
        {
          physicalLocation: {
            artifactLocation: {
              uri: b.file_path || "main.py"
            },
            region: {
              startLine: b.line_number || 1,
              startColumn: 1
            }
          }
        }
      ],
      properties: {
        fixVerified: b.fix_verified,
        confidence: b.confidence,
        consensusScore: b.consensus_score
      }
    };
  });

  return {
    $schema: "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
    version: "2.1.0",
    runs: [
      {
        tool: {
          driver: {
            name: "SentinelMesh Autonomous Testing Swarm",
            semanticVersion: "2.0.0",
            informationUri: "http://localhost:8000",
            rules
          }
        },
        invocations: [
          {
            executionSuccessful: runData.status === "completed",
            endTimeUtc: runData.completed_at || new Date().toISOString()
          }
        ],
        results
      }
    ]
  };
}

// ---------------------------------------------------------------------------
// 2. JUnit XML Exporter
// ---------------------------------------------------------------------------
export function generateJUnitXml(runData) {
  if (!runData) return "";

  const tests = runData.test_results || [];
  const failures = tests.filter((t) => t.status === "failed").length;
  const total = tests.length || (runData.bugs?.length || 0);

  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  xml += `<testsuites name="SentinelMesh" tests="${total}" failures="${failures}" errors="0" time="0.8">\n`;
  xml += `  <testsuite name="SwarmSuite" tests="${total}" failures="${failures}" errors="0" time="0.8">\n`;

  if (tests.length > 0) {
    tests.forEach((t) => {
      xml += `    <testcase classname="${escapeXml(t.test_file || 'test')}" name="${escapeXml(t.test_name || 'test_func')}" time="${((t.duration_ms || 10) / 1000).toFixed(3)}">\n`;
      if (t.status === "failed") {
        xml += `      <failure message="${escapeXml(t.error_message || 'AssertionError')}">${escapeXml(t.stack_trace || t.error_message || '')}</failure>\n`;
      }
      xml += `    </testcase>\n`;
    });
  } else {
    // Generate from bugs if test_results array empty
    (runData.bugs || []).forEach((b) => {
      xml += `    <testcase classname="${escapeXml(b.file_path)}" name="test_line_${b.line_number}" time="0.050">\n`;
      xml += `      <failure message="${escapeXml(b.title)}">${escapeXml(b.description)}</failure>\n`;
      xml += `    </testcase>\n`;
    });
  }

  xml += `  </testsuite>\n`;
  xml += `</testsuites>`;
  return xml;
}

function escapeXml(unsafe) {
  if (!unsafe) return "";
  return String(unsafe).replace(/[<>&'"]/g, (c) => {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
      default: return c;
    }
  });
}

// ---------------------------------------------------------------------------
// 3. Lightweight Pure-JS ZIP File Creator
// ---------------------------------------------------------------------------
export function createZipBundle(files) {
  // files: Array<{ name: string, content: string }>
  const textEncoder = new TextEncoder();
  const fileRecords = [];
  let offset = 0;

  files.forEach((f) => {
    const nameBytes = textEncoder.encode(f.name);
    const contentBytes = textEncoder.encode(f.content);

    // CRC32
    const crc = computeCrc32(contentBytes);

    // Local file header (30 bytes + name + content)
    const header = new Uint8Array(30 + nameBytes.length);
    const dv = new DataView(header.buffer);
    dv.setUint32(0, 0x04034b50, true); // Local file header signature
    dv.setUint16(4, 10, true);         // Version needed
    dv.setUint16(6, 0, true);          // Flags
    dv.setUint16(8, 0, true);          // Compression method (0 = store)
    dv.setUint16(10, 0, true);         // Mod time
    dv.setUint16(12, 0, true);         // Mod date
    dv.setUint32(14, crc, true);       // CRC-32
    dv.setUint32(18, contentBytes.length, true); // Compressed size
    dv.setUint32(22, contentBytes.length, true); // Uncompressed size
    dv.setUint16(26, nameBytes.length, true);    // Filename length
    dv.setUint16(28, 0, true);         // Extra field length
    header.set(nameBytes, 30);

    fileRecords.push({
      header,
      contentBytes,
      nameBytes,
      offset,
      crc,
      size: contentBytes.length
    });

    offset += header.length + contentBytes.length;
  });

  // Central directory
  let centralDirSize = 0;
  const centralDirParts = [];

  fileRecords.forEach((r) => {
    const cd = new Uint8Array(46 + r.nameBytes.length);
    const cdv = new DataView(cd.buffer);
    cdv.setUint32(0, 0x02014b50, true); // Central directory header signature
    cdv.setUint16(4, 10, true);          // Version made by
    cdv.setUint16(6, 10, true);          // Version needed
    cdv.setUint16(8, 0, true);           // Flags
    cdv.setUint16(10, 0, true);          // Compression method
    cdv.setUint16(12, 0, true);          // Mod time
    cdv.setUint16(14, 0, true);          // Mod date
    cdv.setUint32(16, r.crc, true);      // CRC-32
    cdv.setUint32(20, r.size, true);     // Compressed size
    cdv.setUint32(24, r.size, true);     // Uncompressed size
    cdv.setUint16(28, r.nameBytes.length, true); // Filename length
    cdv.setUint16(30, 0, true);          // Extra field length
    cdv.setUint16(32, 0, true);          // Comment length
    cdv.setUint16(34, 0, true);          // Disk number
    cdv.setUint16(36, 0, true);          // Internal attributes
    cdv.setUint32(38, 0, true);          // External attributes
    cdv.setUint32(42, r.offset, true);   // Relative offset of local header
    cd.set(r.nameBytes, 46);

    centralDirParts.push(cd);
    centralDirSize += cd.length;
  });

  // End of Central Directory Record (22 bytes)
  const eocd = new Uint8Array(22);
  const edv = new DataView(eocd.buffer);
  edv.setUint32(0, 0x06054b50, true);          // EOCD signature
  edv.setUint16(4, 0, true);                   // Disk number
  edv.setUint16(6, 0, true);                   // Start disk
  edv.setUint16(8, fileRecords.length, true);  // Records on disk
  edv.setUint16(10, fileRecords.length, true); // Total records
  edv.setUint32(12, centralDirSize, true);     // Central directory size
  edv.setUint32(16, offset, true);             // Offset of central directory
  edv.setUint16(20, 0, true);                  // Comment length

  // Combine into single Blob
  const blobParts = [];
  fileRecords.forEach((r) => {
    blobParts.push(r.header);
    blobParts.push(r.contentBytes);
  });
  centralDirParts.forEach((p) => blobParts.push(p));
  blobParts.push(eocd);

  return new Blob(blobParts, { type: "application/zip" });
}

function computeCrc32(bytes) {
  let crc = -1;
  for (let i = 0; i < bytes.length; i++) {
    crc = (crc >>> 8) ^ CRC32_TABLE[(crc ^ bytes[i]) & 0xFF];
  }
  return (crc ^ -1) >>> 0;
}

const CRC32_TABLE = new Uint32Array(256);
for (let i = 0; i < 256; i++) {
  let c = i;
  for (let j = 0; j < 8; j++) {
    c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
  }
  CRC32_TABLE[i] = c >>> 0;
}
