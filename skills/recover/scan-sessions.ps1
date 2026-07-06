<#
.SYNOPSIS
  Mechanism for /recover. Extracts raw facts from recent Claude Code session
  transcripts so the skill (policy) can classify and rank them.

  Emits a JSON array; one record per *.jsonl under ~/.claude/projects whose last
  write is inside the window. Never classifies — that's the agent's job. Read-only.

.PARAMETER Hours
  How far back to consider a session a recovery candidate. Default 6.

.PARAMETER AllProjects
  Scan every ~/.claude/projects/* dir. Default: also all — but the agent filters
  to the project(s) that actually crashed. Use -ProjectDir to pre-narrow.

.PARAMETER ProjectDir
  Restrict to one ~/.claude/projects/<name> dir (the escaped launch path).

.PARAMETER ExcludeId
  Session id (filename stem) to drop — pass the CURRENT session so it isn't
  reported as something to resume.
#>
[CmdletBinding()]
param(
  [double]$Hours = 6,
  [switch]$AllProjects,
  [string]$ProjectDir,
  [string]$ExcludeId
)

$ErrorActionPreference = 'SilentlyContinue'
$root = Join-Path $env:USERPROFILE '.claude\projects'
if (-not (Test-Path $root)) { Write-Output '[]'; return }

$cutoff = (Get-Date).AddHours(-1 * $Hours)

$dirs =
  if ($ProjectDir) { @(Join-Path $root $ProjectDir) }
  else { Get-ChildItem $root -Directory | Select-Object -ExpandProperty FullName }

function Get-Text($content) {
  if ($null -eq $content) { return '' }
  if ($content -is [string]) { return $content }
  $parts = @()
  foreach ($b in $content) {
    switch ($b.type) {
      'text'        { $parts += $b.text }
      'tool_use'    { $parts += ('[tool:' + $b.name + '] ' + ($b.input | ConvertTo-Json -Compress -Depth 6)) }
      'tool_result' { $parts += '[tool_result]' }
    }
  }
  return ($parts -join ' | ')
}
function Clean($s, $n) {
  if ($null -eq $s) { return '' }
  $s = ($s -replace '\s+', ' ').Trim()
  if ($s.Length -gt $n) { return $s.Substring(0, $n) }
  return $s
}

$records = foreach ($d in $dirs) {
  if (-not (Test-Path $d)) { continue }
  $proj = Split-Path $d -Leaf
  $files = Get-ChildItem (Join-Path $d '*.jsonl') | Where-Object { $_.LastWriteTime -gt $cutoff }
  foreach ($f in $files) {
    if ($ExcludeId -and $f.BaseName -eq $ExcludeId) { continue }

    $head = Get-Content $f.FullName -TotalCount 60
    $tail = Get-Content $f.FullName -Tail 20

    # First real user turn = the task (skip context/reminders/tool results).
    $task = ''
    foreach ($ln in $head) {
      try { $o = $ln | ConvertFrom-Json } catch { continue }
      if ($o.type -eq 'user' -and $o.message) {
        $t = Get-Text $o.message.content
        if ($t -and $t.Trim().Length -gt 8 -and $t -notmatch '^\[tool_result' -and $t -notmatch 'system-reminder' -and $t -notmatch 'local-command') { $task = $t; break }
      }
    }

    # Tail-derived state: last cwd/branch/timestamp, last text, last tool, bg-job signal.
    $cwd = ''; $branch = ''; $lastTs = ''; $lastText = ''; $lastTool = ''
    $bg = $false; $bgCmd = ''
    $parsedTail = @()
    foreach ($ln in $tail) {
      try { $o = $ln | ConvertFrom-Json } catch { continue }
      $parsedTail += $o
      if ($o.cwd) { $cwd = $o.cwd }
      if ($o.gitBranch) { $branch = $o.gitBranch }
      if ($o.timestamp) { $lastTs = $o.timestamp }
      if ($o.type -eq 'assistant' -and $o.message.content) {
        foreach ($b in $o.message.content) {
          if ($b.type -eq 'text' -and $b.text.Trim().Length -gt 0) { $lastText = $b.text }
          if ($b.type -eq 'tool_use') {
            $lastTool = $b.name + ' ' + ($b.input | ConvertTo-Json -Compress -Depth 6)
            $cmd = $b.input.command
            if ($b.name -eq 'Bash' -and $b.input.run_in_background) { $bg = $true; $bgCmd = $cmd }
            elseif ($b.name -eq 'Bash' -and $cmd -match '\buntil\b|\bwhile\b[\s\S]*sleep|sleep\s+\d') { $bg = $true; $bgCmd = $cmd }
          }
        }
      }
    }

    # Pending tool = the session's LAST message is an assistant tool_use with no
    # following tool_result → the call was executing when the crash hit.
    $pending = $false
    if ($parsedTail.Count -gt 0) {
      $last = $parsedTail[$parsedTail.Count - 1]
      if ($last.type -eq 'assistant' -and $last.message.content) {
        foreach ($b in $last.message.content) { if ($b.type -eq 'tool_use') { $pending = $true } }
      }
    }

    [pscustomobject][ordered]@{
      id          = $f.BaseName
      project     = $proj
      lastWrite   = $f.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')
      ageMin      = [int][math]::Round(((Get-Date) - $f.LastWriteTime).TotalMinutes)
      sizeKB      = [int][math]::Round($f.Length / 1KB)
      task        = Clean $task 200
      cwd         = $cwd
      branch      = $branch
      lastTs      = $lastTs
      lastText    = Clean $lastText 320
      lastTool    = Clean $lastTool 200
      pendingTool = $pending
      bgJob       = $bg
      bgCmd       = Clean $bgCmd 320
    }
  }
}

$records = @($records | Sort-Object lastWrite -Descending)
if ($records.Count -eq 0)      { Write-Output '[]' }
elseif ($records.Count -eq 1)  { Write-Output ('[' + ($records[0] | ConvertTo-Json -Depth 5) + ']') }
else                           { Write-Output ($records | ConvertTo-Json -Depth 5) }
