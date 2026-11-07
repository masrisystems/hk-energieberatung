#!/usr/bin/env node

/**
 * Git Time & Ticket Extractor CLI
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const options = {
  repoDir: process.cwd(),
  outDir: process.cwd(),
  since: null,
  until: null,
  clientName: 'Client',
  projectName: 'Project',
  sanitizeClockTimes: true,
  gapMinutes: 90,
  minSessionMinutes: 30,
  perCommitMinutes: 25
};

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg === '--repo' && args[i + 1]) options.repoDir = path.resolve(args[++i]);
  else if (arg === '--out-dir' && args[i + 1]) options.outDir = path.resolve(args[++i]);
  else if (arg === '--since' && args[i + 1]) options.since = args[++i];
  else if (arg === '--until' && args[i + 1]) options.until = args[++i];
  else if (arg === '--client' && args[i + 1]) options.clientName = args[++i];
  else if (arg === '--project' && args[i + 1]) options.projectName = args[++i];
  else if (arg === '--include-clock-times') options.sanitizeClockTimes = false;
  else if (arg === '--gap' && args[i + 1]) options.gapMinutes = parseInt(args[++i], 10);
}

function cleanSubject(s) {
  if (!s) return '';
  return s
    .split('\n')[0]
    .replace(/[\/\\]+$/, '')
    .replace(/--+$/, '')
    .replace(/---+/g, ' — ')
    .replace(/\|/g, '/')
    .trim();
}

function extractCommits(repoDir, since, until) {
  let gitCmd = 'git log --all --date=iso-strict --pretty=format:"COMMIT_SEP%h||%H||%an||%ae||%ad||%s||%b"';
  if (since) gitCmd += ` --since="${since}"`;
  if (until) gitCmd += ` --until="${until}"`;

  try {
    const output = execSync(gitCmd, { cwd: repoDir, maxBuffer: 30 * 1024 * 1024 }).toString();
    const rawEntries = output.split('COMMIT_SEP').map(e => e.trim()).filter(Boolean);

    const commits = [];
    const seen = new Set();

    for (const raw of rawEntries) {
      const parts = raw.split('||');
      if (parts.length < 6) continue;
      const shortHash = parts[0].trim();
      const hash = parts[1].trim();
      const author = parts[2].trim();
      const email = parts[3].trim();
      const dateStr = parts[4].trim();
      const subject = parts[5].trim();
      const body = parts.slice(6).join('||').trim();

      if (seen.has(shortHash)) continue;
      seen.add(shortHash);

      commits.push({
        shortHash,
        hash,
        author,
        email,
        dateStr,
        date: new Date(dateStr),
        subject,
        body,
        isBot: author.toLowerCase().includes('dependabot') || email.toLowerCase().includes('dependabot')
      });
    }

    commits.sort((a, b) => a.date - b.date);
    return commits;
  } catch (err) {
    console.error(`Error executing git log in ${repoDir}:`, err.message);
    return [];
  }
}

function clusterSessions(commits, options) {
  const days = {};
  for (const c of commits) {
    const dateBerlin = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin' }).format(c.date);
    if (!days[dateBerlin]) days[dateBerlin] = [];
    days[dateBerlin].push(c);
  }

  const dailySessions = [];
  for (const [day, dayCommits] of Object.entries(days)) {
    const humanCommits = dayCommits.filter(c => !c.isBot);
    if (humanCommits.length === 0) continue;

    const sessions = [];
    let currentSession = [humanCommits[0]];

    for (let i = 1; i < humanCommits.length; i++) {
      const prev = humanCommits[i - 1];
      const curr = humanCommits[i];
      const diffMinutes = (curr.date - prev.date) / (1000 * 60);

      if (diffMinutes <= options.gapMinutes) {
        currentSession.push(curr);
      } else {
        sessions.push(currentSession);
        currentSession = [curr];
      }
    }
    if (currentSession.length > 0) sessions.push(currentSession);

    const sessionDetails = sessions.map((sess, idx) => {
      const first = sess[0];
      const last = sess[sess.length - 1];
      const elapsedMinutes = Math.round((last.date - first.date) / (1000 * 60));
      const estimatedMinutes = Math.max(elapsedMinutes + options.minSessionMinutes, sess.length * options.perCommitMinutes);
      const estimatedHours = parseFloat((estimatedMinutes / 60).toFixed(2));

      const startTime = first.date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Berlin' });
      const endTime = last.date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Berlin' });

      return {
        sessionNum: idx + 1,
        startTime,
        endTime,
        commitCount: sess.length,
        elapsedMinutes,
        estimatedMinutes,
        estimatedHours,
        commits: sess
      };
    });

    const totalDayEstimatedHours = parseFloat(sessionDetails.reduce((sum, s) => sum + s.estimatedHours, 0).toFixed(2));

    dailySessions.push({
      day,
      commits: dayCommits,
      humanCommits,
      sessions: sessionDetails,
      totalDayEstimatedHours
    });
  }

  const monthlySummary = {};
  for (const ds of dailySessions) {
    const monthKey = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(new Date(ds.day));
    if (!monthlySummary[monthKey]) monthlySummary[monthKey] = { commits: 0, hours: 0, days: 0 };
    monthlySummary[monthKey].commits += ds.humanCommits.length;
    monthlySummary[monthKey].hours += ds.totalDayEstimatedHours;
    monthlySummary[monthKey].days += 1;
  }

  const totalHours = parseFloat(dailySessions.reduce((sum, d) => sum + d.totalDayEstimatedHours, 0).toFixed(2));

  return {
    dailySessions,
    monthlySummary,
    totalHours
  };
}

const allCommits = extractCommits(options.repoDir, options.since, options.until);
const humanCommits = allCommits.filter(c => !c.isBot);
const clustered = clusterSessions(allCommits, options);

console.log(`[Git Time Extractor] Project: ${options.projectName} | Client: ${options.clientName}`);
console.log(`Total Commits: ${allCommits.length} (Human: ${humanCommits.length})`);
console.log(`Active Work Days: ${clustered.dailySessions.length}`);
console.log(`Total Estimated Effort: ${clustered.totalHours.toFixed(2)} Hours`);

if (!fs.existsSync(options.outDir)) {
  fs.mkdirSync(options.outDir, { recursive: true });
}

// Generate Timings CSV
let timingsCsv = 'Date,Work_Unit,Commits_Count,Effective_Hours,Activities_Summary\n';
clustered.dailySessions.forEach(ds => {
  ds.sessions.forEach(sess => {
    const desc = sess.commits.map(c => cleanSubject(c.subject)).join('; ').replace(/"/g, '""');
    timingsCsv += `${ds.day},Unit ${sess.sessionNum},${sess.commitCount},${sess.estimatedHours},"${desc}"\n`;
  });
});
fs.writeFileSync(path.join(options.outDir, 'timings_report.csv'), timingsCsv, 'utf8');

// Generate JSON Output
fs.writeFileSync(path.join(options.outDir, 'extracted_timings.json'), JSON.stringify({ options, stats: { totalCommits: allCommits.length, humanCommits: humanCommits.length, activeDays: clustered.dailySessions.length, totalHours: clustered.totalHours }, monthlySummary: clustered.monthlySummary, dailySessions: clustered.dailySessions }, null, 2), 'utf8');

console.log(`Generated timings_report.csv and extracted_timings.json in ${options.outDir}`);
